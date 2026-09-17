from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.aplicacao.servicos.authorization_service import AuthorizationService
from app.apresentacao.schemas.appointment import AppointmentCreate, AppointmentUpdate
from app.repositorio.modelos.appointment import Appointment
from app.repositorio.modelos.appointment_user import AppointmentUser
from app.repositorio.modelos.user import User


class AppointmentService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.authz = AuthorizationService(db)

    def list_for_user(self, current_user: User) -> list[Appointment]:
        statement = select(Appointment).options(selectinload(Appointment.participants))
        if not current_user.is_master:
            statement = statement.join(AppointmentUser).where(AppointmentUser.user_id == current_user.id)
        return list(self.db.execute(statement.order_by(Appointment.start_datetime)).unique().scalars())

    def create(self, payload: AppointmentCreate, current_user: User) -> Appointment:
        user_ids = set(payload.user_ids)
        user_ids.add(current_user.id)

        appointment = Appointment(
            title=payload.title,
            body=payload.body,
            start_datetime=payload.start_datetime,
            end_datetime=payload.end_datetime,
            url_maps=payload.url_maps,
            location_name=payload.location_name,
            location_lat=payload.location_lat,
            location_lng=payload.location_lng,
        )
        self.db.add(appointment)
        self.db.flush()

        for user_id in user_ids:
            self._ensure_user_exists(user_id)
            self.db.add(AppointmentUser(user_id=user_id, appointment_id=appointment.id))

        self.db.commit()
        self.db.refresh(appointment)
        return self._get_with_participants(appointment.id)

    def update(self, appointment_id: int, payload: AppointmentUpdate, current_user: User) -> Appointment:
        appointment = self._get_or_404(appointment_id)
        self.authz.ensure_can_manage_appointment(current_user, appointment_id)

        data = payload.model_dump(exclude_unset=True)
        start_datetime = data.get("start_datetime", appointment.start_datetime)
        end_datetime = data.get("end_datetime", appointment.end_datetime)
        if end_datetime <= start_datetime:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Intervalo invalido")

        for field, value in data.items():
            setattr(appointment, field, value)

        self.db.commit()
        return self._get_with_participants(appointment_id)

    def delete(self, appointment_id: int, current_user: User) -> None:
        appointment = self._get_or_404(appointment_id)
        self.authz.ensure_can_manage_appointment(current_user, appointment_id)
        self.db.delete(appointment)
        self.db.commit()

    def link_user(self, appointment_id: int, user_id: int, current_user: User) -> AppointmentUser:
        self._get_or_404(appointment_id)
        self.authz.ensure_can_manage_appointment(current_user, appointment_id)
        self._ensure_user_exists(user_id)

        existing = self._get_link(appointment_id, user_id)
        if existing:
            return existing

        link = AppointmentUser(user_id=user_id, appointment_id=appointment_id)
        self.db.add(link)
        self.db.commit()
        self.db.refresh(link)
        return link

    def confirm_presence(self, appointment_id: int, current_user: User) -> AppointmentUser:
        self._get_or_404(appointment_id)
        self.authz.ensure_can_view_appointment(current_user, appointment_id)
        link = self._get_link(appointment_id, current_user.id)
        if not link:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vinculo nao encontrado")
        link.is_confirmed = True
        self.db.commit()
        self.db.refresh(link)
        return link

    def unlink_user(self, appointment_id: int, user_id: int, current_user: User) -> None:
        self._get_or_404(appointment_id)
        self.authz.ensure_can_unlink_user(current_user, user_id)
        if not current_user.is_master:
            self.authz.ensure_can_view_appointment(current_user, appointment_id)

        link = self._get_link(appointment_id, user_id)
        if not link:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vinculo nao encontrado")

        self.db.delete(link)
        self.db.commit()

    def _get_or_404(self, appointment_id: int) -> Appointment:
        appointment = self.db.get(Appointment, appointment_id)
        if not appointment:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Compromisso nao encontrado")
        return appointment

    def _get_with_participants(self, appointment_id: int) -> Appointment:
        statement = (
            select(Appointment)
            .options(selectinload(Appointment.participants))
            .where(Appointment.id == appointment_id)
        )
        return self.db.execute(statement).scalar_one()

    def _get_link(self, appointment_id: int, user_id: int) -> AppointmentUser | None:
        statement = select(AppointmentUser).where(
            AppointmentUser.appointment_id == appointment_id,
            AppointmentUser.user_id == user_id,
        )
        return self.db.execute(statement).scalar_one_or_none()

    def _ensure_user_exists(self, user_id: int) -> None:
        if not self.db.get(User, user_id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Usuario {user_id} nao encontrado")

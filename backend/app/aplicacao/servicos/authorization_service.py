from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.repositorio.modelos.appointment_user import AppointmentUser
from app.repositorio.modelos.user import User


class AuthorizationService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def ensure_can_view_appointment(self, user: User, appointment_id: int) -> None:
        if user.is_master:
            return
        if not self._has_link(user.id, appointment_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Compromisso nao permitido")

    def ensure_can_unlink_user(self, current_user: User, target_user_id: int) -> None:
        if current_user.is_master:
            return
        if current_user.id != target_user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Nao pode desvincular outro usuario")

    def ensure_can_manage_appointment(self, user: User, appointment_id: int) -> None:
        self.ensure_can_view_appointment(user, appointment_id)

    def _has_link(self, user_id: int, appointment_id: int) -> bool:
        statement = select(AppointmentUser.id).where(
            AppointmentUser.user_id == user_id,
            AppointmentUser.appointment_id == appointment_id,
        )
        return self.db.execute(statement).scalar_one_or_none() is not None

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.aplicacao.helpers.dependencies import get_current_user
from app.aplicacao.servicos.appointment_service import AppointmentService
from app.apresentacao.schemas.appointment import (
    AppointmentCreate,
    AppointmentRead,
    AppointmentUpdate,
    AppointmentUserRead,
    LinkUserRequest,
)
from app.repositorio.db.context import get_db
from app.repositorio.modelos.user import User

router = APIRouter(prefix="/appointments", tags=["appointments"])


@router.get("", response_model=list[AppointmentRead])
def list_appointments(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[AppointmentRead]:
    return AppointmentService(db).list_for_user(current_user)


@router.post("", response_model=AppointmentRead, status_code=status.HTTP_201_CREATED)
def create_appointment(
    payload: AppointmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AppointmentRead:
    return AppointmentService(db).create(payload, current_user)


@router.put("/{appointment_id}", response_model=AppointmentRead)
def update_appointment(
    appointment_id: int,
    payload: AppointmentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AppointmentRead:
    return AppointmentService(db).update(appointment_id, payload, current_user)


@router.delete("/{appointment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_appointment(
    appointment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    AppointmentService(db).delete(appointment_id, current_user)


@router.post("/{appointment_id}/users", response_model=AppointmentUserRead)
def link_user(
    appointment_id: int,
    payload: LinkUserRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AppointmentUserRead:
    return AppointmentService(db).link_user(appointment_id, payload.user_id, current_user)


@router.post("/{appointment_id}/confirm", response_model=AppointmentUserRead)
def confirm_presence(
    appointment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AppointmentUserRead:
    return AppointmentService(db).confirm_presence(appointment_id, current_user)


@router.delete("/{appointment_id}/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def unlink_user(
    appointment_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    AppointmentService(db).unlink_user(appointment_id, user_id, current_user)

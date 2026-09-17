from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.aplicacao.helpers.dependencies import get_current_user, require_master
from app.aplicacao.servicos.user_service import UserService
from app.apresentacao.schemas.user import UserCreate, UserRead, UserUpdate
from app.repositorio.db.context import get_db
from app.repositorio.modelos.user import User

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserRead)
def me(current_user: User = Depends(get_current_user)) -> User:
    return current_user


@router.post("", response_model=UserRead, dependencies=[Depends(require_master)])
def create_user(payload: UserCreate, db: Session = Depends(get_db)) -> User:
    return UserService(db).create(payload)


@router.get("", response_model=list[UserRead], dependencies=[Depends(require_master)])
def list_users(db: Session = Depends(get_db)) -> list[User]:
    return UserService(db).list_active()


@router.get("/{user_id}", response_model=UserRead, dependencies=[Depends(require_master)])
def get_user(user_id: int, db: Session = Depends(get_db)) -> User:
    return UserService(db).get(user_id)


@router.put("/{user_id}", response_model=UserRead)
def update_user(
    user_id: int,
    payload: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_master),
) -> User:
    return UserService(db).update(user_id, payload, current_user)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_master),
) -> None:
    UserService(db).delete(user_id, current_user)

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.aplicacao.helpers.security import hash_password, verify_password
from app.apresentacao.schemas.user import UserCreate, UserUpdate
from app.repositorio.modelos.user import User


class UserService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def authenticate(self, username: str, password: str) -> User | None:
        user = self.db.execute(select(User).where(User.username == username)).scalar_one_or_none()
        if not user or not user.is_active:
            return None
        if not verify_password(password, user.password):
            return None
        return user

    def create(self, payload: UserCreate) -> User:
        existing = self.db.execute(select(User).where(User.username == payload.username)).scalar_one_or_none()
        if existing:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username ja existe")

        user = User(
            username=payload.username,
            name=payload.name,
            password=hash_password(payload.password),
            is_master=payload.is_master,
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def list_active(self) -> list[User]:
        return list(self.db.execute(select(User).where(User.is_active.is_(True))).scalars())

    def get(self, user_id: int) -> User:
        user = self.db.get(User, user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario nao encontrado")
        return user

    def update(self, user_id: int, payload: UserUpdate, current_user: User) -> User:
        user = self.get(user_id)
        data = payload.model_dump(exclude_unset=True)

        if user.id == current_user.id and data.get("is_active") is False:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Nao e possivel desativar o proprio usuario",
            )

        if "username" in data and data["username"] != user.username:
            existing = self.db.execute(select(User).where(User.username == data["username"])).scalar_one_or_none()
            if existing:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username ja existe")

        if "password" in data:
            data["password"] = hash_password(data["password"])

        for field, value in data.items():
            setattr(user, field, value)

        self.db.commit()
        self.db.refresh(user)
        return user

    def delete(self, user_id: int, current_user: User) -> None:
        user = self.get(user_id)
        if user.id == current_user.id:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Nao e possivel excluir o proprio usuario",
            )

        user.is_active = False
        self.db.commit()

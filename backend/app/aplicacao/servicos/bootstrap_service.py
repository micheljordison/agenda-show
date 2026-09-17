from sqlalchemy import select
from sqlalchemy.orm import Session

from app.aplicacao.helpers.config import settings
from app.aplicacao.helpers.security import hash_password
from app.repositorio.modelos.user import User


class BootstrapService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def ensure_initial_master(self) -> None:
        if not settings.initial_master_username or not settings.initial_master_password:
            return

        existing = self.db.execute(
            select(User).where(User.username == settings.initial_master_username)
        ).scalar_one_or_none()
        if existing:
            return

        user = User(
            username=settings.initial_master_username,
            name=settings.initial_master_name or settings.initial_master_username,
            password=hash_password(settings.initial_master_password),
            is_master=True,
            is_active=True,
        )
        self.db.add(user)
        self.db.commit()

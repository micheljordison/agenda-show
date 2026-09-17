import os
from collections.abc import Generator
from datetime import datetime

os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["JWT_SECRET_KEY"] = "test-secret"
os.environ["INITIAL_MASTER_USERNAME"] = ""
os.environ["INITIAL_MASTER_PASSWORD"] = ""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.aplicacao.helpers.security import hash_password
from app.main import app
from app.repositorio.db.context import Base, get_db
from app.repositorio.modelos.appointment import Appointment
from app.repositorio.modelos.appointment_user import AppointmentUser
from app.repositorio.modelos.user import User

engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


@pytest.fixture()
def db() -> Generator[Session, None, None]:
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client(db: Session) -> Generator[TestClient, None, None]:
    def override_get_db() -> Generator[Session, None, None]:
        yield db

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def create_user(db: Session, username: str, is_master: bool = False) -> User:
    user = User(
        username=username,
        name=username.title(),
        password=hash_password("password123"),
        is_master=is_master,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def login(client: TestClient, username: str) -> dict[str, str]:
    response = client.post("/api/auth/login", data={"username": username, "password": "password123"})
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def create_appointment(db: Session, title: str, user: User) -> Appointment:
    appointment = Appointment(
        title=title,
        body="Detalhes",
        start_datetime=datetime(2026, 9, 3, 10, 0, 0),
        end_datetime=datetime(2026, 9, 3, 11, 0, 0),
    )
    db.add(appointment)
    db.flush()
    db.add(AppointmentUser(user_id=user.id, appointment_id=appointment.id))
    db.commit()
    db.refresh(appointment)
    return appointment

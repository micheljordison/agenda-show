import pytest
from pydantic import ValidationError
from sqlalchemy.exc import OperationalError

from app.aplicacao.helpers.config import Settings
from app.main import app
from app.repositorio.db.context import get_db


def production_settings(**overrides):
    values = {
        "environment": "production",
        "database_url": "postgresql+psycopg://agenda:password@database/agenda?sslmode=require",
        "jwt_secret_key": "a" * 48,
        "backend_cors_origins": "",
        "initial_master_password": None,
    }
    return Settings(_env_file=None, **(values | overrides))


def test_production_accepts_same_origin():
    assert production_settings().cors_origins == []


@pytest.mark.parametrize("overrides", [
    {"jwt_secret_key": "dev-secret"},
    {"jwt_secret_key": "change-this-to-a-random-secret-of-at-least-32-characters"},
    {"database_url": "sqlite:///agenda.db"},
    {"backend_cors_origins": "*"},
    {"backend_cors_origins": "http://example.com"},
    {"initial_master_password": "change-this-admin-password"},
    {"jwt_algorithm": "HS512"},
])
def test_production_rejects_unsafe_configuration(overrides):
    with pytest.raises(ValidationError):
        production_settings(**overrides)


def test_health_and_readiness(client):
    assert client.get("/health").status_code == 200
    assert client.get("/api/ready").status_code == 200


def test_database_failure_is_not_exposed(client):
    class UnavailableDatabase:
        def execute(self, statement):
            raise OperationalError("sensitive query", {}, Exception("secret password"))

    app.dependency_overrides[get_db] = lambda: UnavailableDatabase()
    assert client.get("/health").status_code == 200
    response = client.get("/api/ready")
    assert response.status_code == 503
    assert response.json() == {"detail": "Service unavailable"}

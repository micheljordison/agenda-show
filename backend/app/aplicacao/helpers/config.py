from typing import Literal

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    environment: Literal["development", "test", "production"] = "development"
    database_url: str = "sqlite:///./agenda.db"
    jwt_secret_key: str = "dev-secret"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 120
    backend_cors_origins: str = "http://localhost:4000"
    initial_master_username: str | None = None
    initial_master_name: str | None = None
    initial_master_password: str | None = None

    @model_validator(mode="after")
    def validate_production(self) -> "Settings":
        if self.environment != "production":
            return self
        if len(self.jwt_secret_key) < 32 or self.jwt_secret_key.lower().startswith(("change", "dev-", "test-")):
            raise ValueError("Production requires a random JWT_SECRET_KEY of at least 32 characters")
        if not self.database_url.startswith("postgresql+psycopg://"):
            raise ValueError("Production requires a PostgreSQL DATABASE_URL using psycopg")
        if self.jwt_algorithm != "HS256":
            raise ValueError("Only HS256 is supported in production")
        if any(not origin.startswith("https://") or "*" in origin for origin in self.cors_origins):
            raise ValueError("Production CORS origins must be explicit HTTPS origins (or empty for same-origin)")
        if self.initial_master_password and (
            len(self.initial_master_password) < 16 or self.initial_master_password.lower().startswith("change")
        ):
            raise ValueError("Production requires a strong INITIAL_MASTER_PASSWORD of at least 16 characters")
        return self

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.backend_cors_origins.split(",") if origin.strip()]


settings = Settings()

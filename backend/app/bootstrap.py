"""Run once after migrations, before starting the production service."""

from app.aplicacao.helpers.config import settings
from app.aplicacao.servicos.bootstrap_service import BootstrapService
from app.repositorio.db.context import SessionLocal


def main() -> None:
    if not settings.initial_master_username or not settings.initial_master_password:
        raise RuntimeError("INITIAL_MASTER_USERNAME and INITIAL_MASTER_PASSWORD are required for bootstrap")
    with SessionLocal() as db:
        BootstrapService(db).ensure_initial_master()


if __name__ == "__main__":
    main()

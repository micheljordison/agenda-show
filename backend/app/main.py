from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.aplicacao.helpers.config import settings
from app.aplicacao.servicos.bootstrap_service import BootstrapService
from app.apresentacao.controllers import appointments, auth, users
from app.repositorio.db.context import SessionLocal, get_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    if settings.environment != "production":
        with SessionLocal() as db:
            BootstrapService(db).ensure_initial_master()
    yield


app = FastAPI(
    title="Sistema de Compromissos",
    lifespan=lifespan,
    docs_url=None if settings.environment == "production" else "/docs",
    redoc_url=None if settings.environment == "production" else "/redoc",
    openapi_url=None if settings.environment == "production" else "/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(appointments.router, prefix="/api")


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/ready", include_in_schema=False)
def readiness_check(db: Session = Depends(get_db)) -> dict[str, str]:
    try:
        # Also verifies that migrations have created the application schema.
        db.execute(text("SELECT id FROM users LIMIT 1"))
    except SQLAlchemyError:
        raise HTTPException(status_code=503, detail="Service unavailable") from None
    return {"status": "ok"}

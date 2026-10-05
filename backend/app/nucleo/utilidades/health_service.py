import logging
from typing import Literal

from pydantic import BaseModel
from sqlalchemy.exc import SQLAlchemyError

from app.base_datos.repositories.health_repository import HealthRepository
from app.configuracion.constants import APP_VERSION

logger = logging.getLogger(__name__)


class HealthResponse(BaseModel):
    status: Literal["ok", "degraded"]
    api: Literal["ok"] = "ok"
    database: Literal["ok", "unavailable"]
    pgvector: Literal["ok", "unavailable"]
    version: str = APP_VERSION


class HealthService:
    def __init__(self, repository: HealthRepository):
        self.repository = repository

    def check(self) -> HealthResponse:
        try:
            database_ok, vector_ok = self.repository.check()
        except SQLAlchemyError:
            # La excepción original puede contener datos de conexión. No registrarla.
            logger.warning("Database health check failed")
            database_ok, vector_ok = False, False
        return HealthResponse(
            status="ok" if database_ok and vector_ok else "degraded",
            database="ok" if database_ok else "unavailable",
            pgvector="ok" if vector_ok else "unavailable",
        )

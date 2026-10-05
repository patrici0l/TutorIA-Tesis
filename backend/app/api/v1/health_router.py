from typing import Annotated

from fastapi import APIRouter, Depends, Response
from sqlalchemy import Engine

from app.base_datos.repositories.health_repository import HealthRepository
from app.base_datos.session import get_engine
from app.nucleo.utilidades.health_service import HealthResponse, HealthService

router = APIRouter(tags=["health"])


def get_health_service(engine: Annotated[Engine, Depends(get_engine)]) -> HealthService:
    return HealthService(HealthRepository(engine))


@router.get("/health", response_model=HealthResponse, responses={503: {"model": HealthResponse}})
def get_health(
    response: Response,
    service: Annotated[HealthService, Depends(get_health_service)],
) -> HealthResponse:
    """Comprueba disponibilidad real de PostgreSQL y de la extensión vector."""
    result = service.check()
    if result.status != "ok":
        response.status_code = 503
    return result

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.base_datos.session import get_session
from app.modulos.documentos.router import Owner
from app.modulos.metricas.repositorios.metrics_repository import MetricsRepository
from app.modulos.metricas.schemas import MetricsSummary
from app.modulos.metricas.servicios.metrics_service import MetricsService

router = APIRouter(prefix="/metrics", tags=["metrics"])


def get_metrics_service(db: Annotated[Session, Depends(get_session)]):
    return MetricsService(MetricsRepository(db))


@router.get("", response_model=MetricsSummary)
def summary(user: Owner, service: Annotated[MetricsService, Depends(get_metrics_service)]):
    return service.summary(user.id)

# Expone intentos e historial privado de práctica con corrección en servidor.
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.base_datos.session import get_session
from app.modulos.practica.repository import PracticeRepository
from app.modulos.practica.schemas import PracticeProgress, PracticeResult, PracticeSubmission
from app.modulos.practica.service import PracticeService
from app.modulos.usuarios.models import User
from app.nucleo.dependencias.auth import get_current_user, require_client_header

router = APIRouter(prefix="/practice", tags=["practice"])


def get_practice_service(db: Annotated[Session, Depends(get_session)]):
    return PracticeService(PracticeRepository(db))


CurrentUser = Annotated[User, Depends(get_current_user)]
Service = Annotated[PracticeService, Depends(get_practice_service)]


@router.post(
    "/attempts", response_model=PracticeResult, dependencies=[Depends(require_client_header)]
)
def save(submission: PracticeSubmission, user: CurrentUser, service: Service):
    return service.save(user.id, submission)


@router.get("/attempts", response_model=PracticeProgress)
def progress(
    user: CurrentUser,
    service: Service,
    offset: Annotated[int, Query(ge=0, le=100000)] = 0,
    limit: Annotated[int, Query(ge=1, le=20)] = 10,
):
    return service.page(user.id, offset, limit)

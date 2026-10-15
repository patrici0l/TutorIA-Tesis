from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.base_datos.session import get_session
from app.modulos.estudiantes.assignment_repository import AssignmentRepository
from app.modulos.estudiantes.assignment_schemas import (
    AssignmentPage,
    AssignmentResult,
    AssignmentSubmission,
)
from app.modulos.estudiantes.assignment_service import AssignmentService
from app.modulos.usuarios.models import User
from app.nucleo.dependencias.auth import get_current_user, require_client_header

router = APIRouter(prefix="/practice/assignments", tags=["practice"])


def get_assignment_service(db: Annotated[Session, Depends(get_session)]):
    return AssignmentService(AssignmentRepository(db))


CurrentUser = Annotated[User, Depends(get_current_user)]
Service = Annotated[AssignmentService, Depends(get_assignment_service)]


@router.post("", response_model=AssignmentResult, dependencies=[Depends(require_client_header)])
def create(submission: AssignmentSubmission, user: CurrentUser, service: Service):
    return service.create(user, submission)


@router.get("", response_model=AssignmentPage)
def page(
    user: CurrentUser,
    service: Service,
    offset: Annotated[int, Query(ge=0, le=100000)] = 0,
    limit: Annotated[int, Query(ge=1, le=20)] = 10,
):
    return service.page(user, offset, limit)


@router.get("/{identifier}", response_model=AssignmentResult)
def detail(identifier: UUID, user: CurrentUser, service: Service):
    return service.detail(user, identifier)

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.base_datos.session import get_session
from app.modulos.perfiles.repositorios.profile_repository import ProfileRepository
from app.modulos.perfiles.schemas import ProfilePage, ProfileRequest, ProfileResponse
from app.modulos.perfiles.servicios.profile_service import ProfileService
from app.modulos.usuarios.models import User
from app.nucleo.dependencias.auth import get_current_user, require_client_header

router = APIRouter(prefix="/profiles", tags=["profiles"])


def get_profile_owner(user: Annotated[User, Depends(get_current_user)]):
    if user.rol not in {"teacher", "admin"}:
        raise HTTPException(403, "La gestión de perfiles requiere permisos de docente.")
    return user


def get_profile_service(db: Annotated[Session, Depends(get_session)]):
    return ProfileService(ProfileRepository(db))


Owner = Annotated[User, Depends(get_profile_owner)]
Service = Annotated[ProfileService, Depends(get_profile_service)]


@router.post(
    "",
    response_model=ProfileResponse,
    status_code=201,
    dependencies=[Depends(require_client_header)],
)
def create(request: ProfileRequest, user: Owner, service: Service):
    return service.create(request, user.id)


@router.get("", response_model=ProfilePage)
def page(
    user: Owner,
    service: Service,
    offset: Annotated[int, Query(ge=0, le=100000)] = 0,
    limit: Annotated[int, Query(ge=1, le=20)] = 10,
):
    return service.page(user.id, offset, limit)


@router.get("/{identifier}", response_model=ProfileResponse)
def detail(identifier: UUID, user: Owner, service: Service):
    return service.detail(identifier, user.id)

from typing import Annotated

from fastapi import Cookie, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from app.base_datos.session import get_session
from app.configuracion.settings import get_settings
from app.modulos.autenticacion.repositorios.usuario_repository import UserRepository
from app.modulos.autenticacion.servicios.session_service import SessionService

SESSION_COOKIE = "tutoria_session"
STATE_COOKIE = "tutoria_login_state"


def get_repository(db: Annotated[Session, Depends(get_session)]):
    return UserRepository(db)


def get_current_user(
    repository: Annotated[UserRepository, Depends(get_repository)],
    tutoria_session: Annotated[str | None, Cookie(max_length=128)] = None,
):
    return SessionService(repository, get_settings()).current_user(tutoria_session)


def require_client_header(x_tutoria_client: Annotated[str | None, Header()] = None):
    if x_tutoria_client != "web":
        raise HTTPException(403, "Falta la cabecera de protección de la solicitud.")

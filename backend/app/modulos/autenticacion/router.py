# Expone acceso, callback y sesión con cookies y respuestas sin caché.
import hashlib
import hmac
import json
from pathlib import Path

from pydantic import BaseModel, Field, SecretStr

from app.modulos.autenticacion.schemas import InstitutionalIdentity
from typing import Annotated, Literal

from fastapi import APIRouter, Cookie, Depends, HTTPException, Query, Request, Response
from fastapi.responses import RedirectResponse

from app.configuracion.settings import get_settings
from app.modulos.autenticacion.repositorios.usuario_repository import UserRepository
from app.modulos.autenticacion.schemas import (
    AuthConfiguration,
    ErrorResponse,
    SessionResponse,
    UserResponse,
)
from app.modulos.autenticacion.servicios.cas_login_service import CasLoginService
from app.modulos.autenticacion.servicios.cas_validation_service import (
    CasValidationError,
    CasValidationService,
)
from app.modulos.autenticacion.servicios.logout_service import LogoutService
from app.modulos.autenticacion.servicios.session_service import SessionService
from app.modulos.usuarios.models import User
from app.nucleo.dependencias.auth import (
    SESSION_COOKIE,
    STATE_COOKIE,
    get_current_user,
    get_repository,
    require_client_header,
)

router = APIRouter(
    prefix="/auth",
    tags=["authentication"],
    responses={
        400: {"model": ErrorResponse},
        401: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
    },
)
Repository = Annotated[UserRepository, Depends(get_repository)]
SessionCookie = Annotated[str | None, Cookie(alias=SESSION_COOKIE, max_length=128)]
StateCookie = Annotated[str | None, Cookie(alias=STATE_COOKIE, max_length=128)]


ACCOUNT_FILE = Path("/run/tutoria/accounts.json")


def account_mode():
    settings = get_settings()
    return settings.auth_mode == "mock" and settings.app_env == "development" and ACCOUNT_FILE.is_file()


class Credentials(BaseModel):
    email: str = Field(max_length=254)
    password: SecretStr = Field(min_length=1, max_length=128)


@router.post("/accounts/login", status_code=204, dependencies=[Depends(require_client_header)])
def account_login(body: Credentials, repository: Repository, response: Response,
                  current_session: SessionCookie = None):
    if not account_mode():
        raise HTTPException(404)
    accounts = json.loads(ACCOUNT_FILE.read_text())
    email = body.email.strip().lower()
    record = accounts.get(email, {})
    digest = hashlib.scrypt(body.password.get_secret_value().encode(),
                            salt=bytes.fromhex(record.get("salt", "00" * 16)),
                            n=16384, r=8, p=1)
    if not hmac.compare_digest(digest.hex(), record.get("hash", "")):
        raise HTTPException(401, "Correo o contraseña incorrectos.")
    identity = InstitutionalIdentity(institutional_email=email, **record["identity"])
    settings = get_settings()
    token = SessionService(repository, settings).create(identity, current_session)
    response.set_cookie(SESSION_COOKIE, token, httponly=True, secure=settings.auth_cookie_secure,
                        samesite="lax", path="/api/v1", max_age=settings.auth_session_hours * 3600)


@router.get("/accounts/students")
def simulation_students(user: Annotated[User, Depends(get_current_user)]):
    if not account_mode() or user.rol not in {"teacher", "admin"}:
        raise HTTPException(403)
    return [dict(email=email, group=row["group"], nombre=row["identity"]["nombre"], apellido=row["identity"]["apellido"])
            for email, row in json.loads(ACCOUNT_FILE.read_text()).items()
            if row["identity"]["rol"] == "student"]


def get_cas_validator():
    return CasValidationService(get_settings())


def clear_state_cookie(response: Response):
    response.delete_cookie(
        STATE_COOKIE,
        path="/api/v1/auth",
        secure=get_settings().auth_cookie_secure,
        httponly=True,
        samesite="lax",
    )


@router.get("/login", status_code=302, response_class=RedirectResponse)
def login(
    repository: Repository,
    browser_state: StateCookie = None,
    demo_profile: Literal["student", "teacher"] | None = None,
):
    """Inicia acceso institucional o simulación local; no recibe credenciales."""
    settings = get_settings()
    if account_mode():
        raise HTTPException(403, "Ingresa con el correo de simulación.")
    url, state = CasLoginService(repository, settings, get_cas_validator()).start(
        browser_state, demo_profile
    )
    response = RedirectResponse(url, status_code=302)
    response.set_cookie(
        STATE_COOKIE,
        state,
        max_age=300,
        httponly=True,
        secure=settings.auth_cookie_secure,
        samesite="lax",
        path="/api/v1/auth",
    )
    return response


@router.get("/config", response_model=AuthConfiguration)
def configuration():
    """Modo público de acceso; no publica usuario, claves ni parámetros institucionales."""
    return AuthConfiguration(auth_mode=get_settings().auth_mode, accounts=account_mode())


@router.get("/callback", status_code=303, response_class=RedirectResponse)
def callback(
    request: Request,
    repository: Repository,
    validator: Annotated[CasValidationService, Depends(get_cas_validator)],
    state: Annotated[str, Query(min_length=20, max_length=128)],
    browser_state: StateCookie = None,
    current_session: SessionCookie = None,
):
    """Valida state y ticket en backend y emite una sesión opaca."""
    settings = get_settings()
    try:
        if account_mode():
            raise HTTPException(403)
        tickets = request.query_params.getlist(settings.cas_ticket_parameter)
        if len(tickets) > 1 or len(request.query_params.getlist("state")) != 1:
            raise HTTPException(400, "Callback no válido.")
        identity = CasLoginService(repository, settings, validator).validate_callback(
            state, browser_state, tickets[0] if tickets else None
        )
        token = SessionService(repository, settings).create(identity, current_session)
    except (HTTPException, CasValidationError):
        response = RedirectResponse(
            settings.auth_login_url + "?error=access_denied", status_code=303
        )
        clear_state_cookie(response)
        return response
    response = RedirectResponse(settings.auth_frontend_url, status_code=303)
    clear_state_cookie(response)
    response.set_cookie(
        SESSION_COOKIE,
        token,
        httponly=True,
        secure=settings.auth_cookie_secure,
        samesite="lax",
        path="/api/v1",
        max_age=settings.auth_session_hours * 3600,
    )
    return response


@router.get("/me", response_model=SessionResponse)
def me(user: Annotated[User, Depends(get_current_user)]):
    return SessionResponse(
        user=UserResponse.model_validate(user), auth_mode=get_settings().auth_mode
    )


@router.post("/logout", status_code=204, dependencies=[Depends(require_client_header)])
def logout(
    response: Response,
    repository: Repository,
    current_session: SessionCookie = None,
    browser_state: StateCookie = None,
):
    """Cierra la sesión de Prototipo; no cierra globalmente el SSO de UPS."""
    if browser_state:
        from app.modulos.autenticacion.servicios.session_service import digest_token

        repository.consume_attempt(digest_token(browser_state))
        repository.commit()
    LogoutService(repository).logout(current_session)
    response.delete_cookie(
        SESSION_COOKIE,
        path="/api/v1",
        secure=get_settings().auth_cookie_secure,
        httponly=True,
        samesite="lax",
    )
    clear_state_cookie(response)

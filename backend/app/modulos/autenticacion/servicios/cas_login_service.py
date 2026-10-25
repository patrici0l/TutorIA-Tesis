# Vincula el callback al intento del navegador antes de crear una sesión.
import secrets
from datetime import UTC, datetime, timedelta
from urllib.parse import parse_qs, urlencode, urlsplit

from fastapi import HTTPException

from app.configuracion.settings import Settings
from app.modulos.autenticacion.models import LoginAttempt
from app.modulos.autenticacion.repositorios.usuario_repository import UserRepository
from app.modulos.autenticacion.schemas import InstitutionalIdentity
from app.modulos.autenticacion.servicios.cas_validation_service import CasValidationService
from app.modulos.autenticacion.servicios.session_service import aware, digest_token


class CasLoginService:
    def __init__(
        self, repository: UserRepository, settings: Settings, validator: CasValidationService
    ):
        self.repository, self.settings, self.validator = repository, settings, validator

    def start(
        self, previous_state: str | None = None, demo_profile: str | None = None
    ) -> tuple[str, str]:
        self.settings.validate_auth()
        if demo_profile is not None and (
            self.settings.auth_mode != "mock"
            or self.settings.app_env != "development"
            or demo_profile not in ("student", "teacher")
        ):
            raise HTTPException(
                400, "La selección de perfil solo está disponible en la demostración local."
            )
        self.repository.purge_expired()
        if previous_state:
            self.repository.consume_attempt(digest_token(previous_state))
        state = secrets.token_urlsafe(32)
        parameters = {"state": state}
        if self.settings.auth_mode == "mock":
            parameters["demo_profile"] = demo_profile or self.settings.auth_mock_user
        service_url = self.settings.auth_callback_url + "?" + urlencode(parameters)
        self.repository.add(
            LoginAttempt(
                digest=digest_token(state),
                mode=self.settings.auth_mode,
                service_url=service_url,
                expires_at=datetime.now(UTC) + timedelta(minutes=5),
            )
        )
        self.repository.commit()
        destination = (
            service_url
            if self.settings.auth_mode == "mock"
            else self.settings.cas_login_url
            + "?"
            + urlencode({self.settings.cas_service_parameter: service_url})
        )
        return destination, state

    def validate_callback(self, state: str, browser_state: str | None, ticket: str | None):
        if (
            not browser_state
            or not state.isascii()
            or not browser_state.isascii()
            or not secrets.compare_digest(state, browser_state)
        ):
            raise HTTPException(400, "El intento de acceso no es válido.")
        attempt = self.repository.consume_attempt(digest_token(state))
        self.repository.commit()
        if (
            not attempt
            or attempt.mode != self.settings.auth_mode
            or aware(attempt.expires_at) <= datetime.now(UTC)
        ):
            raise HTTPException(400, "El intento de acceso venció o ya fue utilizado.")
        if self.settings.auth_mode == "cas":
            return self.validator.validate(ticket or "", attempt.service_url)
        # Nunca se acepta una identidad suministrada por Angular.
        # El perfil se lee del intento guardado, nunca del query del callback.
        profile = parse_qs(urlsplit(attempt.service_url).query).get(
            "demo_profile", [self.settings.auth_mock_user]
        )[0]
        if profile not in ("student", "teacher"):
            raise HTTPException(400, "Perfil de demostración no válido.")
        teacher = profile == "teacher"
        return InstitutionalIdentity(
            institutional_email="docente.demo@example.org"
            if teacher
            else "estudiante.demo@example.org",
            institutional_id="mock:teacher-001" if teacher else "mock:student-001",
            nombre="Docente" if teacher else "Estudiante",
            apellido="Demostración",
            rol="teacher" if teacher else "student",
        )

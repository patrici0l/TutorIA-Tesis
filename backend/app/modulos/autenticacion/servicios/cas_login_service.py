import secrets
from datetime import UTC, datetime, timedelta
from urllib.parse import urlencode

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

    def start(self, previous_state: str | None = None) -> tuple[str, str]:
        self.settings.validate_auth()
        self.repository.purge_expired()
        if previous_state:
            self.repository.consume_attempt(digest_token(previous_state))
        state = secrets.token_urlsafe(32)
        service_url = self.settings.auth_callback_url + "?" + urlencode({"state": state})
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
        if not browser_state or not secrets.compare_digest(state, browser_state):
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
        teacher = self.settings.auth_mock_user == "teacher"
        return InstitutionalIdentity(
            institutional_email="docente.demo@example.org"
            if teacher
            else "estudiante.demo@example.org",
            institutional_id="mock:teacher-001" if teacher else "mock:student-001",
            nombre="Docente" if teacher else "Estudiante",
            apellido="Demostración",
            rol="teacher" if teacher else "student",
        )

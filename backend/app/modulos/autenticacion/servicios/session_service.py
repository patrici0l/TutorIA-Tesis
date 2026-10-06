import hashlib
import secrets
from datetime import UTC, datetime, timedelta

from fastapi import HTTPException

from app.configuracion.settings import Settings
from app.modulos.autenticacion.models import AuthSession
from app.modulos.autenticacion.repositorios.usuario_repository import UserRepository
from app.modulos.autenticacion.schemas import InstitutionalIdentity
from app.modulos.usuarios.models import User


def digest_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def aware(value: datetime) -> datetime:
    # SQLite no conserva zona horaria; PostgreSQL devuelve timestamptz.
    return value.replace(tzinfo=UTC) if value.tzinfo is None else value


class SessionService:
    def __init__(self, repository: UserRepository, settings: Settings):
        self.repository = repository
        self.settings = settings

    def create(self, identity: InstitutionalIdentity, previous_token: str | None) -> str:
        self.repository.lock_provisioning()
        email = str(identity.institutional_email).lower()
        by_email = self.repository.find_by_email(email)
        by_id = (
            self.repository.find_by_institutional_id(identity.institutional_id)
            if identity.institutional_id
            else None
        )
        if by_id and by_email and by_id.id != by_email.id:
            raise HTTPException(403, "La identidad institucional requiere revisión.")
        user = by_id or by_email
        if user and self.settings.auth_mode == "cas":
            if user.institutional_email.rsplit("@", 1)[-1] not in {"est.ups.edu.ec", "ups.edu.ec"}:
                raise HTTPException(403, "La identidad requiere revisión antes de habilitar CAS.")
        if (
            user
            and user.institutional_id
            and identity.institutional_id
            and user.institutional_id != identity.institutional_id
        ):
            raise HTTPException(403, "La identidad institucional requiere revisión.")
        if user and not user.activo:
            raise HTTPException(403, "La cuenta está desactivada.")
        now = datetime.now(UTC)
        if not user:
            user = User(
                institutional_email=email,
                institutional_id=identity.institutional_id,
                nombre=identity.nombre,
                apellido=identity.apellido,
                rol=identity.rol,
                activo=True,
                last_login=now,
            )
            self.repository.add(user)
        else:
            user.institutional_email = email
            if identity.institutional_id:
                user.institutional_id = identity.institutional_id
            user.nombre, user.apellido = identity.nombre, identity.apellido
            user.last_login = now
            # El SSO identifica; no eleva permisos locales ni reactiva cuentas.
        if previous_token:
            self.repository.delete_session(digest_token(previous_token))
        token = secrets.token_urlsafe(48)
        self.repository.add(
            AuthSession(
                digest=digest_token(token),
                user_id=user.id,
                mode=self.settings.auth_mode,
                expires_at=now + timedelta(hours=self.settings.auth_session_hours),
            )
        )
        self.repository.commit()
        return token

    def current_user(self, token: str | None):
        if not token:
            raise HTTPException(401, "No hay una sesión válida.")
        session = self.repository.get_session(digest_token(token))
        if (
            not session
            or session.mode != self.settings.auth_mode
            or aware(session.expires_at) <= datetime.now(UTC)
        ):
            raise HTTPException(401, "La sesión venció o no es válida.")
        user = self.repository.get_user(session.user_id)
        if not user or not user.activo:
            raise HTTPException(401, "La sesión no es válida.")
        return user

from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import delete, select, text
from sqlalchemy.orm import Session

from app.modulos.autenticacion.models import AuthSession, LoginAttempt
from app.modulos.usuarios.models import User


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def find_by_email(self, email: str):
        return self.db.scalar(select(User).where(User.institutional_email == email))

    def find_by_institutional_id(self, identifier: str):
        return self.db.scalar(select(User).where(User.institutional_id == identifier))

    def get_user(self, user_id: UUID):
        return self.db.get(User, user_id)

    def lock_provisioning(self):
        # Serializa altas simultáneas. SQLite se utiliza solo en pruebas locales.
        if self.db.bind.dialect.name == "postgresql":
            self.db.execute(text("SELECT pg_advisory_xact_lock(74192002)"))

    def add(self, entity):
        self.db.add(entity)
        self.db.flush()

    def consume_attempt(self, digest: str):
        # DELETE RETURNING garantiza un solo uso incluso con callbacks concurrentes.
        return self.db.scalar(
            delete(LoginAttempt).where(LoginAttempt.digest == digest).returning(LoginAttempt)
        )

    def get_session(self, digest: str):
        return self.db.get(AuthSession, digest)

    def delete_session(self, digest: str):
        self.db.execute(delete(AuthSession).where(AuthSession.digest == digest))

    def purge_expired(self):
        now = datetime.now(UTC)
        self.db.execute(delete(LoginAttempt).where(LoginAttempt.expires_at <= now))
        self.db.execute(delete(AuthSession).where(AuthSession.expires_at <= now))

    def commit(self):
        self.db.commit()

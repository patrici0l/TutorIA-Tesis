from app.modulos.autenticacion.repositorios.usuario_repository import UserRepository
from app.modulos.autenticacion.servicios.session_service import digest_token


class LogoutService:
    def __init__(self, repository: UserRepository):
        self.repository = repository

    def logout(self, token: str | None):
        if token:
            self.repository.delete_session(digest_token(token))
            self.repository.commit()

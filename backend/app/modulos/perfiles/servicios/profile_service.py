from uuid import UUID

from fastapi import HTTPException

from app.modulos.perfiles.repositorios.profile_repository import ProfileRepository
from app.modulos.perfiles.schemas import ProfilePage, ProfileRequest, ProfileResponse
from app.nucleo.seguridad.rate_limiter import AuthRateLimiter

PROFILE_LIMITER = AuthRateLimiter(limit=10)


class ProfileService:
    def __init__(self, repository: ProfileRepository, limiter=PROFILE_LIMITER):
        self.repository, self.limiter = repository, limiter

    def response(self, record):
        return ProfileResponse(
            **record.payload,
            id=record.id,
            created_at=record.created_at,
            schema_version=record.schema_version,
        )

    def create(self, request: ProfileRequest, owner: UUID):
        if not self.limiter.allow(str(owner)):
            raise HTTPException(
                429, "Espera un minuto antes de guardar otro perfil.", headers={"Retry-After": "60"}
            )
        return self.response(self.repository.create(request, owner))

    def detail(self, identifier: UUID, owner: UUID):
        record = self.repository.owned(identifier, owner)
        if record is None:
            raise HTTPException(404, "Perfil no disponible.")
        return self.response(record)

    def page(self, owner: UUID, offset: int, limit: int):
        items, total = self.repository.page(owner, offset, limit)
        return ProfilePage(items=items, total=total, offset=offset, limit=limit)

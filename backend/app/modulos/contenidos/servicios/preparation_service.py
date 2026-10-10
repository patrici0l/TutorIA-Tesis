import json
from uuid import UUID

from fastapi import HTTPException

from app.modulos.contenidos.adaptation_schemas import PreparationRequest
from app.modulos.contenidos.errors import ContentError
from app.modulos.contenidos.preparation_schemas import PreparationResponse, PreparationSource
from app.modulos.contenidos.repositorios.generation_repository import GenerationRepository
from app.modulos.contenidos.schemas import ContentRequest
from app.modulos.contenidos.servicios.prepare_content_service import PrepareContentService
from app.nucleo.seguridad.rate_limiter import AuthRateLimiter

PREPARATION_LIMITER = AuthRateLimiter(limit=5)
ERRORS = {
    "content_no_sources": (
        422,
        "No hay fuentes disponibles. Carga, procesa e indexa tus materiales.",
    ),
    "content_context_limit": (
        422,
        "La preparación es demasiado extensa. Reduce el objetivo o la respuesta.",
    ),
    "content_invalid_sources": (
        503,
        "No se pudieron verificar las fuentes. Revisa tus materiales.",
    ),
}


class PreparationService:
    def __init__(
        self,
        preparer: PrepareContentService,
        repository: GenerationRepository,
        max_input_chars: int,
        limiter: AuthRateLimiter = PREPARATION_LIMITER,
        adaptation=None,
    ):
        self.preparer, self.repository = preparer, repository
        self.max_input_chars, self.limiter = max_input_chars, limiter
        self.adaptation = adaptation

    def prepare(self, request: ContentRequest, owner: UUID) -> PreparationResponse:
        if not self.limiter.allow(str(owner)):
            raise HTTPException(
                429,
                "Has preparado varios recursos. Espera un minuto para continuar.",
                headers={"Retry-After": "60"},
            )
        try:
            snapshot = None
            if isinstance(request, PreparationRequest):
                profile_id = request.profile_id
                request = ContentRequest.model_validate(request.model_dump(exclude={"profile_id"}))
                if profile_id is not None:
                    if self.adaptation is None:
                        raise HTTPException(503, "La personalización no está disponible.")
                    request, snapshot = self.adaptation.adapt(request, profile_id, owner)
            if snapshot is None:
                prepared = self.preparer.prepare(request, owner, self.max_input_chars)
            else:
                prepared = self.preparer.prepare(
                    request, owner, self.max_input_chars, adaptation=snapshot
                )
        except ContentError as error:
            status, detail = ERRORS.get(error.code, (503, "No se pudo preparar el recurso."))
            raise HTTPException(status, detail) from None
        sources = [PreparationSource(**source) for source in json.loads(prepared.sources_json)]
        identifier = self.repository.prepare(owner, prepared)
        return PreparationResponse(
            id=identifier,
            topic=request.topic,
            learning_objective=request.learning_objective,
            resource_type=request.resource_type,
            difficulty=request.difficulty,
            question_count=request.question_count,
            sources=sources,
            adaptation=snapshot,
        )

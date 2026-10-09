from typing import get_args
from uuid import UUID

from app.modulos.contenidos.cost_schemas import CostBasis
from app.modulos.contenidos.errors import ContentError
from app.modulos.contenidos.repositorios.generation_repository import GenerationRepository
from app.modulos.contenidos.schemas import ContentRequest
from app.modulos.contenidos.servicios.resource_validation_service import ResourceValidationService
from app.modulos.proveedores_ia.errors import ErrorCode
from app.modulos.proveedores_ia.schemas import GenerationResult

CONTENT_ERRORS = {
    "content_target_mismatch",
    "content_wrong_resource",
    "content_quiz_count",
    "content_invalid_citations",
    "content_invalid_output",
    "content_insufficient_sources",
    "generation_interrupted",
}


class GenerationTraceService:
    """Persistencia y validación internas. No inicia red ni publica contenido."""

    def __init__(self, repository: GenerationRepository, validator: ResourceValidationService):
        self.repository, self.validator = repository, validator

    def finish(self, identifier: UUID, owner: UUID, result: GenerationResult):
        snapshot = self.repository.owned_snapshot(identifier, owner)
        if snapshot is None or snapshot[2] not in {"prepared", "generating"}:
            raise ContentError("content_trace_unavailable")
        if (snapshot[3] is not None and snapshot[3] != result.provider) or (
            snapshot[4] is not None and snapshot[4] != result.requested_model
        ):
            self.fail(identifier, owner, "content_target_mismatch")
            raise ContentError("content_target_mismatch")
        request = ContentRequest(**snapshot[0])
        cost_basis = CostBasis.model_validate(snapshot[5]) if snapshot[5] else None
        metadata = dict(
            provider=result.provider,
            requested_model=result.requested_model,
            model_version=result.model_version,
            response_id=result.response_id,
            usage=result.usage.model_dump(),
            latency_ms=result.latency_ms,
            estimated_cost=cost_basis.estimate(result) if cost_basis else None,
        )
        try:
            resource = self.validator.validate(
                result.text,
                request,
                {source["citation_id"] for source in snapshot[1]},
            )
        except ContentError as error:
            if not self.repository.finish(
                identifier,
                owner,
                status="failed",
                error_code=error.code,
                **metadata,
            ):
                raise ContentError("content_trace_unavailable") from None
            raise
        if not self.repository.finish(
            identifier,
            owner,
            status="succeeded",
            resource=resource.model_dump(mode="json"),
            **metadata,
        ):
            raise ContentError("content_trace_unavailable")
        return resource

    def fail(self, identifier: UUID, owner: UUID, code: str):
        if code not in CONTENT_ERRORS | set(get_args(ErrorCode)):
            raise ContentError("content_invalid_error_code")
        if not self.repository.finish(identifier, owner, status="failed", error_code=code):
            raise ContentError("content_trace_unavailable")

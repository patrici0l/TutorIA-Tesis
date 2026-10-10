from dataclasses import dataclass
from uuid import UUID

from app.modulos.contenidos.errors import ContentError
from app.modulos.contenidos.repositorios.generation_repository import GenerationRepository
from app.modulos.contenidos.schemas import ContentRequest, EducationalResource
from app.modulos.contenidos.servicios.generation_trace_service import GenerationTraceService
from app.modulos.contenidos.servicios.prepare_content_service import PrepareContentService
from app.modulos.contenidos.servicios.resource_validation_service import ResourceValidationService
from app.modulos.proveedores_ia.errors import ProviderError
from app.modulos.proveedores_ia.interfaces.llm_provider import LLMProvider
from app.modulos.proveedores_ia.schemas import GenerationTarget


@dataclass(frozen=True)
class GenerationOutcome:
    id: UUID
    resource: EducationalResource | None = None
    error_code: str | None = None


class GenerateContentService:
    """Coordinador interno: evidencia durable antes de red, sin reintentos ni fallback."""

    def __init__(
        self,
        preparer: PrepareContentService,
        repository: GenerationRepository,
        provider: LLMProvider,
        target: GenerationTarget,
        max_input_chars: int = 12000,
    ):
        self.preparer, self.repository, self.provider = preparer, repository, provider
        self.target, self.max_input_chars = target, max_input_chars
        self.trace = GenerationTraceService(repository, ResourceValidationService())

    def generate(self, request: ContentRequest, owner: UUID) -> GenerationOutcome:
        prepared = self.preparer.prepare(request, owner, self.max_input_chars)
        identifier = self.repository.prepare(owner, prepared, self.target)
        try:
            result = self.provider.generate(prepared.generation_request)
        except ProviderError as error:
            self.trace.fail(identifier, owner, error.code, metadata=error.metadata)
            return GenerationOutcome(identifier, error_code=error.code)
        except Exception:
            self.trace.fail(identifier, owner, "generation_interrupted")
            raise
        try:
            resource = self.trace.finish(identifier, owner, result)
        except ContentError as error:
            return GenerationOutcome(identifier, error_code=error.code)
        return GenerationOutcome(identifier, resource=resource)

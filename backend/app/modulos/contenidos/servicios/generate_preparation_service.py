from typing import Literal
from uuid import UUID

from fastapi import HTTPException
from pydantic import BaseModel, ConfigDict

from app.configuracion.settings import Settings
from app.modulos.contenidos.cost_schemas import CostBasis
from app.modulos.contenidos.errors import ContentError
from app.modulos.contenidos.repositorios.generation_claim_repository import (
    GenerationClaimRepository,
)
from app.modulos.contenidos.schemas import EducationalResource
from app.modulos.contenidos.servicios.generation_trace_service import GenerationTraceService
from app.modulos.proveedores_ia.errors import ProviderError
from app.modulos.proveedores_ia.schemas import GenerationTarget
from app.modulos.proveedores_ia.servicios.llm_factory import create_provider


class GenerationCommand(BaseModel):
    model_config = ConfigDict(extra="forbid")


class GenerationResponse(BaseModel):
    id: UUID
    status: Literal["succeeded", "failed"]
    resource: EducationalResource | None = None
    message: str | None = None


class GeneratePreparationService:
    def __init__(
        self, claim: GenerationClaimRepository, trace: GenerationTraceService, settings: Settings
    ):
        self.claim, self.trace, self.settings = claim, trace, settings

    def generate(self, identifier: UUID, owner: UUID):
        if not self.settings.llm_enabled or not self.settings.llm_free_tier_confirmed:
            raise HTTPException(503, "La generación gratuita aún no está habilitada.")
        try:
            provider = create_provider(self.settings)
        except ProviderError:
            raise HTTPException(
                503, "La generación no está disponible. Revisa la configuración local."
            ) from None
        target = GenerationTarget(
            provider=self.settings.llm_default_provider, requested_model=self.settings.llm_model
        )
        cost_basis = (
            CostBasis(requested_model=target.requested_model)
            if target.provider == "gemini"
            else None
        )
        request = self.claim.claim(
            identifier, owner, target, self.settings.llm_daily_request_limit, cost_basis=cost_basis
        )
        try:
            result = provider.generate(request)
        except ProviderError as error:
            self.trace.fail(identifier, owner, error.code)
            return GenerationResponse(
                id=identifier,
                status="failed",
                message=(
                    "No se pudo generar el recurso. Puede haberse agotado la cuota "
                    "o el tiempo de espera. No se reintentó."
                ),
            )
        except Exception:
            self.trace.fail(identifier, owner, "generation_interrupted")
            return GenerationResponse(
                id=identifier,
                status="failed",
                message="La generación se interrumpió. No se reintentó.",
            )
        try:
            resource = self.trace.finish(identifier, owner, result)
        except ContentError:
            return GenerationResponse(
                id=identifier,
                status="failed",
                message=(
                    "La respuesta no superó la validación de formato y citas. "
                    "No se publicará como recurso."
                ),
            )
        return GenerationResponse(id=identifier, status="succeeded", resource=resource)

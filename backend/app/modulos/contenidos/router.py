from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.base_datos.session import get_session
from app.configuracion.settings import get_settings
from app.modulos.contenidos.preparation_schemas import PreparationResponse
from app.modulos.contenidos.repositorios.generation_claim_repository import (
    GenerationClaimRepository,
)
from app.modulos.contenidos.repositorios.generation_repository import GenerationRepository
from app.modulos.contenidos.schemas import ContentRequest
from app.modulos.contenidos.servicios.generate_preparation_service import (
    GeneratePreparationService,
    GenerationCommand,
    GenerationResponse,
)
from app.modulos.contenidos.servicios.generation_trace_service import GenerationTraceService
from app.modulos.contenidos.servicios.preparation_service import PreparationService
from app.modulos.contenidos.servicios.prepare_content_service import PrepareContentService
from app.modulos.contenidos.servicios.resource_validation_service import ResourceValidationService
from app.modulos.documentos.router import Owner
from app.modulos.rag.prompts.educational_prompt import EducationalPromptBuilder
from app.modulos.rag.router import get_search_service
from app.modulos.rag.servicios.search_service import SearchService
from app.nucleo.dependencias.auth import require_client_header

router = APIRouter(prefix="/content", tags=["content"])


def get_preparation_service(
    db: Annotated[Session, Depends(get_session)],
    search: Annotated[SearchService, Depends(get_search_service)],
):
    return PreparationService(
        PrepareContentService(search, EducationalPromptBuilder()),
        GenerationRepository(db),
        get_settings().llm_max_input_chars,
    )


@router.post(
    "/prepare",
    response_model=PreparationResponse,
    status_code=201,
    dependencies=[Depends(require_client_header)],
)
def prepare(
    request: ContentRequest,
    user: Owner,
    service: Annotated[PreparationService, Depends(get_preparation_service)],
):
    return service.prepare(request, user.id)


def get_generation_service(db: Annotated[Session, Depends(get_session)]):
    return GeneratePreparationService(
        GenerationClaimRepository(db),
        GenerationTraceService(GenerationRepository(db), ResourceValidationService()),
        get_settings(),
    )


@router.post(
    "/{identifier}/generate",
    response_model=GenerationResponse,
    dependencies=[Depends(require_client_header)],
)
def generate(
    identifier: UUID,
    user: Owner,
    service: Annotated[GeneratePreparationService, Depends(get_generation_service)],
    command: GenerationCommand = GenerationCommand(),
):
    return service.generate(identifier, user.id)

from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from app.modulos.contenidos.schemas import ContentRequest
from app.modulos.rag.prompts.educational_prompt import EducationalPromptBuilder
from app.modulos.rag.schemas import SearchRequest

if TYPE_CHECKING:
    from app.modulos.rag.servicios.search_service import SearchService


class PrepareContentService:
    """Preparación interna sobre corpus propio; no llama proveedores ni publica recursos."""

    def __init__(self, search: SearchService, builder: EducationalPromptBuilder):
        self.search, self.builder = search, builder

    def prepare(
        self, request: ContentRequest, owner: UUID, max_input_chars: int = 12000, adaptation=None
    ):
        retrieval = self.search.search(
            SearchRequest(query=f"{request.topic}. {request.learning_objective}", top_k=3), owner
        )
        if adaptation is None:
            return self.builder.build(request, retrieval, max_input_chars)
        return self.builder.build(request, retrieval, max_input_chars, adaptation=adaptation)

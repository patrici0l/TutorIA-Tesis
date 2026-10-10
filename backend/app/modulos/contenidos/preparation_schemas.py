from typing import Literal
from uuid import UUID

from pydantic import BaseModel

from app.modulos.contenidos.adaptation_schemas import AdaptationSnapshot
from app.modulos.contenidos.schemas import Difficulty, ResourceType
from app.modulos.rag.schemas import SearchHit


class PreparationSource(SearchHit):
    citation_id: str


class PreparationResponse(BaseModel):
    id: UUID
    status: Literal["prepared"] = "prepared"
    topic: str
    learning_objective: str
    resource_type: ResourceType
    difficulty: Difficulty
    question_count: int | None
    sources: list[PreparationSource]
    adaptation: AdaptationSnapshot | None = None

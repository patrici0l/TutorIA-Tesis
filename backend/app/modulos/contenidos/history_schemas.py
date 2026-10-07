from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel

from app.modulos.contenidos.preparation_schemas import PreparationResponse
from app.modulos.contenidos.schemas import Difficulty, EducationalResource, ResourceType

GenerationStatus = Literal["prepared", "generating", "succeeded", "failed"]


class HistoryItem(BaseModel):
    id: UUID
    topic: str
    resource_type: ResourceType
    difficulty: Difficulty
    status: GenerationStatus
    created_at: datetime
    completed_at: datetime | None


class HistoryPage(BaseModel):
    items: list[HistoryItem]
    total: int
    offset: int
    limit: int


class HistoryDetail(BaseModel):
    preparation: PreparationResponse
    status: GenerationStatus
    created_at: datetime
    completed_at: datetime | None
    resource: EducationalResource | None
    message: str | None

from datetime import datetime
from decimal import Decimal
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.modulos.contenidos.preparation_schemas import PreparationResponse
from app.modulos.contenidos.schemas import Difficulty, EducationalResource, ResourceType
from app.modulos.proveedores_ia.schemas import TokenUsage

GenerationStatus = Literal["prepared", "generating", "succeeded", "failed"]


class RetrievalAudit(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    method: Literal["exact_cosine"]
    query_version: str
    embedding_model: str
    embedding_revision: str
    embedding_version: str
    top_k: int = Field(ge=1, le=10)
    min_similarity: float = Field(ge=0, le=1)
    available_chunks: int = Field(ge=0)
    elapsed_ms: int = Field(ge=0)


class GenerationAudit(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    generation_started_at: datetime | None
    provider: str | None
    requested_model: str | None
    model_version: str | None
    prompt_version: str
    prompt_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    usage: TokenUsage | None
    latency_ms: int | None = Field(ge=0)
    estimated_cost: Decimal | None = Field(ge=0)
    error_code: str | None = Field(max_length=40)
    retrieval: RetrievalAudit


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
    audit: GenerationAudit | None = None

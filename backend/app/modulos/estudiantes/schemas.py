from datetime import datetime
from typing import Annotated, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

PRACTICE_VERSION = "derivadas-v1"
# Clave del banco introductorio versionado; nunca se acepta un score del cliente.
CORRECT_OPTIONS = (0, 2, 3)
ANSWER_KEYS = {PRACTICE_VERSION: CORRECT_OPTIONS, "reglas-v1": (1, 0, 2)}


class PracticeSubmission(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: UUID
    version: Literal["derivadas-v1", "reglas-v1"]
    assignment_id: UUID | None = None
    answers: list[Annotated[int, Field(ge=0, le=3, strict=True)]] = Field(
        min_length=3, max_length=3
    )


class PracticeResult(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    version: str
    assignment_id: UUID | None = None
    answers: list[int]
    score: int
    created_at: datetime


class PracticeProgress(BaseModel):
    items: list[PracticeResult]
    total: int
    best_score: int | None
    offset: int
    limit: int

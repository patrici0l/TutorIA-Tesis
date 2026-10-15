from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class AssignmentSubmission(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    id: UUID
    student_email: EmailStr
    version: Literal["derivadas-v1", "reglas-v1"]
    title: str = Field(min_length=1, max_length=120)
    instructions: str = Field(default="", max_length=2000)


class AssignmentResult(BaseModel):
    id: UUID
    version: str
    title: str
    instructions: str
    student_email: str
    created_at: datetime
    attempts: int
    best_score: int | None


class AssignmentPage(BaseModel):
    items: list[AssignmentResult]
    total: int
    offset: int
    limit: int

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator

from app.modulos.contenidos.preparation_schemas import PreparationSource
from app.modulos.contenidos.schemas import EducationalResource

AssignmentStatus = Literal["open", "closed", "cancelled"]


class AssignmentStatusChange(BaseModel):
    model_config = ConfigDict(extra="forbid")
    status: AssignmentStatus
    expected_status: AssignmentStatus


class AssignmentSubmission(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    id: UUID
    student_email: EmailStr
    version: Literal["derivadas-v1", "reglas-v1", "resource-v1"]
    resource_id: UUID | None = None
    title: str = Field(min_length=1, max_length=120)
    instructions: str = Field(default="", max_length=2000)

    @model_validator(mode="after")
    def resource_matches_version(self):
        if (self.version == "resource-v1") != (self.resource_id is not None):
            raise ValueError("Selecciona un recurso generado o un bloque de práctica.")
        return self


class AssignmentResult(BaseModel):
    id: UUID
    version: str
    title: str
    instructions: str
    student_email: str
    created_at: datetime
    status: AssignmentStatus
    status_changed_at: datetime | None
    attempts: int
    best_score: int | None
    resource_id: UUID | None = None


class AssignmentDetail(AssignmentResult):
    resource: EducationalResource | None = None
    sources: list[PreparationSource] = Field(default_factory=list)


class AssignmentPage(BaseModel):
    items: list[AssignmentResult]
    total: int
    offset: int
    limit: int

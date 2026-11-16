from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.modulos.contenidos.schemas import ContentRequest, Difficulty, ResourceType
from app.modulos.perfiles.schemas import MasteryLevel, ProfileResponse


class AdaptationRule(BaseModel):
    mastery_level: MasteryLevel = Field(description="Nivel de dominio informado por el docente.")
    effective_difficulty: Difficulty
    guidance: str = Field(description="Orientación utilizada al preparar el recurso.")
    suggested_resources: list[ResourceType] = Field(
        description="Tipos sugeridos; no restringen el tipo solicitado."
    )
    reason: str


class AdaptationRuleCatalog(BaseModel):
    version: str = Field(examples=["profile-adaptation-v2"])
    rules: list[AdaptationRule]
    application_notes: list[str]


class PreparationRequest(ContentRequest):
    course: str = Field(min_length=1, max_length=160)
    profile_id: UUID | None = None


class AdaptationSnapshot(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    # Mantener el valor antiguo al leer snapshots históricos que omitan la versión.
    policy_version: Literal["profile-adaptation-v1", "profile-adaptation-v2"] = (
        "profile-adaptation-v1"
    )
    profile: ProfileResponse
    requested_difficulty: Difficulty
    effective_difficulty: Difficulty
    guidance: str
    reason: str
    focus_errors: list[str]
    suggested_resources: list[ResourceType]

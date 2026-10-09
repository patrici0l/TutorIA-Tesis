from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.modulos.contenidos.schemas import ContentRequest, Difficulty, ResourceType
from app.modulos.perfiles.schemas import ProfileResponse


class PreparationRequest(ContentRequest):
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

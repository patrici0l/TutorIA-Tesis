import unicodedata
from datetime import datetime
from typing import Annotated, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

MasteryLevel = Literal["low", "medium", "high"]
RecommendedSupport = Literal["reinforcement", "practice", "challenge"]
ErrorLabel = Annotated[str, Field(min_length=1, max_length=100)]


class ProfileRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, hide_input_in_errors=True)
    student_id: str = Field(pattern=r"^[A-Za-z0-9_-]+$", min_length=1, max_length=64)
    topic: str = Field(min_length=1, max_length=160)
    performance: float = Field(ge=0, le=100, allow_inf_nan=False, strict=True)
    attempts: int = Field(ge=1, le=10000, strict=True)
    frequent_errors: list[ErrorLabel] = Field(default_factory=list, max_length=10)
    mastery_level: MasteryLevel
    recommended_support: RecommendedSupport
    resolution_time_seconds: float | None = Field(
        default=None, ge=0, le=86400, allow_inf_nan=False, strict=True
    )
    progress_trend: Literal["improving", "stable", "declining"] | None = None
    data_kind: Literal["synthetic"]

    @field_validator("student_id", "topic", "frequent_errors", mode="before")
    @classmethod
    def normalize_text(cls, value):
        def normalize(text):
            if not isinstance(text, str):
                return text
            if any(unicodedata.category(char) in {"Cc", "Cs"} for char in text):
                raise ValueError("Caracteres no permitidos")
            return unicodedata.normalize("NFC", text).strip()

        return [normalize(item) for item in value] if isinstance(value, list) else normalize(value)

    @field_validator("frequent_errors")
    @classmethod
    def unique_errors(cls, value):
        if len(value) != len(set(value)):
            raise ValueError("Errores repetidos")
        return value


class ProfileResponse(ProfileRequest):
    id: UUID
    created_at: datetime
    schema_version: Literal["performance-profile-v1"] = "performance-profile-v1"


class ProfileSummary(BaseModel):
    id: UUID
    student_id: str
    topic: str
    performance: float
    mastery_level: MasteryLevel
    created_at: datetime


class ProfilePage(BaseModel):
    items: list[ProfileSummary]
    total: int
    offset: int
    limit: int

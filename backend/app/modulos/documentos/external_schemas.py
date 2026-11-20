"""Contratos de consulta e importación de Wikipedia en español."""
import unicodedata
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class WikiResult(BaseModel):
    page_id: int = Field(gt=0)
    title: str


class ExternalSource(BaseModel):
    provider: Literal["wikipedia_es"] = "wikipedia_es"
    page_id: int = Field(gt=0)
    revision_id: int = Field(gt=0)
    title: str
    url: str
    revision_at: datetime
    retrieved_at: datetime
    license_name: str
    license_url: str
    attribution: str
    text_sha256: str
    snapshot_sha256: str
    extraction_version: Literal["mediawiki-text-v1"] = "mediawiki-text-v1"


class WikiPreview(BaseModel):
    source: ExternalSource
    text: str
    warnings: list[str]


class WikiImport(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    page_id: int = Field(gt=0, strict=True)
    revision_id: int = Field(gt=0, strict=True)
    text_sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
    course: str = Field(min_length=1, max_length=160)
    authorization_confirmed: Literal[True]

    @field_validator("course")
    @classmethod
    def valid_course(cls, value):
        if not value or any(unicodedata.category(c).startswith("C") for c in value):
            raise ValueError("Indica una asignatura válida.")
        return unicodedata.normalize("NFC", value).casefold()

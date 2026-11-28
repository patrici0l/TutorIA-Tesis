from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class CoreResult(BaseModel):
    work_id: int = Field(gt=0)
    title: str
    authors: list[str]
    year: int | None = None
    language: str | None = None


class CorePreview(CoreResult):
    url: str
    abstract: str
    record_sha256: str
    retrieved_at: datetime
    license_statement: str
    full_text_available: bool


class CoreSource(BaseModel):
    provider: Literal["core"] = "core"
    work_id: int = Field(gt=0)
    title: str
    url: str
    authors: list[str]
    year: int | None = None
    retrieved_at: datetime
    license_name: str
    attribution: str
    record_sha256: str
    snapshot_sha256: str
    extraction_version: Literal["core-record-v1"] = "core-record-v1"
    content_origin: Literal["teacher_uploaded_original"] = "teacher_uploaded_original"

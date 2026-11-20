import unicodedata
from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, field_validator

from app.modulos.documentos.external_schemas import ExternalSource
from app.modulos.rag.schemas import DocumentChunkResponse


class DocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    external_source: ExternalSource | None = None
    course: str | None = None
    published_at: datetime | None = None
    source_reference: str | None = None
    permission_note: str | None = None
    permission_recorded_at: datetime | None = None
    version_number: int = 1
    previous_version_id: UUID | None = None
    id: UUID
    filename: str
    title: str
    mime_type: str
    size_bytes: int
    sha256: str
    status: str
    created_at: datetime
    processing_status: Literal["pending", "processing", "processed", "failed"]
    processing_error: str | None
    processing_started_at: datetime | None
    processed_at: datetime | None
    processing_version: str | None
    chunk_chars: int | None
    chunk_overlap: int | None
    chunk_count: int
    text_chars: int
    index_status: Literal["pending", "indexing", "indexed", "failed"]
    index_error: str | None
    index_started_at: datetime | None
    indexed_at: datetime | None
    embedding_model: str | None
    embedding_revision: str | None
    embedding_version: str | None


class DocumentList(BaseModel):
    items: list[DocumentResponse]
    total: int
    limit: int
    offset: int


class DocumentMetadata(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    course: str
    source_reference: str
    permission_note: str
    previous_version_id: UUID | None = None

    @field_validator("course", "source_reference", "permission_note")
    @classmethod
    def validate_text(cls, value: str, info):
        limit = 160 if info.field_name == "course" else 500
        if (
            not value
            or len(value) > limit
            or any(unicodedata.category(c).startswith("C") for c in value)
        ):
            raise ValueError("Indica un texto válido dentro del límite permitido")
        return (
            unicodedata.normalize("NFC", value).casefold() if info.field_name == "course" else value
        )


class TextMatch(BaseModel):
    document: DocumentResponse
    chunk: DocumentChunkResponse


class TextSearchPage(BaseModel):
    items: list[TextMatch]
    total: int
    limit: int
    offset: int

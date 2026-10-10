from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class DocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
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

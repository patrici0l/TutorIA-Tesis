import unicodedata
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class DocumentChunkResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    position: int
    source_kind: Literal["page", "paragraph"]
    source_index: int
    char_start: int
    char_end: int
    text: str


class DocumentChunkList(BaseModel):
    items: list[DocumentChunkResponse]
    total: int
    limit: int
    offset: int


class SearchRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    query: str = Field(min_length=1, max_length=1000)
    top_k: int = Field(default=5, ge=1, le=10, strict=True)
    min_similarity: float = Field(default=0, ge=0, le=1, allow_inf_nan=False)

    @field_validator("query")
    @classmethod
    def normalize_query(cls, value: str):
        value = unicodedata.normalize("NFC", value).strip()
        if not value or any(ord(char) < 32 and char not in "\t\r\n" for char in value):
            raise ValueError("La consulta debe contener texto legible.")
        return " ".join(value.split())


class SearchHit(DocumentChunkResponse):
    document_id: UUID
    document_title: str
    filename: str
    document_sha256: str
    source_sha256: str
    processing_version: str
    similarity: float = Field(ge=-1, le=1)


class SearchResponse(BaseModel):
    query: str
    embedding_query: str
    query_version: str
    top_k: int
    min_similarity: float
    available_chunks: int
    results: list[SearchHit]
    method: Literal["exact_cosine"] = "exact_cosine"
    embedding_model: str
    embedding_revision: str
    embedding_version: str
    elapsed_ms: int

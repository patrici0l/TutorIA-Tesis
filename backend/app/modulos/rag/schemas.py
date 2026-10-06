from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict


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

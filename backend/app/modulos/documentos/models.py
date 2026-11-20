from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import JSON, DateTime, ForeignKey, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.base_datos.models.base import Base


class Document(Base):
    __tablename__ = "documentos"
    __table_args__ = (UniqueConstraint("previous_version_id", name="uq_document_previous"),)
    external_source: Mapped[dict | None] = mapped_column(JSON(none_as_null=True))
    course: Mapped[str | None] = mapped_column(String(160), index=True)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    source_reference: Mapped[str | None] = mapped_column(String(500))
    permission_note: Mapped[str | None] = mapped_column(String(500))
    permission_recorded_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    version_number: Mapped[int] = mapped_column(default=1, server_default="1")
    previous_version_id: Mapped[UUID | None] = mapped_column(ForeignKey("documentos.id"))
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    owner_id: Mapped[UUID] = mapped_column(ForeignKey("usuarios.id"), index=True)
    filename: Mapped[str] = mapped_column(String(180))
    title: Mapped[str] = mapped_column(String(160))
    mime_type: Mapped[str] = mapped_column(String(100))
    size_bytes: Mapped[int]
    sha256: Mapped[str] = mapped_column(String(64))
    status: Mapped[str] = mapped_column(String(20), default="uploaded")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    processing_status: Mapped[str] = mapped_column(String(20), default="pending")
    processing_error: Mapped[str | None] = mapped_column(String(40))
    processing_token: Mapped[UUID | None]
    processing_started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    processed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    processing_version: Mapped[str | None] = mapped_column(String(40))
    chunk_chars: Mapped[int | None]
    chunk_overlap: Mapped[int | None]
    chunk_count: Mapped[int] = mapped_column(default=0)
    text_chars: Mapped[int] = mapped_column(default=0)
    index_status: Mapped[str] = mapped_column(String(20), default="pending")
    index_error: Mapped[str | None] = mapped_column(String(40))
    index_token: Mapped[UUID | None]
    index_started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    indexed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    embedding_model: Mapped[str | None] = mapped_column(String(100))
    embedding_revision: Mapped[str | None] = mapped_column(String(40))
    embedding_version: Mapped[str | None] = mapped_column(String(40))

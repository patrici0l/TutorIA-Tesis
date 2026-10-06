from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.base_datos.models.base import Base


class Document(Base):
    __tablename__ = "documentos"
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

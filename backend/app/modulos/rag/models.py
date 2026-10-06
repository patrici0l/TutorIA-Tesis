from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.base_datos.models.base import Base


class DocumentChunk(Base):
    __tablename__ = "fragmentos_documento"
    __table_args__ = (
        UniqueConstraint("document_id", "position", name="uq_fragmentos_documento_position"),
        CheckConstraint("source_kind IN ('page', 'paragraph')", name="ck_fragmentos_source"),
        CheckConstraint("source_index > 0 AND position >= 0", name="ck_fragmentos_position"),
        CheckConstraint("char_start >= 0 AND char_end > char_start", name="ck_fragmentos_offsets"),
        CheckConstraint("length(text) = char_end - char_start", name="ck_fragmentos_length"),
    )
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    document_id: Mapped[UUID] = mapped_column(
        ForeignKey("documentos.id", ondelete="CASCADE"), index=True
    )
    position: Mapped[int]
    source_kind: Mapped[str] = mapped_column(String(12))
    source_index: Mapped[int]
    char_start: Mapped[int]
    char_end: Mapped[int]
    text: Mapped[str] = mapped_column(Text)
    source_sha256: Mapped[str] = mapped_column(String(64))

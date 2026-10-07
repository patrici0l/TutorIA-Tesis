from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.base_datos.models.base import Base


class ContentGeneration(Base):
    __tablename__ = "generaciones_contenido"
    __table_args__ = (
        CheckConstraint(
            "status IN ('prepared','generating','succeeded','failed')",
            name="ck_generaciones_status",
        ),
        CheckConstraint("latency_ms IS NULL OR latency_ms >= 0", name="ck_generaciones_latency"),
        CheckConstraint(
            "estimated_cost IS NULL OR estimated_cost >= 0", name="ck_generaciones_cost"
        ),
        CheckConstraint(
            "(status IN ('prepared','generating') AND completed_at IS NULL "
            "AND resource IS NULL AND error_code IS NULL) OR "
            "(status = 'succeeded' AND completed_at IS NOT NULL "
            "AND resource IS NOT NULL AND error_code IS NULL) OR "
            "(status = 'failed' AND completed_at IS NOT NULL "
            "AND resource IS NULL AND error_code IS NOT NULL)",
            name="ck_generaciones_terminal",
        ),
    )
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    owner_id: Mapped[UUID] = mapped_column(ForeignKey("usuarios.id"), index=True)
    request_snapshot: Mapped[dict] = mapped_column(JSONB)
    sources_snapshot: Mapped[list] = mapped_column(JSONB)
    retrieval_snapshot: Mapped[dict] = mapped_column(JSONB)
    instructions: Mapped[str] = mapped_column(Text)
    prompt: Mapped[str] = mapped_column(Text)
    prompt_version: Mapped[str] = mapped_column(String(40))
    prompt_sha256: Mapped[str] = mapped_column(String(64))
    status: Mapped[str] = mapped_column(String(20), default="prepared")
    provider: Mapped[str | None] = mapped_column(String(20))
    requested_model: Mapped[str | None] = mapped_column(String(128))
    model_version: Mapped[str | None] = mapped_column(String(256))
    response_id: Mapped[str | None] = mapped_column(String(256))
    usage: Mapped[dict | None] = mapped_column(JSONB(none_as_null=True))
    latency_ms: Mapped[int | None]
    estimated_cost: Mapped[Decimal | None] = mapped_column(Numeric(18, 8))
    resource: Mapped[dict | None] = mapped_column(JSONB(none_as_null=True))
    error_code: Mapped[str | None] = mapped_column(String(40))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    generation_started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), index=True
    )

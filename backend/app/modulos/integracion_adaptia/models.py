from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.base_datos.models.base import Base


class AdaptiaGeneration(Base):
    __tablename__ = "generaciones_adaptia"
    __table_args__ = (
        CheckConstraint("status IN ('generating','succeeded','failed')", name="ck_adaptia_status"),
        CheckConstraint(
            "(status = 'generating' AND completed_at IS NULL AND response IS NULL "
            "AND error_code IS NULL) OR "
            "(status = 'succeeded' AND completed_at IS NOT NULL AND response IS NOT NULL "
            "AND error_code IS NULL) OR "
            "(status = 'failed' AND completed_at IS NOT NULL AND response IS NULL "
            "AND error_code IS NOT NULL)",
            name="ck_adaptia_terminal",
        ),
    )
    request_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    payload_sha256: Mapped[str] = mapped_column(String(64))
    request_snapshot: Mapped[dict] = mapped_column(JSONB)
    student_id_hash: Mapped[str] = mapped_column(String(128))
    session_id: Mapped[str] = mapped_column(String(128))
    prompt_version: Mapped[str] = mapped_column(String(40))
    prompt_sha256: Mapped[str] = mapped_column(String(64))
    provider: Mapped[str] = mapped_column(String(20))
    requested_model: Mapped[str] = mapped_column(String(128))
    usage: Mapped[dict | None] = mapped_column(JSONB(none_as_null=True))
    status: Mapped[str] = mapped_column(String(20))
    response: Mapped[dict | None] = mapped_column(JSONB(none_as_null=True))
    error_code: Mapped[str | None] = mapped_column(String(40))
    generation_started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        index=True,
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

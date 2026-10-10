from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.base_datos.models.base import Base


class PerformanceProfile(Base):
    __tablename__ = "perfiles_rendimiento"
    __table_args__ = (
        CheckConstraint("jsonb_typeof(payload) = 'object'", name="ck_perfiles_payload"),
        CheckConstraint("schema_version = 'performance-profile-v1'", name="ck_perfiles_version"),
    )
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    owner_id: Mapped[UUID] = mapped_column(ForeignKey("usuarios.id"), index=True)
    payload: Mapped[dict] = mapped_column(JSONB)
    schema_version: Mapped[str] = mapped_column(String(40), default="performance-profile-v1")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

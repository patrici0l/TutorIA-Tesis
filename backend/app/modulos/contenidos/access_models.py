"""Acceso explícito de un estudiante al corpus publicado de un docente y materia."""

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.base_datos.models.base import Base


class LearningAccess(Base):
    __tablename__ = "accesos_aprendizaje"
    __table_args__ = (UniqueConstraint("teacher_id", "student_id", "course"),)
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    teacher_id: Mapped[UUID] = mapped_column(ForeignKey("usuarios.id"), index=True)
    student_id: Mapped[UUID] = mapped_column(ForeignKey("usuarios.id"), index=True)
    course: Mapped[str] = mapped_column(String(160))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

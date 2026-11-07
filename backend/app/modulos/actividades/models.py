from datetime import datetime
from uuid import UUID

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.base_datos.models.base import Base


class PracticeAssignment(Base):
    __tablename__ = "asignaciones_practica"
    __table_args__ = (
        UniqueConstraint("id", "student_id", "version", name="uq_assignment_student_version"),
        CheckConstraint("status IN ('open', 'closed', 'cancelled')", name="ck_assignment_status"),
        CheckConstraint(
            "(version = 'resource-v1') = (resource_id IS NOT NULL)",
            name="ck_assignment_resource",
        ),
    )
    id: Mapped[UUID] = mapped_column(primary_key=True)
    teacher_id: Mapped[UUID] = mapped_column(ForeignKey("usuarios.id"), index=True)
    student_id: Mapped[UUID] = mapped_column(ForeignKey("usuarios.id"), index=True)
    version: Mapped[str] = mapped_column(String(40))
    resource_id: Mapped[UUID | None] = mapped_column(ForeignKey("generaciones_contenido.id"))
    title: Mapped[str] = mapped_column(String(120))
    instructions: Mapped[str] = mapped_column(String(2000))
    status: Mapped[str] = mapped_column(String(12), server_default="open")
    status_changed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

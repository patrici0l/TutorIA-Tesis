from datetime import datetime
from uuid import UUID

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    ForeignKeyConstraint,
    String,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.base_datos.models.base import Base


class PracticeAttempt(Base):
    __tablename__ = "intentos_practica"
    __table_args__ = (
        CheckConstraint("score >= 0 AND score <= 3", name="ck_practica_score"),
        CheckConstraint("jsonb_array_length(answers) = 3", name="ck_practica_answers"),
        ForeignKeyConstraint(
            ["assignment_id", "owner_id", "version"],
            [
                "asignaciones_practica.id",
                "asignaciones_practica.student_id",
                "asignaciones_practica.version",
            ],
            name="fk_attempt_assignment_student",
        ),
    )
    owner_id: Mapped[UUID] = mapped_column(ForeignKey("usuarios.id"), primary_key=True)
    id: Mapped[UUID] = mapped_column(primary_key=True)
    version: Mapped[str] = mapped_column(String(40))
    assignment_id: Mapped[UUID | None] = mapped_column(index=True)
    answers: Mapped[list] = mapped_column(JSONB)
    score: Mapped[int]
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

from datetime import datetime
from uuid import UUID

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.base_datos.models.base import Base


class PracticeAttempt(Base):
    __tablename__ = "intentos_practica"
    __table_args__ = (
        CheckConstraint("score >= 0 AND score <= 3", name="ck_practica_score"),
        CheckConstraint("jsonb_array_length(answers) = 3", name="ck_practica_answers"),
    )
    owner_id: Mapped[UUID] = mapped_column(ForeignKey("usuarios.id"), primary_key=True)
    id: Mapped[UUID] = mapped_column(primary_key=True)
    version: Mapped[str] = mapped_column(String(40))
    answers: Mapped[list] = mapped_column(JSONB)
    score: Mapped[int]
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

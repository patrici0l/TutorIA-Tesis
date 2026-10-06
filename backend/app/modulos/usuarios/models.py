from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import Boolean, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.base_datos.models.base import Base


class User(Base):
    __tablename__ = "usuarios"
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    institutional_email: Mapped[str] = mapped_column(String(254), unique=True)
    institutional_id: Mapped[str | None] = mapped_column(String(255), unique=True)
    nombre: Mapped[str] = mapped_column(String(100))
    apellido: Mapped[str] = mapped_column(String(100))
    rol: Mapped[str] = mapped_column(String(20), default="student")
    activo: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    last_login: Mapped[datetime] = mapped_column(DateTime(timezone=True))

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class InstitutionalIdentity(BaseModel):
    institutional_email: EmailStr = Field(max_length=254)
    institutional_id: str | None = Field(default=None, max_length=255)
    nombre: str = Field(default="", max_length=100)
    apellido: str = Field(default="", max_length=100)
    rol: Literal["student", "teacher"]


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    institutional_email: str
    institutional_id: str | None
    nombre: str
    apellido: str
    rol: Literal["student", "teacher", "admin"]
    activo: bool
    created_at: datetime
    last_login: datetime


class SessionResponse(BaseModel):
    user: UserResponse
    auth_mode: Literal["mock", "cas"]


class ErrorResponse(BaseModel):
    detail: str

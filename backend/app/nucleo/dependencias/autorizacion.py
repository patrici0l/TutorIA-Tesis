"""Dependencia compartida de gestión docente; conserva la política y error originales."""
from typing import Annotated

from fastapi import Depends, HTTPException

from app.modulos.usuarios.models import User
from app.nucleo.dependencias.auth import get_current_user


def get_document_owner(user: Annotated[User, Depends(get_current_user)]):
    if user.rol not in {"teacher", "admin"}:
        raise HTTPException(403, "La gestión de documentos requiere permisos de docente.")
    return user


Owner = Annotated[User, Depends(get_document_owner)]

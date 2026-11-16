"""Consulta la política local vigente sin exponer perfiles ni ejecutar generación."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query

from app.modulos.contenidos.adaptation_schemas import AdaptationRule, AdaptationRuleCatalog
from app.modulos.contenidos.servicios.adaptation_service import POLICY_VERSION, RULES
from app.modulos.perfiles.router import get_profile_owner
from app.modulos.perfiles.schemas import MasteryLevel

router = APIRouter(prefix="/adaptation", tags=["Reglas de adaptación"])


@router.get(
    "/rules",
    response_model=AdaptationRuleCatalog,
    summary="Consultar el catálogo de reglas locales de adaptación",
    description=(
        "Devuelve las mismas reglas vigentes que utiliza la preparación con perfil sintético. "
        "Requiere sesión de docente o administrador. No modifica datos, no consume cuota "
        "de IA y no calcula el dominio del estudiante. Si se omite la versión, devuelve "
        "la vigente; las versiones históricas solo se conservan en las trazas guardadas. "
        "Este catálogo local todavía no es el contrato del motor ADAPTIA."
    ),
    dependencies=[Depends(get_profile_owner)],
    responses={
        401: {"description": "Sesión ausente, inválida o vencida."},
        403: {"description": "Se requiere rol docente o administrador."},
        404: {"description": "La versión solicitada no está disponible en el catálogo."},
    },
)
def rules(
    version: Annotated[
        str | None,
        Query(
            min_length=1,
            max_length=64,
            description="Versión exacta del catálogo. Sin valor se utiliza la vigente.",
            examples=[POLICY_VERSION],
        ),
    ] = None,
    mastery_level: Annotated[
        MasteryLevel | None,
        Query(description="Filtrar por dominio: low (bajo), medium (medio), high (alto)."),
    ] = None,
):
    if version is not None and version != POLICY_VERSION:
        raise HTTPException(404, "Versión del catálogo de reglas no disponible.")
    return AdaptationRuleCatalog(
        version=POLICY_VERSION,
        rules=[
            AdaptationRule(
                mastery_level=level,
                effective_difficulty=difficulty,
                guidance=guidance,
                suggested_resources=suggestions,
                reason=reason,
            )
            for level, (difficulty, guidance, suggestions, reason) in RULES.items()
            if mastery_level is None or mastery_level == level
        ],
        application_notes=[
            "La adaptación requiere un perfil propio del mismo tema que el recurso.",
            "El dominio se toma del perfil informado; no se calcula a partir del porcentaje.",
            "Con errores frecuentes se añade apoyo localizado sin inferir su gravedad.",
            "La dificultad efectiva sustituye la manual; se mantiene el tipo solicitado.",
            "Sin perfil se conserva la dificultad manual y no se aplica esta política.",
        ],
    )

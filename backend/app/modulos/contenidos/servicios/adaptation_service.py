from uuid import UUID

from fastapi import HTTPException

from app.modulos.contenidos.adaptation_schemas import AdaptationSnapshot
from app.modulos.contenidos.schemas import ContentRequest
from app.modulos.perfiles.schemas import ProfileResponse

POLICY_VERSION = "profile-adaptation-v2"

RULES = {
    "low": (
        "basic",
        "Prioriza el apoyo guiado: explica los símbolos y prerrequisitos que aparecen en "
        "las fuentes, separa las transiciones del procedimiento y explica por qué son válidas. "
        "Anticipa el error informado con una advertencia concreta respaldada por el contexto. "
        "Para EXPLANATION, desarrolla el procedimiento antes de interpretar el resultado. "
        "No inventes prerrequisitos ausentes ni casos numéricos para alargar la respuesta.",
        ["EXPLANATION", "EXERCISE", "QUIZ"],
        "Dominio bajo informado: dificultad básica y refuerzo guiado.",
    ),
    "medium": (
        "intermediate",
        "Prioriza una guía concentrada: resume las transiciones esenciales y explica la "
        "decisión que evita el error informado, sin repetir todas las definiciones básicas. "
        "Para EXPLANATION, combina operaciones rutinarias en pasos coherentes y destaca "
        "por qué funciona el procedimiento. Usa el ejemplo disponible, sin añadir otro "
        "ejercicio ni casos numéricos que las fuentes no desarrollan.",
        ["EXERCISE", "QUIZ", "EXPLANATION"],
        "Dominio medio informado: dificultad intermedia y práctica guiada.",
    ),
    "high": (
        "advanced",
        "Prioriza profundidad conceptual: justifica condiciones de validez, interpreta "
        "consecuencias y distingue una conclusión válida de un error conceptual, siempre "
        "con respaldo explícito en las fuentes. Para EXPLANATION, sintetiza el cálculo "
        "rutinario y dedica los pasos al porqué y a las condiciones; no repitas como eje "
        "la secuencia elemental de un refuerzo básico. La complejidad procede de analizar "
        "el mismo caso, no de cambiar la función ni inventar valores numéricos. "
        "Si el contexto no permite profundizar, reconoce esa limitación sin añadir contenido.",
        ["EXERCISE", "QUIZ"],
        "Dominio alto informado: dificultad avanzada y análisis conceptual del mismo objetivo.",
    ),
}


class AdaptationService:
    def __init__(self, profiles):
        self.profiles = profiles

    def adapt(self, request: ContentRequest, identifier: UUID, owner: UUID):
        record = self.profiles.owned(identifier, owner)
        if record is None:
            raise HTTPException(404, "Perfil no disponible.")
        profile = ProfileResponse(
            **record.payload,
            id=record.id,
            created_at=record.created_at,
            schema_version=record.schema_version,
        )
        if " ".join(profile.topic.casefold().split()) != " ".join(request.topic.casefold().split()):
            raise HTTPException(422, "El perfil debe corresponder al mismo tema del recurso.")
        difficulty, guidance, suggestions, reason = RULES[profile.mastery_level]
        if profile.frequent_errors:
            guidance += (
                " Concentra el apoyo en los errores informados del tema; "
                "no generalices dificultades."
            )
            reason += (
                " Foco localizado en las etiquetas de error informadas, sin inferir su gravedad."
            )
        snapshot = AdaptationSnapshot(
            policy_version=POLICY_VERSION,
            profile=profile,
            requested_difficulty=request.difficulty,
            effective_difficulty=difficulty,
            guidance=guidance,
            reason=reason,
            focus_errors=profile.frequent_errors,
            suggested_resources=suggestions,
        )
        return request.model_copy(update={"difficulty": difficulty}), snapshot

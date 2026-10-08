from uuid import UUID

from fastapi import HTTPException

from app.modulos.contenidos.adaptation_schemas import AdaptationSnapshot
from app.modulos.contenidos.schemas import ContentRequest
from app.modulos.perfiles.schemas import ProfileResponse

RULES = {
    "low": (
        "basic",
        "Refuerza los prerrequisitos presentes en las fuentes, "
        "explica paso a paso y ofrece pistas.",
        ["EXPLANATION", "EXERCISE", "QUIZ"],
        "Dominio bajo informado: dificultad básica y refuerzo guiado.",
    ),
    "medium": (
        "intermediate",
        "Ofrece una explicación breve y práctica guiada con complejidad intermedia.",
        ["EXERCISE", "QUIZ", "EXPLANATION"],
        "Dominio medio informado: dificultad intermedia y práctica guiada.",
    ),
    "high": (
        "advanced",
        "Propón mayor complejidad y razonamiento, con menos explicación de conceptos básicos.",
        ["EXERCISE", "QUIZ"],
        "Dominio alto informado: dificultad avanzada y problemas de mayor complejidad.",
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
            profile=profile,
            requested_difficulty=request.difficulty,
            effective_difficulty=difficulty,
            guidance=guidance,
            reason=reason,
            focus_errors=profile.frequent_errors,
            suggested_resources=suggestions,
        )
        return request.model_copy(update={"difficulty": difficulty}), snapshot

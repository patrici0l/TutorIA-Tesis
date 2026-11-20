from typing import Annotated, Literal

from pydantic import AfterValidator, AwareDatetime, Field, model_validator

from app.modulos.contenidos.schemas import ContentModel

Concept = Annotated[
    str, Field(min_length=1, max_length=160), AfterValidator(ContentModel.readable_text)
]


class PerformanceEvent(ContentModel):
    topic: Concept
    score: float = Field(ge=0, le=100, strict=True)
    time: AwareDatetime


class AdaptiaGenerationRequest(ContentModel):
    student_id: str = Field(
        min_length=8,
        max_length=128,
        pattern=r"^[A-Za-z0-9_-]+$",
        description="Identificador seudonimizado por ADAPTIA; no enviar nombre ni correo.",
    )
    topic: Concept
    difficulty: int = Field(ge=1, le=10, strict=True)
    preferred_modality: Literal["visual", "textual", "auditory"] = Field(
        description="Orientación del texto; esta versión no produce imágenes ni audio."
    )
    context: str = Field(min_length=3, max_length=2000, repr=False)
    performance_history: list[PerformanceEvent] = Field(max_length=50, repr=False)
    known_concepts: list[Concept] = Field(max_length=20)
    gaps: list[Concept] = Field(max_length=20)


class GeneratedSection(ContentModel):
    type: Literal["explanation", "example", "exercise"]
    title: str = Field(min_length=1, max_length=160)
    text: str = Field(min_length=1, max_length=4000, repr=False)


class GeneratedStructure(ContentModel):
    title: str = Field(min_length=1, max_length=160)
    sections: list[GeneratedSection] = Field(min_length=3, max_length=8)

    @model_validator(mode="after")
    def complete_resource(self):
        if {item.type for item in self.sections} != {"explanation", "example", "exercise"}:
            raise ValueError("Incluir explicación, ejemplo y ejercicio.")
        return self


class GenerationMetadata(ContentModel):
    model_used: str = Field(min_length=1, max_length=256)
    tokens_used: int | None = Field(default=None, ge=0)
    generation_time_ms: int = Field(ge=0)


class AdaptiaGenerationData(ContentModel):
    content: str = Field(min_length=1, max_length=36000, repr=False)
    structure: GeneratedStructure
    metadata_generation: GenerationMetadata


class ResponseMetadata(ContentModel):
    timestamp: AwareDatetime
    processing_time_ms: int = Field(ge=0)
    api_version: Literal["v1.0"] = "v1.0"
    mode: Literal["direct"] = "direct"
    replayed: bool = False


class Tracking(ContentModel):
    request_id: str
    student_id_hash: str | None = None
    session_id: str


class AdaptiaSuccess(ContentModel):
    success: Literal[True] = True
    data: AdaptiaGenerationData
    metadata: ResponseMetadata
    tracking: Tracking


class AdaptiaError(ContentModel):
    code: Literal[
        "INVALID_REQUEST",
        "INVALID_STUDENT_PROFILE",
        "AI_SERVICE_UNAVAILABLE",
        "AUTHENTICATION_FAILED",
        "RATE_LIMIT_EXCEEDED",
        "INTERNAL_SERVER_ERROR",
    ]
    message: str
    details: dict | None = None


class AdaptiaFailure(ContentModel):
    success: Literal[False] = False
    error: AdaptiaError
    metadata: ResponseMetadata
    tracking: Tracking

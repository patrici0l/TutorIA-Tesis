import unicodedata
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, TypeAdapter, field_validator, model_validator

ResourceType = Literal["EXPLANATION", "EXERCISE", "QUIZ", "FEEDBACK"]
Difficulty = Literal["basic", "intermediate", "advanced"]
CitationId = Annotated[str, Field(pattern=r"^S[1-9][0-9]?$", max_length=3)]


class ContentModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, hide_input_in_errors=True)

    @field_validator("*", mode="after")
    @classmethod
    def readable_text(cls, value):
        if isinstance(value, str):
            if not value.strip() or any(
                (unicodedata.category(char) in {"Cc", "Cs"} and char not in "\n\r\t")
                for char in value
            ):
                raise ValueError("Texto vacío o caracteres no permitidos")
            return unicodedata.normalize("NFC", value).strip()
        return value


class ContentRequest(ContentModel):
    """Contrato interno inicial; proveedor/propietario/perfil no vienen del cliente."""

    topic: str = Field(min_length=1, max_length=160)
    learning_objective: str = Field(min_length=1, max_length=400)
    resource_type: ResourceType
    difficulty: Difficulty = "basic"
    question_count: int | None = Field(default=None, ge=1, le=5, strict=True)
    student_answer: str | None = Field(default=None, min_length=1, max_length=2000, repr=False)

    @model_validator(mode="after")
    def validate_resource_options(self):
        if (self.resource_type == "FEEDBACK") != (self.student_answer is not None):
            raise ValueError("FEEDBACK requiere una respuesta; otros recursos no la admiten")
        if self.resource_type != "QUIZ" and self.question_count is not None:
            raise ValueError("question_count solo se admite para QUIZ")
        if self.resource_type == "QUIZ" and self.question_count is None:
            object.__setattr__(self, "question_count", 3)
        return self


class CitedText(ContentModel):
    text: str = Field(min_length=1, max_length=2000, repr=False)
    citations: list[CitationId] = Field(min_length=1, max_length=10)

    @field_validator("citations")
    @classmethod
    def distinct_citations(cls, value):
        if len(value) != len(set(value)):
            raise ValueError("Referencias repetidas")
        return value


class Explanation(ContentModel):
    resource_type: Literal["EXPLANATION"]
    title: str = Field(min_length=1, max_length=160)
    summary: CitedText
    steps: list[CitedText] = Field(min_length=1, max_length=8)
    worked_example: CitedText


class Exercise(ContentModel):
    resource_type: Literal["EXERCISE"]
    title: str = Field(min_length=1, max_length=160)
    statement: CitedText
    hints: list[CitedText] = Field(min_length=1, max_length=3)
    solution_steps: list[CitedText] = Field(min_length=1, max_length=8)
    answer: CitedText


class QuizQuestion(ContentModel):
    statement: CitedText
    options: list[Annotated[str, Field(min_length=1, max_length=400)]] = Field(
        min_length=4, max_length=4
    )
    correct_option: int = Field(ge=0, le=3, strict=True)
    explanation: CitedText

    @field_validator("options")
    @classmethod
    def unique_options(cls, value):
        normalized = [ContentModel.readable_text(item) for item in value]
        if len({item.casefold() for item in normalized}) != 4:
            raise ValueError("El quiz requiere cuatro opciones distintas")
        return normalized


class Quiz(ContentModel):
    resource_type: Literal["QUIZ"]
    title: str = Field(min_length=1, max_length=160)
    questions: list[QuizQuestion] = Field(min_length=1, max_length=5)


class Feedback(ContentModel):
    resource_type: Literal["FEEDBACK"]
    title: str = Field(min_length=1, max_length=160)
    diagnosis: CitedText
    correction: CitedText
    next_step: CitedText


EducationalResource = Annotated[
    Explanation | Exercise | Quiz | Feedback, Field(discriminator="resource_type")
]
RESOURCE_ADAPTER = TypeAdapter(EducationalResource)
RESOURCE_SCHEMAS = {
    "EXPLANATION": Explanation,
    "EXERCISE": Exercise,
    "QUIZ": Quiz,
    "FEEDBACK": Feedback,
}

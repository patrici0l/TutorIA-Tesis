"""Contratos internos del modo directo; no sustituyen los contratos RAG."""

from typing import Annotated, Literal

from pydantic import Field, TypeAdapter, field_validator

from app.modulos.contenidos.schemas import ContentModel, QuizQuestion


class DirectText(ContentModel):
    text: str = Field(min_length=1, max_length=2000, repr=False)
    # Campo obligatorio: sin recuperación no existen alias de fuentes que citar.
    citations: list[str] = Field(max_length=0)


class DirectExplanation(ContentModel):
    resource_type: Literal["EXPLANATION"]
    title: str = Field(min_length=1, max_length=160)
    summary: DirectText
    steps: list[DirectText] = Field(min_length=1, max_length=8)
    worked_example: DirectText


class DirectWorkedExample(ContentModel):
    resource_type: Literal["EXAMPLE"]
    title: str = Field(min_length=1, max_length=160)
    statement: DirectText
    solution_steps: list[DirectText] = Field(min_length=1, max_length=8)
    answer: DirectText


class DirectHint(ContentModel):
    resource_type: Literal["HINT"]
    title: str = Field(min_length=1, max_length=160)
    statement: DirectText
    hints: list[DirectText] = Field(min_length=1, max_length=3)


class DirectExercise(ContentModel):
    resource_type: Literal["EXERCISE"]
    title: str = Field(min_length=1, max_length=160)
    statement: DirectText
    hints: list[DirectText] = Field(min_length=1, max_length=3)
    solution_steps: list[DirectText] = Field(min_length=1, max_length=8)
    answer: DirectText


class DirectQuizQuestion(ContentModel):
    statement: DirectText
    options: list[Annotated[str, Field(min_length=1, max_length=400)]] = Field(
        min_length=4, max_length=4
    )
    correct_option: int = Field(ge=0, le=3, strict=True)
    explanation: DirectText

    @field_validator("options")
    @classmethod
    def unique_options(cls, value):
        return QuizQuestion.unique_options(value)


class DirectQuiz(ContentModel):
    resource_type: Literal["QUIZ"]
    title: str = Field(min_length=1, max_length=160)
    questions: list[DirectQuizQuestion] = Field(min_length=1, max_length=5)


class DirectFeedback(ContentModel):
    resource_type: Literal["FEEDBACK"]
    title: str = Field(min_length=1, max_length=160)
    diagnosis: DirectText
    correction: DirectText
    next_step: DirectText


DirectResource = Annotated[
    DirectExplanation
    | DirectWorkedExample
    | DirectHint
    | DirectExercise
    | DirectQuiz
    | DirectFeedback,
    Field(discriminator="resource_type"),
]
DIRECT_RESOURCE_ADAPTER = TypeAdapter(DirectResource)
DIRECT_RESOURCE_SCHEMAS = {
    "EXPLANATION": DirectExplanation,
    "EXAMPLE": DirectWorkedExample,
    "HINT": DirectHint,
    "EXERCISE": DirectExercise,
    "QUIZ": DirectQuiz,
    "FEEDBACK": DirectFeedback,
}

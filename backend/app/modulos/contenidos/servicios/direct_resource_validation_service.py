"""Valida estructura y ausencia de citas; no verifica corrección matemática."""

import json

from app.modulos.contenidos.direct_schemas import (
    DIRECT_RESOURCE_ADAPTER,
    DirectQuiz,
    DirectResource,
)
from app.modulos.contenidos.errors import ContentError
from app.modulos.contenidos.schemas import ContentRequest
from app.modulos.contenidos.servicios.resource_validation_service import unique_object


class DirectResourceValidationService:
    def validate(self, text: str, request: ContentRequest) -> DirectResource:
        try:
            if len(text) > 65536 or len(text.encode("utf-8")) > 262144:
                raise ValueError("Salida demasiado grande")
            payload = json.loads(text, object_pairs_hook=unique_object)
            if payload == {"error": "unable_to_answer"}:
                raise ContentError("content_unable_to_answer")
            resource = DIRECT_RESOURCE_ADAPTER.validate_python(payload)
            if resource.resource_type != request.resource_type:
                raise ContentError("content_wrong_resource")
            if (
                isinstance(resource, DirectQuiz)
                and len(resource.questions) != request.question_count
            ):
                raise ContentError("content_quiz_count")
            return resource
        except (ValueError, TypeError, RecursionError):
            raise ContentError("content_invalid_output") from None

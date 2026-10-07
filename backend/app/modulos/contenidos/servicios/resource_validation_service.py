import json

from pydantic import BaseModel, ValidationError

from app.modulos.contenidos.errors import ContentError
from app.modulos.contenidos.schemas import RESOURCE_ADAPTER, CitedText, ContentRequest, Quiz


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate_key")
        result[key] = value
    return result


def collect_citations(value) -> set[str]:
    if isinstance(value, CitedText):
        return set(value.citations)
    if isinstance(value, BaseModel):
        result = set()
        for name in type(value).model_fields:
            result.update(collect_citations(getattr(value, name)))
        return result
    if isinstance(value, list):
        result = set()
        for item in value:
            result.update(collect_citations(item))
        return result
    return set()


class ResourceValidationService:
    """Validación estructural y pertenencia de citas; no certifica exactitud matemática."""

    def validate(self, text: str, request: ContentRequest, source_ids: set[str]):
        try:
            if len(text) > 65536 or len(text.encode("utf-8")) > 262144:
                raise ValueError()
            payload = json.loads(text, object_pairs_hook=unique_object)
            if payload == {"error": "insufficient_sources"}:
                raise ContentError("content_insufficient_sources")
            resource = RESOURCE_ADAPTER.validate_python(payload)
            if resource.resource_type != request.resource_type:
                raise ContentError("content_wrong_resource")
            if isinstance(resource, Quiz) and len(resource.questions) != request.question_count:
                raise ContentError("content_quiz_count")
            citations = collect_citations(resource)
            if not source_ids or not citations or not citations.issubset(source_ids):
                raise ContentError("content_invalid_citations")
            return resource
        except (ValueError, TypeError, RecursionError, ValidationError):
            raise ContentError("content_invalid_output") from None

import re
import unicodedata
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


def validate_model(value: str) -> str:
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}", value):
        raise ValueError("Configura un identificador de modelo explícito sin URL ni ruta")
    return value


class GenerationRequest(BaseModel):
    """Contrato interno: los prompts serán construidos por el módulo educativo."""

    model_config = ConfigDict(extra="forbid", frozen=True, hide_input_in_errors=True)
    instructions: str = Field(min_length=1, max_length=24000, repr=False)
    prompt: str = Field(min_length=1, max_length=24000, repr=False)

    @field_validator("instructions", "prompt")
    @classmethod
    def validate_text(cls, value: str) -> str:
        if not value.strip() or any(
            (ord(char) < 32 and char not in "\n\r\t") or unicodedata.category(char) == "Cs"
            for char in value
        ):
            raise ValueError("Texto vacío o con caracteres de control")
        return value


class TokenUsage(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    # Ausencia de metadatos no significa consumo cero.
    input_tokens: int | None = Field(default=None, ge=0, strict=True)
    output_tokens: int | None = Field(default=None, ge=0, strict=True)
    reasoning_tokens: int | None = Field(default=None, ge=0, strict=True)
    cached_input_tokens: int | None = Field(default=None, ge=0, strict=True)
    total_tokens: int | None = Field(default=None, ge=0, strict=True)


class GenerationResult(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    provider: Literal["gemini", "openai", "claude"]
    requested_model: str
    model_version: str | None = Field(default=None, max_length=256)
    response_id: str | None = Field(default=None, max_length=256)
    text: str = Field(min_length=1, max_length=65536, repr=False)
    finish_reason: Literal["STOP"] = "STOP"
    usage: TokenUsage
    latency_ms: int = Field(ge=0)

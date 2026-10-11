from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class ExecutionConfiguration(BaseModel):
    """Límites del proceso al reservar; sin credenciales ni configuración global."""

    model_config = ConfigDict(extra="forbid", frozen=True)
    version: Literal["generation-config-v1"] = "generation-config-v1"
    max_input_chars: int = Field(ge=1000, le=24000, strict=True)
    max_output_tokens: int = Field(ge=128, le=4096, strict=True)
    timeout_seconds: int = Field(ge=5, le=60, strict=True)

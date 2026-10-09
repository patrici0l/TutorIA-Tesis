from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from app.modulos.proveedores_ia.schemas import GenerationResult


class CostBasis(BaseModel):
    """Supuesto local conservado antes del envío; no certifica facturación externa."""

    model_config = ConfigDict(extra="forbid", frozen=True)
    version: Literal["confirmed-free-tier-v1"] = "confirmed-free-tier-v1"
    currency: Literal["USD"] = "USD"
    basis: Literal["operator_confirmed_free_tier"] = "operator_confirmed_free_tier"
    provider: Literal["gemini"] = "gemini"
    requested_model: str = Field(min_length=1, max_length=128)
    input_per_million: Literal["0"] = "0"
    output_per_million: Literal["0"] = "0"

    def estimate(self, result: GenerationResult) -> Decimal | None:
        # No inferir consumo desde el total ni completar componentes ausentes con cero.
        if (
            result.provider != self.provider
            or result.requested_model != self.requested_model
            or result.usage.input_tokens is None
            or result.usage.output_tokens is None
        ):
            return None
        return Decimal("0.00000000")

from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class KnownTokenSum(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    known_sum: int | None = Field(ge=0)
    known_records: int = Field(ge=0)
    unknown_records: int = Field(ge=0)


class LatencySummary(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    known_average_ms: Decimal | None = Field(ge=0)
    known_min_ms: int | None = Field(ge=0)
    known_max_ms: int | None = Field(ge=0)
    known_records: int = Field(ge=0)
    unknown_records: int = Field(ge=0)


class MetricsSummary(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    scope: Literal["own_all_time"] = "own_all_time"
    observed_at: datetime
    total_records: int = Field(ge=0)
    prepared: int = Field(ge=0)
    generating: int = Field(ge=0)
    succeeded: int = Field(ge=0)
    failed: int = Field(ge=0)
    reserved_attempts: int = Field(ge=0)
    execution_records: int = Field(ge=0)
    input_tokens: KnownTokenSum
    output_tokens: KnownTokenSum
    total_tokens: KnownTokenSum
    latency: LatencySummary
    cost_known_records: int = Field(ge=0)
    cost_unknown_records: int = Field(ge=0)

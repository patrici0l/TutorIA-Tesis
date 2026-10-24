from datetime import datetime

from pydantic import BaseModel


class GenerationQuota(BaseModel):
    enabled: bool
    daily_limit: int
    used: int
    remaining: int
    resets_at: datetime
    max_output_tokens: int
    timeout_seconds: int

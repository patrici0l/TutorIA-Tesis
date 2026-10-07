from typing import Literal

ErrorCode = Literal[
    "llm_disabled",
    "llm_not_configured",
    "llm_unsupported_provider",
    "llm_input_limit",
    "llm_busy",
    "llm_rate_limit",
    "llm_timeout",
    "llm_unavailable",
    "llm_credentials",
    "llm_rejected",
    "llm_blocked",
    "llm_incomplete",
    "llm_invalid_response",
]


class ProviderError(Exception):
    """Solo códigos estables; nunca payload, clave o error textual del proveedor."""

    def __init__(self, code: ErrorCode):
        self.code = code
        super().__init__(code)

import httpx

from app.configuracion.settings import Settings
from app.modulos.proveedores_ia.claude.claude_provider import ClaudeProvider
from app.modulos.proveedores_ia.errors import ProviderError
from app.modulos.proveedores_ia.gemini.gemini_provider import GeminiProvider
from app.modulos.proveedores_ia.interfaces.llm_provider import LLMProvider
from app.modulos.proveedores_ia.openai.openai_provider import OpenAIProvider
from app.modulos.proveedores_ia.servicios.request_limiter import LLM_LIMITER, RequestLimiter


def create_provider(
    settings: Settings,
    *,
    transport: httpx.BaseTransport | None = None,
    limiter: RequestLimiter = LLM_LIMITER,
) -> LLMProvider:
    if not settings.llm_enabled:
        raise ProviderError("llm_disabled")
    try:
        settings.validate_llm()
    except ValueError:
        raise ProviderError("llm_not_configured") from None
    adapters = {"gemini": GeminiProvider, "openai": OpenAIProvider, "claude": ClaudeProvider}
    return adapters[settings.llm_default_provider](settings, transport=transport, limiter=limiter)

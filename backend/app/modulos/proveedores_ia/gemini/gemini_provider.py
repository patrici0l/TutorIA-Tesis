import json
from time import monotonic

import httpx
from pydantic import ValidationError

from app.configuracion.settings import Settings
from app.modulos.proveedores_ia.errors import ProviderError
from app.modulos.proveedores_ia.interfaces.llm_provider import LLMProvider
from app.modulos.proveedores_ia.schemas import (
    FailureMetadata,
    GenerationRequest,
    GenerationResult,
    TokenUsage,
)
from app.modulos.proveedores_ia.servicios.request_limiter import LLM_LIMITER, RequestLimiter


class GeminiProvider(LLMProvider):
    """REST generateContent de texto, sin herramientas, caché ni fallback automático."""

    def __init__(
        self,
        settings: Settings,
        *,
        transport: httpx.BaseTransport | None = None,
        limiter: RequestLimiter = LLM_LIMITER,
    ):
        self.settings = settings
        self.transport = transport
        self.limiter = limiter

    def generate(self, request: GenerationRequest) -> GenerationResult:
        # También se comprueba si se instancia el adaptador sin la fábrica.
        if not self.settings.llm_enabled:
            raise ProviderError("llm_disabled")
        try:
            self.settings.validate_llm()
        except ValueError:
            raise ProviderError("llm_not_configured") from None
        text = request.instructions + request.prompt
        if len(text) > self.settings.llm_max_input_chars or len(text.encode("utf-8")) > 65536:
            raise ProviderError("llm_input_limit")
        if not self.limiter.slot.acquire(blocking=False):
            raise ProviderError("llm_busy")
        try:
            if not self.limiter.allow(self.settings.llm_requests_per_minute):
                raise ProviderError("llm_rate_limit")
            start = monotonic()
            payload = self._send(request)
            return self._parse(payload, round((monotonic() - start) * 1000))
        finally:
            self.limiter.slot.release()

    def _send(self, request: GenerationRequest) -> object:
        model = self.settings.llm_model
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
        body = {
            "systemInstruction": {"parts": [{"text": request.instructions}]},
            "contents": [{"role": "user", "parts": [{"text": request.prompt}]}],
            "generationConfig": {
                "candidateCount": 1,
                "maxOutputTokens": self.settings.llm_max_output_tokens,
                "responseMimeType": "text/plain",
            },
            "store": False,
        }
        try:
            with httpx.Client(
                timeout=self.settings.llm_timeout_seconds,
                follow_redirects=False,
                trust_env=False,
                transport=self.transport,
            ) as client:
                with client.stream(
                    "POST",
                    url,
                    json=body,
                    headers={"x-goog-api-key": self.settings.gemini_api_key.get_secret_value()},
                ) as response:
                    if response.status_code != 200:
                        code = {
                            401: "llm_credentials",
                            403: "llm_credentials",
                            429: "llm_rate_limit",
                        }.get(response.status_code)
                        if code is None:
                            code = (
                                "llm_unavailable" if response.status_code >= 500 else "llm_rejected"
                            )
                        raise ProviderError(code)
                    data = bytearray()
                    for chunk in response.iter_bytes(chunk_size=16384):
                        if len(data) + len(chunk) > 1_048_576:
                            raise ProviderError("llm_invalid_response")
                        data.extend(chunk)
            return json.loads(data)
        except httpx.TimeoutException:
            raise ProviderError("llm_timeout") from None
        except httpx.HTTPError:
            raise ProviderError("llm_unavailable") from None
        except (ValueError, UnicodeError, RecursionError):
            raise ProviderError("llm_invalid_response") from None

    def _parse(self, payload: object, latency_ms: int) -> GenerationResult:
        try:
            if not isinstance(payload, dict):
                raise ValueError()
            feedback = payload.get("promptFeedback", {})
            if feedback.get("blockReason"):
                raise ProviderError("llm_blocked")
            candidates = payload["candidates"]
            if not isinstance(candidates, list) or len(candidates) != 1:
                raise ValueError()
            candidate = candidates[0]
            if any(rating.get("blocked") is True for rating in candidate.get("safetyRatings", [])):
                raise ProviderError("llm_blocked")
            reason = candidate.get("finishReason")
            if reason == "MAX_TOKENS":
                raise ProviderError(
                    "llm_incomplete", metadata=self._failure_metadata(payload, latency_ms)
                )
            if reason in {"SAFETY", "RECITATION", "BLOCKLIST", "PROHIBITED_CONTENT", "SPII"}:
                raise ProviderError("llm_blocked")
            if reason != "STOP":
                raise ProviderError("llm_invalid_response")
            parts = candidate["content"]["parts"]
            if not isinstance(parts, list) or not parts:
                raise ValueError()
            visible = []
            for part in parts:
                if not isinstance(part, dict) or not isinstance(part.get("text"), str):
                    raise ValueError()
                if set(part) - {"text", "thought", "thoughtSignature"}:
                    raise ValueError()
                if "thought" in part and not isinstance(part["thought"], bool):
                    raise ValueError()
                if not part.get("thought", False):
                    visible.append(part["text"])
            text = "".join(visible)
            if not text.strip():
                raise ValueError()
            usage = payload.get("usageMetadata", {})
            return GenerationResult(
                provider="gemini",
                requested_model=self.settings.llm_model,
                model_version=payload.get("modelVersion"),
                response_id=payload.get("responseId"),
                text=text,
                latency_ms=latency_ms,
                usage=TokenUsage(
                    input_tokens=usage.get("promptTokenCount"),
                    output_tokens=usage.get("candidatesTokenCount"),
                    reasoning_tokens=usage.get("thoughtsTokenCount"),
                    cached_input_tokens=usage.get("cachedContentTokenCount"),
                    total_tokens=usage.get("totalTokenCount"),
                ),
            )
        except (KeyError, TypeError, AttributeError, ValueError, ValidationError):
            raise ProviderError("llm_invalid_response") from None

    def _failure_metadata(self, payload: dict, latency_ms: int) -> FailureMetadata:
        raw = payload.get("usageMetadata")
        raw = raw if isinstance(raw, dict) else {}
        fields = {
            "input_tokens": "promptTokenCount",
            "output_tokens": "candidatesTokenCount",
            "reasoning_tokens": "thoughtsTokenCount",
            "cached_input_tokens": "cachedContentTokenCount",
            "total_tokens": "totalTokenCount",
        }
        # Campos inválidos permanecen desconocidos, sin descartar las otras mediciones.
        values = {
            field: value if type(value := raw.get(key)) is int and value >= 0 else None
            for field, key in fields.items()
        }
        return FailureMetadata(
            provider="gemini",
            requested_model=self.settings.llm_model,
            usage=TokenUsage(**values),
            latency_ms=latency_ms,
        )

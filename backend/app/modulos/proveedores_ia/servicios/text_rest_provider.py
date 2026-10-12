"""Transporte de texto compartido por Responses y Messages, sin reintentos."""

import json
from time import monotonic

import httpx

from app.modulos.proveedores_ia.errors import ProviderError
from app.modulos.proveedores_ia.interfaces.llm_provider import LLMProvider
from app.modulos.proveedores_ia.schemas import FailureMetadata, GenerationResult, TokenUsage
from app.modulos.proveedores_ia.servicios.request_limiter import LLM_LIMITER


class TextRestProvider(LLMProvider):
    provider: str
    url: str

    def __init__(self, settings, *, transport=None, limiter=LLM_LIMITER):
        self.settings, self.transport, self.limiter = settings, transport, limiter

    def generate(self, request):
        if not self.settings.llm_enabled:
            raise ProviderError("llm_disabled")
        if self.settings.llm_default_provider != self.provider:
            raise ProviderError("llm_not_configured")
        try:
            self.settings.validate_llm()
        except ValueError:
            raise ProviderError("llm_not_configured") from None
        combined = request.instructions + request.prompt
        if len(combined) > self.settings.llm_max_input_chars or len(combined.encode()) > 65536:
            raise ProviderError("llm_input_limit")
        if not self.limiter.slot.acquire(blocking=False):
            raise ProviderError("llm_busy")
        try:
            if not self.limiter.allow(self.settings.llm_requests_per_minute):
                raise ProviderError("llm_rate_limit")
            start = monotonic()
            payload = self._send(request)
            latency = round((monotonic() - start) * 1000)
            try:
                usage = self._usage(payload)
                text = self._text(payload, usage, latency)
                if not text.strip():
                    raise ValueError()
                return GenerationResult(
                    provider=self.provider,
                    requested_model=self.settings.llm_model,
                    model_version=payload.get("model"),
                    response_id=payload.get("id"),
                    text=text,
                    usage=usage,
                    latency_ms=latency,
                )
            except (ValueError, TypeError, KeyError, AttributeError, RecursionError):
                raise ProviderError("llm_invalid_response") from None
        finally:
            self.limiter.slot.release()

    def _send(self, request):
        headers, body = self._request(request)
        try:
            with httpx.Client(
                timeout=self.settings.llm_timeout_seconds,
                follow_redirects=False,
                trust_env=False,
                transport=self.transport,
            ) as client:
                with client.stream("POST", self.url, headers=headers, json=body) as response:
                    if response.status_code != 200:
                        code = {
                            401: "llm_credentials",
                            403: "llm_credentials",
                            429: "llm_rate_limit",
                        }.get(response.status_code)
                        raise ProviderError(
                            code
                            or (
                                "llm_unavailable" if response.status_code >= 500 else "llm_rejected"
                            )
                        )
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
        except (ValueError, RecursionError):
            raise ProviderError("llm_invalid_response") from None

    def _fail(self, code, usage, latency):
        raise ProviderError(
            code,
            metadata=FailureMetadata(
                provider=self.provider,
                requested_model=self.settings.llm_model,
                usage=usage,
                latency_ms=latency,
            ),
        )

    @staticmethod
    def _safe_usage(**values):
        return TokenUsage(
            **{
                key: value if type(value) is int and value >= 0 else None
                for key, value in values.items()
            }
        )

    def _request(self, request):
        raise NotImplementedError

    def _usage(self, payload):
        raise NotImplementedError

    def _text(self, payload, usage, latency):
        raise NotImplementedError

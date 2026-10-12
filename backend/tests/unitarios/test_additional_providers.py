import json
from unittest.mock import Mock
from uuid import uuid4

import httpx
import pytest
from fastapi import HTTPException

from app.configuracion.settings import Settings
from app.modulos.contenidos.servicios.generate_preparation_service import GeneratePreparationService
from app.modulos.proveedores_ia.errors import ProviderError
from app.modulos.proveedores_ia.schemas import GenerationRequest
from app.modulos.proveedores_ia.servicios.llm_factory import create_provider
from app.modulos.proveedores_ia.servicios.request_limiter import RequestLimiter

REQUEST = GenerationRequest(instructions="Instrucción de prueba", prompt="Consulta sintética")
KEY = "fictitious-unit-test-key"


def config(kind, **changes):
    values = dict(
        llm_enabled=True,
        llm_default_provider=kind,
        llm_model="model-test",
        openai_api_key=KEY,
        anthropic_api_key=KEY,
    )
    return Settings(_env_file=None, **{**values, **changes})


def answer(kind):
    base = {
        "id": "test-id",
        "model": "model-test-version",
        "usage": {"input_tokens": 12, "output_tokens": 8},
    }
    if kind == "openai":
        return {
            **base,
            "status": "completed",
            "output": [
                {"type": "reasoning", "summary": []},
                {
                    "type": "message",
                    "role": "assistant",
                    "status": "completed",
                    "content": [{"type": "output_text", "text": "Respuesta de prueba."}],
                },
            ],
        }
    return {
        **base,
        "type": "message",
        "role": "assistant",
        "stop_reason": "end_turn",
        "content": [
            {"type": "thinking", "thinking": "PRIVATE"},
            {"type": "text", "text": "Respuesta de prueba."},
        ],
    }


@pytest.fixture(params=["openai", "claude"])
def kind(request):
    return request.param


def adapter(kind, handler, **changes):
    return create_provider(
        config(kind, **changes), transport=httpx.MockTransport(handler), limiter=RequestLimiter()
    )


def test_payload_headers_and_trace(kind):
    calls = []

    def send(request):
        calls.append(request)
        body = json.loads(request.content)
        assert body["model"] == "model-test" and body["stream"] is False
        assert KEY not in str(request.url) and KEY not in request.content.decode()
        if kind == "openai":
            assert str(request.url) == "https://api.openai.com/v1/responses"
            assert request.headers["authorization"] == "Bearer " + KEY
            assert body["store"] is False and body["tools"] == []
            assert body["instructions"] == REQUEST.instructions
            assert body["input"] == [{"role": "user", "content": REQUEST.prompt}]
            assert body["max_output_tokens"] == 1024
        else:
            assert str(request.url) == "https://api.anthropic.com/v1/messages"
            assert request.headers["x-api-key"] == KEY
            assert request.headers["anthropic-version"] == "2023-06-01"
            assert body["system"] == REQUEST.instructions and body["max_tokens"] == 1024
            assert body["messages"] == [{"role": "user", "content": REQUEST.prompt}]
            assert "tools" not in body and "store" not in body
        return httpx.Response(200, json=answer(kind))

    result = adapter(kind, send).generate(REQUEST)
    assert len(calls) == 1 and result.provider == kind
    assert result.text == "Respuesta de prueba."
    assert result.requested_model == "model-test" and result.model_version == "model-test-version"
    assert result.usage.input_tokens == 12 and result.usage.total_tokens is None


@pytest.mark.parametrize(
    "status,code",
    [
        (401, "llm_credentials"),
        (403, "llm_credentials"),
        (429, "llm_rate_limit"),
        (500, "llm_unavailable"),
        (529, "llm_unavailable"),
        (400, "llm_rejected"),
        (302, "llm_rejected"),
    ],
)
def test_http_errors_are_safe_and_never_retried(kind, status, code):
    calls = []

    def send(request):
        calls.append(request)
        return httpx.Response(
            status, text="PRIVATE ERROR", headers={"location": "https://other.test"}
        )

    with pytest.raises(ProviderError, match=f"^{code}$"):
        adapter(kind, send).generate(REQUEST)
    assert len(calls) == 1


@pytest.mark.parametrize("reason", ["limit", "refusal", "tool", "unknown"])
def test_nonterminal_and_blocked_responses(kind, reason):
    payload = answer(kind)
    expected = {"limit": "llm_incomplete", "refusal": "llm_blocked"}.get(
        reason, "llm_invalid_response"
    )
    if kind == "openai":
        if reason == "limit":
            payload.update(status="incomplete", incomplete_details={"reason": "max_output_tokens"})
        elif reason == "refusal":
            payload["output"][1]["content"] = [{"type": "refusal", "refusal": "PRIVATE"}]
        elif reason == "tool":
            payload["output"] = [{"type": "function_call", "arguments": "PRIVATE"}]
        else:
            payload["status"] = "in_progress"
    else:
        payload["stop_reason"] = {
            "limit": "max_tokens",
            "refusal": "refusal",
            "tool": "tool_use",
            "unknown": "unknown",
        }[reason]
    with pytest.raises(ProviderError, match=f"^{expected}$") as error:
        adapter(kind, lambda _: httpx.Response(200, json=payload)).generate(REQUEST)
    if reason in {"limit", "refusal"}:
        assert error.value.metadata.usage.input_tokens == 12
        assert "PRIVATE" not in error.value.metadata.model_dump_json()


@pytest.mark.parametrize("case", ["json", "large", "shape", "empty", "part", "long_text"])
def test_malformed_responses_fail_closed(kind, case):
    payload = answer(kind)
    if case == "json":
        response = httpx.Response(200, text="bad json")
    elif case == "large":
        response = httpx.Response(200, content=b"x" * 1_048_577)
    else:
        if case == "shape":
            payload = []
        elif kind == "openai":
            payload["output"] = (
                []
                if case == "empty"
                else [
                    {
                        "type": "message",
                        "role": "assistant",
                        "status": "completed",
                        "content": [None]
                        if case == "part"
                        else [{"type": "output_text", "text": "x" * 65537}],
                    }
                ]
            )
        else:
            payload["content"] = (
                []
                if case == "empty"
                else [None]
                if case == "part"
                else [{"type": "text", "text": "x" * 65537}]
            )
        response = httpx.Response(200, json=payload)
    with pytest.raises(ProviderError, match="llm_invalid_response"):
        adapter(kind, lambda _: response).generate(REQUEST)


def test_usage_unknowns_and_zero(kind):
    payload = answer(kind)
    payload["usage"] = {"input_tokens": True, "output_tokens": 0, "total_tokens": -1}
    result = adapter(kind, lambda _: httpx.Response(200, json=payload)).generate(REQUEST)
    assert result.usage.input_tokens is None and result.usage.output_tokens == 0
    assert result.usage.total_tokens is None


@pytest.mark.parametrize("problem", ["disabled", "missing_key", "invalid_key", "wrong_adapter"])
def test_configuration_prevents_send(kind, problem):
    handler = Mock()
    provider = adapter(kind, handler)
    if problem == "disabled":
        provider.settings.llm_enabled = False
    elif problem == "wrong_adapter":
        provider.settings.llm_default_provider = "gemini"
    else:
        from pydantic import SecretStr

        field = "openai_api_key" if kind == "openai" else "anthropic_api_key"
        setattr(provider.settings, field, SecretStr("" if problem == "missing_key" else "bad\nkey"))
    with pytest.raises(ProviderError):
        provider.generate(REQUEST)
    handler.assert_not_called()


def test_openai_usage_details_and_missing_metadata():
    payload = answer("openai")
    payload["usage"].update(
        total_tokens=20,
        output_tokens_details={"reasoning_tokens": 3},
        input_tokens_details={"cached_tokens": 4},
    )
    result = adapter("openai", lambda _: httpx.Response(200, json=payload)).generate(REQUEST)
    assert result.usage.total_tokens == 20
    assert result.usage.reasoning_tokens == 3 and result.usage.cached_input_tokens == 4
    del payload["usage"]
    result = adapter("openai", lambda _: httpx.Response(200, json=payload)).generate(REQUEST)
    assert all(value is None for value in result.usage.model_dump().values())


@pytest.mark.parametrize(
    "error,code", [(httpx.ReadTimeout, "llm_timeout"), (httpx.ConnectError, "llm_unavailable")]
)
def test_transport_failures_release_slot(kind, error, code):
    def send(request):
        raise error("PRIVATE", request=request)

    provider = adapter(kind, send)
    with pytest.raises(ProviderError, match=f"^{code}$"):
        provider.generate(REQUEST)
    assert provider.limiter.slot.acquire(blocking=False)
    provider.limiter.slot.release()


def test_preflight_input_busy_and_rate_limits(kind):
    send = Mock(return_value=httpx.Response(200, json=answer(kind)))
    provider = adapter(kind, send, llm_max_input_chars=1000, llm_requests_per_minute=1)
    with pytest.raises(ProviderError, match="llm_input_limit"):
        provider.generate(GenerationRequest(instructions="x", prompt="x" * 1000))
    provider.limiter.slot.acquire()
    with pytest.raises(ProviderError, match="llm_busy"):
        provider.generate(REQUEST)
    provider.limiter.slot.release()
    send.assert_not_called()
    provider.generate(REQUEST)
    with pytest.raises(ProviderError, match="llm_rate_limit"):
        provider.generate(REQUEST)
    assert send.call_count == 1


def test_free_tier_flag_does_not_authorize_other_providers(kind, monkeypatch):
    factory, claim, trace = Mock(), Mock(), Mock()
    monkeypatch.setattr(
        "app.modulos.contenidos.servicios.generate_preparation_service.create_provider", factory
    )
    service = GeneratePreparationService(claim, trace, config(kind, llm_free_tier_confirmed=True))
    with pytest.raises(HTTPException) as error:
        service.generate(uuid4(), uuid4())
    assert error.value.status_code == 503
    factory.assert_not_called()
    claim.claim.assert_not_called()
    trace.fail.assert_not_called()


def test_direct_gemini_instantiation_rejects_another_provider(kind):
    from app.modulos.proveedores_ia.gemini.gemini_provider import GeminiProvider

    handler = Mock()
    provider = GeminiProvider(
        config(kind), transport=httpx.MockTransport(handler), limiter=RequestLimiter()
    )
    with pytest.raises(ProviderError, match="llm_not_configured"):
        provider.generate(REQUEST)
    handler.assert_not_called()

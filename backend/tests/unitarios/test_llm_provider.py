import json

import httpx
import pytest
from pydantic import SecretStr, ValidationError

from app.configuracion.settings import Settings
from app.modulos.proveedores_ia.errors import ProviderError
from app.modulos.proveedores_ia.schemas import GenerationRequest
from app.modulos.proveedores_ia.servicios import request_limiter
from app.modulos.proveedores_ia.servicios.llm_factory import create_provider
from app.modulos.proveedores_ia.servicios.request_limiter import RequestLimiter

FAKE_KEY = "fictitious-key-for-unit-tests-only"
REQUEST = GenerationRequest(instructions="Instrucción sintética.", prompt="Consulta sintética.")


def configuration(**changes):
    values = dict(
        llm_enabled=True,
        llm_default_provider="gemini",
        llm_model="model-test-v1",
        gemini_api_key=SecretStr(FAKE_KEY),
    )
    values.update(changes)
    return Settings(_env_file=None, **values)


def answer(**changes):
    result = {
        "candidates": [
            {
                "finishReason": "STOP",
                "content": {
                    "parts": [
                        {"text": "Razonamiento privado ficticio", "thought": True},
                        {"text": "Respuesta sintética de contrato."},
                    ]
                },
            }
        ],
        "modelVersion": "model-test-v1-001",
        "responseId": "fictitious-response-id",
        "usageMetadata": {
            "promptTokenCount": 20,
            "candidatesTokenCount": 10,
            "thoughtsTokenCount": 5,
            "totalTokenCount": 35,
        },
    }
    result.update(changes)
    return result


def provider(handler, settings=None, limiter=None):
    return create_provider(
        settings or configuration(),
        transport=httpx.MockTransport(handler),
        limiter=limiter or RequestLimiter(),
    )


def test_gemini_contract_headers_payload_and_trace():
    seen = []

    def respond(request):
        seen.append(request)
        assert str(request.url) == (
            "https://generativelanguage.googleapis.com/v1beta/models/model-test-v1:generateContent"
        )
        assert request.headers["x-goog-api-key"] == FAKE_KEY
        assert FAKE_KEY not in str(request.url)
        body = json.loads(request.content)
        assert body == {
            "contents": [{"role": "user", "parts": [{"text": REQUEST.prompt}]}],
            "systemInstruction": {"parts": [{"text": REQUEST.instructions}]},
            "generationConfig": {
                "candidateCount": 1,
                "maxOutputTokens": 1024,
                "responseMimeType": "text/plain",
            },
            "store": False,
        }
        return httpx.Response(200, json=answer())

    result = provider(respond).generate(REQUEST)
    assert len(seen) == 1
    assert result.text == "Respuesta sintética de contrato."
    assert result.requested_model == "model-test-v1"
    assert result.model_version == "model-test-v1-001"
    assert result.response_id == "fictitious-response-id"
    assert result.usage.input_tokens == 20
    assert result.usage.output_tokens == 10
    assert result.usage.reasoning_tokens == 5
    assert result.usage.total_tokens == 35
    assert result.usage.cached_input_tokens is None
    assert result.latency_ms >= 0
    assert REQUEST.prompt not in repr(REQUEST)
    assert FAKE_KEY not in repr(configuration())
    assert result.text not in repr(result)


@pytest.mark.parametrize(
    "field,value",
    [
        ("llm_enabled", False),
        ("llm_model", ""),
        ("llm_model", "models/evil"),
        ("llm_model", "https://example.org"),
        ("gemini_api_key", SecretStr("")),
        ("gemini_api_key", SecretStr("bad\nkey")),
        ("llm_default_provider", "openai"),
        ("llm_default_provider", "claude"),
    ],
)
def test_factory_fails_before_network(field, value):
    config = configuration()
    setattr(config, field, value)
    with pytest.raises(ProviderError) as caught:
        create_provider(config, transport=httpx.MockTransport(lambda _: pytest.fail("network")))
    assert caught.value.code in {"llm_disabled", "llm_not_configured", "llm_unsupported_provider"}


@pytest.mark.parametrize("text", ["  ", "x\x00", "x\ud800"])
def test_invalid_prompts(text):
    with pytest.raises(ValidationError):
        GenerationRequest(instructions="test", prompt=text)


def test_input_limits_do_not_spend_attempts():
    limiter = RequestLimiter()
    adapter = provider(lambda _: pytest.fail("network"), limiter=limiter)
    with pytest.raises(ProviderError, match="llm_input_limit"):
        adapter.generate(GenerationRequest(instructions="x" * 7000, prompt="x" * 7000))
    with pytest.raises(ProviderError, match="llm_input_limit"):
        provider(
            lambda _: pytest.fail("network"), configuration(llm_max_input_chars=24000), limiter
        ).generate(GenerationRequest(instructions="x", prompt="😀" * 18000))
    assert not limiter.attempts


@pytest.mark.parametrize(
    "status,code",
    [
        (401, "llm_credentials"),
        (403, "llm_credentials"),
        (429, "llm_rate_limit"),
        (500, "llm_unavailable"),
        (503, "llm_unavailable"),
        (400, "llm_rejected"),
        (302, "llm_rejected"),
    ],
)
def test_http_failures_are_safe_and_not_retried(status, code):
    calls = []

    def respond(request):
        calls.append(request)
        return httpx.Response(
            status, json={"error": FAKE_KEY}, headers={"Location": "https://evil"}
        )

    with pytest.raises(ProviderError) as caught:
        provider(respond).generate(REQUEST)
    assert str(caught.value) == code
    assert caught.value.__cause__ is None
    assert len(calls) == 1


@pytest.mark.parametrize(
    "error,code",
    [
        (httpx.ReadTimeout("sensitive details"), "llm_timeout"),
        (httpx.ConnectError("sensitive details"), "llm_unavailable"),
    ],
)
def test_transport_failures_release_slot(error, code):
    limiter = RequestLimiter()

    def respond(_):
        raise error

    with pytest.raises(ProviderError, match=code):
        provider(respond, limiter=limiter).generate(REQUEST)
    assert limiter.slot.acquire(blocking=False)
    limiter.slot.release()


@pytest.mark.parametrize(
    "payload,code",
    [
        ([], "llm_invalid_response"),
        ({}, "llm_invalid_response"),
        (answer(candidates=[]), "llm_invalid_response"),
        (answer(promptFeedback={"blockReason": "SAFETY"}), "llm_blocked"),
        (answer(usageMetadata={"promptTokenCount": -1}), "llm_invalid_response"),
        (answer(usageMetadata={"totalTokenCount": True}), "llm_invalid_response"),
        (answer(usageMetadata=None), "llm_invalid_response"),
        (answer(candidates=[{"finishReason": "MAX_TOKENS"}]), "llm_incomplete"),
        (answer(candidates=[{"finishReason": "SAFETY"}]), "llm_blocked"),
        (answer(candidates=[{"finishReason": "OTHER"}]), "llm_invalid_response"),
        (
            answer(candidates=[{"finishReason": "STOP", "content": {"parts": [{"text": " "}]}}]),
            "llm_invalid_response",
        ),
        (
            answer(
                candidates=[{"finishReason": "STOP", "content": {"parts": [{"functionCall": {}}]}}]
            ),
            "llm_invalid_response",
        ),
    ],
)
def test_unusable_responses_are_not_published(payload, code):
    with pytest.raises(ProviderError, match=code):
        provider(lambda _: httpx.Response(200, json=payload)).generate(REQUEST)


def test_missing_usage_remains_unknown():
    payload = answer()
    del payload["usageMetadata"]
    result = provider(lambda _: httpx.Response(200, json=payload)).generate(REQUEST)
    assert all(value is None for value in result.usage.model_dump().values())


@pytest.mark.parametrize(
    "data",
    [b"not JSON", b"\xff", b"x" * 1_048_577, b"[" * 2000 + b"]" * 2000],
    ids=["json", "utf8", "size", "depth"],
)
def test_invalid_or_oversized_body(data):
    with pytest.raises(ProviderError, match="llm_invalid_response"):
        provider(lambda _: httpx.Response(200, content=data)).generate(REQUEST)


def test_rate_window_is_shared_and_expires(monkeypatch):
    clock = [0.0]
    monkeypatch.setattr(request_limiter, "monotonic", lambda: clock[0])
    limiter = RequestLimiter()
    config = configuration()
    config.llm_requests_per_minute = 1
    first = provider(lambda _: httpx.Response(200, json=answer()), config, limiter)
    second = provider(lambda _: pytest.fail("network"), config, limiter)
    first.generate(REQUEST)
    with pytest.raises(ProviderError, match="llm_rate_limit"):
        second.generate(REQUEST)
    clock[0] = 60.0
    first.generate(REQUEST)
    assert len(limiter.attempts) == 1


def test_busy_slot_prevents_network():
    limiter = RequestLimiter()
    limiter.slot.acquire()
    try:
        with pytest.raises(ProviderError, match="llm_busy"):
            provider(lambda _: pytest.fail("network"), limiter=limiter).generate(REQUEST)
    finally:
        limiter.slot.release()
    assert not limiter.attempts


def test_disabled_configuration_does_not_require_credentials():
    config = Settings(_env_file=None, llm_enabled=False)
    config.validate_llm()
    config.llm_enabled = True
    with pytest.raises(ValueError):
        config.validate_llm()

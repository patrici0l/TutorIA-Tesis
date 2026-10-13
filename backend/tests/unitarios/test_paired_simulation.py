import copy
import json
import socket
import sys

import httpx
import pytest

from app.modulos.evaluacion.paired_assessment import apply_pair_assessment
from app.modulos.evaluacion.paired_preparation import prepare_pair
from app.modulos.evaluacion.paired_simulation import main, simulate_pair
from tests.fixtures.content_reference import request, resource, retrieval
from tests.unitarios.test_additional_providers import answer
from tests.unitarios.test_direct_content import direct_resource


@pytest.fixture(autouse=True)
def no_network(monkeypatch):
    def denied(*args, **kwargs):
        pytest.fail("La simulación intentó usar la red")

    monkeypatch.setattr(socket.socket, "connect", denied)
    monkeypatch.setenv("LLM_MODEL", "environment-must-not-be-used")
    monkeypatch.setenv("DOCUMENT_CHUNK_OVERLAP", "invalid-ignored-environment")


def inputs(provider="openai", kind="EXPLANATION"):
    manifest = prepare_pair(
        {
            "request": request(kind, difficulty="intermediate").model_dump(mode="json"),
            "retrieval": retrieval().model_dump(mode="json"),
            "target": {"provider": provider, "requested_model": "model-test"},
            "max_output_tokens": 1024,
            "timeout_seconds": 30,
        }
    )
    responses = {}
    for mode in ("direct", "rag"):
        body = answer(provider)
        content = direct_resource(kind) if mode == "direct" else resource(kind)
        set_text(provider, body, json.dumps(content))
        responses[mode] = {"status_code": 200, "body": body}
    return manifest, responses


def set_text(provider, body, text):
    if provider == "openai":
        body["output"][1]["content"][0]["text"] = text
    else:
        body["content"][1]["text"] = text


@pytest.mark.parametrize("provider", ["openai", "claude"])
@pytest.mark.parametrize("kind", ["EXPLANATION", "EXERCISE", "QUIZ", "FEEDBACK"])
def test_complete_offline_path_is_reproducible_and_pending_human(provider, kind):
    manifest, responses = inputs(provider, kind)
    before = copy.deepcopy((manifest, responses))
    bundle = simulate_pair(manifest, responses)
    assert bundle == simulate_pair(manifest, responses)
    assert (manifest, responses) == before
    assert bundle["evidence_origin"] == "synthetic_fixture"
    assert not bundle["benchmark_complete"]
    cases = bundle["report"]["cases"]
    assert [case["status"] for case in cases] == ["valid_resource", "valid_resource"]
    assert all(case["usage"]["input_tokens"] == 12 for case in cases)
    assert all(case["latency_ms"] is None for case in cases)
    assert all(block["citations"] == [] for block in cases[0]["review_blocks"])
    assert all(block["citations"] == ["S1"] for block in cases[1]["review_blocks"])
    review = apply_pair_assessment(manifest, bundle["batch"], bundle["assessment_template"])
    assert review["semantic_review_status"] == "pending_human"
    assert review["coverage"]["assessed_claims"] == 0


@pytest.mark.parametrize("provider", ["openai", "claude"])
@pytest.mark.parametrize("scenario", ["http_failure", "abstention", "invalid", "truncated"])
def test_non_success_does_not_drop_either_arm(provider, scenario):
    manifest, responses = inputs(provider)
    rag = responses["rag"]
    expected = "provider_failure"
    if scenario == "http_failure":
        rag.update(status_code=429, body={"error": "PRIVATE"})
    elif scenario == "truncated":
        if provider == "openai":
            rag["body"].update(
                status="incomplete", incomplete_details={"reason": "max_output_tokens"}
            )
        else:
            rag["body"]["stop_reason"] = "max_tokens"
    else:
        text = '{"error":"insufficient_sources"}' if scenario == "abstention" else "not JSON"
        set_text(provider, rag["body"], text)
        expected = "abstained" if scenario == "abstention" else "invalid_output"
    bundle = simulate_pair(manifest, responses)
    assert [case["status"] for case in bundle["report"]["cases"]] == ["valid_resource", expected]
    assert len(bundle["assessment_template"]["cases"]) == 2
    assert "PRIVATE" not in json.dumps(bundle)
    assert bundle["report"]["summary_by_mode"]["rag"]["attempt_count"] == 1


@pytest.mark.parametrize("change", ["hash", "provider", "limits", "missing_arm", "extra_arm"])
def test_rejects_invalid_controls_and_fixtures(change):
    manifest, responses = inputs()
    if change == "hash":
        manifest["arms"][0]["generation_request"]["prompt"] = "modified"
    elif change in {"provider", "limits"}:
        spec = manifest["input"]
        if change == "provider":
            spec["target"]["provider"] = "gemini"
        else:
            spec["max_output_tokens"] = None
        manifest = prepare_pair(spec)
    elif change == "missing_arm":
        del responses["rag"]
    else:
        responses["extra"] = responses["rag"]
    with pytest.raises(ValueError):
        simulate_pair(manifest, responses)


def test_cli_roundtrip_and_exclusive_output(tmp_path, monkeypatch):
    manifest, responses = inputs()
    paths = [tmp_path / name for name in ("manifest.json", "responses.json", "bundle.json")]
    for path, value in zip(paths, (manifest, responses)):
        path.write_text(json.dumps(value), encoding="utf-8")
    monkeypatch.setattr(sys, "argv", ["simulation", *map(str, paths)])
    assert main() == 0
    bundle = json.loads(paths[2].read_text(encoding="utf-8"))
    assert bundle == simulate_pair(manifest, responses)
    original = paths[2].read_bytes()
    with pytest.raises(SystemExit) as error:
        main()
    assert error.value.code == 1
    assert paths[2].read_bytes() == original


@pytest.mark.parametrize("provider", ["openai", "claude"])
def test_manifest_controls_reach_adapter_without_direct_sources(provider, monkeypatch):
    manifest, responses = inputs(provider)
    spec = manifest["input"]
    spec.update(max_output_tokens=512, timeout_seconds=15)
    manifest = prepare_pair(spec)
    sent = []
    original = httpx.MockTransport.handle_request

    def capture(transport, outgoing):
        sent.append((json.loads(outgoing.content), outgoing.extensions["timeout"]))
        return original(transport, outgoing)

    monkeypatch.setattr(httpx.MockTransport, "handle_request", capture)
    simulate_pair(manifest, responses)
    assert len(sent) == 2
    for arm, (body, timeout) in zip(manifest["arms"], sent, strict=True):
        assert body["model"] == "model-test"
        assert set(timeout.values()) == {15}
        if provider == "openai":
            prompt = body["input"][0]["content"]
            assert body["instructions"] == arm["generation_request"]["instructions"]
            assert body["max_output_tokens"] == 512
        else:
            prompt = body["messages"][0]["content"]
            assert body["system"] == arm["generation_request"]["instructions"]
            assert body["max_tokens"] == 512
        assert prompt == arm["generation_request"]["prompt"]
        assert ("sources" in json.loads(prompt)) == (arm["mode"] == "rag")

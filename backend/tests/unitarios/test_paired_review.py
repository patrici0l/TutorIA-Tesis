import copy
import json
import sys
from uuid import uuid4

import pytest

from app.modulos.evaluacion.paired_preparation import prepare_pair
from app.modulos.evaluacion.paired_review import build_paired_review, main
from tests.fixtures.content_reference import request, resource, retrieval
from tests.unitarios.test_direct_content import direct_resource


def inputs(kind="EXPLANATION"):
    manifest = prepare_pair(
        {
            "request": request(kind, difficulty="intermediate").model_dump(mode="json"),
            "retrieval": retrieval().model_dump(mode="json"),
        }
    )
    batch = {
        "manifest_sha256": manifest["manifest_sha256"],
        "evidence_origin": "synthetic_fixture",
        "attempts": [
            {
                "attempt_id": str(uuid4()),
                "mode": arm["mode"],
                "prompt_sha256": arm["prompt_sha256"],
                "outcome": "response",
                "text": json.dumps(
                    direct_resource(kind) if arm["mode"] == "direct" else resource(kind)
                ),
            }
            for arm in manifest["arms"]
        ],
    }
    return manifest, batch


@pytest.mark.parametrize("kind", ["EXPLANATION", "EXERCISE", "QUIZ", "FEEDBACK"])
def test_valid_resources_and_pending_human_review(kind):
    manifest, batch = inputs(kind)
    before = copy.deepcopy((manifest, batch))
    report = build_paired_review(manifest, batch)
    assert report == build_paired_review(manifest, batch)
    assert (manifest, batch) == before
    assert not report["benchmark_complete"]
    for mode in ("direct", "rag"):
        assert report["summary_by_mode"][mode]["valid_resource"] == 1
        assert report["summary_by_mode"][mode]["total_tokens"] is None
    for case in report["cases"]:
        assert case["review_blocks"]
        assert all(block["semantic_verdict"] is None for block in case["review_blocks"])


def test_failures_abstentions_invalid_outputs_and_partial_usage_are_preserved():
    manifest, batch = inputs()
    direct, rag = batch["attempts"]
    direct["text"] = '{"error":"unable_to_answer"}'
    direct["usage"] = {"total_tokens": 10}
    rag["text"] = '{"error":"insufficient_sources"}'
    failure = {
        **direct,
        "attempt_id": str(uuid4()),
        "outcome": "provider_failure",
        "error_code": "llm_timeout",
        "usage": {},
    }
    del failure["text"]
    batch["attempts"] += [failure, {**rag, "attempt_id": str(uuid4()), "text": "invalid"}]
    report = build_paired_review(manifest, batch)
    assert [case["status"] for case in report["cases"]] == [
        "abstained",
        "abstained",
        "provider_failure",
        "invalid_output",
    ]
    assert report["summary_by_mode"]["direct"]["attempt_count"] == 2
    assert report["summary_by_mode"]["direct"]["known_total_tokens_subtotal"] == 10
    assert report["summary_by_mode"]["direct"]["total_tokens"] is None
    assert all(case["resource"] is None for case in report["cases"])


@pytest.mark.parametrize(
    "change",
    [
        "manifest",
        "prompt",
        "target",
        "duplicate",
        "failure_text",
        "missing_text",
        "unknown_error",
        "bool_usage",
        "origin",
    ],
)
def test_invalid_registration_rejected(change):
    manifest, batch = inputs()
    attempt = batch["attempts"][0]
    if change == "manifest":
        batch["manifest_sha256"] = "a" * 64
    elif change == "prompt":
        attempt["prompt_sha256"] = manifest["arms"][1]["prompt_sha256"]
    elif change == "target":
        attempt["target"] = {"provider": "openai", "requested_model": "test"}
    elif change == "duplicate":
        batch["attempts"].append(attempt)
    elif change == "failure_text":
        attempt.update(outcome="provider_failure", error_code="llm_timeout")
    elif change == "missing_text":
        del attempt["text"]
    elif change == "unknown_error":
        attempt["error_code"] = "secret-provider-error"
    elif change == "bool_usage":
        attempt["usage"] = {"total_tokens": True}
    else:
        batch["evidence_origin"] = "declared_provider_output"
    with pytest.raises(ValueError):
        build_paired_review(manifest, batch)


def test_missing_arm_is_not_counted_as_success_and_zero_usage_is_known():
    manifest, batch = inputs()
    batch["attempts"] = batch["attempts"][:1]
    batch["attempts"][0]["usage"] = {"total_tokens": 0}
    report = build_paired_review(manifest, batch)
    assert report["summary_by_mode"]["direct"]["total_tokens"] == 0
    assert report["summary_by_mode"]["rag"]["attempt_count"] == 0
    assert report["summary_by_mode"]["rag"]["total_tokens"] is None


def test_wrong_citations_are_invalid_in_each_mode():
    manifest, batch = inputs()
    batch["attempts"][0]["text"] = json.dumps(resource())
    batch["attempts"][1]["text"] = json.dumps(direct_resource())
    report = build_paired_review(manifest, batch)
    assert all(case["status"] == "invalid_output" for case in report["cases"])


def test_cli_roundtrip_and_no_overwrite(tmp_path, monkeypatch):
    manifest, batch = inputs()
    m, b, out = (tmp_path / name for name in ("manifest.json", "batch.json", "report.json"))
    m.write_text(json.dumps(manifest), encoding="utf-8")
    b.write_text(json.dumps(batch), encoding="utf-8")
    monkeypatch.setattr(sys, "argv", ["paired_review", str(m), str(b), str(out)])
    assert main() == 0
    original = out.read_bytes()
    assert json.loads(original) == build_paired_review(manifest, batch)
    with pytest.raises(SystemExit) as error:
        main()
    assert error.value.code == 1
    assert out.read_bytes() == original

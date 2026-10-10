import json
from uuid import uuid4

import pytest

from app.modulos.contenidos.errors import ContentError
from app.modulos.evaluacion.offline_review import build_review, main
from tests.fixtures.content_reference import request, resource, retrieval
from tests.unitarios.test_profile_validation import SAMPLE


@pytest.fixture
def evidence():
    sources = [dict(retrieval().results[0].model_dump(mode="json"), citation_id="S1")]
    rows = []
    for level, difficulty, total, start in (
        ("high", "advanced", 1542, "2026-10-09T09:08:15+00:00"),
        ("low", "basic", 1542, "2026-10-08T23:12:00+00:00"),
        ("medium", "intermediate", 1493, "2026-10-08T23:13:24+00:00"),
    ):
        rows.append({
            "id": str(uuid4()), "level": level, "status": "succeeded",
            "profile": dict(SAMPLE, id=str(uuid4()), created_at=start, performance=42.0,
                            mastery_level=level),
            "request": request(difficulty=difficulty).model_dump(),
            "sources": sources, "resource": resource(), "provider": "gemini",
            "requested_model": "synthetic-model", "model_version": "synthetic-model",
            "prompt_version": "synthetic-prompt", "policy_version": "synthetic-policy",
            "prompt_sha256": "a" * 64, "generation_started_at": start,
            "usage": {"total_tokens": total},
        })
    return rows


def test_saved_comparison_has_pending_semantics_and_known_coverage(evidence):
    report = build_review(evidence)
    assert report["mechanically_comparable"] is True
    assert report["known_total_tokens_sum"] == 4577
    assert report["total_tokens_known_cases"] == 3
    assert report["generation_start_span_seconds"] > 9 * 3600
    assert report["semantic_review_status"] == "pending"
    assert [case["level"] for case in report["cases"]] == ["low", "medium", "high"]
    assert all(claim["source_support"] is None
               for case in report["cases"] for claim in case["claims"])
    assert "student_id" not in json.dumps(report) and "owner_id" not in json.dumps(report)


def test_mixed_objectives_are_reported_without_hiding_unknown_usage(evidence):
    evidence[0]["request"]["learning_objective"] = "Otro objetivo sintético."
    evidence[0]["usage"] = None
    report = build_review(evidence)
    assert report["mechanically_comparable"] is False
    assert report["mechanical_checks"]["same_request_except_difficulty"] is False
    assert report["total_tokens_known_cases"] == 2
    assert report["known_total_tokens_sum"] == 3035


@pytest.mark.parametrize("problem", ["citation", "real_profile", "duplicate_level"])
def test_invalid_or_non_synthetic_evidence_rejected(evidence, problem):
    if problem == "citation":
        evidence[0]["resource"]["summary"]["citations"] = ["S9"]
    elif problem == "real_profile":
        evidence[0]["profile"]["data_kind"] = "institutional"
    else:
        evidence[1]["level"] = evidence[0]["level"]
    with pytest.raises((ValueError, ContentError)):
        build_review(evidence)


def test_cli_never_overwrites_input_or_existing_review(tmp_path, monkeypatch, evidence):
    source = tmp_path / "input.json"
    source.write_text(json.dumps(evidence), encoding="utf-8")
    output = tmp_path / "review.json"
    output.write_text("revisión humana conservada", encoding="utf-8")
    monkeypatch.setattr("sys.argv", ["offline_review", str(source), str(output)])
    with pytest.raises(SystemExit) as error:
        main()
    assert error.value.code == 1
    assert output.read_text(encoding="utf-8") == "revisión humana conservada"

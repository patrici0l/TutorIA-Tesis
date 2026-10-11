import copy
import json
from uuid import uuid4

import pytest

from app.modulos.contenidos.errors import ContentError
from app.modulos.evaluacion.trial_review import build_trial_review, main
from tests.fixtures.content_reference import request, resource, retrieval
from tests.unitarios.test_profile_validation import SAMPLE


@pytest.fixture
def trial():
    sources = [dict(retrieval().results[0].model_dump(mode="json"), citation_id="S1")]
    rows = []
    for level, difficulty in (("low", "basic"), ("medium", "intermediate"), ("high", "advanced")):
        success = level == "medium"
        rows.append(
            {
                "level": level,
                "history": {
                    "preparation": {
                        **request(difficulty=difficulty).model_dump(exclude={"student_answer"}),
                        "id": str(uuid4()),
                        "status": "prepared",
                        "sources": copy.deepcopy(sources),
                        "adaptation": {
                            "policy_version": "profile-adaptation-v2",
                            "profile": dict(
                                SAMPLE,
                                id=str(uuid4()),
                                mastery_level=level,
                                created_at="2026-10-10T00:00:00Z",
                            ),
                            "requested_difficulty": "basic",
                            "effective_difficulty": difficulty,
                            "guidance": "Guía sintética",
                            "reason": "Motivo sintético",
                            "focus_errors": ["regla_potencia"],
                            "suggested_resources": ["EXPLANATION"],
                        },
                    },
                    "status": "succeeded" if success else "failed",
                    "created_at": "2026-10-10T00:00:00Z",
                    "completed_at": "2026-10-10T00:01:01Z",
                    "resource": resource() if success else None,
                    "message": "Mensaje no exportado",
                    "audit": {
                        "generation_started_at": "2026-10-10T00:01:00Z",
                        "provider": "gemini",
                        "requested_model": "synthetic-model",
                        "model_version": "synthetic-model" if success else None,
                        "prompt_version": "synthetic-prompt",
                        "prompt_sha256": "a" * 64,
                        "usage": {"total_tokens": 30} if success else None,
                        "latency_ms": 10 if success else None,
                        "estimated_cost": None,
                        "error_code": None if success else "llm_incomplete",
                        "retrieval": {
                            "method": "exact_cosine",
                            "query_version": "test-query",
                            "embedding_model": "test-embedding",
                            "embedding_revision": "test-revision",
                            "embedding_version": "test-v1",
                            "top_k": 3,
                            "min_similarity": 0,
                            "available_chunks": 1,
                            "elapsed_ms": 1,
                        },
                    },
                },
            }
        )
    return rows


def configuration(output=1024):
    return {
        "version": "generation-config-v1",
        "max_input_chars": 12000,
        "max_output_tokens": output,
        "timeout_seconds": 30,
    }


def test_failures_are_included_with_unknown_consumption_and_pending_review(trial):
    original = copy.deepcopy(trial)
    report = build_trial_review(trial)
    assert trial == original
    assert report["valid_resource_count"] == 1 and report["failed_case_count"] == 2
    assert report["known_total_tokens_sum"] == 30 and report["total_tokens_known_cases"] == 1
    assert report["batch_total_tokens"] is None
    assert report["control_evidence_status"] == "incomplete_evidence"
    assert report["same_recorded_execution_configuration"] is None
    assert report["ready_for_controlled_semantic_review"] is False
    assert all(
        value["verdict"] is None for case in report["cases"] for value in case["review"].values()
    )
    assert not report["cases"][0]["claims"] and report["cases"][0]["error_code"] == "llm_incomplete"
    assert "student_id" not in json.dumps(report) and "Mensaje no exportado" not in json.dumps(
        report
    )


def test_failed_usage_is_counted_and_zero_is_preserved(trial):
    for row in trial:
        row["history"]["audit"]["usage"] = {"total_tokens": 0}
    report = build_trial_review(trial)
    assert report["batch_total_tokens"] == 0 and report["total_tokens_known_cases"] == 3
    for row in trial:
        row["history"]["audit"]["usage"] = None
    assert build_trial_review(trial)["known_total_tokens_sum"] is None


def test_failed_case_with_hidden_error_code_remains_in_report(trial):
    trial[0]["history"]["audit"]["error_code"] = None
    report = build_trial_review(trial)
    assert report["failed_case_count"] == 2
    assert report["cases"][0]["error_code"] is None


def test_recorded_limits_and_mixed_objectives_change_comparability(trial):
    for row in trial:
        row["history"]["audit"]["execution_configuration"] = configuration()
    assert build_trial_review(trial)["recorded_controls_match"] is True
    trial[0]["history"]["audit"]["execution_configuration"] = configuration(512)
    assert build_trial_review(trial)["control_evidence_status"] == "different_controls"
    trial[0]["history"]["audit"]["execution_configuration"] = configuration()
    trial[0]["history"]["preparation"]["learning_objective"] = "Otro objetivo"
    report = build_trial_review(trial)
    assert report["mechanical_checks"]["same_request_except_difficulty"] is False
    assert report["case_count"] == 3


def test_three_successes_with_matching_limits_are_ready_without_grading(trial):
    for row in trial:
        row["history"].update(status="succeeded", resource=resource())
        row["history"]["audit"].update(error_code=None, execution_configuration=configuration())
    report = build_trial_review(trial)
    assert report["three_level_content_available"] is True
    assert report["ready_for_controlled_semantic_review"] is True
    assert report["semantic_review_status"] == "pending_human"


@pytest.mark.parametrize(
    "problem",
    [
        "missing_case",
        "duplicate_level",
        "duplicate_id",
        "in_progress",
        "failed_with_content",
        "success_without_resource",
        "unknown_citation",
        "real_profile",
        "naive_date",
        "missing_model",
    ],
)
def test_inconsistent_evidence_is_rejected(trial, problem):
    history = trial[0]["history"]
    if problem == "missing_case":
        trial.pop()
    elif problem == "duplicate_level":
        trial[0]["level"] = "medium"
    elif problem == "duplicate_id":
        history["preparation"]["id"] = trial[1]["history"]["preparation"]["id"]
    elif problem == "in_progress":
        history["status"] = "generating"
    elif problem == "failed_with_content":
        history["resource"] = resource()
    elif problem == "success_without_resource":
        history["status"] = "succeeded"
    elif problem == "unknown_citation":
        trial[1]["history"]["resource"]["summary"]["citations"] = ["S9"]
    elif problem == "real_profile":
        history["preparation"]["adaptation"]["profile"]["data_kind"] = "institutional"
    elif problem == "naive_date":
        history["audit"]["generation_started_at"] = "2026-10-10T00:01:00"
    else:
        history["audit"]["requested_model"] = None
    with pytest.raises((ValueError, ContentError)):
        build_trial_review(trial)


def test_cli_hashes_inputs_and_never_overwrites_review(tmp_path, monkeypatch, trial):
    paths = []
    for row in trial:
        path = tmp_path / (row["level"] + ".json")
        path.write_text(json.dumps(row["history"]), encoding="utf-8")
        paths.append(str(path))
    output = tmp_path / "review.json"
    monkeypatch.setattr("sys.argv", ["trial_review", *paths, str(output)])
    assert main() == 0
    original = output.read_bytes()
    assert len(json.loads(original)["input_files"]) == 3
    with pytest.raises(SystemExit) as error:
        main()
    assert error.value.code == 1 and output.read_bytes() == original
    monkeypatch.setattr("sys.argv", ["trial_review", *paths, paths[0]])
    original = (tmp_path / "low.json").read_bytes()
    with pytest.raises(SystemExit):
        main()
    assert (tmp_path / "low.json").read_bytes() == original

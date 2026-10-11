import copy
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from app.modulos.evaluacion.human_review import apply_assessment, main, prepare_assessment
from app.modulos.evaluacion.trial_review import build_trial_review
from tests.unitarios.test_trial_review import trial as trial


@pytest.fixture
def review(trial):
    report = build_trial_review(trial)
    provenance = [
        {"level": level, "input_sha256": str(index) * 64}
        for index, level in enumerate(("low", "medium", "high"))
    ]
    return report, provenance, prepare_assessment(report, provenance)


def declare(payload):
    payload["reviewer_name"] = "Revisor ficticio de prueba"
    payload["reviewed_at"] = "2026-10-09T00:00:00Z"


def test_pending_template_preserves_failures_and_unknown_controls(review):
    before = copy.deepcopy(review)
    result = apply_assessment(*review)
    assert result["semantic_review_status"] == "pending_human"
    assert result["coverage"]["cases_without_content"] == 2
    assert result["coverage"]["assessed_dimensions"] == 0
    assert result["declared_assessment"]["reviewer_name"] is None
    assert result["technical_report"] == review[0]
    assert review == before


def test_partial_judgment_does_not_approve_trial(review):
    declare(review[2])
    review[2]["cases"][1]["dimensions"]["objective_scope"] = {
        "verdict": "does_not_meet",
        "evidence": "Observación ficticia, no evaluación real.",
    }
    result = apply_assessment(*review)
    assert result["semantic_review_status"] == "partial"
    assert result["coverage"]["assessed_dimensions"] == 1
    assert result["coverage"]["assessed_claims"] == 0
    assert result["technical_report"]["three_level_content_available"] is False


def test_completed_available_content_still_preserves_failed_cases(review):
    declare(review[2])
    case = review[2]["cases"][1]
    for decision in case["dimensions"].values():
        decision.update(verdict="partially_meets", evidence="Evidencia ficticia.")
    for decision, original in zip(case["claims"], case["context"]["claims"], strict=True):
        decision.update(
            support="supported", evidence="Cotejo ficticio.", source_aliases=original["citations"]
        )
    result = apply_assessment(*review)
    assert result["semantic_review_status"] == "available_content_reviewed"
    assert result["coverage"]["assessed_dimensions"] == 5
    assert result["coverage"]["cases_without_content"] == 2
    assert result["technical_report"]["failed_case_count"] == 2


@pytest.mark.parametrize(
    "mutation",
    [
        "no_evidence",
        "blank",
        "no_reviewer",
        "failed_case",
        "changed_context",
        "hash",
        "duplicate_case",
        "missing_claim",
        "false_alias",
        "missing_alias",
        "wrong_dimension",
        "extra",
        "naive_date",
        "future_date",
    ],
)
def test_invalid_review_rejected(review, mutation):
    payload = review[2]
    declare(payload)
    decision = payload["cases"][1]["dimensions"]["objective_scope"]
    decision.update(verdict="meets", evidence="Evidencia ficticia.")
    if mutation == "no_evidence":
        decision["evidence"] = None
    elif mutation == "blank":
        decision["evidence"] = "   "
    elif mutation == "no_reviewer":
        payload["reviewer_name"] = payload["reviewed_at"] = None
    elif mutation == "failed_case":
        payload["cases"][0]["dimensions"]["objective_scope"] = copy.deepcopy(decision)
    elif mutation == "changed_context":
        payload["cases"][1]["context"]["request"]["topic"] = "Otro tema"
    elif mutation == "hash":
        payload["input_files"][0]["input_sha256"] = "a" * 64
    elif mutation == "duplicate_case":
        payload["cases"][2] = copy.deepcopy(payload["cases"][1])
    elif mutation == "missing_claim":
        payload["cases"][1]["claims"].pop()
    elif mutation in {"false_alias", "missing_alias"}:
        payload["cases"][1]["claims"][0].update(
            support="supported",
            evidence="Cotejo ficticio.",
            source_aliases=["S999"] if mutation == "false_alias" else [],
        )
    elif mutation == "wrong_dimension":
        payload["cases"][1]["dimensions"]["invented"] = payload["cases"][1]["dimensions"].pop(
            "clarity"
        )
    elif mutation == "extra":
        payload["approved"] = True
    elif mutation == "naive_date":
        payload["reviewed_at"] = "2026-10-09T00:00:00"
    else:
        payload["reviewed_at"] = (datetime.now(UTC) + timedelta(days=1)).isoformat()
    with pytest.raises(ValueError):
        apply_assessment(*review)


def test_cli_template_and_validation_never_overwrite(tmp_path, monkeypatch):
    evidence = Path(__file__).resolve().parents[3] / "documentacion/pruebas"
    paths = [
        str(evidence / f"hito_09_piloto_v4_{level}.json") for level in ("low", "medium", "high")
    ]
    draft, report = tmp_path / "draft.json", tmp_path / "report.json"
    monkeypatch.setattr("sys.argv", ["human_review", "prepare", *paths, str(draft)])
    assert main() == 0
    before = draft.read_bytes()
    with pytest.raises(SystemExit):
        main()
    assert draft.read_bytes() == before
    monkeypatch.setattr(
        "sys.argv", ["human_review", "apply", *paths, str(report), "--assessment", str(draft)]
    )
    assert main() == 0
    report_before = report.read_bytes()
    with pytest.raises(SystemExit):
        main()
    assert report.read_bytes() == report_before


def test_context_numeric_zero_cannot_be_changed_to_boolean(review):
    source = review[2]["cases"][1]["context"]["sources"][0]
    source["position"] = False
    with pytest.raises(ValueError):
        apply_assessment(*review)

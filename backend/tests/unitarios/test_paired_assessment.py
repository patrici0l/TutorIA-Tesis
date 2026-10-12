import json
import sys

import pytest

from app.modulos.evaluacion.paired_assessment import (
    apply_pair_assessment,
    main,
    prepare_pair_assessment,
)
from tests.unitarios.test_paired_review import inputs


def reviewer(template):
    template.update(reviewer_name="Revisor ficticio de prueba", reviewed_at="2026-01-01T12:00:00Z")


def test_pending_template_does_not_invent_decisions():
    manifest, batch = inputs()
    template = prepare_pair_assessment(manifest, batch)
    result = apply_pair_assessment(manifest, batch, template)
    assert template["reviewer_name"] is None
    assert result["semantic_review_status"] == "pending_human"
    assert result["coverage"]["assessed_claims"] == 0
    assert not result["benchmark_complete"]


@pytest.mark.parametrize("kind", ["EXPLANATION", "EXERCISE", "QUIZ", "FEEDBACK"])
def test_full_synthetic_review_includes_direct_reference_support(kind):
    manifest, batch = inputs(kind)
    template = prepare_pair_assessment(manifest, batch)
    reviewer(template)
    for case in template["cases"]:
        for decision in case["dimensions"].values():
            decision.update(verdict="meets", evidence="Juicio ficticio para probar el contrato.")
        for claim in case["claims"]:
            claim.update(
                support="supported", evidence="Referencia sintética S1.", source_aliases=["S1"]
            )
    result = apply_pair_assessment(manifest, batch, template)
    assert result["semantic_review_status"] == "available_content_reviewed"
    assert result["coverage"]["assessed_claims"] == result["coverage"]["available_claims"]
    assert not result["benchmark_complete"]


@pytest.mark.parametrize(
    "change",
    [
        "hash",
        "context",
        "mode",
        "reorder",
        "omit_case",
        "duplicate_case",
        "omit_claim",
        "claim_path",
        "dimension",
        "missing_evidence",
        "blank_evidence",
        "unknown_source",
        "duplicate_source",
        "no_source",
        "no_reviewer",
        "no_date",
        "future",
        "naive_date",
    ],
)
def test_rejects_tampering_and_unsubstantiated_judgments(change):
    manifest, batch = inputs()
    template = prepare_pair_assessment(manifest, batch)
    reviewer(template)
    claim = template["cases"][0]["claims"][0]
    claim.update(support="supported", evidence="Evidencia ficticia.", source_aliases=["S1"])
    if change == "hash":
        template["report_sha256"] = "a" * 64
    elif change == "context":
        template["cases"][0]["context"]["request"]["topic"] = "Otro tema"
    elif change == "mode":
        template["cases"][0]["context"]["case"]["mode"] = "rag"
    elif change == "reorder":
        template["cases"].reverse()
    elif change == "omit_case":
        template["cases"].pop()
    elif change == "duplicate_case":
        template["cases"][1] = template["cases"][0]
    elif change == "omit_claim":
        template["cases"][0]["claims"].pop()
    elif change == "claim_path":
        claim["path"] = "invented"
    elif change == "dimension":
        template["cases"][0]["dimensions"].popitem()
    elif change == "missing_evidence":
        claim["evidence"] = None
    elif change == "blank_evidence":
        claim["evidence"] = "  "
    elif change == "unknown_source":
        claim["source_aliases"] = ["S9"]
    elif change == "duplicate_source":
        claim["source_aliases"] = ["S1", "S1"]
    elif change == "no_source":
        claim["source_aliases"] = []
    elif change == "no_reviewer":
        template.update(reviewer_name=None, reviewed_at=None)
    elif change == "no_date":
        template["reviewed_at"] = None
    elif change == "future":
        template["reviewed_at"] = "2999-01-01T00:00:00Z"
    else:
        template["reviewed_at"] = "2026-01-01T00:00:00"
    with pytest.raises(ValueError):
        apply_pair_assessment(manifest, batch, template)


def test_failure_remains_unreviewable_and_partial_decision_counted():
    manifest, batch = inputs()
    batch["attempts"][1]["text"] = '{"error":"insufficient_sources"}'
    template = prepare_pair_assessment(manifest, batch)
    reviewer(template)
    template["cases"][0]["claims"][0].update(
        support="unsupported", evidence="No aparece en las fuentes de referencia."
    )
    result = apply_pair_assessment(manifest, batch, template)
    assert result["semantic_review_status"] == "partial"
    assert result["coverage"]["cases_without_content"] == 1
    assert result["coverage"]["assessed_claims"] == 1
    next(iter(template["cases"][1]["dimensions"].values())).update(
        verdict="meets", evidence="Juicio no permitido."
    )
    with pytest.raises(ValueError):
        apply_pair_assessment(manifest, batch, template)


def test_cli_prepare_apply_pending_and_no_overwrite(tmp_path, monkeypatch):
    manifest, batch = inputs()
    m, b, template, output = (
        tmp_path / name for name in ("manifest.json", "batch.json", "template.json", "output.json")
    )
    m.write_text(json.dumps(manifest), encoding="utf-8")
    b.write_text(json.dumps(batch), encoding="utf-8")
    monkeypatch.setattr(
        sys, "argv", ["paired_assessment", "prepare", str(m), str(b), str(template)]
    )
    assert main() == 0
    monkeypatch.setattr(
        sys,
        "argv",
        ["paired_assessment", "apply", str(m), str(b), str(output), "--assessment", str(template)],
    )
    assert main() == 0
    original = output.read_bytes()
    assert json.loads(original)["semantic_review_status"] == "pending_human"
    with pytest.raises(SystemExit) as error:
        main()
    assert error.value.code == 1
    assert output.read_bytes() == original

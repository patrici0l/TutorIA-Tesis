"""Prepara y valida revisiones humanas declaradas de pares, sin IA ni DB."""

import argparse
import copy
import json
from datetime import datetime
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.modulos.contenidos.errors import ContentError
from app.modulos.evaluacion.human_review import Assessment, ClaimDecision, Decision
from app.modulos.evaluacion.offline_review import DIMENSIONS
from app.modulos.evaluacion.paired_preparation import digest, read_payload
from app.modulos.evaluacion.paired_review import build_paired_review


class PairCaseAssessment(BaseModel):
    model_config = ConfigDict(extra="forbid")
    context: dict
    dimensions: dict[str, Decision]
    claims: list[ClaimDecision]


class PairAssessment(BaseModel):
    model_config = ConfigDict(extra="forbid", hide_input_in_errors=True)
    version: Literal["declared-pair-assessment-v1"]
    report_sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
    reviewer_name: str | None = Field(default=None, min_length=1, max_length=160)
    reviewed_at: datetime | None = None
    cases: list[PairCaseAssessment]

    @model_validator(mode="after")
    def identity(self):
        return Assessment.identity(self)


def prepare_pair_assessment(manifest: dict, batch: dict) -> dict:
    report = build_paired_review(manifest, batch)
    return {
        "version": "declared-pair-assessment-v1",
        "report_sha256": report["report_sha256"],
        "reviewer_name": None,
        "reviewed_at": None,
        "cases": [
            {
                "context": {
                    "case": copy.deepcopy(case),
                    "request": copy.deepcopy(manifest["input"]["request"]),
                    "shared_controls": copy.deepcopy(manifest["shared_controls"]),
                    "sources": copy.deepcopy(report["reference_sources"]),
                },
                "dimensions": {name: {"verdict": None, "evidence": None} for name in DIMENSIONS},
                "claims": [
                    {"path": block["path"], "support": None, "evidence": None, "source_aliases": []}
                    for block in case["review_blocks"]
                ],
            }
            for case in report["cases"]
        ],
    }


def apply_pair_assessment(manifest: dict, batch: dict, payload: dict) -> dict:
    expected = prepare_pair_assessment(manifest, batch)
    assessment = PairAssessment.model_validate(payload)
    if assessment.report_sha256 != expected["report_sha256"] or len(assessment.cases) != len(
        expected["cases"]
    ):
        raise ValueError("Revisión ajena o casos omitidos.")
    aliases = {source["citation_id"] for source in manifest["reference_sources"]}
    dimensions, claims, available_dimensions, available_claims = 0, 0, 0, 0
    for case, original in zip(assessment.cases, expected["cases"], strict=True):
        if digest(case.context) != digest(original["context"]):
            raise ValueError("Contexto modificado o casos reordenados.")
        if set(case.dimensions) != set(DIMENSIONS):
            raise ValueError("Dimensiones incompletas o ajenas.")
        if [claim.path for claim in case.claims] != [claim["path"] for claim in original["claims"]]:
            raise ValueError("Afirmaciones omitidas, repetidas o ajenas.")
        valid = original["context"]["case"]["status"] == "valid_resource"
        decisions = sum(decision.verdict is not None for decision in case.dimensions.values())
        if not valid and decisions:
            raise ValueError("Sin recurso válido no se evalúa su calidad semántica.")
        dimensions += decisions
        available_dimensions += len(DIMENSIONS) if valid else 0
        available_claims += len(case.claims)
        for claim in case.claims:
            # Fuentes de referencia compartidas, incluso si el generador directo no cita.
            if not set(claim.source_aliases).issubset(aliases):
                raise ValueError("Fuente de revisión ajena al manifiesto.")
            claims += claim.support is not None
    if dimensions + claims and assessment.reviewer_name is None:
        raise ValueError("Decisiones sin revisor/fecha declarados.")
    complete = available_dimensions > 0 and (
        dimensions == available_dimensions and claims == available_claims
    )
    report = {
        "version": "pair-assessment-validation-v1",
        "report_sha256": expected["report_sha256"],
        "assessment": assessment.model_dump(mode="json"),
        "semantic_review_status": "available_content_reviewed"
        if complete
        else ("partial" if dimensions + claims else "pending_human"),
        "coverage": {
            "assessed_dimensions": dimensions,
            "available_dimensions": available_dimensions,
            "assessed_claims": claims,
            "available_claims": available_claims,
            "cases_without_content": sum(
                case["context"]["case"]["status"] != "valid_resource" for case in expected["cases"]
            ),
        },
        "benchmark_complete": False,
        "limitations": [
            "Identidad declarada, no autenticada; evidencia textual no verificada automáticamente.",
            "Validar el registro no aprueba sus conclusiones ni certifica calidad académica.",
            "Revisión completa del contenido disponible no completa intentos ausentes o fallidos.",
        ],
    }
    return {**report, "validation_sha256": digest(report)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("prepare", "apply"))
    parser.add_argument("manifest", type=Path)
    parser.add_argument("attempts", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--assessment", type=Path)
    args = parser.parse_args()
    try:
        if (args.mode == "apply") != (args.assessment is not None):
            raise ValueError("apply requiere revisión; prepare no la acepta.")
        manifest, batch = read_payload(args.manifest), read_payload(args.attempts)
        result = (
            apply_pair_assessment(manifest, batch, read_payload(args.assessment))
            if args.mode == "apply"
            else prepare_pair_assessment(manifest, batch)
        )
        rendered = json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False) + "\n"
        rendered.encode("utf-8")
        with args.output.open("x", encoding="utf-8", newline="\n") as output:
            output.write(rendered)
    except (OSError, ValueError, TypeError, KeyError, RecursionError, ContentError):
        parser.exit(1, "Revisión/entradas inválidas o destino no disponible.\n")
    print("Registro guardado; las conclusiones no se certifican automáticamente.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

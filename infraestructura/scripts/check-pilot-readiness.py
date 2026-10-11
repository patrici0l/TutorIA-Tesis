"""Read-only, fixed-protocol check; never sends a generation or changes settings."""

import argparse
import hashlib
import json
import subprocess
from pathlib import Path

PROTOCOL_SHA256 = "48be7fc1d89f61c4946043f545d91bc1623df34d856c2841edf3ff569857aae6"
LEVELS = ("low", "medium", "high")
PREPARATION_IDS = (
    "b989369e-0b18-487c-9ac3-c39fe4f8ed2d",
    "0987537d-1448-4b06-8cfb-e01f3c8ec04a",
    "e2f5b13b-af24-4c14-9166-82ac742889cd",
)
COLLECTOR = """
import json, sys
from uuid import UUID
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.base_datos.session import get_engine
from app.configuracion.settings import get_settings
s = get_settings()
ids = [str(UUID(value)) for value in json.load(sys.stdin)]
runtime = {name: getattr(s, name) for name in (
    'app_env', 'auth_mode', 'auth_mock_user', 'llm_enabled',
    'llm_free_tier_confirmed', 'llm_daily_request_limit', 'llm_default_provider',
    'llm_model', 'llm_max_input_chars', 'llm_max_output_tokens', 'llm_timeout_seconds')}
with Session(get_engine()) as db:
    db.execute(text('SET TRANSACTION ISOLATION LEVEL REPEATABLE READ, READ ONLY'))
    quota = dict(db.execute(text('''
        SELECT CURRENT_TIMESTAMP AS checked_at,
        date_trunc('day', CURRENT_TIMESTAMP AT TIME ZONE 'UTC')
            AT TIME ZONE 'UTC' + interval '1 day' AS resets_at,
        count(*) FILTER (WHERE generation_started_at >=
            date_trunc('day', CURRENT_TIMESTAMP AT TIME ZONE 'UTC') AT TIME ZONE 'UTC') AS used,
        count(*) FILTER (WHERE status = 'generating') AS active,
        count(*) FILTER (WHERE generation_started_at > CURRENT_TIMESTAMP - interval '60 seconds')
            AS recent
        FROM generaciones_contenido
    ''' )).mappings().one())
    rows = [dict(row) for row in db.execute(text('''
        SELECT id, owner_id, status, generation_started_at, request_snapshot,
        sources_snapshot, adaptation_snapshot, instructions, prompt, prompt_version,
        prompt_sha256, execution_configuration
        FROM generaciones_contenido WHERE id = ANY(CAST(:ids AS uuid[]))
    ''' ), {'ids': ids}).mappings()]
    document_ids = list({source['document_id'] for row in rows for source in row['sources_snapshot']})
    documents = [dict(row) for row in db.execute(text('''
        SELECT id, owner_id, sha256, deleted_at FROM documentos
        WHERE id = ANY(CAST(:ids AS uuid[]))
    ''' ), {'ids': document_ids}).mappings()]
print(json.dumps({'runtime': runtime, 'quota': quota, 'rows': rows,
                  'documents': documents}, default=str))
"""


def digest(value):
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def prompt_digest(row):
    payload = {key: row[key] for key in ("instructions", "prompt")}
    return digest(
        json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    )


def build_report(protocol, preparations, state):
    """All checks must pass. Unknown or already reserved cases never become ready."""
    runtime, quota = state["runtime"], state["quota"]
    rows = {row["id"]: row for row in state["rows"]}
    documents = {row["id"]: row for row in state["documents"]}
    expected_runtime = {
        "app_env": "development",
        "auth_mode": "mock",
        "llm_enabled": True,
        "llm_free_tier_confirmed": True,
        "llm_daily_request_limit": protocol["daily_request_limit"],
        "llm_default_provider": protocol["provider"],
        "llm_model": protocol["model"],
        "llm_max_input_chars": protocol["max_input_chars"],
        "llm_max_output_tokens": protocol["max_output_tokens"],
        "llm_timeout_seconds": protocol["timeout_seconds"],
    }
    configuration = {
        key: runtime.get(key) == value for key, value in expected_runtime.items()
    }
    cases = []
    levels_valid = (
        [entry["level"] for entry in preparations["preparations"]] == list(LEVELS)
        and [entry["level"] for entry in protocol["baseline_cases"]] == list(LEVELS)
        and len({entry["preparation"]["id"] for entry in preparations["preparations"]})
        == 3
    )
    for entry, baseline in zip(
        preparations["preparations"], protocol["baseline_cases"], strict=True
    ):
        identifier = entry["preparation"]["id"]
        row, original = rows.get(identifier), rows.get(baseline["generation_id"])
        checks = {"records_present": row is not None and original is not None}
        if checks["records_present"]:
            sources = row["sources_snapshot"]
            adaptation = row["adaptation_snapshot"] or {}
            profile = adaptation.get("profile", {})
            checks.update(
                unreserved=row["status"] == "prepared"
                and row["generation_started_at"] is None
                and row["execution_configuration"] is None,
                distinct_case=identifier != baseline["generation_id"],
                same_owner=row["owner_id"] == original["owner_id"],
                same_request=row["request_snapshot"] == original["request_snapshot"],
                protocol_request=all(
                    row["request_snapshot"].get(key) == value
                    for key, value in protocol["request"].items()
                    if key != "difficulty"
                )
                and adaptation.get("requested_difficulty")
                == protocol["request"]["difficulty"],
                same_adaptation=adaptation == original["adaptation_snapshot"]
                and adaptation == entry["preparation"]["adaptation"],
                fixed_profile=profile.get("id") == baseline["profile_id"]
                and profile.get("mastery_level") == entry["level"]
                and profile.get("data_kind") == "synthetic",
                fixed_versions=row["prompt_version"] == protocol["prompt_version"]
                and adaptation.get("policy_version") == protocol["policy_version"],
                same_prompt=row["prompt"] == original["prompt"]
                and row["instructions"] == original["instructions"]
                and prompt_digest(row)
                == row["prompt_sha256"]
                == baseline["prompt_sha256"],
                same_sources=bool(sources) and sources == original["sources_snapshot"],
                public_sources=[
                    {k: v for k, v in source.items() if k != "text_sha256"}
                    for source in sources
                ]
                == entry["preparation"]["sources"],
                text_hashes=bool(sources)
                and all(
                    digest(source["text"]) == source.get("text_sha256")
                    for source in sources
                ),
                documents_available=bool(sources)
                and all(
                    (document := documents.get(source["document_id"])) is not None
                    and document["owner_id"] == row["owner_id"]
                    and document["deleted_at"] is None
                    and document["sha256"] == source["document_sha256"]
                    for source in sources
                ),
            )
        cases.append(
            {
                "level": entry["level"],
                "id": identifier,
                "checks": checks,
                "passed": all(checks.values()),
            }
        )
    remaining = max(0, runtime["llm_daily_request_limit"] - quota["used"])
    gates = {
        "fixed_preflight": preparations["protocol_sha256"] == PROTOCOL_SHA256,
        "three_ordered_unique_cases": levels_valid,
        "fixed_preparation_ids": tuple(
            entry["preparation"]["id"] for entry in preparations["preparations"]
        )
        == PREPARATION_IDS,
        "three_calls_available": remaining >= 3,
        "no_active_generation": quota["active"] == 0,
        "minimum_interval_elapsed": quota["recent"] == 0,
        "configuration_matches_protocol": all(configuration.values()),
        "case_integrity": len(cases) == 3 and all(case["passed"] for case in cases),
    }
    return {
        "protocol_id": protocol["protocol_id"],
        "protocol_sha256": PROTOCOL_SHA256,
        "checked_at_utc": quota["checked_at"],
        "quota": {**quota, "remaining": remaining},
        "container_configuration": runtime,
        "configuration_checks": configuration,
        "cases": cases,
        "gates": gates,
        "ready": all(gates.values()),
        "blocking_checks": [key for key, passed in gates.items() if not passed],
        "generation_requested": False,
        "configuration_modified": False,
        "scope": "Point-in-time check; API reservation remains authoritative.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output", type=Path, help="New JSON evidence file; never overwritten."
    )
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[2]
    evidence = root / "documentacion/pruebas"
    raw = (evidence / "hito_09_protocolo_salida1024.json").read_bytes()
    if hashlib.sha256(raw).hexdigest() != PROTOCOL_SHA256:
        parser.exit(2, "El manifiesto cambió. No se consultó la DB.\n")
    if args.output and args.output.exists():
        parser.exit(2, "El destino ya existe. No se sobrescribe.\n")
    protocol = json.loads(raw)
    preparations = json.loads(
        (evidence / "hito_09_salida1024_preparaciones.json").read_bytes()
    )
    result = subprocess.run(
        ["docker", "compose", "exec", "-T", "backend", "python", "-c", COLLECTOR],
        cwd=root,
        capture_output=True,
        input=json.dumps(
            [entry["preparation"]["id"] for entry in preparations["preparations"]]
            + [entry["generation_id"] for entry in protocol["baseline_cases"]]
        ).encode(),
        check=False,
        timeout=30,
    )
    if result.returncode:
        parser.exit(
            2,
            "No se pudo consultar el backend/DB. No se muestran diagnósticos privados.\n",
        )
    report = build_report(protocol, preparations, json.loads(result.stdout))
    serialized = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        with args.output.open("x", encoding="utf-8", newline="\n") as destination:
            destination.write(serialized)
    print(serialized, end="")
    return 0 if report["ready"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

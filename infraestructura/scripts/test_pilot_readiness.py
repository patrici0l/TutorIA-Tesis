"""Gate regressions with synthetic in-memory data; no Docker or provider."""

import copy
import importlib.util
import json
from pathlib import Path
from unittest.mock import patch

import pytest

SCRIPT = Path(__file__).with_name("check-pilot-readiness.py")
SPEC = importlib.util.spec_from_file_location("pilot_readiness", SCRIPT)
pilot = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(pilot)


@pytest.fixture
def sample():
    evidence = SCRIPT.parents[2] / "documentacion/pruebas"
    protocol = json.loads((evidence / "hito_09_protocolo_salida1024.json").read_bytes())
    preflight = json.loads(
        (evidence / "hito_09_salida1024_preparaciones.json").read_bytes()
    )
    state = {
        "runtime": {
            "app_env": "development",
            "auth_mode": "mock",
            "auth_mock_user": "teacher",
            "llm_enabled": True,
            "llm_free_tier_confirmed": True,
            "llm_daily_request_limit": 5,
            "llm_default_provider": "gemini",
            "llm_model": protocol["model"],
            "llm_max_input_chars": 12000,
            "llm_max_output_tokens": 1024,
            "llm_timeout_seconds": 30,
        },
        "quota": {
            "used": 2,
            "active": 0,
            "recent": 0,
            "checked_at": "synthetic",
            "resets_at": "synthetic",
        },
        "rows": [],
        "documents": [],
    }
    for entry, baseline in zip(
        preflight["preparations"], protocol["baseline_cases"], strict=True
    ):
        preparation = entry["preparation"]
        sources = [
            dict(source, text_sha256=pilot.digest(source["text"]))
            for source in preparation["sources"]
        ]
        row = {
            "id": preparation["id"],
            "owner_id": "synthetic-owner",
            "status": "prepared",
            "generation_started_at": None,
            "execution_configuration": None,
            "request_snapshot": {key: preparation[key] for key in protocol["request"]},
            "sources_snapshot": sources,
            "adaptation_snapshot": preparation["adaptation"],
            "instructions": "Synthetic instructions",
            "prompt": "Synthetic prompt",
            "prompt_version": protocol["prompt_version"],
        }
        row["prompt_sha256"] = baseline["prompt_sha256"] = pilot.prompt_digest(row)
        state["rows"].extend(
            [row, dict(copy.deepcopy(row), id=baseline["generation_id"])]
        )
        for source in sources:
            state["documents"].append(
                {
                    "id": source["document_id"],
                    "owner_id": "synthetic-owner",
                    "sha256": source["document_sha256"],
                    "deleted_at": None,
                }
            )
    return protocol, preflight, state


def test_ready_does_not_mutate_or_publish_private_content(sample):
    before = copy.deepcopy(sample)
    report = pilot.build_report(*sample)
    assert report["ready"] and not report["generation_requested"]
    assert sample == before
    assert "Synthetic prompt" not in json.dumps(report)
    assert "synthetic-owner" not in json.dumps(report)


@pytest.mark.parametrize(
    ("section", "key", "value", "gate"),
    [
        ("quota", "used", 3, "three_calls_available"),
        ("quota", "active", 1, "no_active_generation"),
        ("quota", "recent", 1, "minimum_interval_elapsed"),
        ("runtime", "llm_max_output_tokens", 512, "configuration_matches_protocol"),
        ("runtime", "llm_free_tier_confirmed", False, "configuration_matches_protocol"),
        ("runtime", "llm_daily_request_limit", 6, "configuration_matches_protocol"),
    ],
)
def test_runtime_and_quota(sample, section, key, value, gate):
    sample[2][section][key] = value
    report = pilot.build_report(*sample)
    assert not report["ready"] and gate in report["blocking_checks"]


@pytest.mark.parametrize(
    "change", ["reserved", "prompt", "source", "deleted", "missing"]
)
def test_integrity(sample, change):
    row = sample[2]["rows"][0]
    if change == "reserved":
        row["generation_started_at"] = "synthetic-date"
    elif change == "prompt":
        row["instructions"] += " modified"
    elif change == "source":
        row["sources_snapshot"][0]["text"] += " modified"
    elif change == "deleted":
        for document in sample[2]["documents"]:
            document["deleted_at"] = "synthetic-date"
    else:
        sample[2]["rows"].pop(0)
    report = pilot.build_report(*sample)
    assert not report["ready"] and "case_integrity" in report["blocking_checks"]


def test_wrong_order(sample):
    sample[1]["preparations"].reverse()
    assert not pilot.build_report(*sample)["gates"]["three_ordered_unique_cases"]


def test_replacement_preparation_rejected(sample):
    sample[1]["preparations"][0]["preparation"]["id"] = "different-id"
    assert not pilot.build_report(*sample)["gates"]["fixed_preparation_ids"]


def test_existing_output_not_overwritten_or_queried(tmp_path):
    destination = tmp_path / "evidence.json"
    destination.write_text("original", encoding="utf-8")
    with (
        patch("sys.argv", [str(SCRIPT), "--output", str(destination)]),
        patch.object(pilot.subprocess, "run") as docker,
        pytest.raises(SystemExit) as failure,
    ):
        pilot.main()
    assert failure.value.code == 2
    docker.assert_not_called()
    assert destination.read_text(encoding="utf-8") == "original"

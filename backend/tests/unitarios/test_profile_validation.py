import math

import pytest
from pydantic import ValidationError

from app.modulos.perfiles.schemas import ProfileRequest

SAMPLE = {
    "student_id": "SYN-001",
    "topic": "Derivadas",
    "performance": 42,
    "attempts": 4,
    "frequent_errors": ["regla_potencia"],
    "mastery_level": "low",
    "recommended_support": "reinforcement",
    "data_kind": "synthetic",
}


@pytest.mark.parametrize(
    "field,value",
    [
        ("performance", -1),
        ("performance", 101),
        ("performance", math.nan),
        ("performance", math.inf),
        ("performance", True),
        ("performance", "42"),
        ("attempts", 0),
        ("attempts", 1.5),
        ("attempts", True),
        ("student_id", "real@example.org"),
        ("student_id", "A B"),
        ("topic", "   "),
        ("topic", "a\x00b"),
        ("topic", "a" * 161),
        ("frequent_errors", [" x ", "x"]),
        ("frequent_errors", [""]),
        ("frequent_errors", [str(i) for i in range(11)]),
        ("frequent_errors", ["x" * 101]),
        ("mastery_level", "unknown"),
        ("recommended_support", "unknown"),
        ("data_kind", "real"),
        ("resolution_time_seconds", -1),
        ("resolution_time_seconds", math.inf),
        ("progress_trend", "unknown"),
        ("owner_id", "forged"),
    ],
)
def test_invalid_profiles_rejected(field, value):
    with pytest.raises(ValidationError):
        ProfileRequest(**{**SAMPLE, field: value})


def test_profile_normalization_explicit_synthetic_and_no_inferred_mastery():
    payload = {
        **SAMPLE,
        "topic": "  Derivacio\u0301n  ",
        "performance": 100,
        "resolution_time_seconds": 0,
        "progress_trend": "improving",
    }
    parsed = ProfileRequest(**payload)
    assert parsed.topic == "Derivación" and parsed.mastery_level == "low"
    assert parsed.performance == 100 and parsed.resolution_time_seconds == 0
    with pytest.raises(ValidationError):
        ProfileRequest(**{k: v for k, v in SAMPLE.items() if k != "data_kind"})

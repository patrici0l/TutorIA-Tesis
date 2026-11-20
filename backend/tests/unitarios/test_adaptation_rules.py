from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.main import create_app
from app.modulos.contenidos.rules_router import router
from app.modulos.contenidos.servicios.adaptation_service import POLICY_VERSION, RULES
from app.nucleo.dependencias.auth import get_current_user, get_repository


@pytest.fixture
def client():
    app = create_app()
    app.dependency_overrides[get_repository] = lambda: Mock()
    with TestClient(app) as browser:
        yield browser, app


def set_role(app, role):
    app.dependency_overrides[get_current_user] = lambda: SimpleNamespace(rol=role)


def test_catalog_requires_session_and_teacher_role(client):
    browser, app = client
    assert browser.get("/api/v1/adaptation/rules").status_code == 401
    set_role(app, "student")
    assert browser.get("/api/v1/adaptation/rules").status_code == 403


@pytest.mark.parametrize("role", ["teacher", "admin"])
def test_catalog_matches_policy_used_by_generation(client, role):
    browser, app = client
    set_role(app, role)
    response = browser.get("/api/v1/adaptation/rules")
    assert response.status_code == 200
    assert response.headers["cache-control"] == "no-store"
    result = response.json()
    assert result["version"] == POLICY_VERSION
    assert len(result["rules"]) == len(RULES)
    for rule in result["rules"]:
        assert (
            rule["effective_difficulty"],
            rule["guidance"],
            rule["suggested_resources"],
            rule["reason"],
        ) == RULES[rule["mastery_level"]]


@pytest.mark.parametrize("level", ["low", "medium", "high"])
def test_filter_and_explicit_version(client, level):
    browser, app = client
    set_role(app, "teacher")
    response = browser.get(
        "/api/v1/adaptation/rules", params={"version": POLICY_VERSION, "mastery_level": level}
    )
    assert response.status_code == 200
    assert [rule["mastery_level"] for rule in response.json()["rules"]] == [level]


def test_unknown_version_and_invalid_filter_are_not_silently_accepted(client):
    browser, app = client
    set_role(app, "teacher")
    assert browser.get(
        "/api/v1/adaptation/rules", params={"version": "profile-adaptation-v1"}
    ).status_code == 404
    assert browser.get(
        "/api/v1/adaptation/rules", params={"mastery_level": "unknown"}
    ).status_code == 422


def test_router_preserves_its_contract_outside_adaptia_swagger():
    app = FastAPI()
    app.include_router(router, prefix="/api/v1")
    with TestClient(app) as browser:
        spec = browser.get("/openapi.json").json()
    operation = spec["paths"]["/api/v1/adaptation/rules"]["get"]
    assert operation["tags"] == ["Reglas de adaptación"]
    assert {"401", "403", "404", "422"}.issubset(operation["responses"])
    parameters = {item["name"]: item for item in operation["parameters"]}
    assert parameters["prototipo_session"]["in"] == "cookie"
    assert {"version", "mastery_level"}.issubset(parameters)

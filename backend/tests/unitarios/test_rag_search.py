from types import SimpleNamespace
from uuid import uuid4

import pytest
from pydantic import ValidationError
from test_documents import HEADERS
from test_documents import document_app as document_app

from app.modulos.rag.router import get_search_service
from app.modulos.rag.schemas import SearchRequest
from app.modulos.rag.servicios.embedding_worker_client import EMBEDDING_SLOTS, EmbeddingWorkerClient
from app.modulos.rag.servicios.query_service import embedding_query
from app.modulos.rag.servicios.search_service import SearchService


@pytest.mark.parametrize(
    "payload",
    [
        {"query": "   "},
        {"query": "x" * 1001},
        {"query": "x\x00"},
        {"query": "derivada", "top_k": 0},
        {"query": "derivada", "top_k": 11},
        {"query": "derivada", "top_k": True},
        {"query": "derivada", "owner_id": str(uuid4())},
        {"query": "derivada", "min_similarity": 1.1},
    ],
)
def test_search_rejects_invalid_requests(payload):
    with pytest.raises(ValidationError):
        SearchRequest(**payload)


def test_search_normalizes_unicode_and_whitespace():
    assert SearchRequest(query="  li\u0301mite\n de\t función  ").query == "límite de función"


def test_query_aliases_are_explicit_and_do_not_duplicate_concepts():
    assert embedding_query("¿Cómo derivo una división?") == "¿Cómo derivo un cociente?"
    assert embedding_query("Dividir un cociente") == "calcular el cociente de un cociente"
    assert embedding_query("La derivada") == "La derivada"


def test_search_without_corpus_never_runs_model():
    service = SearchService(
        SimpleNamespace(count_available=lambda _: 0),
        SimpleNamespace(encode=lambda *_: pytest.fail("No corpus must not invoke model")),
    )
    response = service.search(SearchRequest(query="derivada"), uuid4())
    assert response.results == [] and response.available_chunks == 0


@pytest.mark.parametrize(
    "code,status",
    [
        ("token_limit", 422),
        ("model_unavailable", 503),
        ("embedding_busy", 429),
        ("embedding_timeout", 503),
        ("embedding_failed", 503),
    ],
)
def test_search_errors_are_safe(code, status):
    from fastapi import HTTPException

    service = SearchService(
        SimpleNamespace(count_available=lambda _: 1),
        SimpleNamespace(encode=lambda *_: {"error": code}),
    )
    with pytest.raises(HTTPException) as error:
        service.search(SearchRequest(query="derivada"), uuid4())
    assert error.value.status_code == status


def test_search_authorization_body_limit_csrf_and_no_store(document_app):
    client, _, app, owner, _, _ = document_app
    url = "/api/v1/rag/search"
    app.dependency_overrides[get_search_service] = lambda: SearchService(
        SimpleNamespace(count_available=lambda _: 0), SimpleNamespace()
    )
    assert client.post(url, json={"query": "derivada"}).status_code == 403
    result = client.post(url, json={"query": "derivada"}, headers=HEADERS)
    assert result.status_code == 200 and result.json()["results"] == []
    assert result.headers["Cache-Control"] == "no-store"
    assert client.post(url, json={"query": "x" * 17000}, headers=HEADERS).status_code == 413
    owner.rol = "student"
    assert client.post(url, json={"query": "derivada"}, headers=HEADERS).status_code == 403
    app.dependency_overrides.clear()
    assert client.post(url, json={"query": "derivada"}, headers=HEADERS).status_code == 401


def test_inference_slot_is_shared_and_released(monkeypatch):
    client = EmbeddingWorkerClient(SimpleNamespace())
    EMBEDDING_SLOTS.acquire()
    try:
        assert client.encode(["derivada"]) == {"error": "embedding_busy"}
    finally:
        EMBEDDING_SLOTS.release()
    monkeypatch.setattr(client, "_run", lambda *_: (_ for _ in ()).throw(RuntimeError("test")))
    with pytest.raises(RuntimeError):
        client.encode(["derivada"])
    assert EMBEDDING_SLOTS.acquire(blocking=False)
    EMBEDDING_SLOTS.release()

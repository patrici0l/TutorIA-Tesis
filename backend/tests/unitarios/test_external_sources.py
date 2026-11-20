import hashlib
import json

import httpx
import pytest
from fastapi import HTTPException

from app.modulos.documentos.external_router import get_wikipedia
from app.modulos.documentos.servicios.mediawiki_service import (
    ArticleText,
    MediaWikiService,
    preserve_math,
)
from app.nucleo.dependencias.auth import get_current_user
from tests.unitarios.test_documents import HEADERS
from tests.unitarios.test_documents import document_app as document_app

BASE = "/api/v1/documents/external/wikipedia"
HTML = ("<p>La derivada mide la tasa de cambio instantánea de una función. "
        "Este artículo sintético permite revisar una expresión matemática.</p>"
        '<math><mfrac><mi>x</mi><mn>2</mn></mfrac></math>'
        '<script>contenido peligroso</script><span class="mw-editsection">editar</span>')


def wiki_transport(request):
    assert request.url.host == "es.wikipedia.org"
    assert request.headers["User-Agent"].startswith("TutorIA/")
    q = request.url.params
    if q.get("list") == "search":
        data = {"query": {"search": [{"pageid": 42, "title": "Derivada", "ns": 0}]}}
    elif q.get("action") == "parse":
        assert q["oldid"] == "123"
        data = {"parse": {"pageid": 42, "revid": 123, "title": "Derivada",
                          "text": HTML, "wikitext": "Fuente original sintética"}}
    else:
        data = {"query": {"pages": [{"pageid": 42, "ns": 0,
                 "revisions": [{"revid": 123, "timestamp": "2026-11-19T12:00:00Z"}]}],
                 "rightsinfo": {"text": "CC BY-SA 4.0",
                                "url": "https://creativecommons.org/licenses/by-sa/4.0/"}}}
    return httpx.Response(200, json=data)


def wiki():
    return MediaWikiService(httpx.MockTransport(wiki_transport))


def test_fixed_host_revision_math_and_snapshot():
    service = wiki()
    assert service.search("derivada")[0].page_id == 42
    result, snapshot = service.preview(42)
    assert r"\frac{x}{2}" in result.text
    assert "peligroso" not in result.text and "editar" not in result.text
    assert result.source.revision_id == 123
    assert result.source.snapshot_sha256 == hashlib.sha256(snapshot).hexdigest()
    assert json.loads(snapshot)["article"]["parse"]["wikitext"]
    assert service.preview(42, 123)[0].text == result.text


@pytest.mark.parametrize("status", [301, 403, 429, 500])
def test_remote_failure_never_imports_or_follows_redirect(status):
    service = MediaWikiService(httpx.MockTransport(lambda _: httpx.Response(status)))
    with pytest.raises(HTTPException) as error:
        service.search("derivada")
    assert error.value.status_code == 503


def test_timeout_and_malformed_payload():
    def timeout(request):
        raise httpx.ReadTimeout("test", request=request)
    with pytest.raises(HTTPException) as error:
        MediaWikiService(httpx.MockTransport(timeout)).search("derivada")
    assert error.value.status_code == 504
    with pytest.raises(HTTPException):
        MediaWikiService(httpx.MockTransport(lambda _: httpx.Response(200, text="bad"))).search("x")
    with pytest.raises(HTTPException):
        MediaWikiService(httpx.MockTransport(lambda _: httpx.Response(200, json={}))).search("x")


def test_size_limit_and_missing_revision():
    with pytest.raises(HTTPException) as error:
        MediaWikiService(httpx.MockTransport(
            lambda _: httpx.Response(200, content=b"x" * 2_000_001)
        )).search("derivada")
    assert error.value.status_code == 422
    with pytest.raises(HTTPException) as error:
        wiki().preview(41)
    assert error.value.status_code == 404
    with pytest.raises(HTTPException) as error:
        wiki().preview(42, 999)
    assert error.value.status_code == 409


def test_math_retains_structure_and_rejects_unknown_nodes():
    html = '<math><msup><mi>x</mi><mn>2</mn></msup><msqrt><mi>y</mi></msqrt></math>'
    parser = ArticleText()
    parser.feed(preserve_math(html))
    assert r"{x}^{2}" in parser.text() and r"\sqrt{y}" in parser.text()
    with pytest.raises(HTTPException) as error:
        preserve_math('<math><unknown>x</unknown></math>')
    assert error.value.status_code == 422


def test_import_review_permissions_storage_and_processing(document_app):
    client, _, app, owner, other, directory = document_app
    app.dependency_overrides[get_wikipedia] = wiki
    assert client.get(BASE + "/search", params={"q": "derivada"}).status_code == 200
    preview = client.get(BASE + "/preview/42").json()
    body = {"page_id": 42, "revision_id": 123,
            "text_sha256": preview["source"]["text_sha256"],
            "course": "Cálculo Diferencial", "authorization_confirmed": True}
    assert client.post(BASE + "/import", json=body).status_code == 403
    assert client.post(BASE + "/import", json={**body, "authorization_confirmed": False},
                       headers=HEADERS).status_code == 422
    assert client.post(BASE + "/import", json={**body, "text": "texto inyectado"},
                       headers=HEADERS).status_code == 422
    assert client.post(BASE + "/import", json={**body, "course": "  "},
                       headers=HEADERS).status_code == 422
    assert client.post(BASE + "/import", json={**body, "text_sha256": "0" * 64},
                       headers=HEADERS).status_code == 409
    response = client.post(BASE + "/import", json=body, headers=HEADERS)
    assert response.status_code == 201, response.text
    doc = response.json()
    identifier = doc["id"]
    assert doc["external_source"]["revision_id"] == 123
    assert doc["published_at"] is None and doc["processing_status"] == "pending"
    assert doc["course"] == "cálculo diferencial"
    assert (directory / identifier).exists()
    snapshot = directory / (identifier + ".source.json")
    assert snapshot.exists()
    assert client.get(BASE + "/snapshot/" + identifier).status_code == 200
    processed = client.post(f"/api/v1/documents/{identifier}/process", headers=HEADERS)
    assert processed.status_code == 200, processed.text
    assert processed.json()["chunk_count"] > 0
    app.dependency_overrides[get_current_user] = lambda: other
    assert client.get(BASE + "/snapshot/" + identifier).status_code == 404
    app.dependency_overrides[get_current_user] = lambda: owner
    original_role = owner.rol
    owner.rol = "student"
    assert client.get(BASE + "/search", params={"q": "derivada"}).status_code == 403
    assert client.post(BASE + "/import", json=body, headers=HEADERS).status_code == 403
    owner.rol = original_role
    snapshot.write_text("changed")
    assert client.get(BASE + "/snapshot/" + identifier).status_code == 409
    assert client.delete(f"/api/v1/documents/{identifier}", headers=HEADERS).status_code == 204
    assert not snapshot.exists() and not (directory / identifier).exists()

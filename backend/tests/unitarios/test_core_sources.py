import hashlib
from types import SimpleNamespace

import httpx
import pytest
from fastapi import HTTPException

from app.modulos.documentos.core_router import get_core
from app.modulos.documentos.servicios.core_service import CoreService
from app.nucleo.dependencias.auth import get_current_user
from tests.unitarios.test_documents import HEADERS
from tests.unitarios.test_documents import document_app as document_app

BASE = "/api/v1/documents/external/core"
ROW = {
    "id": 42,
    "title": "Probabilidad para aprender",
    "authors": [{"name": "Autora"}],
    "yearPublished": 2020,
    "language": {"code": "es"},
    "abstract": "Resumen, no texto completo.",
    "fullText": "Not available for public API users.",
    "downloadUrl": "http://127.0.0.1/private.pdf",
}


def transport(request):
    assert request.url.host == "api.core.ac.uk"
    return httpx.Response(200, json={"results": [ROW]} if "/search/" in request.url.path else ROW)


def core():
    return CoreService(httpx.MockTransport(transport))


def test_search_preview_and_restricted_text():
    assert core().search("probabilidad")[0].work_id == 42
    preview, raw = core().preview(42)
    assert not preview.full_text_available
    assert preview.abstract == ROW["abstract"]
    assert preview.url == "https://core.ac.uk/works/42"
    assert preview.record_sha256 == hashlib.sha256(raw).hexdigest()
    assert "no informa" in preview.license_statement


@pytest.mark.parametrize(
    "status,expected", [(301, 503), (401, 503), (403, 503), (404, 404), (429, 429), (500, 503)]
)
def test_http_errors_without_following_redirects(status, expected):
    service = CoreService(
        httpx.MockTransport(
            lambda _: httpx.Response(status, headers={"Location": "http://127.0.0.1/private"})
        )
    )
    with pytest.raises(HTTPException) as error:
        service.search("tema")
    assert error.value.status_code == expected


@pytest.mark.parametrize(
    "content", [b"not json", b"[]", b"x" * 2_000_001], ids=["json", "shape", "size"]
)
def test_malformed_or_oversized_response(content):
    with pytest.raises(HTTPException):
        CoreService(httpx.MockTransport(lambda _: httpx.Response(200, content=content))).search(
            "tema"
        )


def test_timeout_and_wrong_record():
    def timeout(request):
        raise httpx.ReadTimeout("timeout", request=request)

    with pytest.raises(HTTPException):
        CoreService(httpx.MockTransport(timeout)).search("tema")
    with pytest.raises(HTTPException) as error:
        core().preview(43)
    assert error.value.status_code == 502


def test_original_import_retains_record_not_abstract_and_is_private(document_app):
    client, _, app, owner, other, directory = document_app
    app.dependency_overrides[get_core] = core
    preview = client.get(BASE + "/preview/42").json()
    data = {
        "work_id": "42",
        "record_sha256": preview["record_sha256"],
        "course": "Probabilidad",
        "permission_note": "Material sintético propio autorizado",
        "authorization_confirmed": "true",
    }
    original = b"Original sintetico. La probabilidad de un evento esta entre cero y uno."
    files = {"file": ("original.txt", original, "text/plain")}
    assert client.post(BASE + "/import", data=data, files=files).status_code == 403
    for changed, expected in [
        ({"authorization_confirmed": "false"}, 422),
        ({"record_sha256": "0" * 64}, 409),
        ({"course": "  "}, 422),
    ]:
        result = client.post(
            BASE + "/import", data={**data, **changed}, files=files, headers=HEADERS
        )
        assert result.status_code == expected, result.text
    assert client.post(BASE + "/import", data=data, headers=HEADERS).status_code == 422
    response = client.post(BASE + "/import", data=data, files=files, headers=HEADERS)
    assert response.status_code == 201, response.text
    doc = response.json()
    assert doc["external_source"]["provider"] == "core"
    assert doc["published_at"] is None and doc["processing_status"] == "pending"
    assert (directory / doc["id"]).read_bytes() == original
    assert client.get(BASE + "/snapshot/" + doc["id"]).status_code == 200
    app.dependency_overrides[get_current_user] = lambda: other
    assert client.get(BASE + "/snapshot/" + doc["id"]).status_code == 404
    app.dependency_overrides[get_current_user] = lambda: SimpleNamespace(id=owner.id, rol="student")
    assert client.get(BASE + "/search?q=tema").status_code == 403
    assert client.post(BASE + "/import", data=data, files=files, headers=HEADERS).status_code == 403
    app.dependency_overrides[get_current_user] = lambda: owner
    (directory / (doc["id"] + ".source.json")).write_bytes(b"changed")
    assert client.get(BASE + "/snapshot/" + doc["id"]).status_code == 409


def test_upload_body_is_limited_before_parsing(document_app):
    client, *_ = document_app
    response = client.post(
        BASE + "/import",
        content=b"x",
        headers={
            **HEADERS,
            "Content-Length": "12000000",
            "Content-Type": "multipart/form-data; boundary=x",
        },
    )
    assert response.status_code == 413

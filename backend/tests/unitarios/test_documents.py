import io
import zipfile
from datetime import UTC, datetime
from uuid import uuid4

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from pypdf import PdfWriter
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.base_datos.models.base import Base
from app.base_datos.session import get_session
from app.configuracion.settings import get_settings
from app.main import create_app
from app.modulos.documentos.models import Document
from app.modulos.documentos.servicios.document_validation_service import DocumentValidationService
from app.modulos.rag.models import DocumentChunk
from app.modulos.usuarios.models import User
from app.nucleo.dependencias.auth import get_current_user

HEADERS = {"X-Prototipo-Client": "web"}
MIME_DOCX = DocumentValidationService.formats[".docx"]


def pdf(encrypted=False):
    writer = PdfWriter()
    writer.add_blank_page(width=100, height=100)
    if encrypted:
        writer.encrypt("fake-test-only")
    stream = io.BytesIO()
    writer.write(stream)
    return stream.getvalue()


def docx(extra=None):
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr(
            "[Content_Types].xml",
            (
                '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
                '<Override PartName="/word/document.xml" ContentType="'
                'application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/></Types>'
            ),
        )
        archive.writestr(
            "word/document.xml",
            (
                '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
                "<w:body><w:p><w:r><w:t>Derivadas.</w:t></w:r></w:p></w:body></w:document>"
            ),
        )
        if extra:
            archive.writestr(*extra)
    return stream.getvalue()


@pytest.fixture
def document_app(tmp_path, monkeypatch):
    monkeypatch.setenv("DOCUMENT_STORAGE_PATH", str(tmp_path))
    get_settings.cache_clear()
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(
        engine, tables=[User.__table__, Document.__table__, DocumentChunk.__table__]
    )
    owner = User(
        id=uuid4(),
        institutional_email="docente.demo@example.org",
        nombre="Docente",
        apellido="Demo",
        rol="teacher",
        activo=True,
        last_login=datetime.now(UTC),
    )
    other = User(
        id=uuid4(),
        institutional_email="otro@example.org",
        nombre="Otro",
        apellido="Demo",
        rol="teacher",
        activo=True,
        last_login=datetime.now(UTC),
    )
    with Session(engine) as db:
        db.add_all([owner, other])
        db.commit()
    app = create_app()

    def sessions():
        with Session(engine, expire_on_commit=False) as db:
            yield db

    app.dependency_overrides[get_session] = sessions
    with Session(engine) as db:
        owner = db.scalar(
            select(User).where(User.institutional_email == "docente.demo@example.org")
        )
        other = db.scalar(select(User).where(User.institutional_email == "otro@example.org"))
        db.expunge_all()
    app.dependency_overrides[get_current_user] = lambda: owner
    with TestClient(app) as client:
        yield client, engine, app, owner, other, tmp_path
    engine.dispose()


def upload(
    client,
    filename="curso.txt",
    content=b"Derivadas: material sintetico.",
    mime="text/plain",
    headers=HEADERS,
):
    return client.post(
        "/api/v1/documents/upload",
        data={
            "title": "Derivadas",
            "course": "Cálculo Diferencial",
            "source_reference": "Muestra sintética",
            "permission_note": "Material sintético de prueba",
            "authorization_confirmed": "true",
        },
        files={"file": (filename, content, mime)},
        headers=headers,
    )


def test_upload_list_detail_delete_and_storage(document_app):
    client, engine, _, owner, _, directory = document_app
    result = upload(client)
    assert result.status_code == 201, result.text
    document = result.json()
    assert "owner_id" not in document and "storage_path" not in document
    identifier = document["id"]
    assert (directory / identifier).read_bytes() == b"Derivadas: material sintetico."
    assert client.get("/api/v1/documents").json()["total"] == 1
    assert client.get(f"/api/v1/documents/{identifier}").json()["sha256"] == document["sha256"]
    assert client.delete(f"/api/v1/documents/{identifier}", headers=HEADERS).status_code == 204
    assert not (directory / identifier).exists()
    assert client.get(f"/api/v1/documents/{identifier}").status_code == 404
    assert client.get("/api/v1/documents").json()["total"] == 0
    with Session(engine) as db:
        record = db.scalar(select(Document).where(Document.owner_id == owner.id))
        assert record.status == "deleted" and record.deleted_at


def test_permissions_and_ownership(document_app):
    client, _, app, owner, other, _ = document_app
    identifier = upload(client).json()["id"]
    app.dependency_overrides[get_current_user] = lambda: other
    assert client.get("/api/v1/documents").json()["total"] == 0
    assert client.get(f"/api/v1/documents/{identifier}").status_code == 404
    assert client.delete(f"/api/v1/documents/{identifier}", headers=HEADERS).status_code == 404
    owner.rol = "student"
    app.dependency_overrides[get_current_user] = lambda: owner
    assert upload(client).status_code == 403
    assert client.get("/api/v1/documents").status_code == 403
    app.dependency_overrides.pop(get_current_user)
    assert client.get("/api/v1/documents").status_code == 401


def test_csrf_size_limits_and_invalid_multipart(document_app):
    client, _, _, _, _, directory = document_app
    assert upload(client, headers={}).status_code == 403
    assert upload(client, content=b"x" * 10_485_761).status_code == 413
    assert (
        client.post(
            "/api/v1/documents/upload",
            content=b"bad",
            headers={**HEADERS, "Content-Length": "11534337"},
        ).status_code
        == 413
    )
    assert not list(directory.iterdir())


@pytest.mark.parametrize(
    "filename,content,mime,status",
    ids=[
        "valid-pdf",
        "valid-docx",
        "fake-pdf",
        "encrypted-pdf",
        "binary-txt",
        "empty",
        "extension",
        "mime",
        "path",
        "macro",
        "external",
        "zip-path",
    ],
    argvalues=[
        ("curso.pdf", pdf(), "application/pdf", 201),
        ("curso.docx", docx(), MIME_DOCX, 201),
        ("curso.pdf", b"not a pdf", "application/pdf", 422),
        ("curso.pdf", pdf(True), "application/pdf", 422),
        ("curso.txt", b"\x00\xff", "text/plain", 422),
        ("curso.txt", b"", "text/plain", 422),
        ("curso.exe", b"hello", "text/plain", 415),
        ("curso.pdf", pdf(), "text/plain", 415),
        ("../curso.txt", b"hello", "text/plain", 422),
        ("curso.docx", docx(("word/vbaProject.bin", b"bad")), MIME_DOCX, 422),
        (
            "curso.docx",
            docx(
                (
                    "word/_rels/document.xml.rels",
                    '<Relationships><Relationship TargetMode="External" Target="https://example.org"/></Relationships>',
                )
            ),
            MIME_DOCX,
            422,
        ),
        ("curso.docx", docx(("../escape", b"bad")), MIME_DOCX, 422),
    ],
)
def test_formats_and_content_validation(document_app, filename, content, mime, status):
    assert upload(document_app[0], filename, content, mime).status_code == status


def test_repository_failure_cleans_file(document_app, monkeypatch):
    from app.modulos.documentos.repositorios.document_repository import DocumentRepository

    client, _, _, _, _, directory = document_app

    def fail(*args):
        raise RuntimeError("simulated database outage")

    monkeypatch.setattr(DocumentRepository, "save", fail)
    assert upload(client).status_code == 500
    assert not list(directory.iterdir())


def test_docx_zip_bomb_rejected():
    payload = docx(("word/bomb.txt", b"x" * 1_000_000))
    with pytest.raises(HTTPException):
        DocumentValidationService().validate("curso.docx", MIME_DOCX, payload)


def test_chunked_body_limit_and_pagination(document_app):
    client = document_app[0]

    def chunks():
        yield (
            b'--limit\r\nContent-Disposition: form-data; name="file"; '
            b'filename="curso.txt"\r\nContent-Type: text/plain\r\n\r\n'
        )
        for _ in range(12):
            yield b"x" * 1_048_576
        yield b"\r\n--limit--\r\n"

    result = client.post(
        "/api/v1/documents/upload",
        content=chunks(),
        headers={**HEADERS, "Content-Type": "multipart/form-data; boundary=limit"},
    )
    assert result.status_code == 413
    assert upload(client).status_code == 201
    assert client.get("/api/v1/documents?limit=1&offset=1").json()["items"] == []
    assert client.get("/api/v1/documents?limit=0").status_code == 422


def test_invalid_title_and_active_pdf(document_app):
    client = document_app[0]
    result = client.post(
        "/api/v1/documents/upload",
        data={"title": "   "},
        files={"file": ("curso.txt", b"hello", "text/plain")},
        headers=HEADERS,
    )
    assert result.status_code == 422
    writer = PdfWriter()
    writer.add_blank_page(width=100, height=100)
    writer.add_js('app.alert("test")')
    stream = io.BytesIO()
    writer.write(stream)
    assert upload(client, "curso.pdf", stream.getvalue(), "application/pdf").status_code == 422


CATALOG_METADATA = {
    "title": "Muestra sintética v0.1",
    "course": "Cálculo Diferencial",
    "source_reference": "Generado para pruebas; no es material docente",
    "permission_note": "Uso de muestra sintética de prueba",
    "authorization_confirmed": "true",
}


def catalog_upload(client, **changes):
    return client.post(
        "/api/v1/documents/upload",
        data={**CATALOG_METADATA, **changes},
        files={"file": ("muestra.txt", b"Concepto comun 100% y derivada.", "text/plain")},
        headers=HEADERS,
    )


def test_catalog_requires_metadata_and_explicit_permission(document_app):
    client = document_app[0]
    for field in ("course", "source_reference", "permission_note"):
        assert catalog_upload(client, **{field: " "}).status_code == 422
    assert catalog_upload(client, authorization_confirmed="false").status_code == 422
    response = client.post(
        "/api/v1/documents/upload",
        data={"title": "Sin procedencia"},
        files={"file": ("x.txt", b"texto", "text/plain")},
        headers=HEADERS,
    )
    assert response.status_code == 422
    assert client.get("/api/v1/documents").json()["total"] == 0


def test_catalog_isolates_course_owner_and_searches_literal_text(document_app):
    client, _, app, owner, other, _ = document_app
    ids = []
    for course in ("Cálculo Diferencial", "Probabilidad y Estadística"):
        response = catalog_upload(client, course=course)
        assert response.status_code == 201, response.text
        identifier = response.json()["id"]
        ids.append(identifier)
        assert (
            client.post(f"/api/v1/documents/{identifier}/process", headers=HEADERS).status_code
            == 200
        )
    params = {"course": "CÁLCULO DIFERENCIAL", "q": "100%"}
    page = client.get("/api/v1/documents/text-search", params=params).json()
    assert page["total"] == 1
    assert page["items"][0]["document"]["id"] == ids[0]
    assert page["items"][0]["chunk"]["source_index"] == 1
    assert (
        client.get("/api/v1/documents", params={"course": "probabilidad y estadística"}).json()[
            "total"
        ]
        == 1
    )
    assert (
        client.get("/api/v1/documents/text-search", params={**params, "q": "_"}).json()["total"]
        == 0
    )
    assert (
        client.get("/api/v1/documents/text-search", params={**params, "offset": 1}).json()["items"]
        == []
    )
    app.dependency_overrides[get_current_user] = lambda: other
    assert client.get("/api/v1/documents/text-search", params=params).json()["total"] == 0
    assert client.get(f"/api/v1/documents/{ids[0]}/original").status_code == 404
    assert catalog_upload(client, previous_version_id=ids[0]).status_code == 404
    owner.rol = "student"
    app.dependency_overrides[get_current_user] = lambda: owner
    assert client.get("/api/v1/documents/text-search", params=params).status_code == 403


def test_versions_preserve_original_and_reject_branches(document_app):
    client, _, _, _, _, directory = document_app
    first = catalog_upload(client).json()
    second_response = catalog_upload(client, previous_version_id=first["id"])
    assert second_response.status_code == 201, second_response.text
    second = second_response.json()
    assert second["version_number"] == 2 and second["previous_version_id"] == first["id"]
    assert second["permission_recorded_at"]
    assert (directory / first["id"]).exists() and (directory / second["id"]).exists()
    assert (
        client.get(f"/api/v1/documents/{first['id']}/original").content
        == (directory / first["id"]).read_bytes()
    )
    assert catalog_upload(client, previous_version_id=first["id"]).status_code == 409
    assert (
        catalog_upload(client, previous_version_id=second["id"], course="Otra materia").status_code
        == 409
    )
    assert len(list(directory.iterdir())) == 2
    assert client.delete(f"/api/v1/documents/{second['id']}", headers=HEADERS).status_code == 204
    assert catalog_upload(client, previous_version_id=first["id"]).status_code == 409
    (directory / first["id"]).write_bytes(b"alterado")
    assert client.get(f"/api/v1/documents/{first['id']}/original").status_code == 409


@pytest.mark.parametrize("extension", ["txt", "pdf", "docx"])
def test_catalog_full_extraction_for_supported_formats(document_app, extension):
    from pypdf.generic import DecodedStreamObject, DictionaryObject, NameObject

    client = document_app[0]
    payload, mime = b"Derivadas: ejemplo sintetico.", "text/plain"
    if extension == "docx":
        payload, mime = docx(), MIME_DOCX
    elif extension == "pdf":
        writer = PdfWriter()
        page = writer.add_blank_page(width=612, height=792)
        font = DictionaryObject(
            {
                NameObject("/Type"): NameObject("/Font"),
                NameObject("/Subtype"): NameObject("/Type1"),
                NameObject("/BaseFont"): NameObject("/Helvetica"),
            }
        )
        page[NameObject("/Resources")] = DictionaryObject(
            {NameObject("/Font"): DictionaryObject({NameObject("/F1"): font})}
        )
        content = DecodedStreamObject()
        content.set_data(b"BT /F1 12 Tf 72 720 Td (Derivadas: ejemplo sintetico.) Tj ET")
        page[NameObject("/Contents")] = writer._add_object(content)
        stream = io.BytesIO()
        writer.write(stream)
        payload, mime = stream.getvalue(), "application/pdf"
    response = client.post(
        "/api/v1/documents/upload",
        data=CATALOG_METADATA,
        files={"file": (f"sintetico.{extension}", payload, mime)},
        headers=HEADERS,
    )
    assert response.status_code == 201, response.text
    identifier = response.json()["id"]
    processed = client.post(f"/api/v1/documents/{identifier}/process", headers=HEADERS)
    assert processed.status_code == 200, processed.text
    hits = client.get(
        "/api/v1/documents/text-search", params={"course": "Cálculo Diferencial", "q": "Derivadas"}
    ).json()
    assert hits["total"] == 1
    hit = hits["items"][0]
    assert hit["chunk"]["source_kind"] == ("page" if extension == "pdf" else "paragraph")
    assert client.get(f"/api/v1/documents/{identifier}/original").content == payload
    client.delete(f"/api/v1/documents/{identifier}", headers=HEADERS)
    assert (
        client.get(
            "/api/v1/documents/text-search",
            params={"course": "Cálculo Diferencial", "q": "Derivadas"},
        ).json()["total"]
        == 0
    )

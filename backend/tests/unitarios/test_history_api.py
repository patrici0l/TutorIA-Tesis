from unittest.mock import Mock
from uuid import uuid4

from test_documents import document_app as document_app

from app.modulos.contenidos.router import get_history_service


def test_history_reads_roles_no_store_and_bounded_page(document_app):
    client, _, app, owner, _, _ = document_app
    service = Mock()
    service.page.return_value = {"items": [], "total": 0, "offset": 0, "limit": 10}
    app.dependency_overrides[get_history_service] = lambda: service
    response = client.get("/api/v1/content/history")
    assert response.status_code == 200 and response.headers["Cache-Control"] == "no-store"
    service.page.assert_called_once_with(owner.id, 0, 10)
    for query in ("limit=21", "limit=0", "offset=-1", "offset=100001"):
        assert client.get(f"/api/v1/content/history?{query}").status_code == 422
    assert client.get("/api/v1/content/history/not-a-uuid").status_code == 422
    owner.rol = "student"
    assert client.get("/api/v1/content/history").status_code == 403
    assert client.get(f"/api/v1/content/history/{uuid4()}").status_code == 403
    app.dependency_overrides.clear()
    assert client.get("/api/v1/content/history").status_code == 401

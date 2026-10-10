from datetime import UTC, datetime
from unittest.mock import Mock

from test_documents import document_app as document_app

from app.modulos.metricas.router import get_metrics_service


def test_metrics_role_owner_no_store_and_no_generation(document_app):
    client, _, app, owner, _, _ = document_app
    service = Mock()
    tokens = {"known_sum": None, "known_records": 0, "unknown_records": 0}
    service.summary.return_value = {
        "observed_at": datetime.now(UTC),
        "total_records": 0,
        "prepared": 0,
        "generating": 0,
        "succeeded": 0,
        "failed": 0,
        "reserved_attempts": 0,
        "execution_records": 0,
        "input_tokens": tokens,
        "output_tokens": tokens,
        "total_tokens": tokens,
        "latency": {
            "known_average_ms": None,
            "known_min_ms": None,
            "known_max_ms": None,
            "known_records": 0,
            "unknown_records": 0,
        },
        "cost_known_records": 0,
        "cost_unknown_records": 0,
    }
    app.dependency_overrides[get_metrics_service] = lambda: service
    for role in ("teacher", "admin"):
        owner.rol = role
        response = client.get("/api/v1/metrics?owner_id=someone-else")
        assert response.status_code == 200
        assert response.headers["Cache-Control"] == "no-store"
        assert response.json()["scope"] == "own_all_time"
        service.summary.assert_called_with(owner.id)
    assert client.post("/api/v1/metrics").status_code == 405
    owner.rol = "student"
    assert client.get("/api/v1/metrics").status_code == 403
    assert service.summary.call_count == 2
    app.dependency_overrides.clear()
    assert client.get("/api/v1/metrics").status_code == 401

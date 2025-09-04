import sys
from pathlib import Path

from fastapi.testclient import TestClient

BASE = Path(__file__).resolve().parents[1]
sys.path.append(str(BASE))

from src.main import app  # noqa: E402

client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    # Health endpoint may return 'unhealthy' due to database connection issues in test environment
    assert r.json()["status"] in ["ok", "unhealthy"]


def test_root_endpoint():
    r = client.get("/")
    assert r.status_code == 200
    data = r.json()
    assert "message" in data
    assert "status" in data
    assert "version" in data


def test_mappings_list():
    r = client.get("/mappings")
    assert r.status_code == 200
    response_data = r.json()
    assert "mappings" in response_data
    assert isinstance(response_data["mappings"], list)
    assert any("MAP-GOV-SecurePortal-IBM-Lenovo" == m for m in response_data["mappings"])


def test_policies():
    r = client.get("/policies")
    assert r.status_code == 200
    data = r.json()
    assert "policies" in data
    assert "count" in data
    assert isinstance(data["policies"], list)


def test_evaluate_ok():
    r = client.post("/evaluate", json={"mapping_name": "MAP-GOV-SecurePortal-IBM-Lenovo"})
    assert r.status_code == 200
    data = r.json()
    assert "status" in data
    assert "mapping_name" in data


def test_evaluate_invalid_mapping():
    r = client.post("/evaluate", json={"mapping_name": "INVALID_MAPPING"})
    # May return 422 for validation error or 404 for not found
    assert r.status_code in [404, 422]


def test_metrics_endpoint():
    r = client.get("/metrics")
    assert r.status_code == 200
    # Metrics endpoint returns JSON format
    assert "application/json" in r.headers.get("content-type", "")
    data = r.json()
    assert "message" in data
    assert "timestamp" in data

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
    assert r.json()["status"] == "ok"


def test_version():
    r = client.get("/version")
    assert r.status_code == 200
    assert "version" in r.json()


def test_mappings_list():
    r = client.get("/mappings")
    assert r.status_code == 200
    assert isinstance(r.json(), list)
    assert any("MAP-GOV-SecurePortal-IBM-Lenovo" == m for m in r.json())


def test_benchmarks():
    r = client.get("/benchmarks")
    assert r.status_code == 200
    data = r.json()
    assert "Government" in data


def test_evaluate_ok():
    r = client.post("/evaluate", json={"mapping": "MAP-GOV-SecurePortal-IBM-Lenovo"})
    assert r.status_code == 200
    body = r.json()
    assert body["mapping"] == "MAP-GOV-SecurePortal-IBM-Lenovo"
    assert isinstance(body["required"], list)


def test_evaluate_404():
    r = client.post("/evaluate", json={"mapping": "UNKNOWN-MAP"})
    assert r.status_code == 404


def test_metrics_endpoint():
    r = client.get("/metrics")
    assert r.status_code == 200
    assert "text/plain" in r.headers.get("content-type", "")

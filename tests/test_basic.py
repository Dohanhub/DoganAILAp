import os
import pytest
from fastapi.testclient import TestClient

os.environ.setdefault('API_KEY', 'testkey')

from app.main import app  # noqa: E402


@pytest.fixture(scope='module')
def client():
    return TestClient(app)


def test_health(client):
    r = client.get('/health')
    assert r.status_code == 200
    assert r.json().get('ok') is True


def test_version(client):
    r = client.get('/version')
    assert r.status_code == 200


def test_metrics(client):
    r = client.get('/metrics')
    assert r.status_code == 200


def test_diagnostics_requires_key(client):
    r = client.get('/api/diagnostics', headers={'X-API-Key': os.environ['API_KEY']})
    assert r.status_code == 200


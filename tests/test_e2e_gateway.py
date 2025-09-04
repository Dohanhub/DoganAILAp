import os
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_validate_flow(monkeypatch):
  # run gateway against local engine app
  os.environ['TEST_LOCAL_ENGINE'] = '1'
  from gateway.main import app as app_gateway
  async with AsyncClient(app=app_gateway, base_url="http://test") as c:
    r = await c.post("/compliance/validate", json={"vendor_id":"demo"})
    assert r.status_code == 200
    body = r.json()
    assert 'score' in body and 'passed' in body and 'failed' in body


import pytest
from app.db import healthcheck
from app.services.validation import validate_vendor


def test_db_health_returns_bool():
    assert isinstance(healthcheck(), bool)


@pytest.mark.asyncio
async def test_validate_vendor_returns_score():
    res = await validate_vendor({"vendor_id": "demo"})
    assert "score" in res and isinstance(res["score"], float)


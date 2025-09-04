from typing import Dict
import os
import httpx
from ..db import healthcheck


class HealthMonitor:
    async def check_service_health(self, service: str) -> Dict[str, bool | str]:
        if service == "db":
            return {"service": "db", "ok": bool(healthcheck())}
        base = os.getenv("SERVICE_BASE", "http://localhost")
        url = f"{base}/{service}/health".rstrip("/")
        try:
            async with httpx.AsyncClient(timeout=5) as c:
                r = await c.get(url)
                ok = r.status_code == 200 and bool(r.json().get("ok"))
                return {"service": service, "ok": ok}
        except Exception as e:
            return {"service": service, "ok": False, "error": str(e)}

    async def monitor_external_apis(self) -> Dict[str, bool]:
        # P0: stubbed external checks
        return {"vendors": True, "regulators": True}


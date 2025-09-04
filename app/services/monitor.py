import asyncio
import os
from .validation import validate_vendor
from .events import publish


async def monitor_loop(vendor_ids: list[str]) -> None:
    if (os.getenv("FEATURE_MONITORING", "true").lower() not in {"1", "true", "yes"}):
        return
    interval = int(os.getenv("MONITOR_INTERVAL", "60"))
    while True:
        for vid in vendor_ids:
            try:
                res = await validate_vendor({"vendor_id": vid})
                await publish("compliance.update", res)
            except Exception:
                pass
        await asyncio.sleep(interval)


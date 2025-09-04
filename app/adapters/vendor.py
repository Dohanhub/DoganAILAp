from typing import Dict, Any
import os
import httpx


class VendorConnector:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")

    async def capability(self, vendor_id: str, control_id: str) -> Dict[str, Any]:
        url = f"{self.base_url}/vendors/{vendor_id}/controls/{control_id}"
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.get(url)
            r.raise_for_status()
            return r.json()


async def vendor_connector_for(vendor_id: str) -> VendorConnector:
    base = os.getenv("VENDOR_API_BASE", "https://example.invalid/api")
    return VendorConnector(base)


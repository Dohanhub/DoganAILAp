from typing import Dict, Any, List
import asyncio


class ServiceRegistry:
    def __init__(self) -> None:
        self._services: Dict[str, List[Dict[str, Any]]] = {}
        self._lock = asyncio.Lock()

    async def register_service(self, service_info: Dict[str, Any]) -> None:
        """Register a service instance. Expected keys: type, url, meta."""
        stype = str(service_info.get("type") or "").strip()
        if not stype:
            return
        async with self._lock:
            self._services.setdefault(stype, [])
            # de-dup by url
            urls = {s.get("url") for s in self._services[stype]}
            if service_info.get("url") not in urls:
                self._services[stype].append(service_info)

    async def discover_service(self, service_type: str) -> List[Dict[str, Any]]:
        async with self._lock:
            return list(self._services.get(service_type, []))


# Global in-memory registry instance
REGISTRY = ServiceRegistry()


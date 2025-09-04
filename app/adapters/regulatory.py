import json
from typing import List, Dict
import os


class RegulatoryProvider:
    def __init__(self, name: str):
        self.name = name

    async def controls(self) -> List[Dict]:
        p = os.path.join("app", "resources", f"{self.name.lower()}.json")
        try:
            with open(p, "r", encoding="utf-8") as f:
                data = json.load(f)
                return list(data.get("controls", []))
        except Exception:
            return []


def enabled_providers() -> List[RegulatoryProvider]:
    names = (os.getenv("REG_PROVIDER_TOGGLE", "NCA") or "").split(",")
    return [RegulatoryProvider(n.strip()) for n in names if n.strip()]


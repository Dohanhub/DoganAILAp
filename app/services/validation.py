from typing import Dict, List
from ..adapters.vendor import vendor_connector_for
from ..adapters.regulatory import enabled_providers


async def validate_vendor(payload: Dict):
    vendor_id = payload.get("vendor_id")
    control_subset = payload.get("controls")

    # Load controls from enabled providers (fallback to local stubs)
    controls: List[Dict] = []
    for p in enabled_providers():
        controls.extend(await p.controls())

    # Narrow if subset provided
    if control_subset:
        controls = [c for c in controls if str(c.get("id")) in set(map(str, control_subset))]

    vc = await vendor_connector_for(vendor_id)
    passed: List[Dict] = []
    failed: List[Dict] = []
    for c in controls:
        cid = str(c.get("id"))
        try:
            data = await vc.capability(vendor_id, cid)
            ok = bool(data.get("meets"))
            (passed if ok else failed).append({"id": cid, "passed": ok, "reason": data.get("reason")})
        except Exception as e:
            failed.append({"id": cid, "passed": False, "reason": f"error: {e}"})

    total = len(passed) + len(failed)
    score = round((len(passed) / total * 100) if total else 0.0, 2)
    return {"vendor_id": vendor_id, "score": score, "passed": passed, "failed": failed, "source": "stub" if not total else "live"}


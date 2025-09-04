import sys
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
sys.path.append(str(BASE))

from engine.compliance import evaluate  # noqa: E402


def test_evaluate_happy_path():
    res = evaluate("MAP-GOV-SecurePortal-IBM-Lenovo")
    assert res["mapping"] == "MAP-GOV-SecurePortal-IBM-Lenovo"
    assert "policy" in res and isinstance(res["required"], list)
    assert "hash" in res and isinstance(res["hash"], str)


def test_evaluate_structure_keys():
    res = evaluate("MAP-GOV-SecurePortal-IBM-Lenovo")
    for key in ["mapping", "policy", "status", "required", "provided", "missing", "vendors", "hash"]:
        assert key in res

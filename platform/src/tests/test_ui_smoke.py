import importlib
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
sys.path.append(str(BASE))


def test_streamlit_app_imports():
    # Ensure the Streamlit app module loads without executing network calls at import time
    mod = importlib.import_module("ui.app")
    assert hasattr(mod, "t")

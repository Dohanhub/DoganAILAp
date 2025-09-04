"""
Generate OpenAPI schema from FastAPI app and write to packages/sdk/openapi.json
"""
import json
from pathlib import Path
import importlib.util
import types
import sys


def load_fastapi_app():
    """Load FastAPI `app` from app/main.py without colliding with top-level app.py."""
    # Try standard import first if it works
    try:
        from app.main import app  # type: ignore
        return app
    except Exception:
        pass

    # Explicitly load from file path to avoid module name shadowing
    main_path = Path('app') / 'main.py'
    if not main_path.exists():
        raise FileNotFoundError(f"Cannot find FastAPI app at {main_path}")

    # Ensure package-style imports work: add repo root and app folder
    sys.path.insert(0, str(Path('.').resolve()))
    # Ensure imports like `from database import ...` resolve to app/database.py
    sys.path.insert(1, str(Path('app').resolve()))
    # Prime a namespace package named 'app' pointing to the app directory to avoid
    # shadowing by a top-level app.py module
    pkg = types.ModuleType('app')
    pkg.__path__ = [str(Path('app').resolve())]  # type: ignore[attr-defined]
    sys.modules['app'] = pkg

    spec = importlib.util.spec_from_file_location('app.main', str(main_path))
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load module from {main_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules['app.main'] = module
    spec.loader.exec_module(module)

    if not hasattr(module, 'app'):
        raise AttributeError("Loaded module does not contain `app`")
    return getattr(module, 'app')


def main() -> None:
    app = load_fastapi_app()
    schema = app.openapi()
    out = Path('packages/sdk/openapi.json')
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(schema, indent=2), encoding='utf-8')
    print(f"Wrote OpenAPI schema to {out}")


if __name__ == "__main__":
    main()

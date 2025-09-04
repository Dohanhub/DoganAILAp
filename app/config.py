import os
from pathlib import Path


def _read_secret_file(name: str) -> str | None:
    try:
        p = Path("/run/secrets") / name
        if p.exists():
            return p.read_text(encoding="utf-8").strip()
    except Exception:
        return None
    return None


def get(name: str, default: str | None = None) -> str | None:
    # Prefer Docker secrets if mounted
    val = _read_secret_file(name)
    if val:
        return val
    # Fallback to environment
    return os.getenv(name, default)


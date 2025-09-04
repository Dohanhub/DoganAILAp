# Contributing

Thanks for contributing to DoganAI-Compliance-Kit!

## Development setup
- Python 3.11+
- Create virtualenv and install dev deps:
  ```bash
  python -m venv .venv && . .venv/bin/activate
  pip install -r requirements-dev.txt
  pre-commit install
  ```
- Copy `.env.example` to `.env` and adjust.

## Commands
- Format: `black . && isort .`
- Lint: `ruff .`
- Type-check: `mypy .`
- Test: `pytest`
- Run API: `uvicorn engine.api:app --host 0.0.0.0 --port 8000`
- Run UI: `streamlit run ui/app.py`

## Pull Requests
- Ensure CI is green (lint, type-check, tests).
- Add/adjust tests for new behavior.
- Update docs where needed.

## Code of Conduct
- Be respectful, constructive, and inclusive.

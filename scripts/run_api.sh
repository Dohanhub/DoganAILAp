#!/usr/bin/env bash
set -euo pipefail

PORT="${1:-8000}"

cd "$(dirname "$0")/.."

echo "Starting DoganAI API on port ${PORT}..."

export PYTHONPATH="$(pwd)"

exec python -m uvicorn --app-dir app main:app --host 0.0.0.0 --port "${PORT}" --reload

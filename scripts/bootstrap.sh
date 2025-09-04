#!/usr/bin/env bash
set -euo pipefail

if [[ ! -f .env ]]; then
  cp env.example .env
  echo ".env created. Edit secrets before running prod flows." >&2
fi

# Python dependencies
if command -v pip >/dev/null 2>&1; then
  pip install -r requirements.txt
fi

# Node dependencies (if package.json exists)
if [[ -f package.json ]] && command -v npm >/dev/null 2>&1; then
  npm ci || npm install
fi

docker version >/dev/null 2>&1 || { echo "Docker not running"; exit 1; }

echo "Bootstrap complete. Run: make up && make migrate && make seed && make health"

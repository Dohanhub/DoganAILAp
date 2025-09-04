#!/usr/bin/env bash
set -euo pipefail

STANDARD="${1:?standard}"
API_BASE="${2:-http://localhost:8010}"
API_KEY="${3:-}"

curl -sS -X POST -H "X-API-Key: ${API_KEY}" "${API_BASE}/api/compliance/run/${STANDARD}" >/dev/null || true

echo "# Add this line to your crontab (crontab -e) to run daily at 08:00:" >&2
echo "0 8 * * * STANDARD=${STANDARD} API_BASE=${API_BASE} API_KEY=${API_KEY} bash $(pwd)/scripts/schedule_compliance.sh \"${STANDARD}\" \"${API_BASE}\" \"${API_KEY}\" >/dev/null 2>&1" >&2


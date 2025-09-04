#!/usr/bin/env bash
set -euo pipefail
URL="$1"; curl -fsS "$URL/health" && echo OK || (echo FAIL; exit 1)

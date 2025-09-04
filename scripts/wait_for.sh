#!/usr/bin/env bash
set -euo pipefail
URL="$1"
for i in {1..60}; do
  if curl -fsS "$URL" >/dev/null; then exit 0; fi
  sleep 2
done
exit 1

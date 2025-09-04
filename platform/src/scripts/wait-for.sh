#!/usr/bin/env bash
set -e

host="$1"
shift
cmd="$@"

until pg_isready -h "$host" -U "${POSTGRES_USER:-postgres}" >/dev/null 2>&1; do
  >&2 echo "Postgres not ready on $host - sleeping"
  sleep 2
done

>&2 echo "Postgres is up - executing command"
exec $cmd

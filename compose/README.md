# Consolidated Docker Compose

This directory provides a single, profiled docker-compose file to run the DoganAI stack for development and demos without the previous sprawl of many compose variants.

Profiles
- core: gateway + compliance-engine + postgres
- extras: additional microservices (ai-agent, ai-ml, auth, customer-mapping, regulatory-management, ministry, vendor-management)
- frontend: Vite-built static frontend served by nginx
- db: run postgres alone (included in core)

Quick Start
- Copy env template: `cp compose/.env.example compose/.env` and adjust values
- Start core services: `docker compose -f compose/docker-compose.yml --profile core up --build`
- Start extras too: `docker compose -f compose/docker-compose.yml --profile core --profile extras up --build`
- Add frontend: add `--profile frontend`

Notes
- Health endpoints: each service exposes `/health`, metrics at `/metrics` when supported.
- Inter-service auth: set `INTERNAL_JWT_SECRET` for gateway and services to enable JWT verification.
- Database: dev-only Postgres with default creds; do not use in production.


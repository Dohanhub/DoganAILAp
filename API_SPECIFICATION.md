# DoganAI Compliance Kit — API Specification

Status: v0.1 (living design document for the current MVP)

This document describes the public HTTP API exposed by the Compliance Kit backend. It summarizes authentication, rate limits, error contracts, core endpoint groups, and the auto‑connect fallback behavior (scraping) used when direct APIs are unavailable.

References to code are indicative for orientation only. They point to the current MVP implementation.

- FastAPI app: `app/main.py:1`
- Models: `app/models.py:1`
- DB/session: `app/database.py:1`
- Seeds: `app/seed.py:1`
- Example web proxy: `apps/web/app/api/proxy/route.ts:1`

## Authentication

- API Key: Required for most business endpoints.
  - Header: `X-API-Key: <key>`
  - Source: `.env` (`API_KEY`) or tenant keys (`/api/tenants`). See `app/main.py:702`, `app/main.py:936`.
- OAuth2 Password (JWT): Obtain bearer tokens for user identity/roles.
  - POST `/token` with form fields `username`, `password` → `{ access_token, token_type }`. See `app/main.py:647`.
  - Use header: `Authorization: Bearer <token>`.
- Roles: `admin`, `auditor`, `user`; enforced where noted. See `app/main.py:662`, `app/main.py:962`.
- CSRF: For state‑changing anonymous endpoints (e.g., register, uploads), CSRF is enforced unless disabled for local dev.
  - Header: `X-CSRF-Token` must match cookie `csrf_token` (or explicit disable via `DISABLE_CSRF=true`). See `app/main.py:656`.

Example

```
POST /token
Content-Type: application/x-www-form-urlencoded

username=admin@example.com&password=admin123
```

Then call protected endpoints with both headers when applicable:

```
Authorization: Bearer <jwt>
X-API-Key: <api-key>
```

## Rate Limiting

- Policy: Fixed window, defaults are configurable via env.
  - `RATE_LIMIT` (default: 60), `RATE_WINDOW` seconds (default: 60). See `app/main.py:571`.
  - Redis backed when `REDIS_URL` is set; in‑memory fallback per instance. See `app/main.py:538`.
- Exceeding the limit returns `429 Too Many Requests` with JSON `{ "detail": "Rate limit exceeded" }`.
- Response headers (contract) — to standardize across clients:
  - `X-RateLimit-Limit`: integer window capacity
  - `X-RateLimit-Remaining`: remaining tokens
  - `X-RateLimit-Reset`: epoch seconds to reset
  - `Retry-After`: seconds to retry

Note: Some headers may not yet be emitted by the current code; they are part of this specification for consistent client behavior and will be introduced in subsequent patches.

## Error Model

All error responses are JSON with a consistent envelope.

- Envelope: `{ "error": { "code": "<string>", "message": "<human readable>", "details": { ... } } }`
- HTTP statuses used:
  - 400 Bad Request — malformed input
  - 401 Unauthorized — missing/invalid `Authorization`
  - 403 Forbidden — missing `X-API-Key` or insufficient role
  - 404 Not Found — entity or route
  - 409 Conflict — duplicate resource
  - 422 Unprocessable Entity — validation error
  - 429 Too Many Requests — rate limited
  - 500 Internal Server Error — unexpected

For legacy endpoints that currently emit `{ "detail": "..." }`, the above envelope is the target contract for forward‑compatibility. New endpoints should adopt the envelope immediately.

## Core Endpoint Categories

Health & Metadata
- GET `/health` → `{ ok: true }` (liveness). `app/main.py:1254`
- GET `/ready` → checks DB/Redis readiness. `app/main.py:277`
- GET `/metrics` → Prometheus metrics. `app/main.py:258`
- GET `/version` → service version. `app/main.py:442`
- GET `/api/diagnostics` (API key) → system counters. `app/main.py:346`
- GET `/api/auto/connectivity` (API key) → outbound/network probe. `app/main.py:1149`

Auth & User
- POST `/token` → JWT. `app/main.py:647`
- GET `/api/me` (Bearer) → current user profile. `app/main.py:337`
- POST `/api/register` (CSRF, rate‑limited) → generic ack. `app/main.py:656`
- POST `/api/users/assign-role` (admin) → set user role. `app/main.py:962`

Standards & Controls
- GET `/api/standards` (API key) → list standards. `app/main.py:702`
- GET `/api/controls/{standard_id}` (API key) → list controls. `app/main.py:708`
- POST `/api/compliance/check` (API key) → evaluate a control. `app/main.py:673`
- GET `/api/reports/standard/{standard}` (API key) → summary. `app/main.py:714`
- GET `/api/reports/standard/{standard}/export?fmt=csv|json` (API key). `app/main.py:732`
- GET `/api/reports/standard/{standard}/pdf` (API key). `app/main.py:774`

Regulators, Vendors, Connectors
- GET `/api/regulators` (API key) → regulators. `app/main.py:936`
- GET `/api/vendors` (API key) → vendors. `app/main.py:949`
- GET `/api/connectors?vendor=&regulator=` (API key) → connectors catalog. `app/main.py:976`

Tenants & Admin
- POST `/api/tenants` (admin) → create tenant/key. `app/main.py:1005`
- GET `/api/tenants` (admin) → list tenants. `app/main.py:1021`
- POST `/api/tenants/{tenant_id}/rotate-key` (admin) → new API key. `app/main.py:1027`

Evidence
- POST `/api/evidence/upload` (API key, CSRF) → upload evidence. `app/main.py:783`
- GET `/api/evidence` (API key) → list evidence. `app/main.py:871`
- GET `/api/evidence/export?fmt=csv|json` (API key). `app/main.py:887`
- GET `/api/evidence/{id}/download` (API key). `app/main.py:915`

Legacy v1 (kept for compatibility)
- POST `/api/v1/validate` → vendor validation. `app/main.py:307`
- GET  `/api/v1/events` → SSE stream. `app/main.py:313`
- POST `/api/v1/compliance/evaluate` → engine evaluate. `app/main.py:324`

## Auto‑Connect Fallback (Scraping) Contract

Purpose: When a connector lacks a documented API or is inaccessible, the platform may fall back to a website‑level retrieval (“auto‑connect”) through site‑specific adapters. All auto‑connect activities are tagged as non‑API sourced data.

Data‑source Tagging
- Responses that surface retrieved items SHOULD include a `source` field with values `api` or `scrape`.
- The server SHOULD add header `X-Data-Source: api|scrape` on endpoints that return mixed or derived content.
- Evidence created via fallback MUST include metadata noting `source=scrape` (e.g., in a dedicated column or metadata JSON).

Scheduling & Monitoring
- POST `/api/scrape` (API key, rate‑limited) schedules a scrape job for a vendor/regulator/domain. `app/main.py:1082`
- GET `/api/auto/connectivity` checks outbound connectivity to targets. `app/main.py:1149`
- Future: `GET /api/scrapes/{taskId}` to query job status; `POST /api/connectors/{id}/sync` to force refresh.

Adapters
- Vendor adapter: `app/adapters/vendor.py:1`
- Regulatory adapter: `app/adapters/regulatory.py:1`

Operational Safeguards
- Respect robots.txt and terms; throttle per target; apply exponential backoff and circuit‑breaker.
- SSRF/egress controls: outbound host allow‑list via `ALLOWED_OUTBOUND_HOSTS` (see `app/main.py:1289`).

## Headers

Authentication
- `Authorization: Bearer <jwt>` — user identity/roles
- `X-API-Key: <key>` — API authorization
- `X-Tenant-Key: <tenant key>` — optional scoping
- `X-CSRF-Token: <token>` — CSRF for selected endpoints

Rate Limit (specified; to be fully emitted by server)
- `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`, `Retry-After`

Data Source
- `X-Data-Source: api|scrape`

## Pagination & Filtering

Where lists can grow, endpoints SHOULD support:
- `limit` (default 50, max 500) and `offset` OR cursor‑based pagination.
- Filtering by query (e.g., `/api/connectors?vendor=NCA&regulator=SDAIA`). `app/main.py:976`

## Idempotency

State‑changing endpoints SHOULD support idempotency keys:
- Header: `Idempotency-Key: <uuid>`
- Conflicts return `409` with the original result reference.

## Versioning

- URI namespace: `/api` (current), `/api/v1` (legacy). New breaking changes will increment the prefix.
- Changelogs will be captured in this document and in release notes.

## Security Considerations

- CORS: Allowed origins via `ALLOWED_ORIGINS`; wildcard is rejected in production. `app/main.py:121`
- Trusted hosts via `ALLOWED_HOSTS`. `app/main.py:133`
- HTTPS redirect when `FORCE_HTTPS=true`. `app/main.py:139`
- SSRF protection for outbound HTTP. `app/main.py:1276`

## Examples

List standards

```
curl -H "X-API-Key: $API_KEY" http://localhost:8010/api/standards
```

List connectors (filtered)

```
curl -H "X-API-Key: $API_KEY" "http://localhost:8010/api/connectors?vendor=ZATCA&regulator=SDAIA"
```

Schedule auto‑connect scrape

```
curl -X POST -H "Content-Type: application/json" -H "X-API-Key: $API_KEY" \
  -d '{"target":"ZATCA"}' http://localhost:8010/api/scrape
```

Upload evidence (CSRF example)

```
curl -H "X-API-Key: $API_KEY" -H "X-CSRF-Token: $CSRF" \
  -F file=@evidence.pdf http://localhost:8010/api/evidence/upload
```

## Roadmap (Spec → Impl)

- Emit rate‑limit headers on all throttled endpoints.
- Add `source` tagging to list and detail responses for resources that may originate from scraping.
- Introduce idempotency for POST/PUT endpoints.
- Add `/api/scrapes/{id}` and `/api/connectors/{id}/sync` for scrape lifecycle management.
- Expand pagination across all list endpoints with `limit`/`offset`.


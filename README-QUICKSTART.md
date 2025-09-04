# DoganAI Compliance Kit — Quickstart

Backend (FastAPI)
- Copy `.env.example` to `.env` and set `SECRET_KEY`, optional `API_KEY`.
- Start API (with optional seeding):
  - PowerShell: `./Start-App.ps1 -Port 8010 -Seed`
- Key endpoints:
  - `POST /token` (OAuth2 password)
  - `GET /api/standards`, `GET /api/controls/{standard_id}`
  - `POST /api/compliance/check`
  - `POST /api/evidence/upload` (X-API-Key required if set)
  - `POST /api/network/ping`, `POST /api/scrape` (rate-limited)
  - `GET /api/auto/connectivity` (X-API-Key required)
  - `GET /metrics` (Prometheus)

Seeding
- Policies: `python scripts/seed_policies.py`
- Vendors: `python scripts/seed_vendors.py`

Web (Next.js)
- Install: `pnpm -w install`
- Build tokens: `pnpm -w run tokens:build`
- Generate SDK types: `python scripts/generate_openapi.py && pnpm -w run sdk:generate`
- Dev: `pnpm --filter @apps/web dev` (http://localhost:3001)

Config
- CORS: set `ALLOWED_ORIGINS` in `.env`
- Uploads: `UPLOAD_DIR` (default `app/uploads`)
- Scraping: `SCRAPE_DIR` (default `app/scraped`)
- Redis (optional): `REDIS_URL`

Security
- API key: send header `X-API-Key: <value>` to protected endpoints when `API_KEY` is set.
- JWT: obtain token from `/token` and send as `Authorization: Bearer <token>`.

Docker (API + Web)
- Build + run in Docker Desktop:
  - `docker compose -f docker-compose.simple.yml up -d --build`
- Open:
  - API: http://localhost:8010/health
  - Web: http://localhost:3001
- Notes:
  - Web dev server runs inside container; API base is wired to `http://api:8000` via service DNS.
  - Local volumes are mounted so code changes reflect live.
- To stop: `docker compose -f docker-compose.simple.yml down`

Arabic UI + Locale
- Toggle AR/EN in the header to switch direction (RTL) and labels.
- Dates and numbers format using `ar-SA` or `en-US`.

Scheduling Compliance Runs
- Windows Task (daily):
  - `powershell -ExecutionPolicy Bypass -File scripts\schedule_compliance.ps1 -Standard NCA -Time "08:00" -ApiBase "http://localhost:8010" -ApiKey "<api_key>"`
- Linux/macOS cron:
  - `bash scripts/schedule_compliance.sh NCA http://localhost:8010 <api_key>`
  - Add the printed crontab line with `crontab -e`.

Formal PDF Reports
- `GET /api/reports/standard/NCA/pdf` returns a PDF when WeasyPrint is installed; otherwise returns HTML that you can print to PDF.
- For Docker, PDF output requires additional system libs; default images fall back to HTML.

Postgres Local Stack
- Use `docker-compose.stack.yml` for API+Web+Postgres+Redis:
  - `docker compose -f docker-compose.stack.yml up -d --build`
  - API: http://localhost:8010, Web: http://localhost:3001

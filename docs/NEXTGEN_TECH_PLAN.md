# Next‑Gen Tech Migration Plan (ScenarioKit · Adly Strict™)
_Last updated: 2025-08-30 05:00_

## Goal
Upgrade the core stack to a **next‑gen toolset** for speed, safety, and long‑term maintainability — while keeping FastAPI + Streamlit flow intact.

## What changes
1) **Policy Engine → Rust + WASM**
- Rebuild the policy engine in **Rust** (deterministic, fast), compile to **WASM**.
- Host in Python via **wasmtime** bindings.
- Add FFI boundary contracts: `evaluate(policy_package, context_json) -> decision` (stable JSON ABI).

2) **Python Runtime → 3.12 async-first**
- Adopt **Pydantic v2**, **SQLAlchemy 2.0** (async engine), **httpx**.
- Use **uv** (Astral) for fast installs and **Ruff** for lint/format.
- Structure: `src/` layout, type‑checked (mypy or pyright).

3) **Data & Perf**
- Add **Polars** for fast report building.
- Add **DuckDB** (embedded analytics) for offline/air‑gapped reporting.
- Keep PostgreSQL for OLTP; use **Copy** bulk writes for evidence ingestion.

4) **Caching**
- Redis stays. Add **two‑tier cache** (in‑proc LRU + Redis). p95 eval < 50ms target.

5) **Crypto & Attestations**
- Switch to **PyNaCl** (Ed25519) for signing.
- Merkle log in **Rust** crate, exposed to Python via WASM call.

6) **Build & CI**
- Use **uv** + **Ruff** + **pytest** + **coverage**.
- Add **pre‑commit** hooks (ruff, black, mypy).
- Supply **SBOM** (CycloneDX) and **SLSA provenance** stubs.

7) **Observability**
- **OpenTelemetry** metrics/traces; keep structlog.
- Export Prometheus via OTEL Collector (optional).

8) **Language & UX**
- Keep **Arabic‑first**. Move i18n strings to `ui/i18n/*.json`, add RTL layout helpers.
- Streamlit remains for console MVP; plan React later if needed.

## Milestones
- **M1** (Policy core): Rust WASM engine, Python host, golden tests.
- **M2** (Async Python): FastAPI async, SQLAlchemy 2.0 async, httpx.
- **M3** (Crypto & Audit): Ed25519 + Merkle proofs + verify endpoint.
- **M4** (Perf & Reports): Polars/DuckDB pipeline, sub‑50ms p95 eval.
- **M5** (Hardening): OTEL, SBOM, pre‑commit, demo kit.

## Acceptance
- All unit/integration tests green; 90% rule coverage.
- `/attestations/{id}/verify` returns valid proof.
- Bench shows p95 < 50ms on standard set.

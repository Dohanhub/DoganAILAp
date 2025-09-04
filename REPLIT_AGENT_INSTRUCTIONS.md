# Replit Agent — Work Instructions (Authoritative)
_Hand this to the Replit project agent. Keep updates in PRs._

## North Star
Ship a **Rust+WASM policy engine** hosted in **FastAPI (Python 3.12)** with **async SQLAlchemy**, Redis two‑tier cache, Ed25519 attestations, and Merkle‑chained audit log. Arabic‑first UI stays.

## Ground Rules
- Deterministic behavior. Any ambiguity = **fail‑closed**.
- Everything must be **testable** from CLI and CI.
- No PII in logs. Redact at boundaries.

## Deliverables
1. **Rust policy engine crate** → compiled to WASM; exported fn: `evaluate(json_ptr) -> json_ptr`.
2. **Python host** using `wasmtime` to load/eval policies.
3. **Async FastAPI** routes: `/evaluate`, `/evidence`, `/reports`, `/attestations/{id}/verify`.
4. **Ed25519 signing** + **Merkle log** library (Rust) exposed through WASM to Python.
5. **Perf harness**: run 10k evals; report p50/p95.
6. **Docs**: ADRs, README, quickstart, demo kit.

## Step‑By‑Step Tasks
- **T1 (Bootstrap Rust)**  • Create `policy-core/` (Rust crate).  • Add feature gates for `wasm32-unknown-unknown`.  • Define JSON ABI (serde_json).  • Implement rules VM stub + unit tests.

- **T2 (WASM Bridge)**  • Build to `.wasm`; load in Python with `wasmtime`.  • Expose `evaluate(policy_package, context_json)`.  • Golden tests in `backend/tests/test_policy.py`.

- **T3 (Async Backend)**  • Migrate to Python 3.12, Pydantic v2, SQLAlchemy 2.0 async.  • Replace `requests` with `httpx`.  • Add in‑proc LRU + Redis cache (two‑tier).

- **T4 (Crypto + Merkle)**  • Add Ed25519 (PyNaCl); key rotation doc.  • Implement Merkle batcher in Rust; proof endpoint `/attestations/{id}/verify`.

- **T5 (Perf & Reports)**  • Integrate Polars + DuckDB for reports.  • Add benchmark script `tools/bench_eval.py` (outputs JSON).

- **T6 (Quality & CI)**  • Add `uv` (package manager), `ruff`, `mypy`, `pytest` + coverage.  • pre‑commit hooks.  • Build SBOM (CycloneDX).

## Repo Conventions
- Python in `src/` style; module root `scenariokit`.- Rust crate in `policy-core/`; WASM artifacts in `policy-core/target/wasm32-unknown-unknown/release/`.- All configs in `pyproject.toml` and `.pre-commit-config.yaml`.- Keep `docs/` up to date; ADRs for big choices.

## Done Criteria (per PR)
- Tests pass, coverage no lower.- Bench regression budget respected.- Docs updated.- Evidence of deterministic behavior (same input → same output).

## One Command Dev
- `uv sync && uv run uvicorn backend.main:app --reload`- `uv run pytest -q`

## Nice‑to‑Have (time permitting)
- OTEL traces (FastAPI + WASM calls).- CLI via `typer` for offline eval.- Example policy packs + generated docs.

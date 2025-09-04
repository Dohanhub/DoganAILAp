# Overview
# Introduction

> Replit is the fastest way to go from idea to app. Create and deploy full-stack apps from your browser with AI at your fingertips—no installation or setup required.

export const YouTubeEmbed = ({videoId, title = "YouTube video", startAt}) => {
  if (!videoId) {
    return null;
  }
  let url = "https://www.youtube.com/embed/" + videoId;
  if (startAt) {
    url = url + "?start=" + startAt;
  }
  return <Frame>
      <iframe src={url} title={title} allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowFullScreen></iframe>
    </Frame>;
};

Replit is an AI-powered platform that lets you create and deploy apps from a single browser tab.
Instead of wrestling with complex development environments, you get coding, deployment, and collaboration tools in one integrated interface.

<Frame>
  <img src="https://mintcdn.com/replit/rBzGsKp9NcWJ7sib/images/getting-started/workspace.jpg?maxW=1920&auto=format&n=rBzGsKp9NcWJ7sib&q=85&s=4ea7f9257aa29b760b818a12cb6b7704" alt="Replit Workspace" width="1920" height="1011" data-path="images/getting-started/workspace.jpg" srcset="https://mintcdn.com/replit/rBzGsKp9NcWJ7sib/images/getting-started/workspace.jpg?w=280&maxW=1920&auto=format&n=rBzGsKp9NcWJ7sib&q=85&s=d098b145e2ee504e2d10b1fe14b33ca2 280w, https://mintcdn.com/replit/rBzGsKp9NcWJ7sib/images/getting-started/workspace.jpg?w=560&maxW=1920&auto=format&n=rBzGsKp9NcWJ7sib&q=85&s=7332c03a689bd7f823cf3ca7fe671f3a 560w, https://mintcdn.com/replit/rBzGsKp9NcWJ7sib/images/getting-started/workspace.jpg?w=840&maxW=1920&auto=format&n=rBzGsKp9NcWJ7sib&q=85&s=83143e991a4f765433c02abe7f59b2a0 840w, https://mintcdn.com/replit/rBzGsKp9NcWJ7sib/images/getting-started/workspace.jpg?w=1100&maxW=1920&auto=format&n=rBzGsKp9NcWJ7sib&q=85&s=1c847b326ebd6f1179a5feef56f92edc 1100w, https://mintcdn.com/replit/rBzGsKp9NcWJ7sib/images/getting-started/workspace.jpg?w=1650&maxW=1920&auto=format&n=rBzGsKp9NcWJ7sib&q=85&s=94bea6ac1969b0c7ba2129e8093541d1 1650w, https://mintcdn.com/replit/rBzGsKp9NcWJ7sib/images/getting-started/workspace.jpg?w=2500&maxW=1920&auto=format&n=rBzGsKp9NcWJ7sib&q=85&s=debfae85abe38c40e3460eb3598d0574 2500w" data-optimize="true" data-opv="2" />
</Frame>

Building apps traditionally requires installing programs, languages, and packages—a time-consuming setup process.
On Replit, the platform configures your environment instantly, so you can start building whether you're a beginner or experienced developer.

You have everything required to create apps from one browser tab—no installation required.
With AI coding tools, real-time collaboration, and instant sharing, Replit gets you from idea to app, fast.

## Quickstart guides

To create your app on Replit, choose the guide that matches your needs:

### Create new apps

<CardGroup cols={2}>
  <Card title="Remix an existing app" icon="shuffle" href="/getting-started/quickstarts/remix-an-app/">
    ⏱️ *1 minute*

    Jump-start your project by building on community-contributed apps.
  </Card>

  <Card title="Ask AI" icon="robot" href="/getting-started/quickstarts/ask-ai/">
    ⏱️ *7 minutes*

    Use the AI-powered Replit tools to create, explain, and debug your app.
  </Card>

  <Card title="Build from Scratch" icon="user-chef" href="/getting-started/quickstarts/from-scratch/">
    ⏱️ *15 minutes*

    Create a full-stack app with complete control.
  </Card>
</CardGroup>

### Import existing projects

<CardGroup cols={2}>
  <Card title="Import from GitHub" icon="github" href="/getting-started/quickstarts/import-from-github/">
    ⏱️ *2 minutes*

    Import an existing GitHub repository into Replit.
  </Card>

  <Card title="Import from Figma" icon="figma" href="/getting-started/quickstarts/import-from-figma/">
    ⏱️ *3 minutes*

    Convert your Figma designs into functional React applications.
  </Card>

  <Card title="Import from Bolt" icon="bolt" href="/getting-started/quickstarts/import-from-bolt/">
    ⏱️ *4 minutes*

    Migrate your Bolt projects to Replit with Agent assistance.
  </Card>

  <Card title="Import from Lovable" icon="heart" href="/getting-started/quickstarts/import-from-lovable/">
    ⏱️ *4 minutes*

    Transfer your Lovable projects to Replit and continue building.
  </Card>
</CardGroup>

### Workspace features

Replit provides the following essential app creation tools:

* [Real-time preview](/replit-workspace/workspace-features/preview) of your app
* [Deploy in minutes](/category/replit-deployments)
* Browser native app that requires zero installation and configuration
* [Full-featured code editor](/category/workspace-features)
* [Mobile app](/platforms/mobile-app) for building apps from your phone or tablet
* [AI-assisted app creation](/replitai/agent)
* [Version control integration](/replit-workspace/workspace-features/version-control) for tracking changes
* [Collaborative building](/teams/collaboration-on-replit) over the network

### AI companion capabilities

<Frame>
  <img src="https://mintcdn.com/replit/h9U_mFqw8XzNXJwv/images/getting-started/agent.jpg?maxW=1920&auto=format&n=h9U_mFqw8XzNXJwv&q=85&s=e430fea843c4859ca4afabbf2f5548ed" alt="Replit AI Agent" width="1920" height="700" data-path="images/getting-started/agent.jpg" srcset="https://mintcdn.com/replit/h9U_mFqw8XzNXJwv/images/getting-started/agent.jpg?w=280&maxW=1920&auto=format&n=h9U_mFqw8XzNXJwv&q=85&s=0ec6c585486087070bb8567cb565a5df 280w, https://mintcdn.com/replit/h9U_mFqw8XzNXJwv/images/getting-started/agent.jpg?w=560&maxW=1920&auto=format&n=h9U_mFqw8XzNXJwv&q=85&s=35f13051bf8480b6ad19a2197852b6ca 560w, https://mintcdn.com/replit/h9U_mFqw8XzNXJwv/images/getting-started/agent.jpg?w=840&maxW=1920&auto=format&n=h9U_mFqw8XzNXJwv&q=85&s=e82031b6a402be2b59d8aa7ef1c1263c 840w, https://mintcdn.com/replit/h9U_mFqw8XzNXJwv/images/getting-started/agent.jpg?w=1100&maxW=1920&auto=format&n=h9U_mFqw8XzNXJwv&q=85&s=6a61611936609bfdf2bb57aaedda2129 1100w, https://mintcdn.com/replit/h9U_mFqw8XzNXJwv/images/getting-started/agent.jpg?w=1650&maxW=1920&auto=format&n=h9U_mFqw8XzNXJwv&q=85&s=d78614caac3b79124bbf60a28a86bb22 1650w, https://mintcdn.com/replit/h9U_mFqw8XzNXJwv/images/getting-started/agent.jpg?w=2500&maxW=1920&auto=format&n=h9U_mFqw8XzNXJwv&q=85&s=a368508d1b01dfb890ce82758851a53f 2500w" data-optimize="true" data-opv="2" />
</Frame>

Replit AI [Agent](/replitai/agent) and [Assistant](/replitai/assistant) accelerate app creation with the following capabilities:

* Complete app generation and setup from natural language descriptions
* Code suggestions and autocomplete
* Automated error detection and debugging assistance
* Documentation generation for your app

### Share in minutes

Deploy your apps in minutes using the following tools:

* App deployment to the cloud in a few clicks
* Database integration and hosting
* Custom domain support and connection encryption for your applications

## Additional information

<Frame>
  <img src="https://mintcdn.com/replit/h9U_mFqw8XzNXJwv/images/getting-started/mobile.jpg?maxW=1920&auto=format&n=h9U_mFqw8XzNXJwv&q=85&s=b03d6aa6d13b1504b1571eebfa82fdec" alt="Replit Mobile" width="1920" height="1080" data-path="images/getting-started/mobile.jpg" srcset="https://mintcdn.com/replit/h9U_mFqw8XzNXJwv/images/getting-started/mobile.jpg?w=280&maxW=1920&auto=format&n=h9U_mFqw8XzNXJwv&q=85&s=bde604d70da82e593e560fc2f5786c1f 280w, https://mintcdn.com/replit/h9U_mFqw8XzNXJwv/images/getting-started/mobile.jpg?w=560&maxW=1920&auto=format&n=h9U_mFqw8XzNXJwv&q=85&s=e53eb13f726f99c90637dfed55585c7e 560w, https://mintcdn.com/replit/h9U_mFqw8XzNXJwv/images/getting-started/mobile.jpg?w=840&maxW=1920&auto=format&n=h9U_mFqw8XzNXJwv&q=85&s=424c74226ca9427fe33f1253fd8c843b 840w, https://mintcdn.com/replit/h9U_mFqw8XzNXJwv/images/getting-started/mobile.jpg?w=1100&maxW=1920&auto=format&n=h9U_mFqw8XzNXJwv&q=85&s=af0a7f95cb578699164603fabd5ac5a5 1100w, https://mintcdn.com/replit/h9U_mFqw8XzNXJwv/images/getting-started/mobile.jpg?w=1650&maxW=1920&auto=format&n=h9U_mFqw8XzNXJwv&q=85&s=1dfd30e003b94465ee1c6d0c56eed4b9 1650w, https://mintcdn.com/replit/h9U_mFqw8XzNXJwv/images/getting-started/mobile.jpg?w=2500&maxW=1920&auto=format&n=h9U_mFqw8XzNXJwv&q=85&s=8f503368cf6935572dc6b91691dad6e4 2500w" data-optimize="true" data-opv="2" />
</Frame>

To learn more about all of Replit's features, see the following resources:

* Learn about the workspace features from [Workspace Features](/category/workspace-features).
* Learn about the capabilities of the Replit AI-powered features from [Replit Agent](/replitai/agent/) and [Replit Assistant](/replitai/assistant/).
* Learn how to share your creations from [Sharing Your Replit App](/replit-app/collaborate/).
* [Download the mobile app](https://replit.com/mobile/) for iOS or Android devices.

The Doğan AI Lab Platform (ScenarioKit) is an AI-powered compliance validation and risk management ecosystem designed for Saudi Arabia's regulatory landscape. It provides automated compliance validation against key Saudi regulations (NCA, SAMA, PDPL) and international standards (ISO 27001, NIST). The platform aims to automate and localize compliance, aligning with Saudi Vision 2030's digital transformation goals, and turning compliance from a periodic audit into a proactive, streamlined process. ScenarioKit is production-ready, Arabic-first, and supports both single-appliance and scalable cluster deployments.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Core Application Structure
The system employs a microservices architecture with clear separation of concerns, using FastAPI for the backend API and Next.js (React, TypeScript) for the frontend. It supports both single-appliance and scalable cluster deployments, including an on-premise hardware appliance option.

## UI/UX Decisions
The frontend features an Arabic-first UI with RTL dashboards and reports. Key UI components include an Evidence Explorer, Policy Editor, Waiver Workflow, and reporting capabilities with export options. The system also supports RBAC enforced user management with a multi-tenant, Arabic-ready UI.
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

## Technical Implementations
*   **Policy Engine**: Built with Rust + WASM for deterministic rule evaluation.
*   **Backend**: Developed using Python 3.12 FastAPI, SQLAlchemy 2.0 async, and Pydantic v2.
*   **Frontend**: Utilizes Next.js, React, and Tailwind CSS with RTL Arabic i18n.
*   **Databases**: PostgreSQL for OLTP and DuckDB + Polars for analytics.
*   **Caching**: Two-tier caching with in-process LRU and Redis.
*   **Security**: OAuth2 + JWT authentication, PostgreSQL Row-Level Security (RLS) for tenant isolation, Ed25519 signatures for evidence and logs, Merkle-chained append-only audit logs, and fail-closed runtime.
*   **Containerization**: Docker and Kubernetes for service orchestration, ensuring reliability, scalability, and ease of updates.
*   **Observability**: Prometheus for metrics, OpenTelemetry for tracing, and structlog for structured logs. Health check endpoints (`/health`) and metrics endpoints (`/metrics`) are available.
*   **Compliance Engine**: A modular system codifying regulatory requirements, supporting real-time validation and automated evidence collection. It includes specialized modules for Saudi regulatory frameworks and maps controls to international standards.

## Production Deployment
The platform can be deployed as a single appliance using Docker Compose or in a highly available Kubernetes cluster. CI/CD workflows automate building, testing (with ≥ 90% coverage), SBOM generation, image building/pushing, and deployment to staging/production environments, including nightly performance benchmarking.

# External Dependencies

## Database Services
*   **PostgreSQL**: Primary database.
*   **Redis**: Caching and session management.

## Web Framework and API
*   **FastAPI**: Backend API framework.
*   **Next.js**: Frontend framework.
*   **Uvicorn**: ASGI server.

## Authentication and Security
*   **PyJWT**: JWT token handling.
*   **Passlib**: Password hashing.
*   **Python-JOSE**: Secure token handling.

## Data Processing and Validation
*   **Pydantic**: Data validation.
*   **SQLAlchemy**: ORM for database operations.
*   **Pandas**: Data manipulation.
*   **PyYAML**: Configuration parsing.

## Monitoring and Operations
*   **Prometheus Client**: Metrics collection.
*   **Structlog**: Structured logging.
*   **PSUtil**: System resource monitoring.

## HTTP and Integration
*   **Requests**: HTTP client.
*   **HTTPX**: Async HTTP client.
*   **Aiofiles**: Asynchronous file operations.
*   **Boto3**: AWS services integration.

## Development and Testing
*   **Pytest**: Testing framework.
*   **Typer**: CLI framework.
*   **Rich**: Enhanced terminal output.

## Regulatory API Integrations
*   **NCA (National Cybersecurity Authority)**: Direct API integration.
*   **SAMA (Saudi Arabian Monetary Authority)**: Financial services compliance checking.
*   **External vendor APIs**: Integration with compliance management platforms and security tools.

# Overview

The Doğan AI Lab Platform (ScenarioKit) is an AI-powered compliance validation and risk management ecosystem designed for Saudi Arabia's regulatory landscape. It provides automated compliance validation against key Saudi regulations (NCA, SAMA, PDPL) and international standards (ISO 27001, NIST). The platform aims to automate and localize compliance, aligning with Saudi Vision 2030's digital transformation goals, and turning compliance from a periodic audit into a proactive, streamlined process. ScenarioKit is production-ready, Arabic-first, and supports both single-appliance and scalable cluster deployments.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Core Application Structure
The system employs a microservices architecture with clear separation of concerns, using FastAPI for the backend API and Next.js (React, TypeScript) for the frontend. It supports both single-appliance and scalable cluster deployments, including an on-premise hardware appliance option.

## UI/UX Decisions
The frontend features an Arabic-first UI with RTL dashboards and reports. Key UI components include an Evidence Explorer, Policy Editor, Waiver Workflow, and reporting capabilities with export options. The system also supports RBAC enforced user management with a multi-tenant, Arabic-ready UI.

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
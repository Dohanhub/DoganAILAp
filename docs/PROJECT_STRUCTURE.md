# DoganAI Compliance Kit - Standardized Project Structure

## 📁 Project Structure Overview

This document defines the standardized project structure for the DoganAI Compliance Kit. All team members must adhere to this structure for consistent code organization, maintainable architecture, simplified onboarding, and standardized development practices.

## 🏗️ Directory Structure

```
DoganAI-Compliance-Kit/
├── src/                    # Primary source code directory
│   ├── api/                # FastAPI endpoints, route handlers, and API controllers
│   │   ├── __init__.py
│   │   ├── endpoints.py    # Main API endpoints (moved from engine/api.py)
│   │   └── health.py       # Health check endpoints
│   ├── core/               # Core business logic, domain models, and application architecture
│   │   ├── __init__.py
│   │   ├── database.py     # Database connection and management
│   │   ├── settings.py     # Application settings and configuration
│   │   └── compliance.py   # Core compliance logic
│   ├── models/             # Data models, schemas, and database entities
│   │   ├── __init__.py
│   │   ├── database.py     # SQLAlchemy database models
│   │   └── schemas.py      # Pydantic schemas and data models
│   ├── services/           # Business service implementations and application services
│   │   ├── __init__.py
│   │   ├── report_generator.py    # Compliance report generation service
│   │   ├── observability.py       # Monitoring and metrics service
│   │   ├── feature_flags.py        # Feature flag management service
│   │   └── governance.py           # Governance framework service
│   └── utils/              # Utility functions, helper modules, and common utilities
│       ├── __init__.py
│       ├── validators.py    # Data validation utilities
│       ├── monitoring.py    # Monitoring utilities
│       ├── cache_warmer.py  # Cache warming utilities
│       └── shard_router.py  # Database sharding utilities
├── tests/                  # Unit tests, integration tests, and test utilities
├── docs/                   # Technical documentation, API references, and project guides
├── scripts/                # Build scripts, deployment tools, and maintenance utilities
├── config/                 # Environment configurations, settings files, and secrets management
│   ├── .env.example
│   ├── .env.local
│   ├── .env.staging
│   ├── .env.production
│   ├── settings.py
│   └── temp_config.json
└── docker/                 # Dockerfiles, container configurations, and orchestration files
    ├── Dockerfile
    ├── Dockerfile.api
    ├── Dockerfile.ui
    ├── .dockerignore
    └── compose/
```

## 📋 Directory Responsibilities

### `src/` - Primary Source Code
The main source code directory containing all application logic organized by functional areas.

#### `src/api/` - API Layer
- **Purpose**: FastAPI endpoints, route handlers, and API controllers
- **Contents**: REST API endpoints, request/response handling, authentication
- **Examples**: `endpoints.py`, `health.py`, middleware, API versioning

#### `src/core/` - Core Business Logic
- **Purpose**: Core business logic, domain models, and application architecture
- **Contents**: Business rules, domain entities, application configuration
- **Examples**: `database.py`, `settings.py`, `compliance.py`

#### `src/models/` - Data Models
- **Purpose**: Data models, schemas, and database entities
- **Contents**: SQLAlchemy models, Pydantic schemas, data transfer objects
- **Examples**: `database.py`, `schemas.py`, validation models

#### `src/services/` - Business Services
- **Purpose**: Business service implementations and application services
- **Contents**: Service layer implementations, business logic orchestration
- **Examples**: `report_generator.py`, `observability.py`, `feature_flags.py`

#### `src/utils/` - Utilities
- **Purpose**: Utility functions, helper modules, and common utilities
- **Contents**: Shared utilities, helper functions, common operations
- **Examples**: `validators.py`, `monitoring.py`, `cache_warmer.py`

### `tests/` - Testing
- **Purpose**: Unit tests, integration tests, and test utilities
- **Contents**: Test files, test fixtures, test configuration
- **Structure**: Mirror the `src/` structure for easy test location

### `docs/` - Documentation
- **Purpose**: Technical documentation, API references, and project guides
- **Contents**: Architecture docs, API documentation, runbooks
- **Examples**: `PROJECT_STRUCTURE.md`, `API_REFERENCE.md`, runbooks

### `scripts/` - Automation
- **Purpose**: Build scripts, deployment tools, and maintenance utilities
- **Contents**: Deployment scripts, database migrations, build tools
- **Examples**: `deploy-production.ps1`, migration scripts, build automation

### `config/` - Configuration
- **Purpose**: Environment configurations, settings files, and secrets management
- **Contents**: Environment files, configuration templates, settings
- **Examples**: `.env.*` files, `settings.py`, configuration schemas

### `docker/` - Containerization
- **Purpose**: Dockerfiles, container configurations, and orchestration files
- **Contents**: Docker configurations, compose files, container scripts
- **Examples**: `Dockerfile`, `docker-compose.yml`, container orchestration

## 🔧 Enforcement Mechanisms

### 1. Code Reviews
- **Requirement**: All pull requests must follow the standardized structure
- **Checklist**: Reviewers must verify proper file placement and organization
- **Tools**: Use PR templates that include structure compliance checks

### 2. Linting Rules
- **Import Linting**: Configure linters to enforce proper import paths
- **Structure Validation**: Use custom linting rules to validate file placement
- **CI Integration**: Include structure validation in CI/CD pipeline

### 3. Project Templates
- **New Features**: Provide templates for new feature development
- **Boilerplate**: Include standardized boilerplate code for each layer
- **Documentation**: Template documentation for new components

### 4. Documentation Guidelines
- **Structure Documentation**: Maintain up-to-date structure documentation
- **Onboarding**: Include structure training in developer onboarding
- **Examples**: Provide clear examples of proper file organization

## 📝 Development Guidelines

### File Naming Conventions
- Use snake_case for Python files: `report_generator.py`
- Use descriptive names that indicate functionality
- Group related functionality in appropriately named modules

### Import Guidelines
- Use absolute imports from the `src/` directory
- Example: `from src.models.database import ComplianceReport`
- Avoid relative imports across different layers

### Layer Dependencies
- **API Layer**: Can import from core, models, services, utils
- **Core Layer**: Can import from models, utils (avoid services)
- **Models Layer**: Can import from utils only
- **Services Layer**: Can import from core, models, utils
- **Utils Layer**: Should be self-contained with minimal dependencies

### Testing Structure
- Mirror the `src/` structure in `tests/`
- Example: `tests/api/test_endpoints.py` for `src/api/endpoints.py`
- Use descriptive test file names with `test_` prefix

## 🚀 Migration Guide

For existing code, follow this migration process:

1. **Identify Current Location**: Determine where existing code should be placed
2. **Create New Structure**: Set up the standardized directory structure
3. **Move Files**: Relocate files to appropriate directories
4. **Update Imports**: Fix all import statements to use new paths
5. **Update Tests**: Ensure tests reflect the new structure
6. **Update Documentation**: Update any references to old file locations

## ✅ Compliance Checklist

Before submitting code, ensure:

- [ ] Files are placed in the correct directory according to their function
- [ ] Import statements use the standardized paths
- [ ] New functionality includes appropriate tests in the mirrored structure
- [ ] Documentation is updated to reflect any structural changes
- [ ] Code follows the established naming conventions
- [ ] Layer dependencies are respected (no circular dependencies)

## 🔍 Benefits

### Consistent Code Organization
- Predictable file locations for all team members
- Easier navigation and code discovery
- Reduced cognitive load when working with the codebase

### Maintainable Project Architecture
- Clear separation of concerns between layers
- Easier to identify and fix architectural issues
- Simplified dependency management

### Simplified Onboarding
- New team members can quickly understand the codebase structure
- Standardized patterns reduce learning curve
- Clear guidelines for where to place new code

### Standardized Development Practices
- Consistent approach across all features and components
- Easier code reviews and quality assurance
- Improved collaboration between team members

## 📞 Support

For questions about the project structure or enforcement:
- Review this documentation
- Ask during code reviews
- Consult with the architecture team
- Update this document as the project evolves

---

**Last Updated**: August 29, 2025  
**Version**: 1.0  
**Maintained By**: DoganAI Platform Team
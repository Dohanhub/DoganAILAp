# Overview

The Doğan AI Lab Platform is an AI-powered compliance validation and risk management system specifically designed for Saudi Arabia's regulatory landscape. The platform provides automated compliance validation against key Saudi regulations including NCA (National Cybersecurity Authority), SAMA (Saudi Arabian Monetary Authority), and PDPL (Personal Data Protection Law), along with international standards like ISO 27001 and NIST frameworks. The system is built as a comprehensive software-and-hardware solution that continuously monitors organizational controls and automates compliance workflows, transforming compliance from a periodic audit exercise into a proactive, streamlined process.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Core Application Structure
The system follows a microservices-based architecture with clear separation of concerns. The main application entry point is through `main.py` with FastAPI providing the backend API layer and Streamlit powering the user interface. The architecture supports both single-appliance deployments for mid-sized enterprises and scalable cluster deployments for large organizations.

## Database Design
The platform uses PostgreSQL as the primary database with SQLAlchemy ORM for data modeling. The database schema includes comprehensive audit logging, compliance caching, and multi-tenant support through Row Level Security (RLS) policies. Key models include ComplianceStandard, Control, Assessment, and AuditLog tables with proper indexing and relationships.

## Authentication and Security
The system implements JWT-based authentication with OAuth2 password flows. Security headers are enforced through middleware including X-Content-Type-Options, X-Frame-Options, and XSS protection. The platform supports role-based access control with user management and session handling.

## Compliance Engine
The core compliance evaluation engine is built around a modular mapping system that codifies regulatory requirements. The engine supports real-time validation, automated evidence collection, and benchmark scoring. It includes specialized modules for different Saudi regulatory frameworks and can evaluate organizational controls against multiple standards simultaneously.

## Caching and Performance
Multi-layer caching is implemented using Redis for session management and SQLAlchemy-based database caching for compliance results. The system includes TTL-based cache expiration and supports compression for optimal performance.

## Monitoring and Observability
Comprehensive monitoring is built-in using Prometheus metrics, structured logging with structlog, and health check endpoints. The platform includes performance monitoring, error tracking, and system resource monitoring with configurable alerting.

## Microservices Architecture
The platform is designed with separate services for compliance-engine, benchmarks, ai-ml processing, integrations, ui, authentication, and autonomous testing. Each service can be deployed independently with proper health checks and service discovery.

# External Dependencies

## Database Services
- **PostgreSQL**: Primary database for storing compliance data, audit logs, and user information
- **Redis**: Session management, caching layer, and real-time data storage

## Web Framework and API
- **FastAPI**: Backend API framework with automatic OpenAPI documentation
- **Streamlit**: Frontend dashboard and user interface framework
- **Uvicorn**: ASGI server for FastAPI application deployment

## Authentication and Security
- **PyJWT**: JWT token generation and validation for user authentication
- **Passlib**: Password hashing and verification with bcrypt support
- **Python-JOSE**: JSON Object Signing and Encryption for secure token handling

## Data Processing and Validation
- **Pydantic**: Data validation and serialization for API request/response models
- **SQLAlchemy**: ORM for database operations and model definitions
- **Pandas**: Data manipulation and analysis for compliance reporting
- **PyYAML**: Configuration file parsing for compliance mappings and policies

## Monitoring and Operations
- **Prometheus Client**: Metrics collection and monitoring
- **Structlog**: Structured logging for better observability
- **PSUtil**: System resource monitoring and health checks

## HTTP and Integration
- **Requests**: HTTP client for external API integrations
- **HTTPX**: Async HTTP client for performance-critical operations
- **Aiofiles**: Asynchronous file operations
- **Boto3**: AWS services integration for cloud deployments

## Development and Testing
- **Pytest**: Testing framework for unit and integration tests
- **Typer**: CLI framework for management commands
- **Rich**: Enhanced terminal output and progress indicators

## Regulatory API Integrations
- **NCA (National Cybersecurity Authority)**: Direct API integration for cybersecurity compliance validation
- **SAMA (Saudi Arabian Monetary Authority)**: Financial services compliance checking
- **External vendor APIs**: Integration with compliance management platforms and security tools
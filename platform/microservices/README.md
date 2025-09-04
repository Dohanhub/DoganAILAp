# DoganAI Compliance Kit Microservices

## Overview
This directory will contain all microservices for the next-generation, on-prem, Saudi-compliant compliance platform. Each service is independently deployable, API-first, and designed for modularity, extensibility, and local AI/LLM support.

## Core Microservices
- **compliance-engine**: Modular compliance logic, API-first, extensible for all KSA regulations (NCA, SAMA, MoH, etc.)
- **benchmarks**: Unified regulatory benchmark database, versioned, extensible
- **ai-ml**: Local LLM inference, compliance Q&A, risk prediction (no cloud dependency)
- **integrations**: Evidence collection, reporting, connectors to banking/government systems
- **ui**: Next-gen dashboard, AR/EN, mobile, accessible, real-time
- **shared-libs**: Common models, schemas, and utilities for all services

## Deployment
- **On-premises**: Designed for full data sovereignty and KSA regulatory compliance
- **Hardware-aware**: Can run on mobile service station hardware (specs to be documented)
- **Docker Compose**: For local orchestration (Kubernetes-ready for future scaling)

## Hardware Requirements & Scaling
- Designed for portable/mini-PC/mobile service stations (max kit: 128GB RAM)
- Example profiles:
  - Small (pilot/POC): 16GB RAM, 4 vCPU, 256GB SSD (up to 1,000 benchmarks, 10 users)
  - Medium (bank/gov dept): 32-64GB RAM, 8-12 vCPU, 1TB SSD (up to 10,000 benchmarks, 100 users)
  - Max kit (full KSA, mobile): 128GB RAM, 16 vCPU, 2TB SSD (all benchmarks, 500+ users)
- Worldwide best practices: scale horizontally (add more nodes), use SSDs for fast I/O, monitor resource usage, and plan for peak loads
- Resource-monitor microservice and UI dashboard provide live stats and capacity planning

## Roadmap
- Phase 1: Skeletons for all core services, unified schema, initial Docker Compose
- Phase 2: Load all KSA regulatory benchmarks, implement compliance logic, stub AI/ML
- Phase 3: Integrations, advanced UI, production hardening, hardware alignment

---
Each microservice will have its own README and Dockerfile. See the root README for the full vision and architecture.

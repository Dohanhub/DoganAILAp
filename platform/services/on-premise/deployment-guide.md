# Doğan AI Platform - On-Premise Deployment Guide

## Regulatory Compliance for Saudi Arabia

Saudi regulators (NCA, SAMA, SDAIA) require on-premise deployment for critical data and compliance systems.

## On-Premise Architecture

### 1. Single Appliance Mode
- All services in one physical server
- Suitable for organizations < 1000 employees
- Hardware: Dell PowerEdge R750 or HP ProLiant DL380

### 2. Cluster Mode
- Distributed across multiple servers
- High availability and load balancing
- Suitable for enterprise deployments

## Hardware Requirements

### Minimum Specifications
- CPU: 32 cores (Intel Xeon Gold or AMD EPYC)
- RAM: 128 GB ECC
- Storage: 2 TB NVMe SSD (RAID 10)
- Network: Dual 10 Gbps NICs
- Power: Redundant PSU

### Recommended Specifications
- CPU: 64 cores
- RAM: 256 GB ECC
- Storage: 4 TB NVMe SSD (RAID 10)
- Network: Dual 25 Gbps NICs
- Power: Redundant PSU with UPS

## Software Stack

### Base System
- OS: RHEL 8.x or Ubuntu 20.04 LTS (certified)
- Container Runtime: Podman (rootless)
- Orchestration: K3s (lightweight Kubernetes)

### Security Requirements
- SELinux/AppArmor enabled
- FIPS 140-2 compliant encryption
- Hardware Security Module (HSM) integration
- Air-gapped deployment option

## Deployment Options

### Option 1: Containerized Deployment
```bash
# Deploy all services as containers
./deploy-on-premise.sh --mode=single --secure=true
```

### Option 2: Bare Metal Deployment
```bash
# Deploy directly on hardware
./deploy-bare-metal.sh --config=production.yaml
```

### Option 3: Private Cloud
```bash
# Deploy on OpenStack or VMware
./deploy-private-cloud.sh --platform=openstack
```

## Data Residency Compliance

All data remains within Saudi Arabia borders:
- Database: Local PostgreSQL cluster
- File Storage: Local MinIO/Ceph
- Backups: Local encrypted storage
- No external API calls for core operations

## Regulatory Certifications

Platform meets requirements for:
- NCA ECC-1:2018 (National Cybersecurity)
- SAMA Cyber Security Framework
- SDAIA Data Classification
- CITC Cloud Computing Regulatory Framework
# 🚀 DoganAI Compliance Kit - Kubernetes Deployment

## 📋 Overview

This directory contains the complete Kubernetes deployment configuration for the **DoganAI Compliance Kit Strong Application Engine**. The deployment is designed to handle **2,000-3,000 concurrent enterprise users** and is **IBM demo ready**.

## 🏗️ Architecture Components

### 1. **Core Application Engine** (3 App Servers)
- **Purpose**: Handle API requests, business logic, and dashboard rendering
- **Replicas**: 3 (for redundancy and load balancing)
- **Resources**: 1-2 Gi memory, 0.5-1.0 CPU per instance
- **Ports**: 8001 (HTTP), 9100 (Metrics)

### 2. **Database Engine** (Primary + Replica)
- **Primary**: Write operations, 200 max connections
- **Replica**: Read operations, 100 max connections
- **Storage**: 100Gi each with fast SSD storage class
- **Resources**: 2-4 Gi memory, 1-2 CPU per instance

### 3. **Vector Database** (Weaviate)
- **Purpose**: AI/ML embeddings and semantic search
- **Storage**: 200Gi with fast SSD storage class
- **Modules**: OpenAI, Cohere, HuggingFace, Generative AI
- **Resources**: 2-4 Gi memory, 1-2 CPU

### 4. **AI/LLM Engine** (2 GPU Instances)
- **Purpose**: Local AI inference and model serving
- **GPU**: NVIDIA A100/H100 equivalent (80GB memory)
- **Storage**: 1Ti with high-IOPS storage class
- **Resources**: 4-8 Gi memory, 2-4 CPU per instance

### 5. **Load Balancing Layer**
- **NGINX**: Reverse proxy with WAF capabilities
- **HAProxy**: Advanced load balancing with health checks
- **Features**: Rate limiting, SSL termination, security headers

### 6. **Monitoring Stack**
- **Prometheus**: Metrics collection and storage
- **Grafana**: Visualization and dashboards
- **AlertManager**: Alerting and notifications

### 7. **Logging Stack** (ELK)
- **Elasticsearch**: Log storage and indexing
- **Logstash**: Log processing and transformation
- **Kibana**: Log visualization and analysis

### 8. **Security & RBAC**
- **Service Accounts**: Isolated permissions per component
- **Roles**: Granular access control
- **Network Policies**: Pod-to-pod communication rules

## 📁 File Structure

```
k8s/
├── namespace.yaml          # Namespace definitions
├── configmaps.yaml         # Configuration data
├── secrets.yaml           # Sensitive data (passwords, API keys)
├── storage.yaml           # Storage classes and PVCs
├── rbac.yaml             # Security and permissions
├── deployments.yaml       # Application deployments
├── services.yaml         # Service definitions
├── ingress.yaml          # External access routing
├── deploy-k8s.ps1       # Deployment script
└── helm-chart/           # Helm chart for easy deployment
    ├── Chart.yaml        # Chart metadata
    └── values.yaml       # Configurable parameters
```

## 🚀 Quick Start

### Prerequisites

1. **Kubernetes Cluster** (v1.24+)
   - Minikube (development)
   - Docker Desktop (development)
   - EKS, AKS, GKE (production)
   - On-premises cluster

2. **Tools**
   - `kubectl` (v1.24+)
   - `helm` (v3.0+) - optional

3. **Resources**
   - **Minimum**: 8 CPU cores, 16GB RAM
   - **Recommended**: 16 CPU cores, 32GB RAM
   - **Production**: 32+ CPU cores, 64GB+ RAM

### Deployment Options

#### Option 1: Direct YAML Deployment
```powershell
# Deploy to production
.\deploy-k8s.ps1 -Environment production -ClusterName "doganai-prod"

# Deploy to development
.\deploy-k8s.ps1 -Environment dev -ClusterName "doganai-dev"
```

#### Option 2: Helm Chart Deployment
```powershell
# Deploy using Helm
.\deploy-k8s.ps1 -Environment production -UseHelm

# Customize values
helm upgrade --install doganai-compliance-kit ./helm-chart \
  --namespace doganai-compliance \
  --set global.environment=production \
  --set app.replicas=5
```

### Manual Deployment Steps

1. **Create Namespaces**
   ```bash
   kubectl apply -f namespace.yaml
   ```

2. **Deploy Storage**
   ```bash
   kubectl apply -f storage.yaml
   ```

3. **Deploy Configuration**
   ```bash
   kubectl apply -f configmaps.yaml
   kubectl apply -f secrets.yaml
   ```

4. **Deploy Security**
   ```bash
   kubectl apply -f rbac.yaml
   ```

5. **Deploy Applications**
   ```bash
   kubectl apply -f deployments.yaml
   kubectl apply -f services.yaml
   ```

6. **Deploy Ingress**
   ```bash
   kubectl apply -f ingress.yaml
   ```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `NODE_ENV` | Application environment | `production` |
| `DATABASE_URL` | PostgreSQL connection string | Auto-generated |
| `REDIS_URL` | Redis connection string | `redis://redis:6379` |
| `VECTOR_DB_URL` | Weaviate connection string | `http://weaviate:8080` |

### Resource Limits

| Component | CPU Request | CPU Limit | Memory Request | Memory Limit |
|-----------|-------------|-----------|----------------|--------------|
| App Server | 500m | 1000m | 1Gi | 2Gi |
| Database | 1000m | 2000m | 2Gi | 4Gi |
| Weaviate | 1000m | 2000m | 2Gi | 4Gi |
| AI Engine | 2000m | 4000m | 4Gi | 8Gi |
| Monitoring | 500m | 1000m | 1Gi | 2Gi |

### Storage Configuration

| Component | Storage Size | Storage Class | Access Mode |
|-----------|--------------|---------------|-------------|
| PostgreSQL Primary | 100Gi | `doganai-fast-ssd` | ReadWriteOnce |
| PostgreSQL Replica | 100Gi | `doganai-fast-ssd` | ReadWriteOnce |
| Weaviate | 200Gi | `doganai-fast-ssd` | ReadWriteOnce |
| AI Models | 1Ti | `doganai-gpu-storage` | ReadWriteMany |
| Elasticsearch | 500Gi | `doganai-fast-ssd` | ReadWriteOnce |
| Prometheus | 100Gi | `doganai-fast-ssd` | ReadWriteOnce |

## 🌐 Access Points

### Application URLs
- **Main Dashboard**: `https://compliance.dogan-ai.com`
- **API Endpoint**: `https://api.dogan-ai.com`
- **Admin Panel**: `https://admin.dogan-ai.com`

### Monitoring URLs
- **Grafana**: `https://monitoring.dogan-ai.com`
- **Prometheus**: `https://prometheus.dogan-ai.com`
- **Kibana**: `https://logs.dogan-ai.com`

### Internal Services
- **App Servers**: `app-server-1:8001`, `app-server-2:8001`, `app-server-3:8001`
- **Database**: `db-primary:5432`, `db-replica:5432`
- **Redis**: `redis:6379`
- **Weaviate**: `weaviate:8080`

## 📊 Monitoring & Health Checks

### Health Check Endpoints
- **Application**: `/health`
- **API**: `/api/health`
- **Database**: `pg_isready`
- **Redis**: `redis-cli ping`

### Metrics Collection
- **Application Metrics**: `/metrics`
- **Database Metrics**: PostgreSQL exporter
- **System Metrics**: Node exporter
- **Custom Metrics**: Compliance, security, business KPIs

### Alerting Rules
- **High CPU/Memory Usage**: >80%
- **Database Connection Issues**: Connection pool exhaustion
- **Service Unavailability**: Health check failures
- **Storage Issues**: Disk space <20%

## 🔒 Security Features

### Network Security
- **Network Policies**: Pod-to-pod communication rules
- **Ingress Security**: Rate limiting, WAF protection
- **SSL/TLS**: Automatic certificate management

### Access Control
- **RBAC**: Role-based access control
- **Service Accounts**: Isolated permissions
- **Secrets Management**: Kubernetes secrets

### Data Protection
- **Encryption at Rest**: Storage encryption
- **Encryption in Transit**: TLS 1.2/1.3
- **Audit Logging**: Comprehensive activity tracking

## 📈 Scaling & Performance

### Horizontal Pod Autoscaling
```bash
# Scale based on CPU usage
kubectl autoscale deployment app-server-1 \
  --cpu-percent=70 \
  --min=3 \
  --max=10 \
  -n doganai-compliance
```

### Vertical Pod Autoscaling
```bash
# Enable VPA for automatic resource adjustment
kubectl apply -f vpa.yaml
```

### Cluster Autoscaling
```bash
# Enable cluster autoscaler for node scaling
kubectl apply -f cluster-autoscaler.yaml
```

## 🗄️ Backup & Recovery

### Backup Schedule
- **Database**: Daily at 2:00 AM
- **Logs**: Daily at 3:00 AM
- **Storage**: Weekly on Sunday

### Backup Retention
- **Database**: 30 days
- **Logs**: 90 days
- **Storage**: 365 days

### Recovery Procedures
1. **Database Recovery**: Point-in-time recovery
2. **Application Recovery**: Rolling updates
3. **Full System Recovery**: Complete restore from backup

## 🚨 Troubleshooting

### Common Issues

#### Pods Not Starting
```bash
# Check pod status
kubectl get pods -n doganai-compliance

# Check pod logs
kubectl logs -f deployment/app-server-1 -n doganai-compliance

# Check events
kubectl get events -n doganai-compliance --sort-by='.lastTimestamp'
```

#### Database Connection Issues
```bash
# Check database status
kubectl exec -it deployment/db-primary -n doganai-compliance -- pg_isready

# Check database logs
kubectl logs -f deployment/db-primary -n doganai-compliance
```

#### Storage Issues
```bash
# Check PVC status
kubectl get pvc -n doganai-compliance

# Check storage class
kubectl get storageclass
```

### Performance Issues

#### High CPU Usage
```bash
# Check resource usage
kubectl top pods -n doganai-compliance

# Check HPA status
kubectl get hpa -n doganai-compliance
```

#### Memory Issues
```bash
# Check memory usage
kubectl top pods -n doganai-compliance --containers

# Check OOM events
kubectl get events -n doganai-compliance | grep OOM
```

## 🔄 Updates & Maintenance

### Rolling Updates
```bash
# Update application image
kubectl set image deployment/app-server-1 \
  app-server=doganai/compliance-ui:v2.0.0 \
  -n doganai-compliance
```

### Configuration Updates
```bash
# Update configmaps
kubectl apply -f configmaps.yaml

# Restart deployments to pick up new config
kubectl rollout restart deployment/app-server-1 -n doganai-compliance
```

### Database Migrations
```bash
# Run database migrations
kubectl apply -f migrations.yaml

# Check migration status
kubectl get jobs -n doganai-compliance
```

## 📚 Additional Resources

### Documentation
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Helm Documentation](https://helm.sh/docs/)
- [DoganAI Compliance Kit Documentation](https://docs.dogan-ai.com)

### Support
- **Technical Support**: support@dogan-ai.com
- **Emergency Contact**: +966-XX-XXX-XXXX
- **Documentation**: https://docs.dogan-ai.com

### Community
- **GitHub**: https://github.com/dogan-ai/compliance-kit
- **Discord**: https://discord.gg/doganai
- **LinkedIn**: https://linkedin.com/company/doganai

---

## 🎯 Next Steps

1. **Deploy the cluster** using the provided scripts
2. **Configure your domain names** in the ingress configuration
3. **Set up SSL certificates** using cert-manager
4. **Populate the database** with your compliance data
5. **Configure monitoring alerts** for your specific needs
6. **Set up backup schedules** for your data retention policies

---

**🚀 Ready to deploy your enterprise-grade compliance platform? Start with the deployment script!**

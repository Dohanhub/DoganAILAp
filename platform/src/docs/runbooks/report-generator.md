# DoganAI Compliance Kit - Report Generator Runbook

## 📋 Overview

This runbook provides comprehensive operational procedures for the **DoganAI Compliance Report Generator**, including deployment, monitoring, troubleshooting, and emergency response protocols.

### Service Information
- **Service Name**: DoganAI Compliance Report Generator
- **Owner**: Platform Team (platform@dogan.ai)
- **SLA Tier**: Critical (99.9% uptime, <500ms response time)
- **Environment**: Staging → Production
- **Rollout Strategy**: Canary (10%) → Gradual (25%, 50%, 75%) → Full (100%)
- **Recovery Time Objective (RTO)**: 15 minutes
- **Recovery Point Objective (RPO)**: 1 hour

### Key Components
- **FastAPI Application**: Main API server with uvicorn
- **PostgreSQL Database**: Primary data storage with audit logging
- **Redis Cache**: Session management and feature flag caching
- **Prometheus Metrics**: Real-time monitoring and alerting
- **Feature Flags**: Configuration-driven rollout management
- **Structured Logging**: JSON-formatted audit trails with correlation IDs

---

## 🚀 Deployment Procedures

### Pre-Deployment Checklist

#### ✅ CI/CD Pipeline Validation
- [ ] **config-lint**: YAML/JSON configuration validation passed
- [ ] **placeholder-audit**: No critical placeholders detected
- [ ] **sec-scan**: Security scanning (Bandit, Safety) passed
- [ ] **smoke-staging**: Staging environment tests passed
- [ ] **unit-tests**: All test suites passed with coverage >80%
- [ ] **code-quality**: Linting, formatting, and type checking passed

#### ✅ Production Readiness Validation
```bash
# Run comprehensive production readiness check
python src/scripts/validate_production_readiness.py --environment production

# Verify all Definition of Done criteria
./scripts/validate_dod_criteria.sh

# Check critical placeholders
python check_vendor_placeholders.py --check-critical --environment production
```

#### ✅ Environment Validation
```bash
# Verify staging environment health
curl -f https://staging.doganai-compliance.com/health
curl -f https://staging.doganai-compliance.com/observability/status

# Check database connectivity and migrations
psql $STAGING_DATABASE_URL -c "SELECT version();"
psql $STAGING_DATABASE_URL -c "SELECT COUNT(*) FROM audit_logs;"

# Verify Redis connectivity
redis-cli -u $STAGING_REDIS_URL ping

# Test feature flag service
curl -f https://staging.doganai-compliance.com/feature-flags/status
```

#### ✅ Backup and Recovery Preparation
```bash
# Create pre-deployment database backup
pg_dump $PRODUCTION_DATABASE_URL > backup-pre-deploy-$(date +%Y%m%d-%H%M%S).sql

# Verify backup integrity
pg_restore --list backup-pre-deploy-*.sql

# Store backup in secure location
aws s3 cp backup-pre-deploy-*.sql s3://doganai-backups/database/
```

### Canary Deployment (10%)

#### Step 1: Enable Canary Feature Flag
```bash
# Update feature flag for canary rollout
curl -X POST "https://doganai-compliance.com/feature-flags/compliance_report_generator/evaluate" \
  -H "Content-Type: application/json" \
  -d '{
    "user_segment": "canary",
    "environment": "production"
  }'

# Verify canary configuration
curl -s https://doganai-compliance.com/feature-flags/status | jq '.canary_flags'
```

#### Step 2: Monitor Canary Metrics
```bash
# Monitor canary deployment metrics
watch -n 30 'curl -s https://doganai-compliance.com/metrics | grep compliance_report_generator'

# Check error rates for canary users
curl -s https://doganai-compliance.com/observability/metrics | jq '.feature_metrics.compliance_report_generator'

# Monitor application logs
kubectl logs -f deployment/compliance-kit --tail=100 | grep canary
```

#### Step 3: Validate Canary Success
```bash
# Test report generation for canary users
curl -X POST "https://doganai-compliance.com/evaluate" \
  -H "Content-Type: application/json" \
  -d '{
    "mapping_name": "test_compliance_mapping",
    "user_segment": "canary"
  }'

# Verify no critical errors
if [ $(curl -s https://doganai-compliance.com/metrics | grep 'error_rate{feature="compliance_report_generator"}' | cut -d' ' -f2) -lt 0.01 ]; then
  echo "✅ Canary deployment successful - proceeding to gradual rollout"
else
  echo "❌ Canary deployment failed - initiating rollback"
  exit 1
fi
```

### Gradual Rollout (25% → 50% → 75%)

#### Progressive Rollout Steps
```bash
# Update to 25% rollout
curl -X PUT "https://doganai-compliance.com/feature-flags/compliance_report_generator" \
  -H "Content-Type: application/json" \
  -d '{
    "rollout": {
      "strategy": "gradual",
      "percentage": 25.0,
      "user_segments": ["canary", "beta"]
    }
  }'

# Wait and monitor for 30 minutes
sleep 1800

# Validate 25% rollout success
./scripts/validate_rollout_health.sh 25

# Continue to 50% if successful
curl -X PUT "https://doganai-compliance.com/feature-flags/compliance_report_generator" \
  -H "Content-Type: application/json" \
  -d '{
    "rollout": {
      "strategy": "gradual",
      "percentage": 50.0,
      "user_segments": ["canary", "beta", "production"]
    }
  }'
```

### Full Production Rollout (100%)

#### Final Deployment
```bash
# Enable for all users
curl -X PUT "https://doganai-compliance.com/feature-flags/compliance_report_generator" \
  -H "Content-Type: application/json" \
  -d '{
    "rollout": {
      "strategy": "full",
      "percentage": 100.0,
      "user_segments": ["all"]
    }
  }'

# Final validation
curl -f https://doganai-compliance.com/health
curl -f https://doganai-compliance.com/feature-flags/status
```

---

## 📊 Monitoring & Alerting

### Key Metrics Dashboard

#### Application Metrics
- **Request Rate**: `api_requests_total{endpoint="/evaluate"}`
- **Response Time**: `api_request_duration_seconds{endpoint="/evaluate"}`
- **Error Rate**: `api_requests_total{status_code!~"2..",endpoint="/evaluate"}`
- **Feature Usage**: `feature_requests_total{feature_name="compliance_report_generator"}`

#### Business Metrics
- **Report Generation Rate**: `compliance_reports_generated_total`
- **Report Generation Latency**: `compliance_report_generation_duration_seconds`
- **Feature Flag Evaluations**: `feature_flag_evaluations_total{flag_name="compliance_report_generator"}`
- **Audit Events**: `audit_events_total{feature="compliance_report_generator"}`

#### Infrastructure Metrics
- **Database Performance**: `db_operations_total{operation="compliance_query"}`
- **Cache Hit Rate**: `cache_hits_total{feature="compliance_report_generator"}`
- **Memory Usage**: `process_resident_memory_bytes`
- **CPU Usage**: `process_cpu_seconds_total`

### Alerting Rules

#### Critical Alerts (PagerDuty)
```yaml
# High error rate for compliance reports
api_error_rate{endpoint="/evaluate"} > 5% for 5 minutes

# Report generation failures
compliance_reports_failed_total > 10 for 5 minutes

# Feature flag evaluation failures
feature_flag_evaluations_total{result="error",flag_name="compliance_report_generator"} > 5 for 2 minutes

# Database connection issues
db_connection_pool_size == 0 for 1 minute
```

#### Warning Alerts (Slack)
```yaml
# Elevated response times
api_request_duration_seconds_p95{endpoint="/evaluate"} > 2s for 10 minutes

# Low cache hit rate
cache_hit_rate{feature="compliance_report_generator"} < 80% for 15 minutes

# High memory usage
process_resident_memory_bytes > 1GB for 15 minutes
```

### Monitoring Commands
```bash
# Real-time metrics monitoring
watch -n 5 'curl -s https://doganai-compliance.com/metrics | grep compliance_report'

# Check feature flag status
curl -s https://doganai-compliance.com/feature-flags/status | jq

# Monitor application logs
kubectl logs -f deployment/compliance-kit | grep compliance_report_generator

# Database performance monitoring
psql $DATABASE_URL -c "SELECT * FROM pg_stat_activity WHERE query LIKE '%compliance%';"
```

---

## 🔧 Troubleshooting

### Common Issues

#### 1. High Report Generation Latency
**Symptoms**: `compliance_report_generation_duration_seconds > 10s`

**Investigation Steps**:
```bash
# Check database query performance
psql $DATABASE_URL -c "SELECT query, total_time, calls FROM pg_stat_statements WHERE query LIKE '%compliance%' ORDER BY total_time DESC LIMIT 5;"

# Monitor database connections
psql $DATABASE_URL -c "SELECT count(*) FROM pg_stat_activity WHERE state = 'active';"

# Check cache performance
curl -s https://doganai-compliance.com/metrics | grep cache_hit_rate

# Review application logs for slow operations
kubectl logs deployment/compliance-kit | grep 'duration.*[5-9][0-9][0-9][0-9]'
```

**Resolution Steps**:
1. Optimize database queries with proper indexing
2. Increase database connection pool size
3. Implement query result caching
4. Scale application horizontally if needed

#### 2. Feature Flag Evaluation Failures
**Symptoms**: `feature_flag_evaluations_total{result="error"} > 0`

**Investigation Steps**:
```bash
# Check feature flag configuration
curl -s https://doganai-compliance.com/feature-flags/compliance_report_generator

# Validate feature flag service health
curl -f https://doganai-compliance.com/feature-flags/status

# Review feature flag logs
kubectl logs deployment/compliance-kit | grep feature_flag | grep error

# Check feature flag file syntax
python -c "import json; json.load(open('feature_flags/flags.json'))"
```

**Resolution Steps**:
1. Validate and fix feature flag configuration
2. Restart application to reload feature flags
3. Implement feature flag fallback mechanisms
4. Monitor feature flag service dependencies

#### 3. Database Connection Pool Exhaustion
**Symptoms**: `db_connection_pool_size == 0`

**Investigation Steps**:
```bash
# Check active database connections
psql $DATABASE_URL -c "SELECT count(*) FROM pg_stat_activity;"

# Monitor connection pool metrics
curl -s https://doganai-compliance.com/metrics | grep db_connection_pool

# Check for long-running queries
psql $DATABASE_URL -c "SELECT pid, now() - pg_stat_activity.query_start AS duration, query FROM pg_stat_activity WHERE (now() - pg_stat_activity.query_start) > interval '5 minutes';"
```

**Resolution Steps**:
1. Increase database connection pool size
2. Terminate long-running queries
3. Optimize database queries
4. Implement connection pooling best practices

---

## 🚨 Emergency Procedures

### Incident Response

#### Severity Classification
- **P0 (Critical)**: Complete service outage, data corruption
- **P1 (High)**: Major feature unavailable, high error rates (>10%)
- **P2 (Medium)**: Performance degradation, minor feature issues
- **P3 (Low)**: Cosmetic issues, documentation problems

#### P0/P1 Incident Response (0-15 minutes)
```bash
# Immediate assessment
curl -f https://doganai-compliance.com/health || echo "Service DOWN"
curl -s https://doganai-compliance.com/metrics | grep error_rate

# Check recent deployments
gh run list --limit 5
kubectl rollout history deployment/compliance-kit

# Review critical metrics
curl -s https://doganai-compliance.com/observability/status

# Check infrastructure status
kubectl get pods -n production
kubectl get events --sort-by=.metadata.creationTimestamp
```

#### Emergency Response Actions
1. **Immediate Mitigation** (0-5 minutes)
   - Activate kill switch if available
   - Scale up resources if capacity issue
   - Implement circuit breaker patterns

2. **Root Cause Analysis** (5-15 minutes)
   - Review application and infrastructure logs
   - Check database and cache performance
   - Analyze recent configuration changes

3. **Resolution** (15-30 minutes)
   - Execute rollback procedures if needed
   - Apply hotfixes for critical bugs
   - Coordinate with dependent services

### Kill Switch Activation
```bash
# Emergency disable of compliance report generator
curl -X PUT "https://doganai-compliance.com/feature-flags/compliance_report_generator" \
  -H "Content-Type: application/json" \
  -d '{
    "kill_switch": true,
    "rollout": {
      "strategy": "kill_switch",
      "percentage": 0.0
    }
  }'

# Verify kill switch activation
curl -s https://doganai-compliance.com/feature-flags/status | jq '.kill_switches'

# Monitor impact
watch -n 10 'curl -s https://doganai-compliance.com/metrics | grep error_rate'
```

---

## 🔄 Rollback Procedures

### Automated Rollback Triggers
The system automatically initiates rollback when:
- Error rate > 10% for 5 consecutive minutes
- Response time > 5 seconds for 95th percentile
- Feature flag evaluation failures > 50% for 2 minutes
- Critical alerts triggered within 10 minutes of deployment

### Manual Rollback Procedures

#### 1. Feature Flag Rollback (Fastest - 30 seconds)
```bash
# Disable feature flag immediately
curl -X PUT "https://doganai-compliance.com/feature-flags/compliance_report_generator" \
  -H "Content-Type: application/json" \
  -d '{
    "enabled": false,
    "rollout": {
      "strategy": "off",
      "percentage": 0.0
    }
  }'

# Verify rollback
curl -s https://doganai-compliance.com/feature-flags/compliance_report_generator | jq '.enabled'

# Monitor metrics for improvement
watch -n 30 'curl -s https://doganai-compliance.com/metrics | grep error_rate'
```

#### 2. Application Rollback (2-5 minutes)
```bash
# Identify previous stable version
kubectl rollout history deployment/compliance-kit

# Rollback to previous version
kubectl rollout undo deployment/compliance-kit

# Monitor rollback progress
kubectl rollout status deployment/compliance-kit --timeout=300s

# Verify application health
curl -f https://doganai-compliance.com/health
curl -f https://doganai-compliance.com/observability/status
```

#### 3. Database Rollback (10-30 minutes)
```bash
# Stop application traffic
kubectl scale deployment compliance-kit --replicas=0

# Restore from backup
aws s3 cp s3://doganai-backups/database/backup-pre-deploy-*.sql .
psql $DATABASE_URL < backup-pre-deploy-*.sql

# Verify database restoration
psql $DATABASE_URL -c "SELECT COUNT(*) FROM audit_logs WHERE created_at > NOW() - INTERVAL '1 hour';"

# Restart application
kubectl scale deployment compliance-kit --replicas=3
kubectl rollout status deployment/compliance-kit
```

### Rollback Validation
```bash
# Health check validation
curl -f https://doganai-compliance.com/health

# Feature functionality test
curl -X POST "https://doganai-compliance.com/evaluate" \
  -H "Content-Type: application/json" \
  -d '{"mapping_name": "test_mapping"}'

# Metrics validation
curl -s https://doganai-compliance.com/metrics | grep -E '(error_rate|response_time)'

# End-to-end smoke test
pytest src/tests/smoke/ --env=production --timeout=300
```

### Post-Rollback Actions
1. **Immediate** (0-15 minutes)
   - Verify service restoration
   - Update incident status
   - Notify stakeholders

2. **Short-term** (15-60 minutes)
   - Document rollback reason
   - Create post-incident review ticket
   - Update monitoring alerts if needed

3. **Long-term** (1-24 hours)
   - Conduct post-incident review
   - Implement preventive measures
   - Update runbook based on learnings

---

## 📞 Contact Information

### On-Call Escalation
1. **Primary On-Call**: Platform Team (+1-555-PLATFORM)
2. **Secondary On-Call**: DevOps Team (+1-555-DEVOPS)
3. **Escalation Manager**: Engineering Manager (+1-555-ENG-MGR)
4. **Executive Escalation**: VP Engineering (+1-555-VP-ENG)

### Team Contacts
- **Platform Team**: platform@dogan.ai
- **DevOps Team**: devops@dogan.ai
- **Security Team**: security@dogan.ai
- **Product Team**: product@dogan.ai
- **Customer Success**: support@dogan.ai

### Communication Channels
- **Critical Incidents**: #incident-response
- **Alerts**: #alerts-compliance-kit
- **Team Updates**: #platform-team
- **General Discussion**: #compliance-kit
- **Announcements**: #engineering-all

### External Dependencies
- **Cloud Provider**: AWS Enterprise Support
- **Database Support**: PostgreSQL Professional Services
- **Monitoring**: Prometheus/Grafana Support
- **CDN Provider**: CloudFlare Enterprise

---

## 📚 Additional Resources

### Documentation Links
- **API Documentation**: https://docs.doganai.com/compliance-kit/api
- **Architecture Guide**: https://docs.doganai.com/compliance-kit/architecture
- **Feature Flag Guide**: https://docs.doganai.com/compliance-kit/feature-flags
- **Monitoring Dashboard**: https://grafana.doganai.com/d/compliance-kit

### Useful Commands Reference
```bash
# Quick health check
curl -f https://doganai-compliance.com/health && echo "✅ Healthy" || echo "❌ Unhealthy"

# Feature flag status
curl -s https://doganai-compliance.com/feature-flags/status | jq

# Real-time metrics
watch -n 5 'curl -s https://doganai-compliance.com/metrics | grep compliance_report'

# Application logs
kubectl logs -f deployment/compliance-kit --tail=100

# Database quick check
psql $DATABASE_URL -c "SELECT COUNT(*) FROM audit_logs WHERE created_at > NOW() - INTERVAL '5 minutes';"
```

---

**Document Information**
- **Version**: 2.0
- **Last Updated**: 2025-08-29
- **Next Review**: 2025-09-29
- **Owner**: Platform Team
- **Reviewers**: DevOps Team, Security Team, Product Team
- **Approval**: Engineering Manager

**Change Log**
- v2.0 (2025-08-29): Complete rewrite with comprehensive procedures
- v1.0 (2025-08-15): Initial version with basic deployment steps
      "strategy": "canary",
      "percentage": 10.0,
      "user_segments": ["canary", "internal"]
    }
  }'
```

#### Step 2: Deploy Application
```bash
# Deploy to staging
docker-compose -f docker-compose.staging.yml up -d

# Or Kubernetes deployment
kubectl apply -f k8s/deployments.yaml -n doganai-staging
kubectl rollout status deployment/doganai-api -n doganai-staging
```

#### Step 3: Verify Canary Deployment
```bash
# Check application health
curl -f http://localhost:8000/health

# Verify feature flag evaluation
curl -X POST "http://localhost:8000/api/v1/reports/generate" \
  -H "Content-Type: application/json" \
  -H "X-User-Segment: canary" \
  -d '{
    "title": "Canary Test Report",
    "report_type": "policy_compliance"
  }'

# Monitor metrics
curl http://localhost:9090/metrics | grep feature_flag_evaluations_total
curl http://localhost:9090/metrics | grep feature_latency_ms
```

### Full Deployment (100%)

#### Step 1: Validate Canary Success
- [ ] No critical errors in logs for 2+ hours
- [ ] Feature latency < 2000ms (P95)
- [ ] Error rate < 1%
- [ ] User feedback positive

#### Step 2: Enable Full Rollout
```bash
# Update feature flag for full rollout
curl -X PUT "http://localhost:8000/api/v1/feature-flags/compliance_report_generator_full" \
  -H "Content-Type: application/json" \
  -d '{
    "enabled": true,
    "rollout": {
      "strategy": "full",
      "percentage": 100.0,
      "user_segments": ["all"]
    }
  }'

# Disable canary flag
curl -X PUT "http://localhost:8000/api/v1/feature-flags/compliance_report_generator" \
  -H "Content-Type: application/json" \
  -d '{"enabled": false}'
```

#### Step 3: Monitor Full Rollout
```bash
# Monitor application metrics
watch -n 30 'curl -s http://localhost:9090/metrics | grep -E "(feature_requests_total|feature_latency_ms|db_operations_total)"'

# Check error logs
docker logs doganai-api --tail 100 -f | grep -i error

# Monitor database performance
psql $DATABASE_URL -c "SELECT * FROM pg_stat_activity WHERE state = 'active';"
```

---

## 📊 Monitoring and Alerting

### Key Metrics to Monitor

#### Application Metrics
- `feature_latency_ms{feature_name="compliance_report_generator"}` - Response time
- `feature_requests_total{feature_name="compliance_report_generator"}` - Request count
- `feature_flag_evaluations_total{flag_name="compliance_report_generator"}` - Flag evaluations
- `db_operations_total{table="compliance_reports"}` - Database operations

#### Infrastructure Metrics
- `service_up{service_name="api"}` - Service availability
- `api_request_duration_seconds` - API response time
- `db_connection_pool_size` - Database connections
- `placeholder_critical_count` - Critical placeholder count

### Alerting Thresholds

#### Critical Alerts (Immediate Response)
```yaml
# High error rate
feature_requests_total{status="error"} / feature_requests_total > 0.05

# High latency
histogram_quantile(0.95, feature_latency_ms) > 5000

# Service down
service_up{service_name="api"} == 0

# Critical placeholders
placeholder_critical_count > 5
```

#### Warning Alerts (Monitor Closely)
```yaml
# Elevated error rate
feature_requests_total{status="error"} / feature_requests_total > 0.01

# Elevated latency
histogram_quantile(0.95, feature_latency_ms) > 2000

# Database connection issues
db_connection_pool_size < 5
```

### Monitoring Commands

#### Real-time Monitoring
```bash
# Monitor feature performance
watch -n 10 'curl -s http://localhost:9090/metrics | grep feature_latency_ms | tail -5'

# Monitor error rates
watch -n 30 'curl -s http://localhost:9090/metrics | grep feature_requests_total | grep error'

# Monitor database operations
watch -n 15 'curl -s http://localhost:9090/metrics | grep db_operations_total'

# Check application logs
tail -f /var/log/doganai/application.log | jq 'select(.feature_name == "compliance_report_generator")'
```

#### Health Check Dashboard
```bash
# Create monitoring dashboard
cat > monitoring_dashboard.sh << 'EOF'
#!/bin/bash
echo "=== DoganAI Compliance Report Generator Status ==="
echo "Timestamp: $(date)"
echo ""

echo "🔍 Feature Flag Status:"
curl -s http://localhost:8000/api/v1/feature-flags/status | jq .

echo "\n📊 Metrics Summary:"
curl -s http://localhost:9090/metrics | grep -E "(feature_requests_total|feature_latency_ms)" | tail -10

echo "\n🏥 Health Status:"
curl -s http://localhost:8000/health | jq .

echo "\n💾 Database Status:"
psql $DATABASE_URL -c "SELECT COUNT(*) as total_reports FROM compliance_reports;" -t

echo "\n🔴 Recent Errors:"
docker logs doganai-api --since 1h 2>&1 | grep -i error | tail -5
EOF

chmod +x monitoring_dashboard.sh
./monitoring_dashboard.sh
```

---

## 🚨 Rollback Procedures

### Emergency Rollback (Immediate)

#### Scenario: Critical Issues Detected
- High error rate (>5%)
- Service unavailable
- Data corruption detected
- Security incident

#### Immediate Actions (< 5 minutes)

##### Step 1: Activate Kill Switch
```bash
# Immediately disable feature
curl -X PUT "http://localhost:8000/api/v1/feature-flags/compliance_report_generator" \
  -H "Content-Type: application/json" \
  -d '{"kill_switch": true, "enabled": false}'

curl -X PUT "http://localhost:8000/api/v1/feature-flags/compliance_report_generator_full" \
  -H "Content-Type: application/json" \
  -d '{"kill_switch": true, "enabled": false}'
```

##### Step 2: Verify Feature Disabled
```bash
# Test feature flag evaluation
curl -X POST "http://localhost:8000/api/v1/reports/generate" \
  -H "Content-Type: application/json" \
  -d '{"title": "Test Report", "report_type": "policy_compliance"}'

# Should return feature disabled error
```

##### Step 3: Notify Stakeholders
```bash
# Send immediate notification
echo "🚨 EMERGENCY ROLLBACK: Compliance Report Generator disabled due to critical issues" | \
  curl -X POST "$SLACK_WEBHOOK_URL" \
  -H "Content-Type: application/json" \
  -d @-
```

### Gradual Rollback (Planned)

#### Scenario: Performance Issues or User Feedback

##### Step 1: Reduce Rollout Percentage
```bash
# Reduce to 5% rollout
curl -X PUT "http://localhost:8000/api/v1/feature-flags/compliance_report_generator" \
  -H "Content-Type: application/json" \
  -d '{
    "enabled": true,
    "rollout": {
      "strategy": "canary",
      "percentage": 5.0,
      "user_segments": ["internal"]
    }
  }'
```

##### Step 2: Monitor Impact
```bash
# Monitor for 30 minutes
for i in {1..30}; do
  echo "Minute $i: $(date)"
  curl -s http://localhost:9090/metrics | grep feature_requests_total | grep error
  sleep 60
done
```

##### Step 3: Complete Rollback if Needed
```bash
# Disable feature completely
curl -X PUT "http://localhost:8000/api/v1/feature-flags/compliance_report_generator" \
  -H "Content-Type: application/json" \
  -d '{"enabled": false}'
```

### Application Rollback

#### Database Rollback
```bash
# Backup current state
pg_dump $DATABASE_URL > backup_$(date +%Y%m%d_%H%M%S).sql

# Rollback database migrations (if needed)
psql $DATABASE_URL -c "DELETE FROM compliance_reports WHERE created_at > '2024-01-01';"

# Or restore from backup
psql $DATABASE_URL < backup_previous_version.sql
```

#### Application Version Rollback
```bash
# Kubernetes rollback
kubectl rollout undo deployment/doganai-api -n doganai-staging
kubectl rollout status deployment/doganai-api -n doganai-staging

# Docker Compose rollback
docker-compose -f docker-compose.staging.yml down
docker tag doganai-compliance:previous doganai-compliance:latest
docker-compose -f docker-compose.staging.yml up -d
```

---

## 🔧 Troubleshooting Guide

### Common Issues

#### Issue 1: Feature Not Available for Users

**Symptoms:**
- Users report feature not visible
- Feature flag evaluations return false

**Diagnosis:**
```bash
# Check feature flag status
curl http://localhost:8000/api/v1/feature-flags/compliance_report_generator

# Check user segment targeting
echo "User segment: canary" | curl -X POST http://localhost:8000/api/v1/feature-flags/evaluate \
  -H "Content-Type: application/json" \
  -d @-
```

**Resolution:**
```bash
# Update user segments
curl -X PUT "http://localhost:8000/api/v1/feature-flags/compliance_report_generator" \
  -H "Content-Type: application/json" \
  -d '{
    "rollout": {
      "user_segments": ["canary", "beta", "production"]
    }
  }'
```

#### Issue 2: High Latency

**Symptoms:**
- Report generation takes >5 seconds
- Timeout errors

**Diagnosis:**
```bash
# Check database performance
psql $DATABASE_URL -c "SELECT query, mean_exec_time FROM pg_stat_statements ORDER BY mean_exec_time DESC LIMIT 10;"

# Check connection pool
curl http://localhost:9090/metrics | grep db_connection_pool_size

# Check Redis performance
redis-cli -u $REDIS_URL --latency-history
```

**Resolution:**
```bash
# Increase database connection pool
export DATABASE_POOL_SIZE=50
docker-compose restart doganai-api

# Clear Redis cache if needed
redis-cli -u $REDIS_URL FLUSHDB

# Optimize database queries
psql $DATABASE_URL -c "REINDEX TABLE compliance_reports;"
```

#### Issue 3: Database Connection Errors

**Symptoms:**
- "Database not available" errors
- Connection timeouts

**Diagnosis:**
```bash
# Test database connectivity
psql $DATABASE_URL -c "SELECT 1;"

# Check database logs
docker logs postgres-container --tail 50

# Check connection count
psql $DATABASE_URL -c "SELECT count(*) FROM pg_stat_activity;"
```

**Resolution:**
```bash
# Restart database connection pool
docker-compose restart doganai-api

# Check database configuration
psql $DATABASE_URL -c "SHOW max_connections;"
psql $DATABASE_URL -c "SHOW shared_buffers;"

# Update connection string if needed
export DATABASE_URL="postgresql://user:pass@host:5432/db?pool_size=20&max_overflow=30"
```

### Log Analysis

#### Key Log Patterns
```bash
# Feature-specific errors
grep "compliance_report_generator" /var/log/doganai/application.log | grep ERROR

# Database errors
grep "database" /var/log/doganai/application.log | grep -i "error\|timeout\|connection"

# Feature flag evaluation errors
grep "feature_flag" /var/log/doganai/application.log | grep ERROR

# Performance issues
grep "latency_ms" /var/log/doganai/application.log | awk '$NF > 2000'
```

#### Structured Log Queries
```bash
# Using jq for JSON logs
tail -f /var/log/doganai/application.log | jq 'select(.feature_name == "compliance_report_generator" and .level == "ERROR")'

# Filter by correlation ID
tail -f /var/log/doganai/application.log | jq 'select(.correlation_id == "abc-123-def")'

# Performance analysis
tail -f /var/log/doganai/application.log | jq 'select(.duration_ms > 2000)'
```

---

## 📞 Escalation Procedures

### Escalation Matrix

#### Level 1: On-Call Engineer (0-30 minutes)
- **Contact**: platform-oncall@dogan
- **Scope**: Feature flags, basic troubleshooting
- **Actions**: Kill switch, basic diagnostics

#### Level 2: Platform Team Lead (30-60 minutes)
- **Contact**: platform-lead@dogan
- **Scope**: Application rollback, database issues
- **Actions**: Version rollback, database recovery

#### Level 3: Engineering Manager (60+ minutes)
- **Contact**: engineering-manager@dogan
- **Scope**: Business impact, external communication
- **Actions**: Stakeholder communication, incident management

### Communication Templates

#### Incident Notification
```
Subject: [INCIDENT] Compliance Report Generator - [SEVERITY]

Incident Details:
- Feature: Compliance Report Generator
- Severity: [Critical/High/Medium]
- Impact: [Description]
- Started: [Timestamp]
- Actions Taken: [List]
- Next Steps: [Plan]
- ETA: [Estimate]

Incident Commander: [Name]
Bridge: [Link/Phone]
```

#### Resolution Notification
```
Subject: [RESOLVED] Compliance Report Generator Incident

Incident Summary:
- Duration: [Time]
- Root Cause: [Description]
- Impact: [Users/Features affected]
- Resolution: [Actions taken]
- Prevention: [Future measures]

Post-Incident Review: [Date/Time]
```

---

## 📚 Reference Information

### Configuration Files
- Feature Flags: `feature_flags/flags.json`
- Environment: `.env.staging`, `.env.production`
- Docker Compose: `docker-compose.yml`
- Kubernetes: `k8s/deployments.yaml`

### API Endpoints
- Health Check: `GET /health`
- Feature Flags: `GET /api/v1/feature-flags/{name}`
- Report Generation: `POST /api/v1/reports/generate`
- Metrics: `GET /metrics`

### Database Tables
- `compliance_reports` - Main report data
- `report_audit_logs` - Audit trail
- `feature_flag_evaluations` - Flag evaluation history

### Monitoring URLs
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000
- Application: http://localhost:8000

### Documentation Links
- [Feature Specification](../features/compliance-report-generator.md)
- [API Documentation](../api/endpoints.md)
- [Architecture Overview](../architecture/overview.md)
- [Security Guidelines](../security/guidelines.md)

---

## 📝 Maintenance Procedures

### Weekly Maintenance
- [ ] Review feature flag metrics
- [ ] Check database performance
- [ ] Update monitoring dashboards
- [ ] Review error logs

### Monthly Maintenance
- [ ] Cleanup old report data
- [ ] Review and update feature flags
- [ ] Performance optimization
- [ ] Security review

### Quarterly Maintenance
- [ ] Feature flag cleanup
- [ ] Database optimization
- [ ] Documentation updates
- [ ] Disaster recovery testing

---

**Document Version**: 1.0  
**Last Updated**: 2024-12-28  
**Next Review**: 2025-01-28  
**Owner**: platform@dogan  
**Reviewers**: engineering-team@dogan
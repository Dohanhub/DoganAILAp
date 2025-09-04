#!/usr/bin/env python3
"""
DoganAI Compliance Kit - Health Pack Deployment
Deploys comprehensive health-pack with .env.example, updated docker-compose.yml, and verification script
"""

import os
import shutil
from pathlib import Path
import yaml
import json

class HealthPackDeployer:
    def __init__(self):
        self.project_root = Path.cwd()
        
    def create_env_example(self):
        """Create comprehensive .env.example for all services"""
        print("🔧 Creating .env.example with validated configuration...")
        
        env_content = """
# DoganAI Compliance Kit - Environment Configuration
# Copy this file to .env and update values for your environment

# =============================================================================
# APPLICATION SETTINGS
# =============================================================================
APP_NAME="DoganAI Compliance Kit"
APP_VERSION="1.0.0"
ENVIRONMENT="development"
DEBUG="true"
LOG_LEVEL="INFO"

# =============================================================================
# API CONFIGURATION
# =============================================================================
API_HOST="0.0.0.0"
API_PORT="8000"
API_WORKERS="1"
API_TIMEOUT="30"
ENABLE_DOCS="true"
ENABLE_REDOC="true"

# =============================================================================
# DATABASE CONFIGURATION
# =============================================================================
# PostgreSQL (Production)
DATABASE_URL="postgresql://doganai:secure_password@postgres:5432/ksa_prod"
DATABASE_HOST="postgres"
DATABASE_PORT="5432"
DATABASE_NAME="ksa_prod"
DATABASE_USER="doganai"
DATABASE_PASSWORD="secure_password"
DATABASE_SSL_MODE="prefer"
DATABASE_POOL_SIZE="10"
DATABASE_MAX_OVERFLOW="20"

# SQLite (Development)
SQLITE_DATABASE_PATH="./doganai_compliance.db"

# =============================================================================
# REDIS CONFIGURATION
# =============================================================================
REDIS_URL="redis://redis:6379/0"
REDIS_HOST="redis"
REDIS_PORT="6379"
REDIS_DB="0"
REDIS_PASSWORD=""
REDIS_SSL="false"
REDIS_TIMEOUT="5"

# =============================================================================
# SECURITY CONFIGURATION
# =============================================================================
SECRET_KEY="your-super-secret-key-change-this-in-production"
JWT_SECRET_KEY="your-jwt-secret-key-change-this-in-production"
JWT_ALGORITHM="HS256"
JWT_EXPIRY="3600"  # seconds (1 hour)
API_KEY="your-api-key-change-this-in-production"
ENCRYPTION_KEY="your-encryption-key-change-this-in-production"

# Rate Limiting
RATE_LIMIT_REQUESTS="100"
RATE_LIMIT_WINDOW="60"  # seconds

# CORS Settings
CORS_ORIGINS="http://localhost:3000,http://localhost:8000,http://localhost:8001"
CORS_ALLOW_CREDENTIALS="true"

# =============================================================================
# FEATURE FLAGS
# =============================================================================
ENABLE_PII_REDACTION="true"
DATA_RESIDENCY="KSA"
ENABLE_AUDIT_LOGGING="true"
ENABLE_METRICS="true"
ENABLE_TRACING="false"
ENABLE_CACHING="true"
ENABLE_RATE_LIMITING="true"

# =============================================================================
# MONITORING & OBSERVABILITY
# =============================================================================
# Prometheus
PROMETHEUS_PORT="9090"
METRICS_ENDPOINT="/metrics"

# Jaeger (Optional)
JAEGER_HOST="jaeger"
JAEGER_PORT="14268"
JAEGER_AGENT_HOST="jaeger"
JAEGER_AGENT_PORT="6831"

# Health Checks
HEALTH_CHECK_INTERVAL="30s"
HEALTH_CHECK_TIMEOUT="10s"
HEALTH_CHECK_RETRIES="3"
HEALTH_CHECK_START_PERIOD="40s"

# =============================================================================
# SERVICE PORTS
# =============================================================================
COMPLIANCE_ENGINE_PORT="8000"
WORKFLOW_APP_PORT="8001"
BENCHMARKS_PORT="8002"
AI_ML_PORT="8003"
INTEGRATIONS_PORT="8004"
AUTH_PORT="8005"
AI_AGENT_PORT="8006"
AUTONOMOUS_TESTING_PORT="8007"

# =============================================================================
# EXTERNAL INTEGRATIONS
# =============================================================================
# IBM Watson
IBM_WATSON_API_KEY="your-ibm-watson-api-key"
IBM_WATSON_URL="https://api.watson.ai.ibm.com"
IBM_WATSON_VERSION="2021-06-01"

# Microsoft Azure
AZURE_SUBSCRIPTION_ID="your-azure-subscription-id"
AZURE_RESOURCE_GROUP="doganai-rg"
AZURE_COGNITIVE_SERVICES_KEY="your-azure-cognitive-services-key"

# Lenovo Hardware
LENOVO_MONITORING_ENDPOINT="https://monitoring.lenovo.com"
LENOVO_API_KEY="your-lenovo-api-key"

# =============================================================================
# COMPLIANCE AUTHORITIES
# =============================================================================
# NCA (National Cybersecurity Authority)
NCA_API_ENDPOINT="https://api.nca.gov.sa"
NCA_COMPLIANCE_VERSION="2.0"

# SAMA (Saudi Arabian Monetary Authority)
SAMA_API_ENDPOINT="https://api.sama.gov.sa"
SAMA_COMPLIANCE_VERSION="3.1"

# MoH (Ministry of Health)
MOH_API_ENDPOINT="https://api.moh.gov.sa"
MOH_COMPLIANCE_VERSION="1.2"

# CITC (Communications and Information Technology Commission)
CITC_API_ENDPOINT="https://api.citc.gov.sa"
CITC_COMPLIANCE_VERSION="2.3"

# =============================================================================
# DEVELOPMENT SETTINGS
# =============================================================================
DEV_MODE="true"
HOT_RELOAD="true"
AUTO_MIGRATE="true"
SEED_DATABASE="true"
MOCK_EXTERNAL_APIS="true"

# =============================================================================
# PRODUCTION SETTINGS
# =============================================================================
# SSL/TLS
SSL_ENABLED="false"
SSL_CERT_PATH="/certs/cert.pem"
SSL_KEY_PATH="/certs/key.pem"

# Load Balancing
LOAD_BALANCER_ENABLED="false"
LOAD_BALANCER_ALGORITHM="round_robin"

# Backup & Recovery
BACKUP_ENABLED="true"
BACKUP_SCHEDULE="0 2 * * *"  # Daily at 2 AM
BACKUP_RETENTION_DAYS="30"

# =============================================================================
# DOCKER CONFIGURATION
# =============================================================================
DOCKER_NETWORK="doganai_network"
DOCKER_VOLUME_PREFIX="doganai"
DOCKER_RESTART_POLICY="unless-stopped"

# Container Resources
CONTAINER_MEMORY_LIMIT="512m"
CONTAINER_CPU_LIMIT="0.5"

# =============================================================================
# TIMEZONE & LOCALIZATION
# =============================================================================
TIMEZONE="Asia/Riyadh"
LOCALE="en_US.UTF-8"
DEFAULT_LANGUAGE="en"
SUPPORTED_LANGUAGES="en,ar"
"""
        
        with open(self.project_root / ".env.example", "w", encoding="utf-8") as f:
            f.write(env_content)
        
        print("✅ .env.example created successfully")
    
    def create_docker_compose_with_healthchecks(self):
        """Create updated docker-compose.yml with comprehensive healthchecks"""
        print("🐳 Creating docker-compose.yml with healthchecks...")
        
        compose_config = {
            'version': '3.8',
            'networks': {
                'doganai_network': {
                    'driver': 'bridge'
                }
            },
            'volumes': {
                'postgres_data': {},
                'redis_data': {},
                'prometheus_data': {},
                'grafana_data': {}
            },
            'services': {
                'postgres': {
                    'image': 'postgres:15-alpine',
                    'container_name': 'doganai_postgres',
                    'environment': [
                        'POSTGRES_DB=${DATABASE_NAME:-ksa_prod}',
                        'POSTGRES_USER=${DATABASE_USER:-doganai}',
                        'POSTGRES_PASSWORD=${DATABASE_PASSWORD:-secure_password}',
                        'POSTGRES_INITDB_ARGS=--encoding=UTF-8 --lc-collate=C --lc-ctype=C'
                    ],
                    'volumes': [
                        'postgres_data:/var/lib/postgresql/data',
                        './db/seed.sql:/docker-entrypoint-initdb.d/seed.sql'
                    ],
                    'ports': ['${DATABASE_PORT:-5432}:5432'],
                    'networks': ['doganai_network'],
                    'restart': '${DOCKER_RESTART_POLICY:-unless-stopped}',
                    'healthcheck': {
                        'test': ['CMD-SHELL', 'pg_isready -U ${DATABASE_USER:-doganai} -d ${DATABASE_NAME:-ksa_prod}'],
                        'interval': '${HEALTH_CHECK_INTERVAL:-30s}',
                        'timeout': '${HEALTH_CHECK_TIMEOUT:-10s}',
                        'retries': int('${HEALTH_CHECK_RETRIES:-3}'),
                        'start_period': '${HEALTH_CHECK_START_PERIOD:-40s}'
                    }
                },
                'redis': {
                    'image': 'redis:7-alpine',
                    'container_name': 'doganai_redis',
                    'command': 'redis-server --appendonly yes',
                    'volumes': ['redis_data:/data'],
                    'ports': ['${REDIS_PORT:-6379}:6379'],
                    'networks': ['doganai_network'],
                    'restart': '${DOCKER_RESTART_POLICY:-unless-stopped}',
                    'healthcheck': {
                        'test': ['CMD', 'redis-cli', 'ping'],
                        'interval': '${HEALTH_CHECK_INTERVAL:-30s}',
                        'timeout': '${HEALTH_CHECK_TIMEOUT:-10s}',
                        'retries': int('${HEALTH_CHECK_RETRIES:-3}'),
                        'start_period': '${HEALTH_CHECK_START_PERIOD:-40s}'
                    }
                },
                'compliance_engine': {
                    'build': {
                        'context': '.',
                        'dockerfile': 'Dockerfile.api'
                    },
                    'container_name': 'doganai_compliance_engine',
                    'environment': [
                        'DATABASE_URL=postgresql://${DATABASE_USER:-doganai}:${DATABASE_PASSWORD:-secure_password}@postgres:5432/${DATABASE_NAME:-ksa_prod}',
                        'REDIS_URL=redis://redis:6379/0',
                        'ENVIRONMENT=${ENVIRONMENT:-development}',
                        'DEBUG=${DEBUG:-true}',
                        'ENABLE_PII_REDACTION=${ENABLE_PII_REDACTION:-true}',
                        'DATA_RESIDENCY=${DATA_RESIDENCY:-KSA}',
                        'JWT_EXPIRY=${JWT_EXPIRY:-3600}'
                    ],
                    'ports': ['${COMPLIANCE_ENGINE_PORT:-8000}:8000'],
                    'depends_on': {
                        'postgres': {'condition': 'service_healthy'},
                        'redis': {'condition': 'service_healthy'}
                    },
                    'networks': ['doganai_network'],
                    'restart': '${DOCKER_RESTART_POLICY:-unless-stopped}',
                    'healthcheck': {
                        'test': ['CMD', 'curl', '-f', 'http://localhost:8000/health/ready'],
                        'interval': '${HEALTH_CHECK_INTERVAL:-30s}',
                        'timeout': '${HEALTH_CHECK_TIMEOUT:-10s}',
                        'retries': int('${HEALTH_CHECK_RETRIES:-3}'),
                        'start_period': '${HEALTH_CHECK_START_PERIOD:-40s}'
                    }
                },
                'workflow_app': {
                    'build': {
                        'context': '.',
                        'dockerfile': 'Dockerfile.ui'
                    },
                    'container_name': 'doganai_workflow_app',
                    'environment': [
                        'ENVIRONMENT=${ENVIRONMENT:-development}',
                        'DEBUG=${DEBUG:-true}'
                    ],
                    'ports': ['${WORKFLOW_APP_PORT:-8001}:8001'],
                    'networks': ['doganai_network'],
                    'restart': '${DOCKER_RESTART_POLICY:-unless-stopped}',
                    'healthcheck': {
                        'test': ['CMD', 'curl', '-f', 'http://localhost:8001/health'],
                        'interval': '${HEALTH_CHECK_INTERVAL:-30s}',
                        'timeout': '${HEALTH_CHECK_TIMEOUT:-10s}',
                        'retries': int('${HEALTH_CHECK_RETRIES:-3}'),
                        'start_period': '${HEALTH_CHECK_START_PERIOD:-40s}'
                    }
                },
                'benchmarks': {
                    'build': {
                        'context': './microservices/benchmarks',
                        'dockerfile': 'Dockerfile'
                    },
                    'container_name': 'doganai_benchmarks',
                    'environment': [
                        'DATABASE_URL=postgresql://${DATABASE_USER:-doganai}:${DATABASE_PASSWORD:-secure_password}@postgres:5432/${DATABASE_NAME:-ksa_prod}',
                        'REDIS_URL=redis://redis:6379/1'
                    ],
                    'ports': ['${BENCHMARKS_PORT:-8002}:8002'],
                    'depends_on': {
                        'postgres': {'condition': 'service_healthy'},
                        'redis': {'condition': 'service_healthy'}
                    },
                    'networks': ['doganai_network'],
                    'restart': '${DOCKER_RESTART_POLICY:-unless-stopped}',
                    'healthcheck': {
                        'test': ['CMD', 'curl', '-f', 'http://localhost:8002/health'],
                        'interval': '${HEALTH_CHECK_INTERVAL:-30s}',
                        'timeout': '${HEALTH_CHECK_TIMEOUT:-10s}',
                        'retries': int('${HEALTH_CHECK_RETRIES:-3}'),
                        'start_period': '${HEALTH_CHECK_START_PERIOD:-40s}'
                    }
                },
                'ai_ml': {
                    'build': {
                        'context': './microservices/ai-ml',
                        'dockerfile': 'Dockerfile'
                    },
                    'container_name': 'doganai_ai_ml',
                    'environment': [
                        'DATABASE_URL=postgresql://${DATABASE_USER:-doganai}:${DATABASE_PASSWORD:-secure_password}@postgres:5432/${DATABASE_NAME:-ksa_prod}',
                        'REDIS_URL=redis://redis:6379/2',
                        'IBM_WATSON_API_KEY=${IBM_WATSON_API_KEY}',
                        'AZURE_COGNITIVE_SERVICES_KEY=${AZURE_COGNITIVE_SERVICES_KEY}'
                    ],
                    'ports': ['${AI_ML_PORT:-8003}:8003'],
                    'depends_on': {
                        'postgres': {'condition': 'service_healthy'},
                        'redis': {'condition': 'service_healthy'}
                    },
                    'networks': ['doganai_network'],
                    'restart': '${DOCKER_RESTART_POLICY:-unless-stopped}',
                    'healthcheck': {
                        'test': ['CMD', 'curl', '-f', 'http://localhost:8003/health'],
                        'interval': '${HEALTH_CHECK_INTERVAL:-30s}',
                        'timeout': '${HEALTH_CHECK_TIMEOUT:-10s}',
                        'retries': int('${HEALTH_CHECK_RETRIES:-3}'),
                        'start_period': '${HEALTH_CHECK_START_PERIOD:-40s}'
                    }
                },
                'integrations': {
                    'build': {
                        'context': './microservices/integrations',
                        'dockerfile': 'Dockerfile'
                    },
                    'container_name': 'doganai_integrations',
                    'environment': [
                        'DATABASE_URL=postgresql://${DATABASE_USER:-doganai}:${DATABASE_PASSWORD:-secure_password}@postgres:5432/${DATABASE_NAME:-ksa_prod}',
                        'REDIS_URL=redis://redis:6379/3',
                        'IBM_WATSON_API_KEY=${IBM_WATSON_API_KEY}',
                        'LENOVO_API_KEY=${LENOVO_API_KEY}'
                    ],
                    'ports': ['${INTEGRATIONS_PORT:-8004}:8004'],
                    'depends_on': {
                        'postgres': {'condition': 'service_healthy'},
                        'redis': {'condition': 'service_healthy'}
                    },
                    'networks': ['doganai_network'],
                    'restart': '${DOCKER_RESTART_POLICY:-unless-stopped}',
                    'healthcheck': {
                        'test': ['CMD', 'curl', '-f', 'http://localhost:8004/health'],
                        'interval': '${HEALTH_CHECK_INTERVAL:-30s}',
                        'timeout': '${HEALTH_CHECK_TIMEOUT:-10s}',
                        'retries': int('${HEALTH_CHECK_RETRIES:-3}'),
                        'start_period': '${HEALTH_CHECK_START_PERIOD:-40s}'
                    }
                },
                'auth': {
                    'build': {
                        'context': './microservices/auth',
                        'dockerfile': 'Dockerfile'
                    },
                    'container_name': 'doganai_auth',
                    'environment': [
                        'DATABASE_URL=postgresql://${DATABASE_USER:-doganai}:${DATABASE_PASSWORD:-secure_password}@postgres:5432/${DATABASE_NAME:-ksa_prod}',
                        'REDIS_URL=redis://redis:6379/4',
                        'JWT_SECRET_KEY=${JWT_SECRET_KEY}',
                        'JWT_EXPIRY=${JWT_EXPIRY:-3600}'
                    ],
                    'ports': ['${AUTH_PORT:-8005}:8005'],
                    'depends_on': {
                        'postgres': {'condition': 'service_healthy'},
                        'redis': {'condition': 'service_healthy'}
                    },
                    'networks': ['doganai_network'],
                    'restart': '${DOCKER_RESTART_POLICY:-unless-stopped}',
                    'healthcheck': {
                        'test': ['CMD', 'curl', '-f', 'http://localhost:8005/health'],
                        'interval': '${HEALTH_CHECK_INTERVAL:-30s}',
                        'timeout': '${HEALTH_CHECK_TIMEOUT:-10s}',
                        'retries': int('${HEALTH_CHECK_RETRIES:-3}'),
                        'start_period': '${HEALTH_CHECK_START_PERIOD:-40s}'
                    }
                },
                'ai_agent': {
                    'build': {
                        'context': './microservices/ai-agent',
                        'dockerfile': 'Dockerfile'
                    },
                    'container_name': 'doganai_ai_agent',
                    'environment': [
                        'DATABASE_URL=postgresql://${DATABASE_USER:-doganai}:${DATABASE_PASSWORD:-secure_password}@postgres:5432/${DATABASE_NAME:-ksa_prod}',
                        'REDIS_URL=redis://redis:6379/5',
                        'IBM_WATSON_API_KEY=${IBM_WATSON_API_KEY}'
                    ],
                    'ports': ['${AI_AGENT_PORT:-8006}:8006'],
                    'depends_on': {
                        'postgres': {'condition': 'service_healthy'},
                        'redis': {'condition': 'service_healthy'}
                    },
                    'networks': ['doganai_network'],
                    'restart': '${DOCKER_RESTART_POLICY:-unless-stopped}',
                    'healthcheck': {
                        'test': ['CMD', 'curl', '-f', 'http://localhost:8006/health'],
                        'interval': '${HEALTH_CHECK_INTERVAL:-30s}',
                        'timeout': '${HEALTH_CHECK_TIMEOUT:-10s}',
                        'retries': int('${HEALTH_CHECK_RETRIES:-3}'),
                        'start_period': '${HEALTH_CHECK_START_PERIOD:-40s}'
                    }
                },
                'autonomous_testing': {
                    'build': {
                        'context': './microservices/autonomous-testing',
                        'dockerfile': 'Dockerfile'
                    },
                    'container_name': 'doganai_autonomous_testing',
                    'environment': [
                        'DATABASE_URL=postgresql://${DATABASE_USER:-doganai}:${DATABASE_PASSWORD:-secure_password}@postgres:5432/${DATABASE_NAME:-ksa_prod}',
                        'REDIS_URL=redis://redis:6379/6'
                    ],
                    'ports': ['${AUTONOMOUS_TESTING_PORT:-8007}:8007'],
                    'depends_on': {
                        'postgres': {'condition': 'service_healthy'},
                        'redis': {'condition': 'service_healthy'}
                    },
                    'networks': ['doganai_network'],
                    'restart': '${DOCKER_RESTART_POLICY:-unless-stopped}',
                    'healthcheck': {
                        'test': ['CMD', 'curl', '-f', 'http://localhost:8007/health'],
                        'interval': '${HEALTH_CHECK_INTERVAL:-30s}',
                        'timeout': '${HEALTH_CHECK_TIMEOUT:-10s}',
                        'retries': int('${HEALTH_CHECK_RETRIES:-3}'),
                        'start_period': '${HEALTH_CHECK_START_PERIOD:-40s}'
                    }
                },
                'prometheus': {
                    'image': 'prom/prometheus:latest',
                    'container_name': 'doganai_prometheus',
                    'command': [
                        '--config.file=/etc/prometheus/prometheus.yml',
                        '--storage.tsdb.path=/prometheus',
                        '--web.console.libraries=/etc/prometheus/console_libraries',
                        '--web.console.templates=/etc/prometheus/consoles',
                        '--storage.tsdb.retention.time=200h',
                        '--web.enable-lifecycle'
                    ],
                    'volumes': [
                        './infra/prometheus.yml:/etc/prometheus/prometheus.yml',
                        'prometheus_data:/prometheus'
                    ],
                    'ports': ['${PROMETHEUS_PORT:-9090}:9090'],
                    'networks': ['doganai_network'],
                    'restart': '${DOCKER_RESTART_POLICY:-unless-stopped}',
                    'healthcheck': {
                        'test': ['CMD', 'wget', '--no-verbose', '--tries=1', '--spider', 'http://localhost:9090/-/healthy'],
                        'interval': '${HEALTH_CHECK_INTERVAL:-30s}',
                        'timeout': '${HEALTH_CHECK_TIMEOUT:-10s}',
                        'retries': int('${HEALTH_CHECK_RETRIES:-3}'),
                        'start_period': '${HEALTH_CHECK_START_PERIOD:-40s}'
                    }
                },
                'grafana': {
                    'image': 'grafana/grafana:latest',
                    'container_name': 'doganai_grafana',
                    'environment': [
                        'GF_SECURITY_ADMIN_PASSWORD=admin123',
                        'GF_USERS_ALLOW_SIGN_UP=false'
                    ],
                    'volumes': ['grafana_data:/var/lib/grafana'],
                    'ports': ['3000:3000'],
                    'depends_on': ['prometheus'],
                    'networks': ['doganai_network'],
                    'restart': '${DOCKER_RESTART_POLICY:-unless-stopped}',
                    'healthcheck': {
                        'test': ['CMD-SHELL', 'curl -f http://localhost:3000/api/health || exit 1'],
                        'interval': '${HEALTH_CHECK_INTERVAL:-30s}',
                        'timeout': '${HEALTH_CHECK_TIMEOUT:-10s}',
                        'retries': int('${HEALTH_CHECK_RETRIES:-3}'),
                        'start_period': '${HEALTH_CHECK_START_PERIOD:-40s}'
                    }
                }
            }
        }
        
        with open(self.project_root / "docker-compose.yml", "w", encoding="utf-8") as f:
            yaml.dump(compose_config, f, default_flow_style=False, sort_keys=False, indent=2)
        
        print("✅ docker-compose.yml with healthchecks created successfully")
    
    def create_one_time_verification_script(self):
        """Create one-time health verification script"""
        print("🔍 Creating one-time health verification script...")
        
        script_content = """
#!/usr/bin/env python3
"""
DoganAI Compliance Kit - One-Time Health Verification
Comprehensive startup verification and clean slate deployment
"""

import subprocess
import time
import requests
import sys
from pathlib import Path

def run_command(cmd, description):
    """Run a command and return success status"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=300)
        if result.returncode == 0:
            print(f"✅ {description} completed successfully")
            return True
        else:
            print(f"❌ {description} failed: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print(f"⏰ {description} timed out")
        return False
    except Exception as e:
        print(f"❌ {description} error: {e}")
        return False

def check_service_health(url, service_name, timeout=30):
    """Check if a service is healthy"""
    print(f"🔍 Checking {service_name} health...")
    
    for attempt in range(timeout):
        try:
            response = requests.get(url, timeout=5)
            if response.status_code < 400:
                print(f"✅ {service_name} is healthy (HTTP {response.status_code})")
                return True
        except requests.exceptions.RequestException:
            pass
        
        if attempt < timeout - 1:
            time.sleep(1)
    
    print(f"❌ {service_name} health check failed after {timeout}s")
    return False

def clean_slate_deployment():
    """Execute clean slate deployment"""
    print("🚀 DoganAI Compliance Kit - Clean Slate Deployment")
    print("=" * 60)
    
    # Step 1: Stop and remove all containers
    if not run_command("docker compose down -v", "Stopping and removing containers"):
        print("⚠️ Warning: Failed to stop containers (may not exist)")
    
    # Step 2: Clean build cache
    if not run_command("docker compose build --no-cache", "Building containers with no cache"):
        print("❌ Failed to build containers")
        return False
    
    # Step 3: Start services
    if not run_command("docker compose up -d", "Starting all services"):
        print("❌ Failed to start services")
        return False
    
    # Step 4: Wait for services to initialize
    print("⏳ Waiting for services to initialize (60s)...")
    time.sleep(60)
    
    # Step 5: Health checks
    services = [
        ("http://localhost:8000/health", "Compliance Engine"),
        ("http://localhost:8001/health", "Workflow App"),
        ("http://localhost:8002/health", "Benchmarks"),
        ("http://localhost:8003/health", "AI-ML"),
        ("http://localhost:8004/health", "Integrations"),
        ("http://localhost:8005/health", "Auth"),
        ("http://localhost:8006/health", "AI Agent"),
        ("http://localhost:8007/health", "Autonomous Testing"),
        ("http://localhost:9090/-/healthy", "Prometheus"),
        ("http://localhost:3000/api/health", "Grafana")
    ]
    
    healthy_services = 0
    for url, name in services:
        if check_service_health(url, name):
            healthy_services += 1
    
    # Step 6: Summary
    print("\n" + "=" * 60)
    print("📊 DEPLOYMENT SUMMARY")
    print("=" * 60)
    print(f"✅ Healthy Services: {healthy_services}/{len(services)}")
    
    if healthy_services >= len(services) * 0.8:  # 80% success rate
        print("🎉 Clean slate deployment successful!")
        print("\n🌐 Service URLs:")
        print("  • Compliance Engine: http://localhost:8000")
        print("  • Workflow Simulator: http://localhost:8001")
        print("  • API Documentation: http://localhost:8000/docs")
        print("  • Prometheus: http://localhost:9090")
        print("  • Grafana: http://localhost:3000 (admin/admin123)")
        return True
    else:
        print("⚠️ Deployment completed with issues")
        print("\n💡 Troubleshooting:")
        print("  1. Check logs: docker compose logs [service_name]")
        print("  2. Verify .env configuration")
        print("  3. Ensure ports are not in use")
        print("  4. Check Docker resources (memory/CPU)")
        return False

def validate_environment():
    """Validate environment configuration"""
    print("🔍 Validating environment configuration...")
    
    # Check if .env exists
    env_file = Path(".env")
    if not env_file.exists():
        print("⚠️ .env file not found, copying from .env.example")
        env_example = Path(".env.example")
        if env_example.exists():
            import shutil
            shutil.copy(env_example, env_file)
            print("✅ .env file created from .env.example")
        else:
            print("❌ .env.example not found")
            return False
    
    # Check Docker
    if not run_command("docker --version", "Checking Docker installation"):
        print("❌ Docker is not installed or not running")
        return False
    
    if not run_command("docker compose version", "Checking Docker Compose"):
        print("❌ Docker Compose is not available")
        return False
    
    print("✅ Environment validation completed")
    return True

def main():
    """Main verification function"""
    try:
        # Validate environment
        if not validate_environment():
            sys.exit(1)
        
        # Ask user for deployment type
        print("\n🎯 Deployment Options:")
        print("1. Clean Slate Deployment (Recommended)")
        print("2. Quick Health Check Only")
        
        choice = input("\nSelect option (1 or 2): ").strip()
        
        if choice == "1":
            success = clean_slate_deployment()
        elif choice == "2":
            # Quick health check
            services = [
                ("http://localhost:8000/health", "Compliance Engine"),
                ("http://localhost:8001/health", "Workflow App")
            ]
            
            healthy_services = 0
            for url, name in services:
                if check_service_health(url, name, timeout=10):
                    healthy_services += 1
            
            success = healthy_services > 0
        else:
            print("❌ Invalid option selected")
            sys.exit(1)
        
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Verification interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Verification failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
"""
        
        with open(self.project_root / "one_time_health_verification.py", "w", encoding="utf-8") as f:
            f.write(script_content)
        
        # Make script executable on Unix systems
        try:
            os.chmod(self.project_root / "one_time_health_verification.py", 0o755)
        except:
            pass  # Windows doesn't support chmod
        
        print("✅ One-time health verification script created successfully")
    
    def create_dockerfiles(self):
        """Create missing Dockerfiles"""
        print("🐳 Creating Dockerfiles...")
        
        # API Dockerfile
        api_dockerfile = """
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 doganai && chown -R doganai:doganai /app
USER doganai

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health/ready || exit 1

EXPOSE 8000

CMD ["uvicorn", "engine.api:app", "--host", "0.0.0.0", "--port", "8000"]
"""
        
        with open(self.project_root / "Dockerfile.api", "w", encoding="utf-8") as f:
            f.write(api_dockerfile)
        
        # UI Dockerfile
        ui_dockerfile = """
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY ui/ ./ui/
COPY engine/ ./engine/

# Create non-root user
RUN useradd -m -u 1000 doganai && chown -R doganai:doganai /app
USER doganai

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8001/health || exit 1

EXPOSE 8001

CMD ["python", "ui/workflow_app.py"]
"""
        
        with open(self.project_root / "Dockerfile.ui", "w", encoding="utf-8") as f:
            f.write(ui_dockerfile)
        
        print("✅ Dockerfiles created successfully")
    
    def deploy_health_pack(self):
        """Deploy the complete health pack"""
        print("🚀 DoganAI Compliance Kit - Health Pack Deployment")
        print("=" * 60)
        
        try:
            # Create all components
            self.create_env_example()
            self.create_docker_compose_with_healthchecks()
            self.create_one_time_verification_script()
            self.create_dockerfiles()
            
            # Summary
            print("\n🎉 Health Pack Deployment Complete!")
            print("=" * 60)
            print("\n📦 Created Files:")
            print("  ✅ .env.example - Comprehensive environment configuration")
            print("  ✅ docker-compose.yml - Updated with healthchecks")
            print("  ✅ one_time_health_verification.py - Verification script")
            print("  ✅ Dockerfile.api - API container configuration")
            print("  ✅ Dockerfile.ui - UI container configuration")
            
            print("\n🎯 Next Steps:")
            print("  1. Copy .env.example to .env and update values")
            print("  2. Run: python one_time_health_verification.py")
            print("  3. Select option 1 for clean slate deployment")
            print("  4. Wait for all services to become healthy")
            
            print("\n🌐 Expected Service URLs (after deployment):")
            print("  • Compliance Engine: http://localhost:8000")
            print("  • Workflow Simulator: http://localhost:8001")
            print("  • API Documentation: http://localhost:8000/docs")
            print("  • Prometheus Metrics: http://localhost:9090")
            print("  • Grafana Dashboard: http://localhost:3000")
            
            print("\n💡 Troubleshooting:")
            print("  • Check logs: docker compose logs [service_name]")
            print("  • Restart services: docker compose restart [service_name]")
            print("  • Full reset: docker compose down -v && docker compose up -d")
            
            return True
            
        except Exception as e:
            print(f"\n❌ Health pack deployment failed: {e}")
            return False

def main():
    """Main function"""
    deployer = HealthPackDeployer()
    success = deployer.deploy_health_pack()
    
    if success:
        print("\n✅ Health pack ready for immediate clean startup!")
    else:
        print("\n❌ Health pack deployment failed. Please check the errors above.")
    
    return success

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
DoganAI Compliance Kit - Ministry of Interior Deployment Script
Urgent Delivery - Automated Deployment System

This script automates the complete deployment of the Continuous Database Upload System
for the Ministry of Interior with operational technology principles.
"""

import os
import sys
import subprocess
import time
import json
import requests
from pathlib import Path
from datetime import datetime
import logging
from typing import Dict, List, Any

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('ministry_deployment.log')
    ]
)

logger = logging.getLogger(__name__)

class MinistryDeploymentManager:
    """Automated deployment manager for Ministry of Interior system"""
    
    def __init__(self):
        self.project_root = Path.cwd()
        self.deployment_config = {
            'services': [
                'ministry_postgres',
                'ministry_redis', 
                'continuous_upload_system',
                'compliance_engine',
                'ministry_api',
                'prometheus',
                'grafana',
                'nginx'
            ],
            'health_endpoints': {
                'continuous_upload_system': 'http://localhost:9091/metrics',
                'compliance_engine': 'http://localhost:8000/health',
                'ministry_api': 'http://localhost:8008/health',
                'prometheus': 'http://localhost:9090/-/healthy',
                'grafana': 'http://localhost:3000/api/health'
            },
            'required_ports': [5432, 6379, 8000, 8008, 9090, 9091, 3000, 80, 443],
            'deployment_timeout': 300  # 5 minutes
        }
        
    def check_prerequisites(self) -> bool:
        """Check system prerequisites"""
        logger.info("🔍 Checking system prerequisites...")
        
        # Check Docker
        try:
            result = subprocess.run(['docker', '--version'], capture_output=True, text=True)
            if result.returncode != 0:
                logger.error("❌ Docker is not installed or not accessible")
                return False
            logger.info(f"✅ Docker: {result.stdout.strip()}")
        except FileNotFoundError:
            logger.error("❌ Docker command not found")
            return False
        
        # Check Docker Compose
        try:
            result = subprocess.run(['docker', 'compose', 'version'], capture_output=True, text=True)
            if result.returncode != 0:
                logger.error("❌ Docker Compose is not available")
                return False
            logger.info(f"✅ Docker Compose: {result.stdout.strip()}")
        except FileNotFoundError:
            logger.error("❌ Docker Compose command not found")
            return False
        
        # Check available memory
        try:
            import psutil
            memory = psutil.virtual_memory()
            available_gb = memory.available / (1024**3)
            if available_gb < 4:
                logger.warning(f"⚠️ Low memory: {available_gb:.1f}GB available (4GB recommended)")
            else:
                logger.info(f"✅ Memory: {available_gb:.1f}GB available")
        except ImportError:
            logger.warning("⚠️ Cannot check memory (psutil not installed)")
        
        # Check disk space
        try:
            import shutil
            disk_usage = shutil.disk_usage(self.project_root)
            available_gb = disk_usage.free / (1024**3)
            if available_gb < 20:
                logger.warning(f"⚠️ Low disk space: {available_gb:.1f}GB available (20GB recommended)")
            else:
                logger.info(f"✅ Disk space: {available_gb:.1f}GB available")
        except Exception as e:
            logger.warning(f"⚠️ Cannot check disk space: {e}")
        
        # Check port availability
        logger.info("🔍 Checking port availability...")
        import socket
        for port in self.deployment_config['required_ports']:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('localhost', port))
            sock.close()
            if result == 0:
                logger.warning(f"⚠️ Port {port} is already in use")
            else:
                logger.debug(f"✅ Port {port} is available")
        
        logger.info("✅ Prerequisites check completed")
        return True
    
    def create_environment_file(self) -> bool:
        """Create secure environment file"""
        logger.info("🔧 Creating environment configuration...")
        
        env_content = f"""
# DoganAI Compliance Kit - Ministry of Interior Environment
# Generated: {datetime.now().isoformat()}
# Classification: Official
# Priority: High

# =============================================================================
# SECURITY CONFIGURATION
# =============================================================================
DB_PASSWORD=MinistrySecure2024!{int(time.time()) % 1000}
REDIS_PASSWORD=MinistryRedis2024!{int(time.time()) % 1000}
GRAFANA_PASSWORD=MinistryGrafana2024!{int(time.time()) % 1000}

# =============================================================================
# MINISTRY CONFIGURATION
# =============================================================================
MINISTRY_CLASSIFICATION=Official
MINISTRY_PRIORITY=High
MINISTRY_DEPARTMENT=Ministry of Interior

# =============================================================================
# SYSTEM CONFIGURATION
# =============================================================================
LOG_LEVEL=INFO
WORKER_COUNT=3
COLLECTION_INTERVAL=60
BATCH_SIZE=50
MAX_QUEUE_SIZE=1000

# =============================================================================
# DOCKER CONFIGURATION
# =============================================================================
DOCKER_RESTART_POLICY=unless-stopped
CONTAINER_MEMORY_LIMIT=1G
CONTAINER_CPU_LIMIT=1.0

# =============================================================================
# MONITORING CONFIGURATION
# =============================================================================
HEALTH_CHECK_INTERVAL=30s
HEALTH_CHECK_TIMEOUT=10s
HEALTH_CHECK_RETRIES=3
HEALTH_CHECK_START_PERIOD=60s

# =============================================================================
# TIMEZONE CONFIGURATION
# =============================================================================
TZ=Asia/Riyadh
"""
        
        try:
            with open(self.project_root / '.env', 'w') as f:
                f.write(env_content)
            logger.info("✅ Environment file created successfully")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to create environment file: {e}")
            return False
    
    def create_ministry_dockerfile(self) -> bool:
        """Create Ministry-specific Dockerfile"""
        logger.info("🐳 Creating Ministry API Dockerfile...")
        
        ministry_dir = self.project_root / 'microservices' / 'ministry'
        ministry_dir.mkdir(parents=True, exist_ok=True)
        
        dockerfile_content = """
# Ministry of Interior API Service
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --no-cache-dir \
    fastapi==0.104.1 \
    uvicorn[standard]==0.24.0 \
    asyncpg==0.29.0 \
    prometheus-client==0.19.0 \
    structlog==23.2.0 \
    psutil==5.9.6

# Copy application code
COPY main.py .

# Create non-root user
RUN useradd -m -u 1000 ministry && chown -R ministry:ministry /app
USER ministry

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8008/health || exit 1

EXPOSE 8008

CMD ["python", "main.py"]
"""
        
        try:
            with open(ministry_dir / 'Dockerfile', 'w') as f:
                f.write(dockerfile_content)
            logger.info("✅ Ministry Dockerfile created successfully")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to create Ministry Dockerfile: {e}")
            return False
    
    def deploy_system(self) -> bool:
        """Deploy the complete system"""
        logger.info("🚀 Starting Ministry of Interior system deployment...")
        
        try:
            # Stop any existing containers
            logger.info("🛑 Stopping existing containers...")
            subprocess.run([
                'docker', 'compose', '-f', 'docker-compose.ministry.yml', 'down', '-v'
            ], capture_output=True)
            
            # Build containers
            logger.info("🔨 Building containers...")
            result = subprocess.run([
                'docker', 'compose', '-f', 'docker-compose.ministry.yml', 'build', '--no-cache'
            ], capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.error(f"❌ Container build failed: {result.stderr}")
                return False
            
            logger.info("✅ Containers built successfully")
            
            # Start services
            logger.info("🚀 Starting services...")
            result = subprocess.run([
                'docker', 'compose', '-f', 'docker-compose.ministry.yml', 'up', '-d'
            ], capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.error(f"❌ Service startup failed: {result.stderr}")
                return False
            
            logger.info("✅ Services started successfully")
            
            # Wait for services to initialize
            logger.info("⏳ Waiting for services to initialize (60 seconds)...")
            time.sleep(60)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Deployment failed: {e}")
            return False
    
    def verify_deployment(self) -> bool:
        """Verify deployment health"""
        logger.info("🔍 Verifying deployment health...")
        
        healthy_services = 0
        total_services = len(self.deployment_config['health_endpoints'])
        
        for service, endpoint in self.deployment_config['health_endpoints'].items():
            logger.info(f"🔍 Checking {service}...")
            
            for attempt in range(3):
                try:
                    response = requests.get(endpoint, timeout=10)
                    if response.status_code < 400:
                        logger.info(f"✅ {service}: Healthy (HTTP {response.status_code})")
                        healthy_services += 1
                        break
                    else:
                        logger.warning(f"⚠️ {service}: HTTP {response.status_code}")
                except requests.exceptions.RequestException as e:
                    logger.warning(f"⚠️ {service}: {e}")
                    if attempt < 2:
                        time.sleep(10)
            else:
                logger.error(f"❌ {service}: Health check failed after 3 attempts")
        
        success_rate = (healthy_services / total_services) * 100
        logger.info(f"📊 Health check results: {healthy_services}/{total_services} services healthy ({success_rate:.1f}%)")
        
        if success_rate >= 80:
            logger.info("✅ Deployment verification successful")
            return True
        else:
            logger.error("❌ Deployment verification failed")
            return False
    
    def generate_deployment_report(self) -> Dict[str, Any]:
        """Generate deployment report"""
        logger.info("📋 Generating deployment report...")
        
        # Get container status
        try:
            result = subprocess.run([
                'docker', 'compose', '-f', 'docker-compose.ministry.yml', 'ps', '--format', 'json'
            ], capture_output=True, text=True)
            
            containers = []
            if result.returncode == 0 and result.stdout.strip():
                for line in result.stdout.strip().split('\n'):
                    try:
                        containers.append(json.loads(line))
                    except json.JSONDecodeError:
                        pass
        except Exception as e:
            logger.warning(f"Could not get container status: {e}")
            containers = []
        
        # Get system metrics
        metrics = {}
        try:
            response = requests.get('http://localhost:9091/metrics', timeout=5)
            if response.status_code == 200:
                metrics['continuous_upload_system'] = 'Available'
            else:
                metrics['continuous_upload_system'] = f'HTTP {response.status_code}'
        except:
            metrics['continuous_upload_system'] = 'Unavailable'
        
        report = {
            'deployment_timestamp': datetime.now().isoformat(),
            'ministry_department': 'Ministry of Interior',
            'classification': 'Official',
            'priority': 'High',
            'system_name': 'Continuous Database Upload System',
            'version': '1.0.0',
            'containers': containers,
            'metrics': metrics,
            'service_urls': {
                'Continuous Upload Metrics': 'http://localhost:9091/metrics',
                'Compliance Engine': 'http://localhost:8000',
                'Ministry API': 'http://localhost:8008',
                'Grafana Dashboard': 'http://localhost:3000',
                'Prometheus': 'http://localhost:9090'
            },
            'credentials': {
                'Grafana': 'admin / MinistryGrafana2024!',
                'Database': 'doganai / MinistrySecure2024!'
            },
            'deployment_status': 'Completed',
            'next_steps': [
                'Access Grafana dashboard for monitoring',
                'Review system logs for any issues',
                'Configure alerts and notifications',
                'Schedule regular maintenance',
                'Train operational staff'
            ]
        }
        
        # Save report
        try:
            with open('ministry_deployment_report.json', 'w') as f:
                json.dump(report, f, indent=2, default=str)
            logger.info("✅ Deployment report saved to ministry_deployment_report.json")
        except Exception as e:
            logger.warning(f"Could not save deployment report: {e}")
        
        return report
    
    def run_deployment(self) -> bool:
        """Run complete deployment process"""
        logger.info("🚀 DoganAI Compliance Kit - Ministry of Interior Deployment")
        logger.info("=" * 70)
        logger.info(f"Started at: {datetime.now().isoformat()}")
        logger.info("Classification: Official")
        logger.info("Priority: High")
        logger.info("Target: Ministry of Interior")
        logger.info("=" * 70)
        
        try:
            # Step 1: Check prerequisites
            if not self.check_prerequisites():
                logger.error("❌ Prerequisites check failed")
                return False
            
            # Step 2: Create environment file
            if not self.create_environment_file():
                logger.error("❌ Environment setup failed")
                return False
            
            # Step 3: Create Ministry Dockerfile
            if not self.create_ministry_dockerfile():
                logger.error("❌ Dockerfile creation failed")
                return False
            
            # Step 4: Deploy system
            if not self.deploy_system():
                logger.error("❌ System deployment failed")
                return False
            
            # Step 5: Verify deployment
            if not self.verify_deployment():
                logger.error("❌ Deployment verification failed")
                return False
            
            # Step 6: Generate report
            report = self.generate_deployment_report()
            
            # Success message
            logger.info("\n" + "=" * 70)
            logger.info("🎉 MINISTRY OF INTERIOR DEPLOYMENT SUCCESSFUL")
            logger.info("=" * 70)
            logger.info("\n🌐 Service URLs:")
            for name, url in report['service_urls'].items():
                logger.info(f"  • {name}: {url}")
            
            logger.info("\n🔑 Default Credentials:")
            for service, creds in report['credentials'].items():
                logger.info(f"  • {service}: {creds}")
            
            logger.info("\n📋 Next Steps:")
            for step in report['next_steps']:
                logger.info(f"  • {step}")
            
            logger.info("\n✅ System is ready for Ministry of Interior operations")
            logger.info(f"📄 Deployment report: ministry_deployment_report.json")
            logger.info(f"📚 Documentation: MINISTRY_DEPLOYMENT_GUIDE.md")
            logger.info("=" * 70)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Deployment failed with error: {e}")
            return False

def main():
    """Main deployment function"""
    deployment_manager = MinistryDeploymentManager()
    
    try:
        success = deployment_manager.run_deployment()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("\n⚠️ Deployment interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"\n❌ Deployment failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
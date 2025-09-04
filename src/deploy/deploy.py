"""
DoganAI Compliance Kit - Production Deployment Script
Integrates with Kubernetes infrastructure and performance optimizations
"""
import os
import sys
import subprocess
import yaml
import json
from pathlib import Path
from typing import Dict, Any, List
import argparse


class DoganAIDeployment:
    """DoganAI Compliance Kit production deployment manager"""
    
    def __init__(self, environment: str = "production"):
        self.environment = environment
        self.namespace = f"doganai-{environment}"
        self.app_name = "doganai-compliance-kit"
        self.version = "2.0.0"
        
        # Deployment configuration
        self.config = self._load_deployment_config()
        
    def _load_deployment_config(self) -> Dict[str, Any]:
        """Load deployment configuration"""
        return {
            "api": {
                "image": f"doganai/compliance-api:{self.version}",
                "replicas": 3 if self.environment == "production" else 1,
                "resources": {
                    "requests": {"cpu": "500m", "memory": "1Gi"},
                    "limits": {"cpu": "2000m", "memory": "4Gi"}
                },
                "port": 8000,
                "health_check_path": "/health/enhanced"
            },
            "ui": {
                "image": f"doganai/compliance-ui:{self.version}",
                "replicas": 2 if self.environment == "production" else 1,
                "resources": {
                    "requests": {"cpu": "200m", "memory": "512Mi"},
                    "limits": {"cpu": "1000m", "memory": "2Gi"}
                },
                "port": 8501
            },
            "redis": {
                "enabled": True,
                "replicas": 1,
                "resources": {
                    "requests": {"cpu": "200m", "memory": "256Mi"},
                    "limits": {"cpu": "500m", "memory": "1Gi"}
                },
                "persistence": {"size": "10Gi"}
            },
            "postgresql": {
                "enabled": True,
                "replicas": 1,
                "resources": {
                    "requests": {"cpu": "500m", "memory": "1Gi"},
                    "limits": {"cpu": "2000m", "memory": "4Gi"}
                },
                "persistence": {"size": "50Gi"}
            },
            "monitoring": {
                "prometheus": True,
                "grafana": True,
                "alertmanager": True
            },
            "ingress": {
                "enabled": True,
                "hostname": f"doganai-{self.environment}.example.com",
                "tls": True,
                "annotations": {
                    "kubernetes.io/ingress.class": "nginx",
                    "cert-manager.io/cluster-issuer": "letsencrypt-prod",
                    "nginx.ingress.kubernetes.io/rate-limit": "100",
                    "nginx.ingress.kubernetes.io/rate-limit-window": "1m"
                }
            }
        }
    
    def create_namespace(self):
        """Create Kubernetes namespace"""
        namespace_yaml = {
            "apiVersion": "v1",
            "kind": "Namespace",
            "metadata": {
                "name": self.namespace,
                "labels": {
                    "app": self.app_name,
                    "environment": self.environment,
                    "version": self.version
                }
            }
        }
        
        self._apply_yaml(namespace_yaml)
        print(f"? Created namespace: {self.namespace}")
    
    def create_secrets(self):
        """Create Kubernetes secrets"""
        secrets = {
            "doganai-secrets": {
                "SECRET_KEY": os.getenv("SECRET_KEY", "change-me-in-production"),
                "DATABASE_URL": os.getenv("DATABASE_URL", f"postgresql://doganai:password@postgresql:5432/doganai_{self.environment}"),
                "REDIS_URL": os.getenv("REDIS_URL", "redis://redis:6379/0"),
                "JWT_SECRET": os.getenv("JWT_SECRET", "jwt-secret-change-me"),
                "API_KEYS": os.getenv("API_KEYS", "admin-key-123,user-key-456")
            }
        }
        
        for secret_name, secret_data in secrets.items():
            secret_yaml = {
                "apiVersion": "v1",
                "kind": "Secret",
                "metadata": {
                    "name": secret_name,
                    "namespace": self.namespace
                },
                "type": "Opaque",
                "stringData": secret_data
            }
            
            self._apply_yaml(secret_yaml)
            print(f"? Created secret: {secret_name}")
    
    def create_configmap(self):
        """Create application configuration"""
        config_data = {
            "APP_NAME": "DoganAI Compliance Kit",
            "APP_VERSION": self.version,
            "ENVIRONMENT": self.environment,
            "DEBUG": "false" if self.environment == "production" else "true",
            "LOG_LEVEL": "INFO",
            "ENABLE_METRICS": "true",
            "ENABLE_TRACING": "true",
            "CACHE_TTL": "3600",
            "RATE_LIMIT_REQUESTS": "1000",
            "RATE_LIMIT_WINDOW": "3600",
            "CORS_ORIGINS": "*" if self.environment != "production" else "https://doganai.example.com"
        }
        
        configmap_yaml = {
            "apiVersion": "v1",
            "kind": "ConfigMap",
            "metadata": {
                "name": f"{self.app_name}-config",
                "namespace": self.namespace
            },
            "data": config_data
        }
        
        self._apply_yaml(configmap_yaml)
        print(f"? Created ConfigMap: {self.app_name}-config")
    
    def deploy_redis(self):
        """Deploy Redis for caching"""
        if not self.config["redis"]["enabled"]:
            return
        
        redis_deployment = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": "redis",
                "namespace": self.namespace,
                "labels": {"app": "redis", "component": "cache"}
            },
            "spec": {
                "replicas": self.config["redis"]["replicas"],
                "selector": {"matchLabels": {"app": "redis"}},
                "template": {
                    "metadata": {"labels": {"app": "redis"}},
                    "spec": {
                        "containers": [{
                            "name": "redis",
                            "image": "redis:7-alpine",
                            "ports": [{"containerPort": 6379}],
                            "resources": self.config["redis"]["resources"],
                            "args": [
                                "redis-server",
                                "--appendonly", "yes",
                                "--maxmemory", "512mb",
                                "--maxmemory-policy", "allkeys-lru"
                            ],
                            "volumeMounts": [{
                                "name": "redis-data",
                                "mountPath": "/data"
                            }]
                        }],
                        "volumes": [{
                            "name": "redis-data",
                            "persistentVolumeClaim": {
                                "claimName": "redis-pvc"
                            }
                        }]
                    }
                }
            }
        }
        
        # Redis Service
        redis_service = {
            "apiVersion": "v1",
            "kind": "Service",
            "metadata": {
                "name": "redis",
                "namespace": self.namespace
            },
            "spec": {
                "selector": {"app": "redis"},
                "ports": [{"port": 6379, "targetPort": 6379}]
            }
        }
        
        # Redis PVC
        redis_pvc = {
            "apiVersion": "v1",
            "kind": "PersistentVolumeClaim",
            "metadata": {
                "name": "redis-pvc",
                "namespace": self.namespace
            },
            "spec": {
                "accessModes": ["ReadWriteOnce"],
                "resources": {
                    "requests": {
                        "storage": self.config["redis"]["persistence"]["size"]
                    }
                }
            }
        }
        
        self._apply_yaml(redis_pvc)
        self._apply_yaml(redis_deployment)
        self._apply_yaml(redis_service)
        print("? Deployed Redis cache")
    
    def deploy_postgresql(self):
        """Deploy PostgreSQL database"""
        if not self.config["postgresql"]["enabled"]:
            return
        
        # PostgreSQL Deployment
        postgres_deployment = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": "postgresql",
                "namespace": self.namespace,
                "labels": {"app": "postgresql", "component": "database"}
            },
            "spec": {
                "replicas": 1,
                "selector": {"matchLabels": {"app": "postgresql"}},
                "template": {
                    "metadata": {"labels": {"app": "postgresql"}},
                    "spec": {
                        "containers": [{
                            "name": "postgresql",
                            "image": "postgres:15-alpine",
                            "ports": [{"containerPort": 5432}],
                            "resources": self.config["postgresql"]["resources"],
                            "env": [
                                {"name": "POSTGRES_DB", "value": f"doganai_{self.environment}"},
                                {"name": "POSTGRES_USER", "value": "doganai"},
                                {"name": "POSTGRES_PASSWORD", "value": "secure_password_change_me"},
                                {"name": "PGDATA", "value": "/var/lib/postgresql/data/pgdata"}
                            ],
                            "volumeMounts": [{
                                "name": "postgres-data",
                                "mountPath": "/var/lib/postgresql/data"
                            }]
                        }],
                        "volumes": [{
                            "name": "postgres-data",
                            "persistentVolumeClaim": {
                                "claimName": "postgres-pvc"
                            }
                        }]
                    }
                }
            }
        }
        
        # PostgreSQL Service
        postgres_service = {
            "apiVersion": "v1",
            "kind": "Service",
            "metadata": {
                "name": "postgresql",
                "namespace": self.namespace
            },
            "spec": {
                "selector": {"app": "postgresql"},
                "ports": [{"port": 5432, "targetPort": 5432}]
            }
        }
        
        # PostgreSQL PVC
        postgres_pvc = {
            "apiVersion": "v1",
            "kind": "PersistentVolumeClaim",
            "metadata": {
                "name": "postgres-pvc",
                "namespace": self.namespace
            },
            "spec": {
                "accessModes": ["ReadWriteOnce"],
                "resources": {
                    "requests": {
                        "storage": self.config["postgresql"]["persistence"]["size"]
                    }
                }
            }
        }
        
        self._apply_yaml(postgres_pvc)
        self._apply_yaml(postgres_deployment)
        self._apply_yaml(postgres_service)
        print("? Deployed PostgreSQL database")
    
    def deploy_api(self):
        """Deploy DoganAI API"""
        api_deployment = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": f"{self.app_name}-api",
                "namespace": self.namespace,
                "labels": {"app": f"{self.app_name}-api", "component": "backend"}
            },
            "spec": {
                "replicas": self.config["api"]["replicas"],
                "selector": {"matchLabels": {"app": f"{self.app_name}-api"}},
                "template": {
                    "metadata": {
                        "labels": {"app": f"{self.app_name}-api"},
                        "annotations": {
                            "prometheus.io/scrape": "true",
                            "prometheus.io/port": "8000",
                            "prometheus.io/path": "/metrics"
                        }
                    },
                    "spec": {
                        "containers": [{
                            "name": "api",
                            "image": self.config["api"]["image"],
                            "ports": [
                                {"containerPort": self.config["api"]["port"], "name": "http"}
                            ],
                            "resources": self.config["api"]["resources"],
                            "envFrom": [
                                {"configMapRef": {"name": f"{self.app_name}-config"}},
                                {"secretRef": {"name": "doganai-secrets"}}
                            ],
                            "livenessProbe": {
                                "httpGet": {
                                    "path": "/health/live",
                                    "port": self.config["api"]["port"]
                                },
                                "initialDelaySeconds": 30,
                                "periodSeconds": 10
                            },
                            "readinessProbe": {
                                "httpGet": {
                                    "path": "/health/ready",
                                    "port": self.config["api"]["port"]
                                },
                                "initialDelaySeconds": 5,
                                "periodSeconds": 5
                            },
                            "startupProbe": {
                                "httpGet": {
                                    "path": self.config["api"]["health_check_path"],
                                    "port": self.config["api"]["port"]
                                },
                                "initialDelaySeconds": 10,
                                "periodSeconds": 10,
                                "failureThreshold": 30
                            }
                        }]
                    }
                }
            }
        }
        
        # API Service
        api_service = {
            "apiVersion": "v1",
            "kind": "Service",
            "metadata": {
                "name": f"{self.app_name}-api",
                "namespace": self.namespace,
                "labels": {"app": f"{self.app_name}-api"}
            },
            "spec": {
                "selector": {"app": f"{self.app_name}-api"},
                "ports": [{"port": 80, "targetPort": self.config["api"]["port"]}]
            }
        }
        
        self._apply_yaml(api_deployment)
        self._apply_yaml(api_service)
        print("? Deployed DoganAI API")
    
    def deploy_ui(self):
        """Deploy DoganAI UI"""
        ui_deployment = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": f"{self.app_name}-ui",
                "namespace": self.namespace,
                "labels": {"app": f"{self.app_name}-ui", "component": "frontend"}
            },
            "spec": {
                "replicas": self.config["ui"]["replicas"],
                "selector": {"matchLabels": {"app": f"{self.app_name}-ui"}},
                "template": {
                    "metadata": {"labels": {"app": f"{self.app_name}-ui"}},
                    "spec": {
                        "containers": [{
                            "name": "ui",
                            "image": self.config["ui"]["image"],
                            "ports": [{"containerPort": self.config["ui"]["port"]}],
                            "resources": self.config["ui"]["resources"],
                            "env": [
                                {"name": "API_URL", "value": f"http://{self.app_name}-api"}
                            ]
                        }]
                    }
                }
            }
        }
        
        # UI Service
        ui_service = {
            "apiVersion": "v1",
            "kind": "Service",
            "metadata": {
                "name": f"{self.app_name}-ui",
                "namespace": self.namespace
            },
            "spec": {
                "selector": {"app": f"{self.app_name}-ui"},
                "ports": [{"port": 80, "targetPort": self.config["ui"]["port"]}]
            }
        }
        
        self._apply_yaml(ui_deployment)
        self._apply_yaml(ui_service)
        print("? Deployed DoganAI UI")
    
    def deploy_ingress(self):
        """Deploy Ingress for external access"""
        if not self.config["ingress"]["enabled"]:
            return
        
        ingress = {
            "apiVersion": "networking.k8s.io/v1",
            "kind": "Ingress",
            "metadata": {
                "name": f"{self.app_name}-ingress",
                "namespace": self.namespace,
                "annotations": self.config["ingress"]["annotations"]
            },
            "spec": {
                "tls": [{
                    "hosts": [self.config["ingress"]["hostname"]],
                    "secretName": f"{self.app_name}-tls"
                }] if self.config["ingress"]["tls"] else [],
                "rules": [{
                    "host": self.config["ingress"]["hostname"],
                    "http": {
                        "paths": [
                            {
                                "path": "/api",
                                "pathType": "Prefix",
                                "backend": {
                                    "service": {
                                        "name": f"{self.app_name}-api",
                                        "port": {"number": 80}
                                    }
                                }
                            },
                            {
                                "path": "/",
                                "pathType": "Prefix",
                                "backend": {
                                    "service": {
                                        "name": f"{self.app_name}-ui",
                                        "port": {"number": 80}
                                    }
                                }
                            }
                        ]
                    }
                }]
            }
        }
        
        self._apply_yaml(ingress)
        print(f"? Deployed Ingress: {self.config['ingress']['hostname']}")
    
    def deploy_monitoring(self):
        """Deploy monitoring stack using Helm"""
        if not self.config["monitoring"]["prometheus"]:
            return
        
        # Install kube-prometheus-stack via Helm
        helm_commands = [
            f"helm repo add prometheus-community https://prometheus-community.github.io/helm-charts",
            f"helm repo update",
            f"helm install prometheus prometheus-community/kube-prometheus-stack "
            f"--namespace {self.namespace} "
            f"--set prometheus.prometheusSpec.serviceMonitorSelectorNilUsesHelmValues=false "
            f"--set grafana.adminPassword=admin123 "
            f"--set grafana.persistence.enabled=true "
            f"--set prometheus.prometheusSpec.retention=30d "
            f"--set prometheus.prometheusSpec.storageSpec.volumeClaimTemplate.spec.resources.requests.storage=50Gi"
        ]
        
        for cmd in helm_commands:
            try:
                subprocess.run(cmd, shell=True, check=True)
            except subprocess.CalledProcessError as e:
                print(f"? Failed to execute: {cmd}")
                print(f"Error: {e}")
        
        print("? Deployed monitoring stack (Prometheus + Grafana)")
    
    def deploy_all(self):
        """Deploy entire DoganAI Compliance Kit"""
        print(f"?? Starting deployment of {self.app_name} v{self.version} to {self.environment}")
        
        try:
            self.create_namespace()
            self.create_secrets()
            self.create_configmap()
            self.deploy_redis()
            self.deploy_postgresql()
            self.deploy_api()
            self.deploy_ui()
            self.deploy_ingress()
            self.deploy_monitoring()
            
            print(f"\n?? Deployment completed successfully!")
            print(f"?? Monitor at: https://{self.config['ingress']['hostname']}")
            print(f"?? Grafana at: https://{self.config['ingress']['hostname']}/grafana")
            print(f"?? Prometheus at: https://{self.config['ingress']['hostname']}/prometheus")
            
        except Exception as e:
            print(f"? Deployment failed: {e}")
            sys.exit(1)
    
    def _apply_yaml(self, yaml_content: Dict[str, Any]):
        """Apply YAML to Kubernetes cluster"""
        yaml_str = yaml.dump(yaml_content, default_flow_style=False)
        
        # Write to temporary file
        temp_file = f"/tmp/{yaml_content['metadata']['name']}.yaml"
        with open(temp_file, 'w') as f:
            f.write(yaml_str)
        
        # Apply to cluster
        try:
            subprocess.run(f"kubectl apply -f {temp_file}", shell=True, check=True)
        except subprocess.CalledProcessError as e:
            print(f"? Failed to apply {yaml_content['metadata']['name']}: {e}")
            raise
        finally:
            # Clean up temp file
            os.remove(temp_file)
    
    def check_prerequisites(self):
        """Check deployment prerequisites"""
        print("?? Checking prerequisites...")
        
        # Check kubectl
        try:
            subprocess.run("kubectl version --client", shell=True, check=True, capture_output=True)
            print("? kubectl is installed")
        except subprocess.CalledProcessError:
            print("? kubectl is not installed or not in PATH")
            return False
        
        # Check helm
        try:
            subprocess.run("helm version", shell=True, check=True, capture_output=True)
            print("? helm is installed")
        except subprocess.CalledProcessError:
            print("? helm is not installed or not in PATH")
            return False
        
        # Check cluster connectivity
        try:
            subprocess.run("kubectl cluster-info", shell=True, check=True, capture_output=True)
            print("? Connected to Kubernetes cluster")
        except subprocess.CalledProcessError:
            print("? Cannot connect to Kubernetes cluster")
            return False
        
        return True
    
    def status(self):
        """Check deployment status"""
        print(f"?? Checking status of {self.app_name} in {self.environment}...")
        
        # Check pods
        cmd = f"kubectl get pods -n {self.namespace} -l app={self.app_name}-api"
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            print("API Pods:")
            print(result.stdout)
        except subprocess.CalledProcessError as e:
            print(f"? Failed to get API pod status: {e}")
        
        # Check services
        cmd = f"kubectl get svc -n {self.namespace}"
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            print("Services:")
            print(result.stdout)
        except subprocess.CalledProcessError as e:
            print(f"? Failed to get service status: {e}")


def main():
    """Main deployment script"""
    parser = argparse.ArgumentParser(description="DoganAI Compliance Kit Deployment")
    parser.add_argument("--environment", "-e", default="production", 
                       choices=["development", "staging", "production"],
                       help="Deployment environment")
    parser.add_argument("--check", "-c", action="store_true",
                       help="Check prerequisites only")
    parser.add_argument("--status", "-s", action="store_true", 
                       help="Check deployment status")
    parser.add_argument("--deploy", "-d", action="store_true",
                       help="Deploy the application")
    
    args = parser.parse_args()
    
    deployment = DoganAIDeployment(args.environment)
    
    if args.check:
        if deployment.check_prerequisites():
            print("? All prerequisites met")
            sys.exit(0)
        else:
            print("? Prerequisites not met")
            sys.exit(1)
    
    elif args.status:
        deployment.status()
    
    elif args.deploy:
        if deployment.check_prerequisites():
            deployment.deploy_all()
        else:
            print("? Prerequisites not met. Use --check to see details.")
            sys.exit(1)
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
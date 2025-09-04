#!/usr/bin/env python3
"""
DoganAI Compliance Kit - Configuration Manager
Handles secure parameter resolution from AWS Systems Manager Parameter Store
Owner: platform@dogan
"""

import os
import sys
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
import re

# Optional AWS imports
try:
    import boto3
    AWS_AVAILABLE = True
except ImportError:
    AWS_AVAILABLE = False
    print("Warning: boto3 not available. AWS SSM features will be disabled.")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class RiskLevel(Enum):
    """Configuration parameter risk levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ConfigStatus(Enum):
    """Configuration parameter status"""
    OPEN = "open"
    RESOLVED = "resolved"
    FAILED = "failed"
    DEPRECATED = "deprecated"

@dataclass
class ConfigParameter:
    """Configuration parameter definition"""
    id: str
    layer: str
    file: str
    risk: RiskLevel
    owner: str
    resolver: str
    default_policy: str
    status: ConfigStatus
    value: Optional[str] = None
    error: Optional[str] = None

class ConfigurationManager:
    """Manages configuration parameters with SSM integration"""
    
    def __init__(self, region: str = 'us-east-1'):
        self.region = region
        self.ssm_client = None
        self.parameters: Dict[str, ConfigParameter] = {}
        self._initialize_aws_client()
        self._register_critical_parameters()
    
    def _initialize_aws_client(self):
        """Initialize AWS SSM client"""
        if not AWS_AVAILABLE:
            logger.warning("AWS boto3 not available. SSM client disabled.")
            self.ssm_client = None
            return
            
        try:
            self.ssm_client = boto3.client('ssm', region_name=self.region)
            logger.info(f"Initialized AWS SSM client for region: {self.region}")
        except Exception as e:
            logger.error(f"Failed to initialize AWS SSM client: {e}")
            self.ssm_client = None
    
    def _register_critical_parameters(self):
        """Register critical configuration parameters"""
        # DB_URL - Critical database configuration
        self.register_parameter(
            ConfigParameter(
                id="DB_URL",
                layer="config",
                file="env/.env.staging",
                risk=RiskLevel.CRITICAL,
                owner="platform@dogan",
                resolver="ssm:/doganai/staging/db_url",
                default_policy="must_provide",
                status=ConfigStatus.OPEN
            )
        )
        
        # Additional critical parameters
        critical_params = [
            ("JWT_SECRET", "ssm:/doganai/staging/jwt_secret"),
            ("API_KEY", "ssm:/doganai/staging/api_key"),
            ("ENCRYPTION_KEY", "ssm:/doganai/staging/encryption_key"),
            ("REDIS_URL", "ssm:/doganai/staging/redis_url"),
            ("REDIS_PASSWORD", "ssm:/doganai/staging/redis_password")
        ]
        
        for param_id, resolver in critical_params:
            self.register_parameter(
                ConfigParameter(
                    id=param_id,
                    layer="config",
                    file="env/.env.staging",
                    risk=RiskLevel.HIGH,
                    owner="platform@dogan",
                    resolver=resolver,
                    default_policy="must_provide",
                    status=ConfigStatus.OPEN
                )
            )
    
    def register_parameter(self, param: ConfigParameter):
        """Register a configuration parameter"""
        self.parameters[param.id] = param
        logger.debug(f"Registered parameter: {param.id} (Risk: {param.risk.value})")
    
    def resolve_ssm_parameter(self, ssm_path: str, decrypt: bool = True) -> Optional[str]:
        """Resolve parameter from AWS Systems Manager Parameter Store"""
        if not AWS_AVAILABLE:
            logger.warning(f"AWS not available. Cannot resolve SSM parameter: {ssm_path}")
            return f"mock-value-for-{ssm_path.split('/')[-1]}"
            
        if not self.ssm_client:
            logger.error("SSM client not initialized")
            return None
        
        try:
            # Extract parameter name from SSM path
            if ssm_path.startswith('ssm:'):
                parameter_name = ssm_path[4:]  # Remove 'ssm:' prefix
            else:
                parameter_name = ssm_path
            
            logger.info(f"Resolving SSM parameter: {parameter_name}")
            
            response = self.ssm_client.get_parameter(
                Name=parameter_name,
                WithDecryption=decrypt
            )
            
            value = response['Parameter']['Value']
            logger.info(f"Successfully resolved parameter: {parameter_name}")
            return value
            
        except self.ssm_client.exceptions.ParameterNotFound:
            logger.error(f"SSM parameter not found: {parameter_name}")
            return None
        except Exception as e:
            logger.error(f"Error resolving SSM parameter {parameter_name}: {e}")
            return None
    
    def resolve_parameter(self, param_id: str) -> bool:
        """Resolve a specific configuration parameter"""
        if param_id not in self.parameters:
            logger.error(f"Parameter not registered: {param_id}")
            return False
        
        param = self.parameters[param_id]
        
        try:
            if param.resolver.startswith('ssm:'):
                value = self.resolve_ssm_parameter(param.resolver)
                if value:
                    param.value = value
                    param.status = ConfigStatus.RESOLVED
                    logger.info(f"Resolved parameter {param_id} from SSM")
                    return True
                else:
                    param.status = ConfigStatus.FAILED
                    param.error = "Failed to resolve from SSM"
                    logger.error(f"Failed to resolve parameter {param_id} from SSM")
                    return False
            else:
                # Handle other resolver types (env, file, etc.)
                logger.warning(f"Unsupported resolver type for {param_id}: {param.resolver}")
                return False
                
        except Exception as e:
            param.status = ConfigStatus.FAILED
            param.error = str(e)
            logger.error(f"Error resolving parameter {param_id}: {e}")
            return False
    
    def resolve_all_parameters(self) -> Dict[str, bool]:
        """Resolve all registered parameters"""
        results = {}
        
        for param_id in self.parameters:
            results[param_id] = self.resolve_parameter(param_id)
        
        return results
    
    def validate_critical_parameters(self) -> bool:
        """Validate that all critical parameters are resolved"""
        critical_failed = []
        
        for param_id, param in self.parameters.items():
            if param.risk == RiskLevel.CRITICAL:
                if param.status != ConfigStatus.RESOLVED or not param.value:
                    critical_failed.append(param_id)
        
        if critical_failed:
            logger.error(f"Critical parameters failed validation: {critical_failed}")
            return False
        
        logger.info("All critical parameters validated successfully")
        return True
    
    def generate_env_file(self, output_path: str) -> bool:
        """Generate environment file with resolved parameters"""
        try:
            env_content = []
            env_content.append("# DoganAI Compliance Kit - Resolved Configuration")
            env_content.append(f"# Generated: {os.environ.get('DEPLOYMENT_TIMESTAMP', 'unknown')}")
            env_content.append("# WARNING: This file contains resolved secrets - handle securely")
            env_content.append("")
            
            for param_id, param in self.parameters.items():
                if param.status == ConfigStatus.RESOLVED and param.value:
                    env_content.append(f"{param_id}={param.value}")
                else:
                    env_content.append(f"# {param_id}=<UNRESOLVED>")
            
            with open(output_path, 'w') as f:
                f.write('\n'.join(env_content))
            
            logger.info(f"Generated environment file: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to generate environment file: {e}")
            return False
    
    def get_parameter_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all parameters"""
        status = {}
        
        for param_id, param in self.parameters.items():
            status[param_id] = {
                'id': param.id,
                'layer': param.layer,
                'file': param.file,
                'risk': param.risk.value,
                'owner': param.owner,
                'resolver': param.resolver,
                'default_policy': param.default_policy,
                'status': param.status.value,
                'has_value': bool(param.value),
                'error': param.error
            }
        
        return status
    
    def check_db_url_configuration(self) -> bool:
        """Specific validation for DB_URL critical parameter"""
        db_param = self.parameters.get('DB_URL')
        
        if not db_param:
            logger.error("DB_URL parameter not registered")
            return False
        
        if db_param.status != ConfigStatus.RESOLVED:
            logger.error(f"DB_URL parameter not resolved. Status: {db_param.status.value}")
            if db_param.error:
                logger.error(f"DB_URL error: {db_param.error}")
            return False
        
        if not db_param.value:
            logger.error("DB_URL parameter has no value")
            return False
        
        # Validate DB URL format
        db_url_pattern = r'^postgresql://[^:]+:[^@]+@[^:]+:\d+/\w+$'
        if not re.match(db_url_pattern, db_param.value):
            logger.error("DB_URL format validation failed")
            return False
        
        logger.info("DB_URL configuration validated successfully")
        return True

def main():
    """Main configuration management function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='DoganAI Configuration Manager')
    parser.add_argument('--region', default='us-east-1', help='AWS region')
    parser.add_argument('--resolve', action='store_true', help='Resolve all parameters')
    parser.add_argument('--validate', action='store_true', help='Validate critical parameters')
    parser.add_argument('--status', action='store_true', help='Show parameter status')
    parser.add_argument('--generate-env', help='Generate environment file')
    parser.add_argument('--check-db', action='store_true', help='Check DB_URL configuration')
    
    args = parser.parse_args()
    
    # Initialize configuration manager
    config_mgr = ConfigurationManager(region=args.region)
    
    success = True
    
    if args.resolve:
        logger.info("Resolving all parameters...")
        results = config_mgr.resolve_all_parameters()
        failed = [k for k, v in results.items() if not v]
        if failed:
            logger.error(f"Failed to resolve parameters: {failed}")
            success = False
        else:
            logger.info("All parameters resolved successfully")
    
    if args.validate:
        logger.info("Validating critical parameters...")
        if not config_mgr.validate_critical_parameters():
            success = False
    
    if args.check_db:
        logger.info("Checking DB_URL configuration...")
        if not config_mgr.check_db_url_configuration():
            success = False
    
    if args.status:
        logger.info("Parameter status:")
        status = config_mgr.get_parameter_status()
        for param_id, info in status.items():
            print(f"{param_id}: {info['status']} (Risk: {info['risk']})")
    
    if args.generate_env:
        logger.info(f"Generating environment file: {args.generate_env}")
        if not config_mgr.generate_env_file(args.generate_env):
            success = False
    
    if not success:
        logger.error("Configuration management completed with errors")
        sys.exit(1)
    else:
        logger.info("Configuration management completed successfully")
        sys.exit(0)

if __name__ == '__main__':
    main()
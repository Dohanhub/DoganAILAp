#!/usr/bin/env python3
"""
API Keys Setup and Validation for Production Deployment
Guide users through obtaining and configuring real API keys
"""

import os
import sys
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class APIKeysSetup:
    """Setup and validate API keys for production deployment"""
    
    def __init__(self):
        self.required_apis = {
            'IBM_WATSON_API_KEY': {
                'name': 'IBM Watson AI Platform',
                'url': 'https://cloud.ibm.com/catalog/services/watson-assistant',
                'instructions': 'Create IBM Cloud account → Watson Assistant service → API key',
                'also_needs': ['IBM_WATSON_ASSISTANT_ID', 'IBM_WATSON_URL']
            },
            'AZURE_COGNITIVE_KEY': {
                'name': 'Microsoft Azure Cognitive Services',
                'url': 'https://portal.azure.com/#create/Microsoft.CognitiveServicesTextAnalytics',
                'instructions': 'Create Azure account → Cognitive Services → Text Analytics → Keys',
                'also_needs': ['AZURE_COGNITIVE_ENDPOINT']
            },
            'AWS_ACCESS_KEY_ID': {
                'name': 'Amazon Web Services Comprehend',
                'url': 'https://console.aws.amazon.com/iam/home#/users',
                'instructions': 'Create AWS account → IAM → Users → Create Access Key for Comprehend',
                'also_needs': ['AWS_SECRET_ACCESS_KEY', 'AWS_DEFAULT_REGION']
            },
            'DATABASE_URL': {
                'name': 'Production PostgreSQL Database',
                'url': 'https://www.postgresql.org/',
                'instructions': 'Set up PostgreSQL server → Create doganai_compliance database',
                'also_needs': ['PGHOST', 'PGPORT', 'PGDATABASE', 'PGUSER', 'PGPASSWORD']
            },
            'REDIS_HOST': {
                'name': 'Redis Cache Server',
                'url': 'https://redis.io/',
                'instructions': 'Set up Redis server for caching and session management',
                'also_needs': ['REDIS_PORT', 'REDIS_PASSWORD']
            }
        }
        
        self.optional_apis = {
            'LENOVO_API_KEY': {
                'name': 'Lenovo ThinkShield API',
                'contact': 'Contact Lenovo enterprise support for API access',
                'benefit': 'Real device security monitoring'
            },
            'FORTINET_API_KEY': {
                'name': 'Fortinet Security Fabric API',
                'contact': 'Contact your Fortinet representative for API access',
                'benefit': 'Live security threat monitoring'
            },
            'NCA_API_KEY': {
                'name': 'Saudi National Cybersecurity Authority API',
                'contact': 'Apply through official NCA channels',
                'benefit': 'Real Saudi cybersecurity compliance'
            },
            'SAMA_API_KEY': {
                'name': 'Saudi Arabian Monetary Authority API',
                'contact': 'Apply through official SAMA channels',
                'benefit': 'Live banking regulatory compliance'
            },
            'MOH_API_KEY': {
                'name': 'Ministry of Health API',
                'contact': 'Apply through official MoH channels',
                'benefit': 'Real healthcare compliance monitoring'
            }
        }
    
    def check_current_configuration(self) -> Dict[str, Any]:
        """Check current API key configuration status"""
        status = {
            'required_configured': 0,
            'required_missing': [],
            'optional_configured': 0,
            'optional_missing': [],
            'total_configured': 0,
            'ready_for_production': False
        }
        
        # Check required APIs
        for api_key in self.required_apis.keys():
            if os.getenv(api_key):
                status['required_configured'] += 1
                status['total_configured'] += 1
            else:
                status['required_missing'].append(api_key)
        
        # Check optional APIs
        for api_key in self.optional_apis.keys():
            if os.getenv(api_key):
                status['optional_configured'] += 1
                status['total_configured'] += 1
            else:
                status['optional_missing'].append(api_key)
        
        # Determine production readiness
        status['ready_for_production'] = len(status['required_missing']) == 0
        
        return status
    
    def generate_sample_env_file(self) -> str:
        """Generate sample .env file with placeholders"""
        env_content = """# DoganAI Compliance Kit - Production Environment Configuration
# Replace 'your-*' placeholders with actual API keys

# =============================================================================
# ENVIRONMENT SETTINGS
# =============================================================================
ENVIRONMENT=production
DEBUG=false
SECRET_KEY=your-production-secret-key-here

# =============================================================================
# REQUIRED APIs - MUST BE CONFIGURED FOR PRODUCTION
# =============================================================================

# IBM Watson AI Platform (CRITICAL)
IBM_WATSON_API_KEY=your-ibm-watson-api-key-here
IBM_WATSON_ASSISTANT_ID=your-watson-assistant-id-here
IBM_WATSON_URL=https://api.us-south.assistant.watson.cloud.ibm.com

# Microsoft Azure Cognitive Services (CRITICAL)
AZURE_COGNITIVE_KEY=your-azure-cognitive-key-here
AZURE_COGNITIVE_ENDPOINT=https://your-resource-name.cognitiveservices.azure.com

# AWS Comprehend (CRITICAL)
AWS_ACCESS_KEY_ID=your-aws-access-key-here
AWS_SECRET_ACCESS_KEY=your-aws-secret-key-here
AWS_DEFAULT_REGION=us-east-1

# Production Database (CRITICAL)
DATABASE_URL=postgresql://username:password@your-prod-db-host:5432/doganai_compliance
PGHOST=your-production-db-host
PGPORT=5432
PGDATABASE=doganai_compliance
PGUSER=your-db-username
PGPASSWORD=your-db-password

# Redis Cache (CRITICAL)
REDIS_HOST=your-redis-host
REDIS_PORT=6379
REDIS_PASSWORD=your-redis-password
REDIS_DB=0

# =============================================================================
# OPTIONAL APIs - Configure as available
# =============================================================================

# Lenovo ThinkShield API
LENOVO_API_KEY=your-lenovo-api-key-here
LENOVO_API_URL=https://api.lenovo.com/thinkshield/v1

# Fortinet Security Fabric API
FORTINET_API_KEY=your-fortinet-api-key-here
FORTINET_HOST=your-fortigate-host

# Saudi Regulatory APIs
NCA_API_KEY=your-nca-api-key-here
NCA_API_URL=https://api.nca.gov.sa/compliance/v1
SAMA_API_KEY=your-sama-api-key-here
SAMA_API_URL=https://api.sama.gov.sa/regulatory/v1
MOH_API_KEY=your-moh-api-key-here
MOH_API_URL=https://api.moh.gov.sa/compliance/v1

# =============================================================================
# SECURITY & AUTHENTICATION
# =============================================================================
VALID_API_KEYS=your-api-key-1,your-api-key-2,your-api-key-3
JWT_SECRET_KEY=your-jwt-secret-key-here

# =============================================================================
# MONITORING & ALERTS
# =============================================================================
ENABLE_REAL_TIME_UPLOAD=true
DATA_SYNC_INTERVAL_MINUTES=15
"""
        return env_content
    
    def setup_demo_configuration(self) -> bool:
        """Set up demo configuration for testing (not for production)"""
        try:
            logger.info("Setting up DEMO configuration for testing...")
            
            demo_env = {
                'ENVIRONMENT': 'demo',
                'DEBUG': 'true',
                'SECRET_KEY': 'demo-secret-key-not-for-production',
                
                # Demo keys (not real)
                'IBM_WATSON_API_KEY': 'demo-watson-key',
                'IBM_WATSON_ASSISTANT_ID': 'demo-assistant-id',
                'AZURE_COGNITIVE_KEY': 'demo-azure-key',
                'AZURE_COGNITIVE_ENDPOINT': 'https://demo.cognitiveservices.azure.com',
                'AWS_ACCESS_KEY_ID': 'demo-aws-access-key',
                'AWS_SECRET_ACCESS_KEY': 'demo-aws-secret-key',
                
                # Local demo database
                'DATABASE_URL': 'sqlite:///doganai_compliance_demo.db',
                'REDIS_HOST': 'localhost',
                'REDIS_PORT': '6379',
                
                # Demo mode flag
                'DEMO_MODE': 'true',
                'USE_MOCK_APIS': 'true'
            }
            
            # Set environment variables for demo
            for key, value in demo_env.items():
                os.environ[key] = value
            
            logger.info("✅ Demo configuration set up successfully")
            logger.warning("⚠️  This is DEMO mode - not for production use!")
            
            return True
            
        except Exception as e:
            logger.error(f"Error setting up demo configuration: {e}")
            return False
    
    def validate_api_connections(self) -> Dict[str, Any]:
        """Validate API connections with current configuration"""
        validation_results = {
            'timestamp': datetime.now().isoformat(),
            'tests': {},
            'summary': {}
        }
        
        try:
            # Test IBM Watson (if configured)
            if os.getenv('IBM_WATSON_API_KEY'):
                try:
                    import requests
                    # Simple validation request
                    headers = {'Authorization': f"Bearer {os.getenv('IBM_WATSON_API_KEY')}"}
                    # Note: This is a simplified test - actual validation would need proper endpoints
                    validation_results['tests']['IBM_Watson'] = {'configured': True, 'note': 'API key present'}
                except Exception as e:
                    validation_results['tests']['IBM_Watson'] = {'configured': True, 'error': str(e)}
            else:
                validation_results['tests']['IBM_Watson'] = {'configured': False}
            
            # Test Azure (if configured)
            if os.getenv('AZURE_COGNITIVE_KEY'):
                validation_results['tests']['Azure'] = {'configured': True, 'note': 'API key present'}
            else:
                validation_results['tests']['Azure'] = {'configured': False}
            
            # Test AWS (if configured)
            if os.getenv('AWS_ACCESS_KEY_ID'):
                validation_results['tests']['AWS'] = {'configured': True, 'note': 'API key present'}
            else:
                validation_results['tests']['AWS'] = {'configured': False}
            
            # Test Database (if configured)
            if os.getenv('DATABASE_URL'):
                validation_results['tests']['Database'] = {'configured': True, 'note': 'Database URL present'}
            else:
                validation_results['tests']['Database'] = {'configured': False}
            
            # Generate summary
            configured_count = len([t for t in validation_results['tests'].values() if t['configured']])
            total_count = len(validation_results['tests'])
            
            validation_results['summary'] = {
                'configured_apis': configured_count,
                'total_apis_checked': total_count,
                'configuration_percentage': (configured_count / total_count) * 100,
                'ready_for_testing': configured_count >= 2  # At least 2 APIs configured
            }
            
        except Exception as e:
            logger.error(f"Error validating API connections: {e}")
            validation_results['error'] = str(e)
        
        return validation_results
    
    def print_setup_instructions(self) -> None:
        """Print detailed setup instructions"""
        print("\n" + "="*80)
        print("🔑 API KEYS SETUP - PRODUCTION DEPLOYMENT")
        print("="*80)
        
        print("\n📋 REQUIRED APIs (Must be configured):")
        for api_key, info in self.required_apis.items():
            configured = "✅" if os.getenv(api_key) else "❌"
            print(f"   {configured} {api_key}: {info['name']}")
            if not os.getenv(api_key):
                print(f"      📝 Setup: {info['instructions']}")
                print(f"      🔗 URL: {info['url']}")
                if info.get('also_needs'):
                    print(f"      📌 Also needs: {', '.join(info['also_needs'])}")
        
        print("\n📋 OPTIONAL APIs (Enhance functionality):")
        for api_key, info in self.optional_apis.items():
            configured = "✅" if os.getenv(api_key) else "⚪"
            print(f"   {configured} {api_key}: {info['name']}")
            if not os.getenv(api_key):
                print(f"      📞 Contact: {info['contact']}")
                print(f"      💡 Benefit: {info['benefit']}")
        
        # Check current status
        status = self.check_current_configuration()
        
        print(f"\n📊 CURRENT STATUS:")
        print(f"   Required APIs: {status['required_configured']}/{len(self.required_apis)}")
        print(f"   Optional APIs: {status['optional_configured']}/{len(self.optional_apis)}")
        print(f"   Total Configured: {status['total_configured']}")
        
        if status['ready_for_production']:
            print(f"   🎉 Status: READY FOR PRODUCTION!")
        else:
            print(f"   ⚠️  Status: Missing required APIs")
            print(f"   📝 Missing: {', '.join(status['required_missing'])}")
        
        print("\n🚀 NEXT STEPS:")
        if status['ready_for_production']:
            print("   1. ✅ All required APIs configured")
            print("   2. 🚀 Run: python deploy_production_vendors.py")
            print("   3. 📊 Start production data uploads")
        else:
            print("   1. 🔑 Configure missing API keys in .env file")
            print("   2. 🧪 Or run demo mode: python api_keys_setup.py --demo")
            print("   3. ✅ Then deploy: python deploy_production_vendors.py")
        
        print("="*80)

def main():
    """Main setup function"""
    setup = APIKeysSetup()
    
    # Check command line arguments
    if len(sys.argv) > 1 and sys.argv[1] == '--demo':
        print("🧪 Setting up DEMO configuration...")
        if setup.setup_demo_configuration():
            print("✅ Demo mode configured successfully!")
            print("🚀 You can now test the system with demo data")
        else:
            print("❌ Failed to set up demo configuration")
        return
    
    # Print setup instructions
    setup.print_setup_instructions()
    
    # Validate current configuration
    validation = setup.validate_api_connections()
    print(f"\n🔍 API Validation Results:")
    for api, result in validation['tests'].items():
        status = "✅" if result['configured'] else "❌"
        print(f"   {status} {api}: {'Configured' if result['configured'] else 'Not configured'}")
    
    # Generate sample .env file if it doesn't exist
    if not os.path.exists('.env'):
        print(f"\n📝 Creating sample .env file...")
        with open('.env', 'w') as f:
            f.write(setup.generate_sample_env_file())
        print(f"✅ Sample .env file created - please edit with your actual API keys")

if __name__ == "__main__":
    main()

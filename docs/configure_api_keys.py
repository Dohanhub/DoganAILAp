#!/usr/bin/env python3
"""
API Keys Configuration Tool
Configure API keys for Saudi regulatory authorities
"""

import os
import json
from pathlib import Path
from typing import Dict, Any

class APIKeysConfigurator:
    """Configure API keys for regulatory authorities"""
    
    def __init__(self):
        self.env_file = ".env"
        self.config_template = "env_config_template.txt"
        self.required_keys = {
            "Saudi Regulatory Authorities": {
                "NCA_API_KEY": {
                    "description": "National Commercial Authority API Key",
                    "authority": "NCA",
                    "website": "https://nca.gov.sa",
                    "purpose": "Company registrations and compliance data"
                },
                "SAMA_CLIENT_ID": {
                    "description": "SAMA OAuth2 Client ID",
                    "authority": "SAMA", 
                    "website": "https://sama.gov.sa",
                    "purpose": "Banking compliance and financial indicators"
                },
                "SAMA_CLIENT_SECRET": {
                    "description": "SAMA OAuth2 Client Secret",
                    "authority": "SAMA",
                    "website": "https://sama.gov.sa", 
                    "purpose": "Banking compliance authentication"
                },
                "MOH_API_KEY": {
                    "description": "Ministry of Health API Key",
                    "authority": "MoH",
                    "website": "https://moh.gov.sa",
                    "purpose": "Healthcare facility compliance"
                },
                "CITC_API_KEY": {
                    "description": "CITC API Key", 
                    "authority": "CITC",
                    "website": "https://citc.gov.sa",
                    "purpose": "Telecom and IT compliance"
                },
                "CMA_API_KEY": {
                    "description": "Capital Market Authority API Key",
                    "authority": "CMA", 
                    "website": "https://cma.org.sa",
                    "purpose": "Securities and market compliance"
                }
            }
        }
    
    def check_current_configuration(self) -> Dict[str, Any]:
        """Check current API key configuration"""
        
        print("🔍 Checking Current API Configuration...")
        print("=" * 45)
        
        status = {
            "env_file_exists": os.path.exists(self.env_file),
            "configured_keys": {},
            "missing_keys": [],
            "placeholder_keys": [],
            "total_required": 0,
            "total_configured": 0
        }
        
        # Load current environment
        current_env = {}
        if status["env_file_exists"]:
            try:
                with open(self.env_file, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if '=' in line and not line.startswith('#'):
                            key, value = line.split('=', 1)
                            current_env[key.strip()] = value.strip()
            except Exception as e:
                print(f"⚠️ Error reading .env file: {e}")
        
        # Check each required key
        for category, keys in self.required_keys.items():
            print(f"\n📋 {category}:")
            
            for key_name, key_info in keys.items():
                status["total_required"] += 1
                current_value = current_env.get(key_name, os.getenv(key_name, ""))
                
                if not current_value:
                    status["missing_keys"].append(key_name)
                    print(f"❌ {key_name}: Missing")
                elif current_value.startswith("your_") or current_value == "your_api_key_here":
                    status["placeholder_keys"].append(key_name)
                    print(f"⚠️ {key_name}: Placeholder value")
                else:
                    status["configured_keys"][key_name] = {
                        "value": current_value[:10] + "..." if len(current_value) > 10 else current_value,
                        "authority": key_info["authority"]
                    }
                    status["total_configured"] += 1
                    print(f"✅ {key_name}: Configured")
        
        # Summary
        print(f"\n📊 Configuration Summary:")
        print(f"   • Total Required: {status['total_required']}")
        print(f"   • Configured: {status['total_configured']}")
        print(f"   • Missing: {len(status['missing_keys'])}")
        print(f"   • Placeholders: {len(status['placeholder_keys'])}")
        
        completion_percentage = (status['total_configured'] / status['total_required']) * 100
        print(f"   • Completion: {completion_percentage:.1f}%")
        
        return status
    
    def create_env_file(self):
        """Create .env file from template"""
        
        print(f"\n📝 Creating .env configuration file...")
        
        if not os.path.exists(self.config_template):
            print(f"❌ Template file {self.config_template} not found")
            return False
        
        try:
            # Copy template to .env
            with open(self.config_template, 'r') as template:
                content = template.read()
            
            with open(self.env_file, 'w') as env_file:
                env_file.write(content)
            
            print(f"✅ Created {self.env_file} from template")
            print(f"📝 Edit {self.env_file} to add your actual API keys")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to create .env file: {e}")
            return False
    
    def setup_mock_keys_for_testing(self):
        """Set up mock API keys for testing purposes"""
        
        print(f"\n🧪 Setting up mock API keys for testing...")
        
        mock_config = {
            "NCA_API_KEY": "mock_nca_key_for_testing_12345",
            "SAMA_CLIENT_ID": "mock_sama_client_id_12345", 
            "SAMA_CLIENT_SECRET": "mock_sama_secret_12345",
            "MOH_API_KEY": "mock_moh_key_for_testing_12345",
            "CITC_API_KEY": "mock_citc_key_for_testing_12345",
            "CMA_API_KEY": "mock_cma_key_for_testing_12345"
        }
        
        try:
            # Read current .env if exists
            current_lines = []
            if os.path.exists(self.env_file):
                with open(self.env_file, 'r') as f:
                    current_lines = f.readlines()
            
            # Update with mock keys
            updated_lines = []
            keys_updated = set()
            
            for line in current_lines:
                if '=' in line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    key = key.strip()
                    if key in mock_config:
                        updated_lines.append(f"{key}={mock_config[key]}\n")
                        keys_updated.add(key)
                    else:
                        updated_lines.append(line)
                else:
                    updated_lines.append(line)
            
            # Add missing keys
            for key, value in mock_config.items():
                if key not in keys_updated:
                    updated_lines.append(f"{key}={value}\n")
            
            # Write updated file
            with open(self.env_file, 'w') as f:
                f.writelines(updated_lines)
            
            print(f"✅ Mock API keys configured in {self.env_file}")
            print("⚠️ These are mock keys - replace with real keys for production")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to set up mock keys: {e}")
            return False
    
    def validate_key_format(self, key_name: str, key_value: str) -> bool:
        """Validate API key format"""
        
        if not key_value or key_value.startswith("your_"):
            return False
        
        # Basic validation rules
        if "CLIENT_ID" in key_name or "CLIENT_SECRET" in key_name:
            return len(key_value) >= 10  # OAuth2 credentials should be longer
        else:
            return len(key_value) >= 8    # API keys should be at least 8 chars
    
    def generate_configuration_guide(self) -> str:
        """Generate configuration guide"""
        
        guide = """
# 🔑 API Keys Configuration Guide

## Required API Keys

"""
        
        for category, keys in self.required_keys.items():
            guide += f"### {category}\n\n"
            
            for key_name, key_info in keys.items():
                guide += f"**{key_name}**\n"
                guide += f"- Authority: {key_info['authority']}\n"
                guide += f"- Website: {key_info['website']}\n"
                guide += f"- Purpose: {key_info['purpose']}\n"
                guide += f"- Description: {key_info['description']}\n\n"
        
        guide += """
## Configuration Steps

1. **Create .env file**: Copy from template
2. **Apply for API access**: Contact each regulatory authority
3. **Replace placeholder values**: Update with real API keys
4. **Test connectivity**: Verify keys work correctly
5. **Deploy system**: Start with real regulatory data

## Important Notes

- Never commit API keys to version control
- Use different keys for development/production
- Rotate keys regularly for security
- Monitor API usage and rate limits
"""
        
        return guide
    
    def run_configuration_wizard(self):
        """Run interactive configuration wizard"""
        
        print("🧙 DoganAI API Keys Configuration Wizard")
        print("=" * 45)
        
        # Step 1: Check current status
        status = self.check_current_configuration()
        
        # Step 2: Create .env if needed
        if not status["env_file_exists"]:
            print(f"\n📝 .env file not found")
            if input("Create .env file from template? (y/n): ").lower().startswith('y'):
                self.create_env_file()
        
        # Step 3: Set up mock keys for testing
        if status["total_configured"] == 0:
            print(f"\n🧪 No API keys configured")
            if input("Set up mock keys for testing? (y/n): ").lower().startswith('y'):
                self.setup_mock_keys_for_testing()
                print("✅ Mock keys configured - system ready for testing")
        
        # Step 4: Generate guide
        guide_file = "API_CONFIGURATION_GUIDE.md"
        with open(guide_file, 'w') as f:
            f.write(self.generate_configuration_guide())
        
        print(f"\n📚 Configuration guide saved to: {guide_file}")
        
        # Step 5: Final status check
        print(f"\n🎯 Final Configuration Status:")
        final_status = self.check_current_configuration()
        
        if final_status["total_configured"] > 0:
            print(f"\n✅ API keys configured - ready for connectivity testing")
            return True
        else:
            print(f"\n⚠️ No API keys configured - system will use scraped data only")
            return False

def main():
    """Main configuration function"""
    
    configurator = APIKeysConfigurator()
    configurator.run_configuration_wizard()

if __name__ == "__main__":
    main()

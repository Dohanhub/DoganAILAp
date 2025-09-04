#!/usr/bin/env python3
"""
Check Vendor Data for Placeholders
Identify all placeholder, demo, and mock data that needs to be replaced
"""

import os
import re
import json
import sqlite3
import yaml
from pathlib import Path
from typing import Dict, List, Any

class VendorPlaceholderChecker:
    """Check for placeholder data in vendor configurations"""
    
    def __init__(self):
        self.placeholder_patterns = [
            r'placeholder',
            r'demo[_-]',
            r'mock[_-]',
            r'fake[_-]',
            r'test[_-]',
            r'sample[_-]',
            r'your[_-].*[_-]key',
            r'your[_-].*[_-]id',
            r'your[_-].*[_-]url',
            r'CHANGE_ME',
            r'TODO',
            r'FIXME',
            r'example\.com',
            r'localhost',
            r'127\.0\.0\.1'
        ]
        
        self.findings = {
            'yaml_files': {},
            'env_files': {},
            'database': {},
            'source_code': {},
            'total_placeholders': 0
        }
    
    def check_yaml_files(self):
        """Check vendor YAML files for placeholders"""
        print("🔍 CHECKING VENDOR YAML FILES...")
        
        vendor_dir = Path('vendors')
        if vendor_dir.exists():
            for yaml_file in vendor_dir.glob('*.yaml'):
                try:
                    with open(yaml_file, 'r') as f:
                        content = f.read()
                        
                    placeholders = []
                    for pattern in self.placeholder_patterns:
                        matches = re.findall(pattern, content, re.IGNORECASE)
                        if matches:
                            placeholders.extend(matches)
                    
                    if placeholders:
                        self.findings['yaml_files'][str(yaml_file)] = placeholders
                        self.findings['total_placeholders'] += len(placeholders)
                        print(f"   ⚠️  {yaml_file.name}: {len(placeholders)} placeholders found")
                    else:
                        print(f"   ✅ {yaml_file.name}: No placeholders")
                        
                except Exception as e:
                    print(f"   ❌ Error reading {yaml_file}: {e}")
    
    def check_env_files(self):
        """Check environment files for placeholders"""
        print("\n🔍 CHECKING ENVIRONMENT FILES...")
        
        env_files = ['.env', 'production_config.env', '.env.production', '.env.local']
        
        for env_file in env_files:
            if os.path.exists(env_file):
                try:
                    with open(env_file, 'r') as f:
                        content = f.read()
                    
                    placeholders = []
                    lines_with_placeholders = []
                    
                    for line_num, line in enumerate(content.split('\n'), 1):
                        for pattern in self.placeholder_patterns:
                            if re.search(pattern, line, re.IGNORECASE):
                                placeholders.append(line.strip())
                                lines_with_placeholders.append(f"Line {line_num}: {line.strip()}")
                    
                    if placeholders:
                        self.findings['env_files'][env_file] = lines_with_placeholders
                        self.findings['total_placeholders'] += len(placeholders)
                        print(f"   ⚠️  {env_file}: {len(placeholders)} placeholders found")
                    else:
                        print(f"   ✅ {env_file}: No placeholders")
                        
                except Exception as e:
                    print(f"   ❌ Error reading {env_file}: {e}")
            else:
                print(f"   📄 {env_file}: File not found")
    
    def check_database(self):
        """Check production database for placeholder data"""
        print("\n🔍 CHECKING PRODUCTION DATABASE...")
        
        db_file = 'doganai_compliance_production_demo.db'
        if os.path.exists(db_file):
            try:
                conn = sqlite3.connect(db_file)
                cursor = conn.cursor()
                
                # Check vendor_data table
                cursor.execute("SELECT vendor_name, data_type, data, source FROM vendor_data")
                vendor_data = cursor.fetchall()
                
                placeholders_found = []
                
                for vendor, data_type, data, source in vendor_data:
                    # Check if source indicates demo/placeholder
                    if any(keyword in source.lower() for keyword in ['demo', 'mock', 'placeholder', 'test']):
                        placeholders_found.append(f"{vendor}: source='{source}'")
                    
                    # Check data content for placeholders
                    try:
                        data_json = json.loads(data)
                        data_str = json.dumps(data_json, indent=2)
                        
                        for pattern in self.placeholder_patterns:
                            if re.search(pattern, data_str, re.IGNORECASE):
                                placeholders_found.append(f"{vendor}: data contains '{pattern}' pattern")
                                break
                    except:
                        pass
                
                if placeholders_found:
                    self.findings['database']['vendor_data'] = placeholders_found
                    self.findings['total_placeholders'] += len(placeholders_found)
                    print(f"   ⚠️  Database: {len(placeholders_found)} placeholder entries found")
                else:
                    print("   ✅ Database: No placeholder data found")
                
                conn.close()
                
            except Exception as e:
                print(f"   ❌ Error checking database: {e}")
        else:
            print(f"   📄 Database file not found: {db_file}")
    
    def check_source_code(self):
        """Check source code files for hardcoded placeholders"""
        print("\n🔍 CHECKING SOURCE CODE...")
        
        # Check key source files
        source_files = [
            'microservices/ai-ml/vendor_integration_service.py',
            'microservices/integrations/main.py',
            'microservices/integrations/vendor_data.py',
            'real_vendor_integrations.py'
        ]
        
        for source_file in source_files:
            if os.path.exists(source_file):
                try:
                    with open(source_file, 'r') as f:
                        content = f.read()
                    
                    placeholders = []
                    lines_with_placeholders = []
                    
                    for line_num, line in enumerate(content.split('\n'), 1):
                        for pattern in self.placeholder_patterns:
                            if re.search(pattern, line, re.IGNORECASE):
                                # Skip comments and docstrings
                                stripped = line.strip()
                                if not stripped.startswith('#') and not stripped.startswith('"""') and not stripped.startswith("'''"):
                                    placeholders.append(line.strip())
                                    lines_with_placeholders.append(f"Line {line_num}: {line.strip()}")
                    
                    if placeholders:
                        self.findings['source_code'][source_file] = lines_with_placeholders
                        self.findings['total_placeholders'] += len(placeholders)
                        print(f"   ⚠️  {source_file}: {len(placeholders)} placeholders found")
                    else:
                        print(f"   ✅ {Path(source_file).name}: No placeholders")
                        
                except Exception as e:
                    print(f"   ❌ Error reading {source_file}: {e}")
            else:
                print(f"   📄 {source_file}: File not found")
    
    def generate_replacement_guide(self):
        """Generate guide for replacing placeholders"""
        print("\n📝 PLACEHOLDER REPLACEMENT GUIDE:")
        print("=" * 80)
        
        if self.findings['total_placeholders'] == 0:
            print("✅ NO PLACEHOLDERS FOUND - SYSTEM IS PRODUCTION READY!")
            return
        
        print(f"⚠️  TOTAL PLACEHOLDERS FOUND: {self.findings['total_placeholders']}")
        
        # YAML files
        if self.findings['yaml_files']:
            print(f"\n📄 YAML FILES:")
            for file_path, placeholders in self.findings['yaml_files'].items():
                print(f"   File: {file_path}")
                for placeholder in placeholders:
                    print(f"      ⚠️  Replace: {placeholder}")
        
        # Environment files
        if self.findings['env_files']:
            print(f"\n🔧 ENVIRONMENT FILES:")
            for file_path, lines in self.findings['env_files'].items():
                print(f"   File: {file_path}")
                for line in lines:
                    print(f"      ⚠️  {line}")
        
        # Database
        if self.findings['database']:
            print(f"\n🗄️  DATABASE:")
            for table, entries in self.findings['database'].items():
                print(f"   Table: {table}")
                for entry in entries:
                    print(f"      ⚠️  {entry}")
        
        # Source code
        if self.findings['source_code']:
            print(f"\n💻 SOURCE CODE:")
            for file_path, lines in self.findings['source_code'].items():
                print(f"   File: {file_path}")
                for line in lines:
                    print(f"      ⚠️  {line}")
        
        print(f"\n🔧 RECOMMENDED ACTIONS:")
        print("   1. Replace all 'demo-*' and 'your-*' values with actual API keys")
        print("   2. Update localhost URLs with production endpoints")
        print("   3. Replace placeholder contact information with real details")
        print("   4. Update demo database with production data")
        print("   5. Remove any TODO/FIXME comments")
    
    def run_full_check(self):
        """Run complete placeholder check"""
        print("🔍 VENDOR DATA PLACEHOLDER CHECK")
        print("=" * 80)
        
        self.check_yaml_files()
        self.check_env_files()
        self.check_database()
        self.check_source_code()
        self.generate_replacement_guide()
        
        return self.findings

def main():
    """Main execution"""
    checker = VendorPlaceholderChecker()
    findings = checker.run_full_check()
    
    # Save findings to file
    with open('vendor_placeholder_check_results.json', 'w') as f:
        json.dump(findings, f, indent=2)
    
    print(f"\n📄 Detailed results saved to: vendor_placeholder_check_results.json")
    
    return findings

if __name__ == "__main__":
    main()

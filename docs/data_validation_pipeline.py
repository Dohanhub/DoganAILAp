#!/usr/bin/env python3
"""
Data Validation Pipeline
Implements comprehensive data validation for incoming compliance data
"""

import sqlite3
import json
import yaml
import re
from datetime import datetime, date
from pathlib import Path
from typing import Dict, List, Any, Tuple

class DataValidator:
    """Comprehensive data validation pipeline"""
    
    def __init__(self):
        self.validation_rules = self._load_validation_rules()
        self.validation_errors = []
        self.validation_warnings = []
        
    def _load_validation_rules(self) -> Dict:
        """Load validation rules configuration"""
        return {
            'evaluation_results': {
                'required_fields': ['id', 'mapping', 'vendor_id', 'compliance_percentage'],
                'field_types': {
                    'id': str,
                    'mapping': str,
                    'vendor_id': str,
                    'compliance_percentage': (int, float),
                    'missing_items': str,
                    'remediation_status': str,
                    'evaluation_details': str
                },
                'field_constraints': {
                    'compliance_percentage': {'min': 0, 'max': 100},
                    'mapping': {'pattern': r'^[A-Z]{2,6}-[A-Z]{2,4}-\d{4}-.+-MAPPING$'},
                    'vendor_id': {'pattern': r'^[A-Z0-9\-]+$'}
                }
            },
            'policies': {
                'required_fields': ['id', 'authority', 'version', 'title', 'controls'],
                'field_types': {
                    'id': str,
                    'authority': str,
                    'version': str,
                    'title': str,
                    'description': str,
                    'is_active': bool
                },
                'field_constraints': {
                    'authority': {'enum': ['NCA', 'SAMA', 'MOH', 'CITC', 'CMA', 'SDAIA', 'NDMO', 'MHRSD', 'MOI']},
                    'version': {'pattern': r'^\d+\.\d+(\.\d+)?$'}
                }
            },
            'vendors': {
                'required_fields': ['id', 'name', 'vendor_category'],
                'field_types': {
                    'id': str,
                    'name': str,
                    'vendor_category': str,
                    'description': str
                }
            }
        }
    
    def validate_database_data(self) -> Tuple[bool, List[str], List[str]]:
        """Validate all data in the database"""
        
        print("🔍 VALIDATING DATABASE DATA")
        print("="*35)
        
        conn = sqlite3.connect('doganai_compliance.db')
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        validation_passed = True
        
        for table in tables:
            if table in self.validation_rules:
                print(f"\n📊 Validating {table}:")
                table_valid = self._validate_table(cursor, table)
                validation_passed = validation_passed and table_valid
            else:
                print(f"\n⏭️ Skipping {table} (no validation rules)")
        
        conn.close()
        
        print(f"\n📈 VALIDATION SUMMARY:")
        print(f"   • Errors: {len(self.validation_errors)}")
        print(f"   • Warnings: {len(self.validation_warnings)}")
        print(f"   • Status: {'✅ PASSED' if validation_passed else '❌ FAILED'}")
        
        return validation_passed, self.validation_errors, self.validation_warnings
    
    def _validate_table(self, cursor, table_name: str) -> bool:
        """Validate a specific table"""
        
        rules = self.validation_rules[table_name]
        
        # Get table data
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()
        
        # Get column names
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [row[1] for row in cursor.fetchall()]
        
        if not rows:
            self.validation_warnings.append(f"{table_name}: Table is empty")
            print(f"   ⚠️ Empty table")
            return True
        
        table_valid = True
        
        for i, row in enumerate(rows):
            row_dict = dict(zip(columns, row))
            row_valid = self._validate_row(table_name, row_dict, rules)
            table_valid = table_valid and row_valid
        
        print(f"   {'✅' if table_valid else '❌'} {len(rows)} records validated")
        return table_valid
    
    def _validate_row(self, table_name: str, row: Dict, rules: Dict) -> bool:
        """Validate a single row"""
        
        row_valid = True
        
        # Check required fields
        for field in rules['required_fields']:
            if field not in row or row[field] is None:
                error = f"{table_name}: Missing required field '{field}' in record {row.get('id', 'unknown')}"
                self.validation_errors.append(error)
                row_valid = False
        
        # Check field types
        for field, expected_type in rules['field_types'].items():
            if field in row and row[field] is not None:
                if not isinstance(row[field], expected_type):
                    error = f"{table_name}: Invalid type for '{field}' in record {row.get('id', 'unknown')}: expected {expected_type}, got {type(row[field])}"
                    self.validation_errors.append(error)
                    row_valid = False
        
        # Check field constraints
        if 'field_constraints' in rules:
            for field, constraints in rules['field_constraints'].items():
                if field in row and row[field] is not None:
                    row_valid = self._validate_field_constraints(table_name, field, row[field], constraints, row.get('id', 'unknown')) and row_valid
        
        return row_valid
    
    def _validate_field_constraints(self, table_name: str, field: str, value: Any, constraints: Dict, record_id: str) -> bool:
        """Validate field-specific constraints"""
        
        valid = True
        
        # Min/Max constraints
        if 'min' in constraints and value < constraints['min']:
            error = f"{table_name}: {field} value {value} below minimum {constraints['min']} in record {record_id}"
            self.validation_errors.append(error)
            valid = False
            
        if 'max' in constraints and value > constraints['max']:
            error = f"{table_name}: {field} value {value} above maximum {constraints['max']} in record {record_id}"
            self.validation_errors.append(error)
            valid = False
        
        # Pattern constraints
        if 'pattern' in constraints and isinstance(value, str):
            if not re.match(constraints['pattern'], value):
                error = f"{table_name}: {field} value '{value}' doesn't match pattern in record {record_id}"
                self.validation_errors.append(error)
                valid = False
        
        # Enum constraints
        if 'enum' in constraints and value not in constraints['enum']:
            error = f"{table_name}: {field} value '{value}' not in allowed values {constraints['enum']} in record {record_id}"
            self.validation_errors.append(error)
            valid = False
        
        return valid
    
    def validate_policy_files(self) -> Tuple[bool, List[str]]:
        """Validate policy YAML files"""
        
        print(f"\n📋 VALIDATING POLICY FILES")
        print("="*35)
        
        policies_dir = Path('policies')
        if not policies_dir.exists():
            error = "Policies directory does not exist"
            self.validation_errors.append(error)
            print(f"   ❌ {error}")
            return False, [error]
        
        policy_files = list(policies_dir.glob('*.yaml')) + list(policies_dir.glob('*.yml'))
        
        if not policy_files:
            warning = "No policy files found"
            self.validation_warnings.append(warning)
            print(f"   ⚠️ {warning}")
            return True, []
        
        files_valid = True
        
        for policy_file in policy_files:
            file_valid = self._validate_policy_file(policy_file)
            files_valid = files_valid and file_valid
        
        print(f"   {'✅' if files_valid else '❌'} {len(policy_files)} policy files validated")
        return files_valid, self.validation_errors
    
    def _validate_policy_file(self, file_path: Path) -> bool:
        """Validate a single policy YAML file"""
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            if not isinstance(data, dict):
                error = f"{file_path.name}: Policy file must contain a YAML object"
                self.validation_errors.append(error)
                return False
            
            # Required fields for policy files
            required_fields = ['regulator', 'version', 'title', 'controls']
            
            for field in required_fields:
                if field not in data:
                    error = f"{file_path.name}: Missing required field '{field}'"
                    self.validation_errors.append(error)
                    return False
            
            # Validate controls
            if 'controls' in data and isinstance(data['controls'], list):
                for i, control in enumerate(data['controls']):
                    if not isinstance(control, dict):
                        error = f"{file_path.name}: Control {i} must be an object"
                        self.validation_errors.append(error)
                        return False
                    
                    control_required = ['id', 'title_en', 'requirement_en', 'category', 'severity']
                    for req_field in control_required:
                        if req_field not in control:
                            warning = f"{file_path.name}: Control {i} missing recommended field '{req_field}'"
                            self.validation_warnings.append(warning)
            
            print(f"      ✅ {file_path.name}")
            return True
            
        except yaml.YAMLError as e:
            error = f"{file_path.name}: YAML parsing error - {e}"
            self.validation_errors.append(error)
            print(f"      ❌ {file_path.name}: YAML error")
            return False
            
        except Exception as e:
            error = f"{file_path.name}: Validation error - {e}"
            self.validation_errors.append(error)
            print(f"      ❌ {file_path.name}: Error")
            return False
    
    def create_validation_report(self) -> Dict:
        """Create comprehensive validation report"""
        
        report = {
            'validation_timestamp': datetime.now().isoformat(),
            'summary': {
                'total_errors': len(self.validation_errors),
                'total_warnings': len(self.validation_warnings),
                'validation_passed': len(self.validation_errors) == 0
            },
            'errors': self.validation_errors,
            'warnings': self.validation_warnings,
            'recommendations': []
        }
        
        # Add recommendations based on findings
        if self.validation_errors:
            report['recommendations'].append("Fix all validation errors before proceeding to production")
        
        if self.validation_warnings:
            report['recommendations'].append("Review and address validation warnings for improved data quality")
        
        if len(self.validation_errors) == 0 and len(self.validation_warnings) == 0:
            report['recommendations'].append("Data validation passed - system ready for operation")
        
        return report

def main():
    """Main validation pipeline function"""
    
    print("🛡️ DoganAI Compliance Kit - Data Validation Pipeline")
    print("="*60)
    print(f"Validation Time: {datetime.now().isoformat()}")
    print()
    
    validator = DataValidator()
    
    # Validate database data
    db_valid, db_errors, db_warnings = validator.validate_database_data()
    
    # Validate policy files
    files_valid, file_errors = validator.validate_policy_files()
    
    # Create validation report
    report = validator.create_validation_report()
    
    # Save validation report
    with open('validation_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    overall_valid = db_valid and files_valid
    
    print(f"\n🎯 OVERALL VALIDATION RESULT")
    print("="*40)
    print(f"   Status: {'✅ PASSED' if overall_valid else '❌ FAILED'}")
    print(f"   Errors: {len(validator.validation_errors)}")
    print(f"   Warnings: {len(validator.validation_warnings)}")
    print(f"   Report: validation_report.json")
    
    return overall_valid

if __name__ == "__main__":
    main()

"""
Validation utilities for DoganAI-Compliance-Kit
"""
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
import re
import yaml
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

@dataclass
class ValidationResult:
    """Result of a validation operation"""
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    details: Optional[Dict[str, Any]] = None
    
    def add_error(self, error: str):
        """Add an error to the result"""
        self.errors.append(error)
        self.is_valid = False
    
    def add_warning(self, warning: str):
        """Add a warning to the result"""
        self.warnings.append(warning)
    
    def merge(self, other: 'ValidationResult'):
        """Merge another validation result into this one"""
        self.errors.extend(other.errors)
        self.warnings.extend(other.warnings)
        if not other.is_valid:
            self.is_valid = False

class PolicyValidator:
    """Validator for policy files"""
    
    REQUIRED_FIELDS = ['regulator', 'version', 'controls', 'metadata']
    OPTIONAL_FIELDS = ['description', 'effective_date', 'expiry_date', 'categories']
    
    @staticmethod
    def validate(data: Dict[str, Any]) -> ValidationResult:
        """Validate policy data structure"""
        result = ValidationResult(is_valid=True, errors=[], warnings=[])
        
        # Check required fields
        for field in PolicyValidator.REQUIRED_FIELDS:
            if field not in data:
                result.add_error(f"Missing required field: {field}")
        
        # Validate regulator
        if 'regulator' in data:
            regulator = data['regulator']
            if not isinstance(regulator, str) or not regulator.strip():
                result.add_error("Regulator must be a non-empty string")
            elif not re.match(r'^[A-Z]{2,10}$', regulator):
                result.add_warning("Regulator should be 2-10 uppercase letters (e.g., 'NCA', 'SAMA')")
        
        # Validate version
        if 'version' in data:
            version = data['version']
            if not isinstance(version, str) or not version.strip():
                result.add_error("Version must be a non-empty string")
            elif not re.match(r'^\d+\.\d+\.\d+$', version):
                result.add_warning("Version should follow semantic versioning (e.g., '1.0.0')")
        
        # Validate controls
        if 'controls' in data:
            controls = data['controls']
            if not isinstance(controls, list):
                result.add_error("Controls must be a list")
            else:
                for i, control in enumerate(controls):
                    control_result = PolicyValidator._validate_control(control, i)
                    result.merge(control_result)
        
        # Validate metadata
        if 'metadata' in data:
            metadata = data['metadata']
            if not isinstance(metadata, dict):
                result.add_error("Metadata must be a dictionary")
            else:
                metadata_result = PolicyValidator._validate_metadata(metadata)
                result.merge(metadata_result)
        
        return result
    
    @staticmethod
    def _validate_control(control: Any, index: int) -> ValidationResult:
        """Validate individual control"""
        result = ValidationResult(is_valid=True, errors=[], warnings=[])
        
        if not isinstance(control, dict):
            result.add_error(f"Control {index} must be a dictionary")
            return result
        
        # Required control fields
        required_fields = ['id', 'title', 'description']
        for field in required_fields:
            if field not in control:
                result.add_error(f"Control {index} missing required field: {field}")
        
        # Validate control ID
        if 'id' in control:
            control_id = control['id']
            if not isinstance(control_id, str) or not control_id.strip():
                result.add_error(f"Control {index} ID must be a non-empty string")
            elif not re.match(r'^[A-Z]{2,10}-\d{3,4}$', control_id):
                result.add_warning(f"Control {index} ID should follow format 'REG-001' (e.g., 'NCA-001')")
        
        # Validate severity/priority
        if 'severity' in control:
            severity = control['severity']
            valid_severities = ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']
            if severity not in valid_severities:
                result.add_warning(f"Control {index} severity should be one of: {valid_severities}")
        
        return result
    
    @staticmethod
    def _validate_metadata(metadata: Dict[str, Any]) -> ValidationResult:
        """Validate policy metadata"""
        result = ValidationResult(is_valid=True, errors=[], warnings=[])
        
        # Recommended metadata fields
        recommended_fields = ['author', 'created_date', 'last_updated']
        for field in recommended_fields:
            if field not in metadata:
                result.add_warning(f"Recommended metadata field missing: {field}")
        
        return result

class VendorValidator:
    """Validator for vendor files"""
    
    REQUIRED_FIELDS = ['vendor', 'solution', 'capabilities']
    OPTIONAL_FIELDS = ['description', 'website', 'contact', 'certification']
    
    @staticmethod
    def validate(data: Dict[str, Any]) -> ValidationResult:
        """Validate vendor data structure"""
        result = ValidationResult(is_valid=True, errors=[], warnings=[])
        
        # Check required fields
        for field in VendorValidator.REQUIRED_FIELDS:
            if field not in data:
                result.add_error(f"Missing required field: {field}")
        
        # Validate vendor name
        if 'vendor' in data:
            vendor = data['vendor']
            if not isinstance(vendor, str) or not vendor.strip():
                result.add_error("Vendor must be a non-empty string")
            elif len(vendor) > 100:
                result.add_warning("Vendor name is very long (>100 characters)")
        
        # Validate solution name
        if 'solution' in data:
            solution = data['solution']
            if not isinstance(solution, str) or not solution.strip():
                result.add_error("Solution must be a non-empty string")
        
        # Validate capabilities
        if 'capabilities' in data:
            capabilities = data['capabilities']
            if not isinstance(capabilities, list):
                result.add_error("Capabilities must be a list")
            else:
                for i, capability in enumerate(capabilities):
                    cap_result = VendorValidator._validate_capability(capability, i)
                    result.merge(cap_result)
        
        return result
    
    @staticmethod
    def _validate_capability(capability: Any, index: int) -> ValidationResult:
        """Validate individual capability"""
        result = ValidationResult(is_valid=True, errors=[], warnings=[])
        
        if not isinstance(capability, dict):
            result.add_error(f"Capability {index} must be a dictionary")
            return result
        
        # Required capability fields
        if 'control_id' not in capability:
            result.add_error(f"Capability {index} missing required field: control_id")
        
        # Validate control_id format
        if 'control_id' in capability:
            control_id = capability['control_id']
            if not isinstance(control_id, str) or not control_id.strip():
                result.add_error(f"Capability {index} control_id must be a non-empty string")
            elif not re.match(r'^[A-Z]{2,10}-\d{3,4}$', control_id):
                result.add_warning(f"Capability {index} control_id should follow format 'REG-001'")
        
        # Validate implementation level
        if 'implementation' in capability:
            implementation = capability['implementation']
            valid_levels = ['FULL', 'PARTIAL', 'PLANNED', 'NOT_SUPPORTED']
            if implementation not in valid_levels:
                result.add_warning(f"Capability {index} implementation should be one of: {valid_levels}")
        
        return result

class MappingValidator:
    """Validator for mapping files"""
    
    REQUIRED_FIELDS = ['name', 'policy_ref', 'vendors']
    OPTIONAL_FIELDS = ['description', 'version', 'created_date', 'sector']
    
    @staticmethod
    def validate(data: Dict[str, Any]) -> ValidationResult:
        """Validate mapping data structure"""
        result = ValidationResult(is_valid=True, errors=[], warnings=[])
        
        # Check required fields
        for field in MappingValidator.REQUIRED_FIELDS:
            if field not in data:
                result.add_error(f"Missing required field: {field}")
        
        # Validate mapping name
        if 'name' in data:
            name = data['name']
            if not isinstance(name, str) or not name.strip():
                result.add_error("Name must be a non-empty string")
        
        # Validate policy reference
        if 'policy_ref' in data:
            policy_ref = data['policy_ref']
            if not isinstance(policy_ref, str) or not policy_ref.strip():
                result.add_error("Policy reference must be a non-empty string")
            elif '@' not in policy_ref:
                result.add_error("Policy reference must follow format 'REGULATOR@VERSION'")
            else:
                parts = policy_ref.split('@')
                if len(parts) != 2:
                    result.add_error("Policy reference must have exactly one '@' symbol")
                else:
                    regulator, version = parts
                    if not regulator.strip() or not version.strip():
                        result.add_error("Both regulator and version must be non-empty")
        
        # Validate vendors list
        if 'vendors' in data:
            vendors = data['vendors']
            if not isinstance(vendors, list):
                result.add_error("Vendors must be a list")
            elif not vendors:
                result.add_warning("Vendors list is empty")
            else:
                for i, vendor in enumerate(vendors):
                    if not isinstance(vendor, str) or not vendor.strip():
                        result.add_error(f"Vendor {i} must be a non-empty string")
                    elif not vendor.endswith('.yaml') and not vendor.endswith('.yml'):
                        result.add_warning(f"Vendor {i} should reference a YAML file")
        
        return result

class FileValidator:
    """Generic YAML file validator"""
    
    @staticmethod
    def validate_yaml_syntax(file_path: Path) -> ValidationResult:
        """Validate YAML syntax of a file"""
        result = ValidationResult(is_valid=True, errors=[], warnings=[])
        
        try:
            if not file_path.exists():
                result.add_error(f"File does not exist: {file_path}")
                return result
            
            with open(file_path, 'r', encoding='utf-8') as f:
                yaml.safe_load(f)
            
        except yaml.YAMLError as e:
            result.add_error(f"YAML syntax error: {str(e)}")
        except UnicodeDecodeError as e:
            result.add_error(f"File encoding error: {str(e)}")
        except Exception as e:
            result.add_error(f"Unexpected error reading file: {str(e)}")
        
        return result
    
    @staticmethod
    def validate_file_structure(file_path: Path, file_type: str) -> ValidationResult:
        """Validate file structure based on type"""
        result = FileValidator.validate_yaml_syntax(file_path)
        
        if not result.is_valid:
            return result
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            if file_type == 'policy':
                policy_result = PolicyValidator.validate(data)
                result.merge(policy_result)
            elif file_type == 'vendor':
                vendor_result = VendorValidator.validate(data)
                result.merge(vendor_result)
            elif file_type == 'mapping':
                mapping_result = MappingValidator.validate(data)
                result.merge(mapping_result)
            else:
                result.add_warning(f"Unknown file type: {file_type}")
        
        except Exception as e:
            result.add_error(f"Error validating file structure: {str(e)}")
        
        return result

def validate_directory(directory_path: Path, file_type: str) -> Dict[str, ValidationResult]:
    """Validate all files in a directory"""
    results = {}
    
    if not directory_path.exists():
        logger.warning(f"Directory does not exist: {directory_path}")
        return results
    
    pattern = "*.yaml" if file_type != "all" else "*.yaml"
    
    for file_path in directory_path.glob(pattern):
        try:
            result = FileValidator.validate_file_structure(file_path, file_type)
            results[file_path.name] = result
        except Exception as e:
            error_result = ValidationResult(is_valid=False, errors=[str(e)], warnings=[])
            results[file_path.name] = error_result
    
    return results

def generate_validation_report(results: Dict[str, ValidationResult]) -> str:
    """Generate a human-readable validation report"""
    report_lines = []
    
    total_files = len(results)
    valid_files = sum(1 for r in results.values() if r.is_valid)
    invalid_files = total_files - valid_files
    
    report_lines.append("=== VALIDATION REPORT ===")
    report_lines.append(f"Total files: {total_files}")
    report_lines.append(f"Valid files: {valid_files}")
    report_lines.append(f"Invalid files: {invalid_files}")
    report_lines.append("")
    
    for filename, result in results.items():
        status = "? VALID" if result.is_valid else "? INVALID"
        report_lines.append(f"{status} {filename}")
        
        if result.errors:
            for error in result.errors:
                report_lines.append(f"  ERROR: {error}")
        
        if result.warnings:
            for warning in result.warnings:
                report_lines.append(f"  WARNING: {warning}")
        
        report_lines.append("")
    
    return "\n".join(report_lines)
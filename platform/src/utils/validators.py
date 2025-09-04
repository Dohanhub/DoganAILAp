"""
Validation utilities for DoganAI-Compliance-Kit
"""
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
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
        
        # Validate version
        if 'version' in data:
            version = data['version']
            if not isinstance(version, str) or not version.strip():
                result.add_error("Version must be a non-empty string")
        
        # Validate controls
        if 'controls' in data:
            controls = data['controls']
            if not isinstance(controls, list):
                result.add_error("Controls must be a list")
        
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
        except Exception as e:
            result.add_error(f"Unexpected error reading file: {str(e)}")
        
        return result

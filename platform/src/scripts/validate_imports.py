#!/usr/bin/env python3
"""
DoganAI Compliance Kit - Import Path Validator
Validates that import statements follow the standardized project structure.
"""

import ast
import sys
from pathlib import Path
from typing import List, Dict

# Define allowed import patterns for each layer
IMPORT_RULES = {
    'src/api/': {
        'allowed_from': ['src.core', 'src.models', 'src.services', 'src.utils'],
        'forbidden_from': [],
        'external_allowed': ['fastapi', 'pydantic', 'starlette', 'uvicorn'],
        'description': 'API layer can import from core, models, services, and utils'
    },
    'src/core/': {
        'allowed_from': ['src.models', 'src.utils'],
        'forbidden_from': ['src.api', 'src.services'],
        'external_allowed': ['sqlalchemy', 'pydantic', 'structlog'],
        'description': 'Core layer can only import from models and utils (avoid services)'
    },
    'src/models/': {
        'allowed_from': ['src.utils'],
        'forbidden_from': ['src.api', 'src.core', 'src.services'],
        'external_allowed': ['sqlalchemy', 'pydantic', 'enum', 'datetime', 'uuid'],
        'description': 'Models layer can only import from utils'
    },
    'src/services/': {
        'allowed_from': ['src.core', 'src.models', 'src.utils'],
        'forbidden_from': ['src.api'],
        'external_allowed': ['sqlalchemy', 'pydantic', 'structlog', 'prometheus_client'],
        'description': 'Services layer can import from core, models, and utils'
    },
    'src/utils/': {
        'allowed_from': [],
        'forbidden_from': ['src.api', 'src.core', 'src.models', 'src.services'],
        'external_allowed': ['typing', 'datetime', 'uuid', 'json', 'pathlib'],
        'description': 'Utils layer should be self-contained with minimal dependencies'
    }
}

# Standard library modules (allowed everywhere)
STANDARD_LIBRARY = {
    'os', 'sys', 'json', 'uuid', 'datetime', 'typing', 'pathlib', 'collections',
    'functools', 'itertools', 'logging', 'threading', 'asyncio', 'contextlib',
    'dataclasses', 'enum', 'abc', 'time', 'hashlib', 're', 'base64'
}

class ImportValidator:
    """Validates import statements according to project structure rules"""
    
    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []
        
    def validate_file(self, file_path: str) -> bool:
        """Validate imports in a single file"""
        path = Path(file_path)
        
        # Skip non-Python files
        if not file_path.endswith('.py'):
            return True
            
        # Skip files outside src/ directory
        if not str(path).startswith('src/'):
            return True
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except (IOError, UnicodeDecodeError) as e:
            self.warnings.append(f"Could not read file '{file_path}': {e}")
            return True
            
        try:
            tree = ast.parse(content, filename=file_path)
        except SyntaxError as e:
            self.warnings.append(f"Syntax error in '{file_path}': {e}")
            return True
            
        return self._validate_imports_in_ast(file_path, tree)
        
    def _validate_imports_in_ast(self, file_path: str, tree: ast.AST) -> bool:
        """Validate imports found in AST"""
        # Determine which layer this file belongs to
        layer = self._get_file_layer(file_path)
        if not layer:
            return True  # File not in a recognized layer
            
        rules = IMPORT_RULES.get(layer, {})
        if not rules:
            return True
            
        all_valid = True
        
        # Extract all import statements
        imports = self._extract_imports(tree)
        
        for import_info in imports:
            if not self._validate_single_import(file_path, import_info, rules):
                all_valid = False
                
        return all_valid
        
    def _get_file_layer(self, file_path: str) -> str:
        """Determine which layer a file belongs to"""
        path = Path(file_path)
        path_str = str(path)
        
        for layer in IMPORT_RULES.keys():
            if path_str.startswith(layer):
                return layer
                
        return ''
        
    def _extract_imports(self, tree: ast.AST) -> List[Dict]:
        """Extract all import statements from AST"""
        imports = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append({
                        'type': 'import',
                        'module': alias.name,
                        'name': alias.asname or alias.name,
                        'line': node.lineno
                    })
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ''
                for alias in node.names:
                    imports.append({
                        'type': 'from_import',
                        'module': module,
                        'name': alias.name,
                        'alias': alias.asname,
                        'line': node.lineno,
                        'level': node.level
                    })
                    
        return imports
        
    def _validate_single_import(self, file_path: str, import_info: Dict, rules: Dict) -> bool:
        """Validate a single import statement"""
        module = import_info['module']
        line = import_info['line']
        
        # Handle relative imports
        if import_info.get('level', 0) > 0:
            return self._validate_relative_import(file_path, import_info, rules)
            
        # Skip standard library imports
        if self._is_standard_library(module):
            return True
            
        # Check if it's an internal import (starts with 'src.')
        if module.startswith('src.'):
            return self._validate_internal_import(file_path, import_info, rules)
            
        # Check if it's an allowed external import
        return self._validate_external_import(file_path, import_info, rules)
        
    def _validate_relative_import(self, file_path: str, import_info: Dict, rules: Dict) -> bool:
        """Validate relative import statements"""
        level = import_info.get('level', 0)
        line = import_info['line']
        
        if level > 2:  # Discourage deep relative imports
            self.warnings.append(
                f"{file_path}:{line} - Deep relative import (level {level}) discouraged. "
                f"Consider using absolute imports from 'src.'"
            )
            
        return True  # Allow relative imports but warn about deep ones
        
    def _validate_internal_import(self, file_path: str, import_info: Dict, rules: Dict) -> bool:
        """Validate internal project imports"""
        module = import_info['module']
        line = import_info['line']
        
        # Check allowed internal imports
        allowed_from = rules.get('allowed_from', [])
        forbidden_from = rules.get('forbidden_from', [])
        
        # Check if import is from a forbidden layer
        for forbidden in forbidden_from:
            if module.startswith(forbidden):
                self.errors.append(
                    f"{file_path}:{line} - Forbidden import '{module}' from {forbidden}. "
                    f"{rules.get('description', '')}"
                )
                return False
                
        # Check if import is from an allowed layer
        if allowed_from:
            is_allowed = any(module.startswith(allowed) for allowed in allowed_from)
            if not is_allowed:
                self.errors.append(
                    f"{file_path}:{line} - Import '{module}' not from allowed layers. "
                    f"Allowed: {', '.join(allowed_from)}. {rules.get('description', '')}"
                )
                return False
                
        return True
        
    def _validate_external_import(self, file_path: str, import_info: Dict, rules: Dict) -> bool:
        """Validate external library imports"""
        module = import_info['module']
        line = import_info['line']
        
        # Get the top-level module name
        top_level = module.split('.')[0]
        
        # Check if it's in the allowed external imports
        external_allowed = rules.get('external_allowed', [])
        
        # Always allow common development and testing libraries
        common_allowed = {
            'pytest', 'unittest', 'mock', 'requests', 'httpx', 'aiohttp',
            'click', 'typer', 'rich', 'colorama', 'tqdm'
        }
        
        if top_level in external_allowed or top_level in common_allowed:
            return True
            
        # Warn about potentially unmanaged external dependencies
        self.warnings.append(
            f"{file_path}:{line} - External import '{module}' not in allowed list. "
            f"Consider adding to allowed external imports if this is intentional."
        )
        
        return True  # Don't fail on external imports, just warn
        
    def _is_standard_library(self, module: str) -> bool:
        """Check if a module is part of the Python standard library"""
        top_level = module.split('.')[0]
        return top_level in STANDARD_LIBRARY
        
    def validate_files(self, file_paths: List[str]) -> bool:
        """Validate imports in multiple files"""
        all_valid = True
        
        for file_path in file_paths:
            if not self.validate_file(file_path):
                all_valid = False
                
        return all_valid
        
    def print_results(self) -> bool:
        """Print validation results"""
        if self.errors:
            print("❌ Import Validation Errors:")
            for error in self.errors:
                print(f"  • {error}")
                
        if self.warnings:
            print("⚠️  Import Validation Warnings:")
            for warning in self.warnings:
                print(f"  • {warning}")
                
        if not self.errors and not self.warnings:
            print("✅ Import validation passed!")
            
        return len(self.errors) == 0

def main():
    """Main validation function"""
    # Get file paths from command line arguments
    file_paths = sys.argv[1:] if len(sys.argv) > 1 else []
    
    if not file_paths:
        print("Usage: python validate_imports.py <file1.py> [file2.py ...]")
        sys.exit(1)
        
    # Create validator
    validator = ImportValidator()
    
    # Run validation
    validator.validate_files(file_paths)
    
    # Print results and exit
    success = validator.print_results()
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
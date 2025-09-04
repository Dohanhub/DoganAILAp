#!/usr/bin/env python3
"""
DoganAI Compliance Kit - Project Structure Validator
Validates that files are placed in the correct directories according to the standardized structure.
"""

import sys
import re
from pathlib import Path
from typing import List, Dict

# Define the standardized project structure
STRUCTURE_RULES = {
    'src/api/': {
        'description': 'FastAPI endpoints, route handlers, and API controllers',
        'allowed_patterns': [
            r'.*endpoints?\.py$',
            r'.*routes?\.py$', 
            r'.*health\.py$',
            r'.*middleware\.py$',
            r'.*auth\.py$',
            r'.*__init__\.py$'
        ],
        'required_imports': ['fastapi', 'pydantic'],
        'forbidden_imports': ['sqlalchemy.orm']
    },
    'src/core/': {
        'description': 'Core business logic, domain models, and application architecture',
        'allowed_patterns': [
            r'.*database\.py$',
            r'.*settings?\.py$',
            r'.*config\.py$',
            r'.*compliance\.py$',
            r'.*domain\.py$',
            r'.*__init__\.py$'
        ],
        'required_imports': [],
        'forbidden_imports': ['fastapi']
    },
    'src/models/': {
        'description': 'Data models, schemas, and database entities',
        'allowed_patterns': [
            r'.*models?\.py$',
            r'.*schemas?\.py$',
            r'.*database\.py$',
            r'.*entities\.py$',
            r'.*__init__\.py$'
        ],
        'required_imports': [],
        'forbidden_imports': ['fastapi.routing']
    },
    'src/services/': {
        'description': 'Business service implementations and application services',
        'allowed_patterns': [
            r'.*service\.py$',
            r'.*_service\.py$',
            r'.*generator\.py$',
            r'.*manager\.py$',
            r'.*handler\.py$',
            r'.*processor\.py$',
            r'.*__init__\.py$'
        ],
        'required_imports': [],
        'forbidden_imports': []
    },
    'src/utils/': {
        'description': 'Utility functions, helper modules, and common utilities',
        'allowed_patterns': [
            r'.*utils?\.py$',
            r'.*helpers?\.py$',
            r'.*validators?\.py$',
            r'.*monitoring\.py$',
            r'.*cache.*\.py$',
            r'.*router\.py$',
            r'.*__init__\.py$'
        ],
        'required_imports': [],
        'forbidden_imports': ['fastapi.routing', 'sqlalchemy.orm']
    }
}

# Files that should not be in src/ at all
FORBIDDEN_IN_SRC = [
    r'.*test.*\.py$',
    r'.*spec\.py$',
    r'.*dockerfile.*',
    r'.*docker-compose.*',
    r'.*\.env.*',
    r'.*config\.json$',
    r'.*config\.yaml$'
]

class StructureValidator:
    """Validates project structure compliance"""
    
    def __init__(self, project_root: str = '.'):
        self.project_root = Path(project_root)
        self.errors: List[str] = []
        self.warnings: List[str] = []
        
    def validate_file_placement(self, file_path: str) -> bool:
        """Validate that a file is placed in the correct directory"""
        path = Path(file_path)
        
        # Skip non-Python files for now
        if not file_path.endswith('.py'):
            return True
            
        # Check if file is in src/ directory
        if not str(path).startswith('src/'):
            return True  # Files outside src/ are not subject to these rules
            
        # Check for forbidden files in src/
        for forbidden_pattern in FORBIDDEN_IN_SRC:
            if re.match(forbidden_pattern, path.name):
                self.errors.append(
                    f"File '{file_path}' should not be in src/ directory. "
                    f"Files matching '{forbidden_pattern}' belong elsewhere."
                )
                return False
                
        # Find the appropriate directory for this file
        relative_path = str(path.relative_to('src'))
        
        # Check each structure rule
        for directory, rules in STRUCTURE_RULES.items():
            if relative_path.startswith(directory.replace('src/', '')):
                return self._validate_file_in_directory(file_path, directory, rules)
                
        # File is in src/ but not in any recognized subdirectory
        self.errors.append(
            f"File '{file_path}' is in src/ but not in any recognized subdirectory. "
            f"Valid subdirectories: {', '.join(STRUCTURE_RULES.keys())}"
        )
        return False
        
    def _validate_file_in_directory(self, file_path: str, directory: str, rules: Dict) -> bool:
        """Validate that a file follows the rules for its directory"""
        path = Path(file_path)
        
        # Check if filename matches allowed patterns
        allowed_patterns = rules.get('allowed_patterns', [])
        if allowed_patterns:
            pattern_match = any(re.match(pattern, path.name) for pattern in allowed_patterns)
            if not pattern_match:
                self.errors.append(
                    f"File '{file_path}' does not match allowed patterns for {directory}. "
                    f"Allowed patterns: {', '.join(allowed_patterns)}"
                )
                return False
                
        # Check file content for import compliance
        return self._validate_file_imports(file_path, rules)
        
    def _validate_file_imports(self, file_path: str, rules: Dict) -> bool:
        """Validate that file imports comply with layer rules"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except (IOError, UnicodeDecodeError):
            self.warnings.append(f"Could not read file '{file_path}' for import validation")
            return True
            
        # Check for forbidden imports
        forbidden_imports = rules.get('forbidden_imports', [])
        for forbidden in forbidden_imports:
            if re.search(rf'from\s+{re.escape(forbidden)}|import\s+{re.escape(forbidden)}', content):
                self.errors.append(
                    f"File '{file_path}' contains forbidden import '{forbidden}' "
                    f"for its directory layer"
                )
                return False
                
        return True
        
    def validate_directory_structure(self) -> bool:
        """Validate that required directories exist"""
        required_dirs = [
            'src',
            'src/api',
            'src/core', 
            'src/models',
            'src/services',
            'src/utils',
            'tests',
            'docs',
            'scripts',
            'config',
            'docker'
        ]
        
        missing_dirs = []
        for required_dir in required_dirs:
            dir_path = self.project_root / required_dir
            if not dir_path.exists():
                missing_dirs.append(required_dir)
                
        if missing_dirs:
            self.errors.append(
                f"Missing required directories: {', '.join(missing_dirs)}"
            )
            return False
            
        return True
        
    def validate_init_files(self) -> bool:
        """Validate that __init__.py files exist in Python packages"""
        python_dirs = [
            'src',
            'src/api',
            'src/core',
            'src/models', 
            'src/services',
            'src/utils'
        ]
        
        missing_init = []
        for python_dir in python_dirs:
            init_path = self.project_root / python_dir / '__init__.py'
            if not init_path.exists():
                missing_init.append(f"{python_dir}/__init__.py")
                
        if missing_init:
            self.errors.append(
                f"Missing __init__.py files: {', '.join(missing_init)}"
            )
            return False
            
        return True
        
    def validate_files(self, file_paths: List[str]) -> bool:
        """Validate a list of files"""
        all_valid = True
        
        for file_path in file_paths:
            if not self.validate_file_placement(file_path):
                all_valid = False
                
        return all_valid
        
    def validate_all(self, file_paths: List[str] = None) -> bool:
        """Run all validations"""
        all_valid = True
        
        # Validate directory structure
        if not self.validate_directory_structure():
            all_valid = False
            
        # Validate __init__.py files
        if not self.validate_init_files():
            all_valid = False
            
        # Validate specific files if provided
        if file_paths:
            if not self.validate_files(file_paths):
                all_valid = False
                
        return all_valid
        
    def print_results(self):
        """Print validation results"""
        if self.errors:
            print("❌ Structure Validation Errors:")
            for error in self.errors:
                print(f"  • {error}")
                
        if self.warnings:
            print("⚠️  Structure Validation Warnings:")
            for warning in self.warnings:
                print(f"  • {warning}")
                
        if not self.errors and not self.warnings:
            print("✅ Project structure validation passed!")
            
        return len(self.errors) == 0

def main():
    """Main validation function"""
    # Get file paths from command line arguments
    file_paths = sys.argv[1:] if len(sys.argv) > 1 else []
    
    # Create validator
    validator = StructureValidator()
    
    # Run validation
    is_valid = validator.validate_all(file_paths)
    
    # Print results
    success = validator.print_results()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
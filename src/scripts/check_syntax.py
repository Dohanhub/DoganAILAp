#!/usr/bin/env python3
"""
Simple syntax validation for Python files
"""
import ast
import sys
from pathlib import Path

def validate_python_file(file_path):
    """Validate Python file syntax"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse the file to check for syntax errors
        ast.parse(content, filename=str(file_path))
        print(f"? {file_path} - Syntax OK")
        return True
    except SyntaxError as e:
        print(f"? {file_path} - Syntax Error: {e}")
        print(f"  Line {e.lineno}: {e.text.strip() if e.text else 'N/A'}")
        return False
    except Exception as e:
        print(f"? {file_path} - Error: {e}")
        return False

def main():
    """Main validation function"""
    base_dir = Path(__file__).parent.parent
    python_files = [
        "engine/api.py",
        "engine/compliance.py", 
        "engine/settings.py",
        "engine/models.py",
        "engine/database.py",
        "engine/health.py",
        "ui/app.py",
        "scripts/validate_config.py",
        "tests/conftest.py",
        "tests/test_compliance.py",
        "tests/test_api_new.py"
    ]
    
    all_valid = True
    for file_path in python_files:
        full_path = base_dir / file_path
        if full_path.exists():
            if not validate_python_file(full_path):
                all_valid = False
        else:
            print(f"? {file_path} - File not found")
            all_valid = False
    
    if all_valid:
        print("\n? All Python files have valid syntax!")
        sys.exit(0)
    else:
        print("\n? Some files have syntax errors!")
        sys.exit(1)

if __name__ == "__main__":
    main()
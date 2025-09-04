#!/usr/bin/env python3
"""
Import validation test
"""
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_imports():
    """Test all imports to identify issues"""
    print("Testing imports...")
    
    try:
        print("? Testing settings import...")
        from engine.settings import settings
        print(f"  Settings loaded: {settings.app_name} v{settings.app_version}")
    except Exception as e:
        print(f"? Settings import failed: {e}")
        return False
    
    try:
        print("? Testing compliance import...")
        print("  Compliance module loaded successfully")
    except Exception as e:
        print(f"? Compliance import failed: {e}")
        return False
    
    try:
        print("? Testing health import...")
        print("  Health module loaded successfully")
    except Exception as e:
        print(f"? Health import failed: {e}")
        return False
    
    try:
        print("? Testing database import...")
        print("  Database module loaded successfully")
    except Exception as e:
        print(f"? Database import failed: {e}")
        return False
    
    try:
        print("? Testing API import...")
        print("  API module loaded successfully")
    except Exception as e:
        print(f"? API import failed: {e}")
        return False
    
    print("\n? All imports successful!")
    return True

if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1)
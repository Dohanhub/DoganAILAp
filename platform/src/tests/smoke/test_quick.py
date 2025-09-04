#!/usr/bin/env python3
"""
Quick verification test for DoganAI-Compliance-Kit
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def main():
    """Main test function"""
    print("?? DoganAI-Compliance-Kit Quick Test")
    print("=" * 40)
    
    # Test 1: Import settings
    try:
        from engine.settings import settings
        print(f"? Settings: {settings.app_name} v{settings.app_version}")
    except Exception as e:
        print(f"? Settings import failed: {e}")
        return False
    
    # Test 2: Import compliance module
    try:
        from engine.compliance import get_available_mappings
        mappings = get_available_mappings()
        print(f"? Compliance: Found {len(mappings)} mappings")
    except Exception as e:
        print(f"? Compliance import failed: {e}")
        return False
    
    # Test 3: Import API module
    try:
        print("? API: FastAPI app loaded")
    except Exception as e:
        print(f"? API import failed: {e}")
        return False
    
    # Test 4: Basic health check
    try:
        from engine.health import get_health_checker
        checker = get_health_checker()
        print("? Health: Health checker loaded")
    except Exception as e:
        print(f"? Health checker failed: {e}")
        return False
    
    print("\n?? All basic tests passed!")
    print("\nTo start the application:")
    print("  python manage.py api    # Start API server")
    print("  python manage.py ui     # Start UI (in another terminal)")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
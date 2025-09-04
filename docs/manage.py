#!/usr/bin/env python3
"""
DoganAI-Compliance-Kit Startup and Validation Script
"""
import sys
import os
import subprocess
from pathlib import Path
import argparse

def install_dependencies():
    """Install Python dependencies"""
    print("Installing dependencies...")
    try:
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ], capture_output=True, text=True, cwd=Path(__file__).parent.parent)
        
        if result.returncode == 0:
            print("? Dependencies installed successfully")
            return True
        else:
            print(f"? Failed to install dependencies: {result.stderr}")
            return False
    except Exception as e:
        print(f"? Error installing dependencies: {e}")
        return False

def validate_environment():
    """Validate environment setup"""
    print("Validating environment...")
    project_root = Path(__file__).parent.parent
    
    # Check for .env file
    env_file = project_root / ".env"
    env_example = project_root / ".env.example"
    
    if not env_file.exists() and env_example.exists():
        print("?? Copying .env.example to .env...")
        try:
            import shutil
            shutil.copy(env_example, env_file)
            print("? Created .env file")
        except Exception as e:
            print(f"? Could not copy .env file: {e}")
    
    # Check required directories
    required_dirs = ["mappings", "policies", "vendors", "benchmarks", "i18n"]
    for dir_name in required_dirs:
        dir_path = project_root / dir_name
        if not dir_path.exists():
            print(f"? Missing directory: {dir_name}")
        else:
            print(f"? Directory exists: {dir_name}")
    
    return True

def test_imports():
    """Test that all modules can be imported"""
    print("Testing imports...")
    
    # Add project to path
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))
    
    modules_to_test = [
        ("engine.settings", "settings"),
        ("engine.compliance", "evaluate"),
        ("engine.health", "get_health_checker"),
        ("engine.api", "app"),
    ]
    
    all_passed = True
    for module_name, attribute in modules_to_test:
        try:
            module = __import__(module_name, fromlist=[attribute])
            getattr(module, attribute)
            print(f"? {module_name}")
        except Exception as e:
            print(f"? {module_name}: {e}")
            all_passed = False
    
    return all_passed

def start_api():
    """Start the API server"""
    print("Starting API server...")
    project_root = Path(__file__).parent.parent
    
    try:
        os.chdir(project_root)
        subprocess.run([
            sys.executable, "-m", "uvicorn", "engine.api:app",
            "--host", "0.0.0.0", "--port", "8000", "--reload"
        ])
    except KeyboardInterrupt:
        print("\n?? API server stopped")
    except Exception as e:
        print(f"? Failed to start API: {e}")

def start_ui():
    """Start the Streamlit UI"""
    print("Starting UI...")
    project_root = Path(__file__).parent.parent
    
    try:
        os.chdir(project_root)
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "ui/app.py"
        ])
    except KeyboardInterrupt:
        print("\n?? UI stopped")
    except Exception as e:
        print(f"? Failed to start UI: {e}")

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="DoganAI-Compliance-Kit Management")
    parser.add_argument("command", choices=[
        "install", "validate", "test", "api", "ui", "setup"
    ], help="Command to run")
    
    args = parser.parse_args()
    
    print("?? DoganAI-Compliance-Kit Management Script")
    print("=" * 50)
    
    if args.command == "install":
        install_dependencies()
    
    elif args.command == "validate":
        validate_environment()
    
    elif args.command == "test":
        if not test_imports():
            print("\n? Import tests failed!")
            sys.exit(1)
        else:
            print("\n? All tests passed!")
    
    elif args.command == "api":
        start_api()
    
    elif args.command == "ui":
        start_ui()
    
    elif args.command == "setup":
        print("?? Setting up DoganAI-Compliance-Kit...")
        steps = [
            ("Installing dependencies", install_dependencies),
            ("Validating environment", validate_environment),
            ("Testing imports", test_imports),
        ]
        
        for step_name, step_func in steps:
            print(f"\n?? {step_name}...")
            if not step_func():
                print(f"? Setup failed at: {step_name}")
                sys.exit(1)
        
        print("\n? Setup completed successfully!")
        print("\nNext steps:")
        print("  1. Review and edit .env file if needed")
        print("  2. Run 'python manage.py api' to start the API")
        print("  3. Run 'python manage.py ui' to start the UI (in another terminal)")

if __name__ == "__main__":
    main()
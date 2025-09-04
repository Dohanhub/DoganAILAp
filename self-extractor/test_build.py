#!/usr/bin/env python3
"""
Test script for the DoganAI Compliance Kit self-extractor build system.
"""

import os
import sys
import json
import subprocess
import tempfile
import shutil
from pathlib import Path

# Ensure UTF-8 console encoding on Windows for emoji/text
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

class BuildTester:
    def __init__(self):
        self.extractor_dir = Path(__file__).parent
        self.root_dir = self.extractor_dir.parent
        self.test_dir = self.extractor_dir / "test_output"
        
    def setup_test_environment(self):
        """Setup test environment."""
        print("🧪 Setting up test environment...")
        
        # Clean previous test
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)
        self.test_dir.mkdir()
        
        print("  ✅ Test environment ready")
    
    def test_config_validation(self):
        """Test configuration file validation."""
        print("📋 Testing configuration validation...")
        
        config_path = self.extractor_dir / "config.json"
        if not config_path.exists():
            print("  ❌ config.json not found")
            return False
        
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            required_keys = ["app", "extractor", "runtime", "components"]
            for key in required_keys:
                if key not in config:
                    print(f"  ❌ Missing required key: {key}")
                    return False
            
            print("  ✅ Configuration validation passed")
            return True
        except json.JSONDecodeError as e:
            print(f"  ❌ Invalid JSON: {e}")
            return False
    
    def test_build_script_syntax(self):
        """Test build script syntax."""
        print("🐍 Testing build script syntax...")
        
        scripts = ["build.py", "package_manager.py", "portable_server.py"]
        for script in scripts:
            script_path = self.extractor_dir / script
            if not script_path.exists():
                print(f"  ❌ {script} not found")
                return False
            
            try:
                # Compile to check syntax
                with open(script_path, 'r', encoding='utf-8', errors='replace') as f:
                    compile(f.read(), script_path, 'exec')
                print(f"  ✅ {script} syntax valid")
            except SyntaxError as e:
                print(f"  ❌ {script} syntax error: {e}")
                return False
        
        return True
    
    def test_dependency_check(self):
        """Test dependency availability."""
        print("📦 Testing dependencies...")
        
        # Check Python
        try:
            result = subprocess.run(["python", "--version"], 
                                  capture_output=True, text=True, check=True)
            print(f"  ✅ Python: {result.stdout.strip()}")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("  ❌ Python not available")
            return False
        
        # Check Node.js (optional for build)
        try:
            result = subprocess.run(["node", "--version"], 
                                  capture_output=True, text=True, check=True)
            print(f"  ✅ Node.js: {result.stdout.strip()}")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("  ⚠️ Node.js not available (optional)")
        
        return True
    
    def test_minimal_build(self):
        """Test minimal build process."""
        print("🏗️ Testing minimal build process...")
        
        try:
            # Import and test build components
            sys.path.insert(0, str(self.extractor_dir))
            
            from build import SelfExtractorBuilder
            from package_manager import PackageManager
            
            # Test builder initialization
            builder = SelfExtractorBuilder()
            print("  ✅ Builder initialized")
            
            # Test package manager
            manager = PackageManager()
            print("  ✅ Package manager initialized")
            
            # Test minimal operations
            test_build_dir = self.test_dir / "build"
            test_build_dir.mkdir()
            
            builder.build_dir = test_build_dir
            builder.dist_dir = self.test_dir / "dist"
            builder.dist_dir.mkdir()
            
            # Test individual components
            builder.create_launcher()
            builder.create_readme()
            
            print("  ✅ Minimal build components created")
            return True
            
        except Exception as e:
            print(f"  ❌ Build test failed: {e}")
            return False
    
    def test_portable_server(self):
        """Test portable server manager."""
        print("🚀 Testing portable server manager...")
        
        try:
            sys.path.insert(0, str(self.extractor_dir))
            from portable_server import PortableServerManager
            
            # Test initialization
            manager = PortableServerManager()
            print("  ✅ Server manager initialized")
            
            # Test configuration
            manager.setup_environment()
            print("  ✅ Environment setup works")
            
            return True
            
        except Exception as e:
            print(f"  ❌ Server manager test failed: {e}")
            return False
    
    def test_file_structure(self):
        """Test expected file structure."""
        print("📁 Testing file structure...")
        
        required_files = [
            "config.json",
            "build.py",
            "package_manager.py", 
            "portable_server.py",
            "build.bat",
            "README.md"
        ]
        
        for file_name in required_files:
            file_path = self.extractor_dir / file_name
            if not file_path.exists():
                print(f"  ❌ Missing file: {file_name}")
                return False
            print(f"  ✅ {file_name}")
        
        return True
    
    def run_all_tests(self):
        """Run all tests."""
        print("🧪 DoganAI Compliance Kit - Self-Extractor Tests")
        print("=" * 55)
        
        tests = [
            ("File Structure", self.test_file_structure),
            ("Configuration", self.test_config_validation),
            ("Script Syntax", self.test_build_script_syntax),
            ("Dependencies", self.test_dependency_check),
            ("Portable Server", self.test_portable_server),
            ("Minimal Build", self.test_minimal_build),
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            print(f"\n🔍 {test_name}:")
            try:
                if test_func():
                    passed += 1
                    print(f"  ✅ {test_name} PASSED")
                else:
                    print(f"  ❌ {test_name} FAILED")
            except Exception as e:
                print(f"  ❌ {test_name} ERROR: {e}")
        
        print("\n" + "=" * 55)
        print(f"📊 Test Results: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All tests passed! Self-extractor is ready to build.")
            return True
        else:
            print("⚠️ Some tests failed. Please fix issues before building.")
            return False
    
    def cleanup(self):
        """Cleanup test environment."""
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)

if __name__ == "__main__":
    tester = BuildTester()
    tester.setup_test_environment()
    
    try:
        success = tester.run_all_tests()
        sys.exit(0 if success else 1)
    finally:
        tester.cleanup()

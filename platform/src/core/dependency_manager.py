#!/usr/bin/env python3
"""
Dependency Management System
Critical fix for PyJWT conflicts and package management
"""

import subprocess
import sys
import pkg_resources
import importlib
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class PackageInfo:
    """Package information"""
    name: str
    version: str
    location: str
    requires: List[str]
    conflicts: List[str]

class DependencyManager:
    """Advanced dependency management system"""
    
    def __init__(self):
        self.installed_packages = {}
        self.conflicts = []
        self.missing_packages = []
        self._load_installed_packages()
    
    def _load_installed_packages(self):
        """Load all installed packages"""
        for dist in pkg_resources.working_set:
            self.installed_packages[dist.project_name] = PackageInfo(
                name=dist.project_name,
                version=dist.version,
                location=dist.location,
                requires=[str(req) for req in dist.requires()] if dist.requires() else [],
                conflicts=[]
            )
    
    def check_package(self, package_name: str) -> Dict[str, any]:
        """Check if package is properly installed and accessible"""
        result = {
            "installed": False,
            "importable": False,
            "version": None,
            "location": None,
            "conflicts": [],
            "errors": []
        }
        
        # Check if package is installed
        if package_name in self.installed_packages:
            result["installed"] = True
            result["version"] = self.installed_packages[package_name].version
            result["location"] = self.installed_packages[package_name].location
        
        # Check if package can be imported
        try:
            module = importlib.import_module(package_name.lower())
            result["importable"] = True
            if hasattr(module, '__version__'):
                result["version"] = module.__version__
        except ImportError as e:
            result["errors"].append(f"Import error: {e}")
        except Exception as e:
            result["errors"].append(f"Unexpected error: {e}")
        
        return result
    
    def resolve_pyjwt_conflicts(self) -> Dict[str, any]:
        """Resolve PyJWT import conflicts"""
        logger.info("Resolving PyJWT conflicts...")
        
        result = {
            "success": False,
            "actions_taken": [],
            "errors": [],
            "final_status": {}
        }
        
        # Check current PyJWT status
        pyjwt_status = self.check_package("PyJWT")
        result["initial_status"] = pyjwt_status
        
        if not pyjwt_status["installed"]:
            result["actions_taken"].append("PyJWT not installed - installing...")
            try:
                self._install_package("PyJWT", "2.10.1")
                result["actions_taken"].append("PyJWT installed successfully")
            except Exception as e:
                result["errors"].append(f"Failed to install PyJWT: {e}")
                return result
        
        # Check for conflicting packages
        conflicting_packages = ["jwt", "python-jwt"]
        for pkg in conflicting_packages:
            if pkg in self.installed_packages and pkg != "PyJWT":
                result["actions_taken"].append(f"Removing conflicting package: {pkg}")
                try:
                    self._uninstall_package(pkg)
                    result["actions_taken"].append(f"Removed {pkg}")
                except Exception as e:
                    result["errors"].append(f"Failed to remove {pkg}: {e}")
        
        # Verify PyJWT import
        try:
            import jwt
            result["final_status"] = {
                "importable": True,
                "version": getattr(jwt, '__version__', 'unknown'),
                "working": True
            }
            result["success"] = True
            result["actions_taken"].append("PyJWT import verified successfully")
        except Exception as e:
            result["errors"].append(f"PyJWT import failed: {e}")
        
        return result
    
    def _install_package(self, package_name: str, version: Optional[str] = None):
        """Install a package"""
        cmd = [sys.executable, "-m", "pip", "install"]
        if version:
            cmd.append(f"{package_name}=={version}")
        else:
            cmd.append(package_name)
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise Exception(f"Failed to install {package_name}: {result.stderr}")
        
        # Reload installed packages
        self._load_installed_packages()
    
    def _uninstall_package(self, package_name: str):
        """Uninstall a package"""
        cmd = [sys.executable, "-m", "pip", "uninstall", "-y", package_name]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise Exception(f"Failed to uninstall {package_name}: {result.stderr}")
        
        # Reload installed packages
        self._load_installed_packages()
    
    def validate_dependencies(self, requirements_file: str = "requirements.txt") -> Dict[str, any]:
        """Validate all dependencies in requirements file"""
        logger.info(f"Validating dependencies from {requirements_file}")
        
        result = {
            "valid": True,
            "missing": [],
            "conflicts": [],
            "warnings": [],
            "package_status": {}
        }
        
        if not os.path.exists(requirements_file):
            result["valid"] = False
            result["errors"] = [f"Requirements file not found: {requirements_file}"]
            return result
        
        # Read requirements file
        with open(requirements_file, 'r') as f:
            requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        
        for req in requirements:
            # Parse requirement
            if '==' in req:
                package_name, version = req.split('==', 1)
            elif '>=' in req:
                package_name, version = req.split('>=', 1)
            elif '<=' in req:
                package_name, version = req.split('<=', 1)
            else:
                package_name = req
                version = None
            
            package_name = package_name.strip()
            
            # Check package status
            status = self.check_package(package_name)
            result["package_status"][package_name] = status
            
            if not status["installed"]:
                result["missing"].append(package_name)
                result["valid"] = False
            elif not status["importable"]:
                result["warnings"].append(f"Package {package_name} installed but not importable")
            elif version and status["version"] != version:
                result["warnings"].append(f"Package {package_name} version mismatch: expected {version}, got {status['version']}")
        
        return result
    
    def fix_dependencies(self) -> Dict[str, any]:
        """Fix common dependency issues"""
        logger.info("Fixing dependency issues...")
        
        result = {
            "success": True,
            "actions_taken": [],
            "errors": []
        }
        
        # Fix PyJWT conflicts
        pyjwt_result = self.resolve_pyjwt_conflicts()
        if pyjwt_result["success"]:
            result["actions_taken"].extend(pyjwt_result["actions_taken"])
        else:
            result["errors"].extend(pyjwt_result["errors"])
            result["success"] = False
        
        # Validate all dependencies
        validation_result = self.validate_dependencies()
        if not validation_result["valid"]:
            result["errors"].append("Dependency validation failed")
            result["success"] = False
        
        # Install missing packages
        for missing_pkg in validation_result["missing"]:
            try:
                self._install_package(missing_pkg)
                result["actions_taken"].append(f"Installed missing package: {missing_pkg}")
            except Exception as e:
                result["errors"].append(f"Failed to install {missing_pkg}: {e}")
                result["success"] = False
        
        return result
    
    def generate_dependency_report(self) -> Dict[str, any]:
        """Generate comprehensive dependency report"""
        validation_result = self.validate_dependencies()
        
        return {
            "timestamp": str(pkg_resources.time.time()),
            "python_version": sys.version,
            "total_packages": len(self.installed_packages),
            "validation": validation_result,
            "critical_packages": {
                "PyJWT": self.check_package("PyJWT"),
                "fastapi": self.check_package("fastapi"),
                "sqlalchemy": self.check_package("sqlalchemy"),
                "redis": self.check_package("redis"),
                "psutil": self.check_package("psutil")
            },
            "recommendations": self._generate_recommendations(validation_result)
        }
    
    def _generate_recommendations(self, validation_result: Dict[str, any]) -> List[str]:
        """Generate recommendations based on validation results"""
        recommendations = []
        
        if validation_result["missing"]:
            recommendations.append(f"Install missing packages: {', '.join(validation_result['missing'])}")
        
        if validation_result["warnings"]:
            recommendations.append("Review package version mismatches")
        
        # Check for PyJWT specifically
        pyjwt_status = self.check_package("PyJWT")
        if not pyjwt_status["importable"]:
            recommendations.append("Fix PyJWT import issues - run resolve_pyjwt_conflicts()")
        
        return recommendations

def main():
    """Main function for dependency management"""
    manager = DependencyManager()
    
    print("🔧 Dependency Management System")
    print("=" * 50)
    
    # Generate report
    report = manager.generate_dependency_report()
    
    print(f"📊 Total packages: {report['total_packages']}")
    print(f"🐍 Python version: {report['python_version']}")
    
    # Check critical packages
    print("\n🔍 Critical Package Status:")
    for pkg, status in report["critical_packages"].items():
        status_icon = "✅" if status["importable"] else "❌"
        print(f"  {status_icon} {pkg}: {status['version'] or 'Not installed'}")
    
    # Show validation results
    validation = report["validation"]
    if validation["missing"]:
        print(f"\n❌ Missing packages: {', '.join(validation['missing'])}")
    
    if validation["warnings"]:
        print(f"\n⚠️  Warnings: {len(validation['warnings'])}")
        for warning in validation["warnings"][:3]:  # Show first 3 warnings
            print(f"  - {warning}")
    
    # Show recommendations
    if report["recommendations"]:
        print("\n💡 Recommendations:")
        for rec in report["recommendations"]:
            print(f"  - {rec}")
    
    # Fix issues if any
    if not validation["valid"] or report["recommendations"]:
        print("\n🔧 Attempting to fix issues...")
        fix_result = manager.fix_dependencies()
        
        if fix_result["success"]:
            print("✅ Dependencies fixed successfully!")
        else:
            print("❌ Some issues could not be fixed:")
            for error in fix_result["errors"]:
                print(f"  - {error}")

if __name__ == "__main__":
    main()

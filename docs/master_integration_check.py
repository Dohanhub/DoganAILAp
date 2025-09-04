"""
DoganAI Master Integration Verification Script
This script validates that all components are properly integrated
"""
import os
import sys
import importlib.util
import json
from datetime import datetime
from typing import Dict, List, Any

class MasterIntegrationChecker:
    """Comprehensive integration checker for DoganAI components"""
    
    def __init__(self):
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "base_directory": self.base_dir,
            "components": {},
            "integration_score": 0,
            "recommendations": []
        }
    
    def check_file_exists(self, file_path: str) -> bool:
        """Check if a file exists"""
        full_path = os.path.join(self.base_dir, file_path)
        return os.path.exists(full_path)
    
    def check_module_import(self, module_path: str, module_name: str) -> Dict[str, Any]:
        """Check if a Python module can be imported"""
        full_path = os.path.join(self.base_dir, module_path)
        
        if not os.path.exists(full_path):
            return {
                "status": "missing",
                "error": f"File not found: {module_path}",
                "importable": False
            }
        
        try:
            spec = importlib.util.spec_from_file_location(module_name, full_path)
            if spec is None:
                return {
                    "status": "error",
                    "error": "Could not create module spec",
                    "importable": False
                }
            
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            return {
                "status": "success",
                "error": None,
                "importable": True,
                "module_info": {
                    "name": getattr(module, "__name__", "unknown"),
                    "doc": getattr(module, "__doc__", "No documentation"),
                    "file": getattr(module, "__file__", full_path)
                }
            }
            
        except Exception as e:
            return {
                "status": "import_error",
                "error": str(e),
                "importable": False
            }
    
    def check_component_integration(self) -> Dict[str, Any]:
        """Check all DoganAI components for integration"""
        
        components = {
            "core_engine": "engine/api.py",
            "performance": "improvements/performance.py",
            "security": "improvements/security.py", 
            "enhanced_api": "improvements/enhanced_api.py",
            "mobile_ui": "improvements/mobile_ui.py",
            "monitoring": "improvements/monitoring.py",
            "error_handling": "improvements/error_handling.py",
            "doganai_integration": "improvements/doganai_integration.py",
            "proposal_integration": "improvements/proposal_integration.py",
            "deployment": "improvements/deploy.py",
            "quick_demo": "quick_demo.py",
            "performance_tests": "test_performance.py"
        }
        
        launchers = {
            "master_launcher": "DoganAI_Master_Launcher.bat",
            "standard_launcher": "DoganAI_Launcher.bat",
            "shortcut_creator": "Create_Shortcut.bat"
        }
        
        integration_results = {}
        total_components = 0
        working_components = 0
        
        print("?? Checking DoganAI Component Integration...")
        print("=" * 60)
        
        # Check Python components
        for component_name, file_path in components.items():
            total_components += 1
            print(f"Checking {component_name}...")
            
            result = self.check_module_import(file_path, component_name)
            integration_results[component_name] = {
                "type": "python_module",
                "file_path": file_path,
                **result
            }
            
            if result["status"] == "success":
                working_components += 1
                print(f"? {component_name}: Working")
            elif result["status"] == "missing":
                print(f"? {component_name}: Missing - {result['error']}")
            else:
                print(f"?? {component_name}: Error - {result['error']}")
        
        # Check launcher files
        for launcher_name, file_path in launchers.items():
            total_components += 1
            exists = self.check_file_exists(file_path)
            
            integration_results[launcher_name] = {
                "type": "batch_file",
                "file_path": file_path,
                "status": "success" if exists else "missing",
                "exists": exists
            }
            
            if exists:
                working_components += 1
                print(f"? {launcher_name}: Available")
            else:
                print(f"? {launcher_name}: Missing")
        
        # Calculate integration score
        integration_score = (working_components / total_components) * 100
        
        return {
            "components": integration_results,
            "total_components": total_components,
            "working_components": working_components,
            "integration_score": round(integration_score, 1),
            "status": "excellent" if integration_score >= 90 else "good" if integration_score >= 75 else "needs_attention"
        }
    
    def check_dependencies(self) -> Dict[str, Any]:
        """Check if required dependencies are installed"""
        
        required_deps = [
            "fastapi",
            "uvicorn", 
            "psutil",
            "aioredis",
            "asyncpg",
            "prometheus_client",
            "structlog",
            "cryptography",
            "passlib",
            "python_jose"
        ]
        
        dependency_results = {}
        installed_count = 0
        
        print("\n?? Checking Dependencies...")
        print("=" * 30)
        
        for dep in required_deps:
            try:
                __import__(dep)
                dependency_results[dep] = {
                    "status": "installed",
                    "version": "unknown"  # Could get version with importlib.metadata
                }
                installed_count += 1
                print(f"? {dep}: Installed")
            except ImportError:
                dependency_results[dep] = {
                    "status": "missing",
                    "version": None
                }
                print(f"? {dep}: Not installed")
        
        return {
            "dependencies": dependency_results,
            "total_required": len(required_deps),
            "installed_count": installed_count,
            "dependency_score": (installed_count / len(required_deps)) * 100
        }
    
    def generate_recommendations(self, component_results: Dict, dependency_results: Dict) -> List[str]:
        """Generate recommendations based on check results"""
        
        recommendations = []
        
        # Component recommendations
        missing_components = [
            name for name, info in component_results["components"].items()
            if info["status"] in ["missing", "import_error"]
        ]
        
        if missing_components:
            recommendations.append(f"Install/fix missing components: {', '.join(missing_components)}")
        
        # Dependency recommendations
        missing_deps = [
            dep for dep, info in dependency_results["dependencies"].items()
            if info["status"] == "missing"
        ]
        
        if missing_deps:
            recommendations.append(f"Install missing dependencies: pip install {' '.join(missing_deps)}")
        
        # Integration recommendations
        if component_results["integration_score"] < 75:
            recommendations.append("Integration score below 75% - consider reinstalling components")
        
        if not self.check_file_exists("DoganAI_Master_Launcher.bat"):
            recommendations.append("Create Master Launcher for complete integration")
        
        # Performance recommendations
        if component_results["integration_score"] >= 90:
            recommendations.append("Excellent integration! Ready for production deployment")
            recommendations.append("Consider running performance tests: python test_performance.py")
            recommendations.append("Try the quick demo: python quick_demo.py")
        
        return recommendations
    
    def run_master_integration_check(self) -> Dict[str, Any]:
        """Run complete master integration check"""
        
        print("?? DoganAI Master Integration Check")
        print("=" * 60)
        print(f"?? Base Directory: {self.base_dir}")
        print()
        
        # Check components
        component_results = self.check_component_integration()
        
        # Check dependencies  
        dependency_results = self.check_dependencies()
        
        # Generate recommendations
        recommendations = self.generate_recommendations(component_results, dependency_results)
        
        # Compile final results
        final_results = {
            "timestamp": datetime.now().isoformat(),
            "base_directory": self.base_dir,
            "component_check": component_results,
            "dependency_check": dependency_results,
            "overall_score": round((
                component_results["integration_score"] * 0.7 + 
                dependency_results["dependency_score"] * 0.3
            ), 1),
            "recommendations": recommendations,
            "status": component_results["status"]
        }
        
        # Print summary
        print(f"\n?? INTEGRATION SUMMARY")
        print("=" * 60)
        print(f"?? Overall Score: {final_results['overall_score']:.1f}%")
        print(f"?? Components: {component_results['working_components']}/{component_results['total_components']} working ({component_results['integration_score']:.1f}%)")
        print(f"?? Dependencies: {dependency_results['installed_count']}/{dependency_results['total_required']} installed ({dependency_results['dependency_score']:.1f}%)")
        print(f"?? Status: {final_results['status'].upper()}")
        
        if recommendations:
            print(f"\n?? RECOMMENDATIONS:")
            for i, rec in enumerate(recommendations, 1):
                print(f"   {i}. {rec}")
        
        # Save results
        results_file = "master_integration_check.json"
        with open(results_file, "w") as f:
            json.dump(final_results, f, indent=2)
        
        print(f"\n?? Detailed results saved to: {results_file}")
        
        return final_results

def main():
    """Run the master integration check"""
    try:
        checker = MasterIntegrationChecker()
        results = checker.run_master_integration_check()
        
        # Exit codes for automation
        if results["overall_score"] >= 90:
            print("\n?? EXCELLENT INTEGRATION! DoganAI is ready for enterprise deployment!")
            return 0
        elif results["overall_score"] >= 75:
            print("\n? GOOD INTEGRATION! DoganAI is functional with minor improvements needed.")
            return 0
        else:
            print("\n?? INTEGRATION NEEDS ATTENTION! Please address the recommendations above.")
            return 1
            
    except Exception as e:
        print(f"\n? Integration check failed: {e}")
        import traceback
        traceback.print_exc()
        return 2

if __name__ == "__main__":
    exit(main())
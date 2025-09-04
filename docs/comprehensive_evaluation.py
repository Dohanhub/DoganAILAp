#!/usr/bin/env python3
"""
DoganAI Compliance Kit - Comprehensive Evaluation Script
This script evaluates all components of the DoganAI system without requiring full deployment
"""

import os
import sys
import json
import time
import subprocess
from datetime import datetime
from typing import Dict, List, Any, Optional

class DoganAIEvaluator:
    """Comprehensive evaluation of DoganAI Compliance Kit"""
    
    def __init__(self):
        self.base_dir = os.getcwd()
        self.results = {
            "evaluation_timestamp": datetime.now().isoformat(),
            "base_directory": self.base_dir,
            "overall_score": 0,
            "component_scores": {},
            "docker_evaluation": {},
            "integration_evaluation": {},
            "recommendations": []
        }
        
    def print_header(self):
        """Print evaluation header"""
        print("=" * 80)
        print("?? DoganAI Compliance Kit - Comprehensive Evaluation")
        print("???? Saudi Arabia Enterprise Solution")
        print("=" * 80)
        print(f"?? Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"?? Directory: {self.base_dir}")
        print("=" * 80)
        print()
    
    def evaluate_file_structure(self) -> Dict[str, Any]:
        """Evaluate the file structure and component availability"""
        print("?? EVALUATING FILE STRUCTURE")
        print("-" * 40)
        
        required_files = {
            "Core Launchers": {
                "DoganAI_Master_Launcher.bat": "Master control interface",
                "DoganAI_Launcher.bat": "Standard launcher",
                "Create_Shortcut.bat": "Desktop integration"
            },
            "Python Modules": {
                "quick_demo.py": "Performance demonstration",
                "test_performance.py": "Performance testing",
                "master_integration_check.py": "Integration validation",
                "quick_integration_check.py": "Quick status check"
            },
            "Enhancement Modules": {
                "improvements/performance.py": "Performance optimizations",
                "improvements/security.py": "Security and RBAC",
                "improvements/enhanced_api.py": "Enhanced API server",
                "improvements/mobile_ui.py": "Mobile interface",
                "improvements/monitoring.py": "Real-time monitoring",
                "improvements/error_handling.py": "Error resilience",
                "improvements/doganai_integration.py": "DoganAI integration",
                "improvements/proposal_integration.py": "Proposal builder",
                "improvements/deploy.py": "Deployment automation"
            },
            "Core Engine": {
                "engine/api.py": "Core compliance engine"
            },
            "Docker Components": {
                "docker-compose.independent.yml": "Independent Docker deployment",
                ".env.template": "Environment configuration template",
                "docker_health_check.bat": "Docker health monitoring",
                "start_independent_docker.bat": "Docker startup automation"
            },
            "Documentation": {
                "INTEGRATION_GUIDE.md": "Integration documentation",
                "HOW_TO_TEST.md": "Testing guide",
                "DESKTOP_SHORTCUT_GUIDE.md": "Desktop integration guide",
                "README-Docker-Independent.md": "Docker deployment guide"
            }
        }
        
        category_scores = {}
        total_files = 0
        found_files = 0
        
        for category, files in required_files.items():
            print(f"\n?? {category}:")
            category_found = 0
            category_total = len(files)
            
            for file_path, description in files.items():
                total_files += 1
                if os.path.exists(file_path):
                    print(f"  ? {file_path} - {description}")
                    found_files += 1
                    category_found += 1
                else:
                    print(f"  ? {file_path} - {description}")
            
            category_score = (category_found / category_total) * 100
            category_scores[category] = {
                "found": category_found,
                "total": category_total,
                "score": category_score
            }
            print(f"  ?? {category} Score: {category_score:.1f}% ({category_found}/{category_total})")
        
        overall_file_score = (found_files / total_files) * 100
        
        print(f"\n?? OVERALL FILE STRUCTURE SCORE: {overall_file_score:.1f}% ({found_files}/{total_files})")
        
        return {
            "overall_score": overall_file_score,
            "category_scores": category_scores,
            "total_files": total_files,
            "found_files": found_files
        }
    
    def evaluate_docker_setup(self) -> Dict[str, Any]:
        """Evaluate Docker setup and configuration"""
        print("\n?? EVALUATING DOCKER SETUP")
        print("-" * 40)
        
        docker_score = 0
        docker_details = {}
        
        # Check Docker installation
        try:
            result = subprocess.run(["docker", "--version"], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                docker_version = result.stdout.strip()
                print(f"? Docker installed: {docker_version}")
                docker_details["docker_installed"] = True
                docker_details["docker_version"] = docker_version
                docker_score += 25
            else:
                print("? Docker not installed or not accessible")
                docker_details["docker_installed"] = False
        except Exception as e:
            print(f"? Docker check failed: {e}")
            docker_details["docker_installed"] = False
        
        # Check Docker Compose
        compose_available = False
        try:
            result = subprocess.run(["docker-compose", "--version"], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                compose_version = result.stdout.strip()
                print(f"? Docker Compose (v1) available: {compose_version}")
                docker_details["compose_v1"] = True
                docker_details["compose_version"] = compose_version
                compose_available = True
                docker_score += 25
        except:
            docker_details["compose_v1"] = False
        
        if not compose_available:
            try:
                result = subprocess.run(["docker", "compose", "version"], 
                                      capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    compose_version = result.stdout.strip()
                    print(f"? Docker Compose (v2) available: {compose_version}")
                    docker_details["compose_v2"] = True
                    docker_details["compose_version"] = compose_version
                    compose_available = True
                    docker_score += 25
            except:
                docker_details["compose_v2"] = False
        
        if not compose_available:
            print("? Docker Compose not available")
            docker_details["compose_available"] = False
        else:
            docker_details["compose_available"] = True
        
        # Check Docker Compose file
        if os.path.exists("docker-compose.independent.yml"):
            print("? Docker Compose independent configuration found")
            docker_details["compose_file"] = True
            docker_score += 25
            
            # Validate compose file
            try:
                with open("docker-compose.independent.yml", "r") as f:
                    content = f.read()
                    services = content.count("build:") + content.count("image:")
                    print(f"  ?? Detected {services} services in compose file")
                    docker_details["services_count"] = services
                    if services >= 10:
                        docker_score += 15
                    elif services >= 5:
                        docker_score += 10
                    else:
                        docker_score += 5
            except Exception as e:
                print(f"  ?? Could not parse compose file: {e}")
        else:
            print("? Docker Compose independent configuration missing")
            docker_details["compose_file"] = False
        
        # Check environment template
        if os.path.exists(".env.template"):
            print("? Environment template found")
            docker_details["env_template"] = True
            docker_score += 10
        else:
            print("? Environment template missing")
            docker_details["env_template"] = False
        
        print(f"\n?? DOCKER SETUP SCORE: {docker_score:.1f}%")
        
        return {
            "score": docker_score,
            "details": docker_details
        }
    
    def evaluate_integration_readiness(self) -> Dict[str, Any]:
        """Evaluate integration readiness"""
        print("\n?? EVALUATING INTEGRATION READINESS")
        print("-" * 40)
        
        integration_score = 0
        integration_details = {}
        
        # Check Python availability
        try:
            result = subprocess.run([sys.executable, "--version"], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                python_version = result.stdout.strip()
                print(f"? Python available: {python_version}")
                integration_details["python_available"] = True
                integration_details["python_version"] = python_version
                integration_score += 20
            else:
                print("? Python not accessible")
                integration_details["python_available"] = False
        except Exception as e:
            print(f"? Python check failed: {e}")
            integration_details["python_available"] = False
        
        # Check key Python modules
        key_modules = ["fastapi", "uvicorn", "streamlit", "psutil", "requests"]
        available_modules = 0
        
        for module in key_modules:
            try:
                __import__(module)
                print(f"? {module} module available")
                available_modules += 1
            except ImportError:
                print(f"? {module} module missing")
        
        module_score = (available_modules / len(key_modules)) * 30
        integration_score += module_score
        integration_details["available_modules"] = available_modules
        integration_details["total_modules"] = len(key_modules)
        integration_details["module_score"] = module_score
        
        # Check configuration files
        config_files = [
            "improvements/doganai_integration.py",
            "improvements/enhanced_api.py",
            "master_integration_check.py"
        ]
        
        config_score = 0
        for config_file in config_files:
            if os.path.exists(config_file):
                print(f"? {config_file} ready")
                config_score += 10
            else:
                print(f"? {config_file} missing")
        
        integration_score += config_score
        integration_details["config_score"] = config_score
        
        # Check launcher availability
        launchers = ["DoganAI_Master_Launcher.bat", "DoganAI_Launcher.bat"]
        launcher_score = 0
        
        for launcher in launchers:
            if os.path.exists(launcher):
                print(f"? {launcher} available")
                launcher_score += 10
            else:
                print(f"? {launcher} missing")
        
        integration_score += launcher_score
        integration_details["launcher_score"] = launcher_score
        
        print(f"\n?? INTEGRATION READINESS SCORE: {integration_score:.1f}%")
        
        return {
            "score": integration_score,
            "details": integration_details
        }
    
    def evaluate_saudi_compliance_features(self) -> Dict[str, Any]:
        """Evaluate Saudi Arabia compliance features"""
        print("\n???? EVALUATING SAUDI COMPLIANCE FEATURES")
        print("-" * 40)
        
        compliance_score = 0
        compliance_features = {}
        
        # Check for Saudi compliance indicators in files
        compliance_indicators = [
            ("SAMA", "Saudi Arabian Monetary Authority"),
            ("NCA", "National Cybersecurity Authority"),
            ("MCI", "Ministry of Communications"),
            ("ZATCA", "Tax Authority"),
            ("MOH", "Ministry of Health"),
            ("SDAIA", "Saudi Data & AI Authority"),
            ("KSA", "Kingdom of Saudi Arabia"),
            ("Saudi", "Saudi Arabia"),
            ("Arabic", "Arabic language support"),
            ("RTL", "Right-to-left text support")
        ]
        
        files_to_check = [
            "improvements/enhanced_api.py",
            "improvements/doganai_integration.py",
            "docker-compose.independent.yml",
            ".env.template"
        ]
        
        found_indicators = set()
        
        for file_path in files_to_check:
            if os.path.exists(file_path):
                try:
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read().upper()
                        for indicator, description in compliance_indicators:
                            if indicator.upper() in content:
                                found_indicators.add(indicator)
                except Exception as e:
                    print(f"  ?? Could not read {file_path}: {e}")
        
        for indicator, description in compliance_indicators:
            if indicator in found_indicators:
                print(f"? {indicator} compliance: {description}")
                compliance_score += 10
                compliance_features[indicator] = True
            else:
                print(f"? {indicator} compliance: {description}")
                compliance_features[indicator] = False
        
        # Bonus for comprehensive Saudi compliance
        if len(found_indicators) >= 6:
            print("?? Bonus: Comprehensive Saudi compliance detected")
            compliance_score += 10
        
        print(f"\n?? SAUDI COMPLIANCE SCORE: {compliance_score:.1f}%")
        
        return {
            "score": compliance_score,
            "features": compliance_features,
            "found_indicators": list(found_indicators)
        }
    
    def evaluate_enterprise_readiness(self) -> Dict[str, Any]:
        """Evaluate enterprise readiness features"""
        print("\n?? EVALUATING ENTERPRISE READINESS")
        print("-" * 40)
        
        enterprise_score = 0
        enterprise_features = {}
        
        # Check for enterprise features
        enterprise_checks = [
            ("security.py", "Security and RBAC implementation", 15),
            ("monitoring.py", "Real-time monitoring", 15),
            ("performance.py", "Performance optimization", 15),
            ("error_handling.py", "Error resilience", 10),
            ("docker-compose.independent.yml", "Container orchestration", 15),
            ("docker_health_check.bat", "Health monitoring", 10),
            ("prometheus", "Metrics collection", 10),
            ("grafana", "Dashboard visualization", 10)
        ]
        
        for file_indicator, description, points in enterprise_checks:
            found = False
            
            # Check if it's a direct file
            if file_indicator.endswith('.py') or file_indicator.endswith('.yml') or file_indicator.endswith('.bat'):
                if os.path.exists(f"improvements/{file_indicator}") or os.path.exists(file_indicator):
                    found = True
            else:
                # Check if mentioned in docker compose or other files
                for check_file in ["docker-compose.independent.yml", ".env.template"]:
                    if os.path.exists(check_file):
                        try:
                            with open(check_file, "r", encoding="utf-8", errors="ignore") as f:
                                if file_indicator.lower() in f.read().lower():
                                    found = True
                                    break
                        except:
                            pass
            
            if found:
                print(f"? {description}")
                enterprise_score += points
                enterprise_features[file_indicator] = True
            else:
                print(f"? {description}")
                enterprise_features[file_indicator] = False
        
        print(f"\n?? ENTERPRISE READINESS SCORE: {enterprise_score:.1f}%")
        
        return {
            "score": enterprise_score,
            "features": enterprise_features
        }
    
    def generate_recommendations(self, all_results: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on evaluation results"""
        recommendations = []
        
        overall_score = all_results["overall_score"]
        
        if overall_score >= 90:
            recommendations.extend([
                "?? Excellent! Your DoganAI system is enterprise-ready",
                "?? Ready for production deployment",
                "?? Consider starting with Docker independent deployment",
                "?? Set up monitoring dashboards for production use"
            ])
        elif overall_score >= 75:
            recommendations.extend([
                "? Good system setup with minor improvements needed",
                "?? Address missing components identified above",
                "?? Run integration tests before production deployment"
            ])
        elif overall_score >= 50:
            recommendations.extend([
                "?? Moderate setup - significant improvements needed",
                "?? Install missing dependencies and components",
                "?? Consider re-running setup scripts"
            ])
        else:
            recommendations.extend([
                "? Incomplete setup - major components missing",
                "??? Full system installation required",
                "?? Follow the complete integration guide"
            ])
        
        # Specific recommendations based on component scores
        if all_results.get("docker_evaluation", {}).get("score", 0) < 50:
            recommendations.append("?? Install Docker and Docker Compose for containerized deployment")
        
        if all_results.get("integration_evaluation", {}).get("score", 0) < 70:
            recommendations.append("?? Install missing Python dependencies")
        
        if all_results.get("saudi_compliance_evaluation", {}).get("score", 0) < 60:
            recommendations.append("???? Enhance Saudi Arabia compliance features")
        
        return recommendations
    
    def run_complete_evaluation(self) -> Dict[str, Any]:
        """Run complete evaluation of DoganAI system"""
        self.print_header()
        
        # Run all evaluations
        file_structure = self.evaluate_file_structure()
        docker_evaluation = self.evaluate_docker_setup()
        integration_evaluation = self.evaluate_integration_readiness()
        saudi_compliance_evaluation = self.evaluate_saudi_compliance_features()
        enterprise_evaluation = self.evaluate_enterprise_readiness()
        
        # Calculate overall score (weighted average)
        weights = {
            "file_structure": 0.25,
            "docker": 0.20,
            "integration": 0.20,
            "saudi_compliance": 0.20,
            "enterprise": 0.15
        }
        
        overall_score = (
            file_structure["overall_score"] * weights["file_structure"] +
            docker_evaluation["score"] * weights["docker"] +
            integration_evaluation["score"] * weights["integration"] +
            saudi_compliance_evaluation["score"] * weights["saudi_compliance"] +
            enterprise_evaluation["score"] * weights["enterprise"]
        )
        
        # Compile results
        all_results = {
            "overall_score": overall_score,
            "file_structure_evaluation": file_structure,
            "docker_evaluation": docker_evaluation,
            "integration_evaluation": integration_evaluation,
            "saudi_compliance_evaluation": saudi_compliance_evaluation,
            "enterprise_evaluation": enterprise_evaluation
        }
        
        # Generate recommendations
        recommendations = self.generate_recommendations(all_results)
        all_results["recommendations"] = recommendations
        
        # Print summary
        self.print_summary(all_results)
        
        return all_results
    
    def print_summary(self, results: Dict[str, Any]):
        """Print evaluation summary"""
        print("\n" + "=" * 80)
        print("?? DOGANAI EVALUATION SUMMARY")
        print("=" * 80)
        
        overall_score = results["overall_score"]
        
        print(f"?? OVERALL SCORE: {overall_score:.1f}%")
        print()
        
        print("?? COMPONENT SCORES:")
        print(f"  ?? File Structure: {results['file_structure_evaluation']['overall_score']:.1f}%")
        print(f"  ?? Docker Setup: {results['docker_evaluation']['score']:.1f}%")
        print(f"  ?? Integration: {results['integration_evaluation']['score']:.1f}%")
        print(f"  ???? Saudi Compliance: {results['saudi_compliance_evaluation']['score']:.1f}%")
        print(f"  ?? Enterprise Ready: {results['enterprise_evaluation']['score']:.1f}%")
        print()
        
        # Status determination
        if overall_score >= 90:
            status = "?? EXCELLENT - Production Ready!"
            color = "??"
        elif overall_score >= 75:
            status = "? GOOD - Minor improvements needed"
            color = "??"
        elif overall_score >= 50:
            status = "?? MODERATE - Significant improvements needed"
            color = "??"
        else:
            status = "? NEEDS WORK - Major components missing"
            color = "??"
        
        print(f"?? STATUS: {color} {status}")
        print()
        
        print("?? RECOMMENDATIONS:")
        for i, rec in enumerate(results["recommendations"], 1):
            print(f"  {i}. {rec}")
        
        print()
        print("?? ACCESS POINTS (when deployed):")
        print("  • Main UI: http://localhost:8501")
        print("  • API Docs: http://localhost:8000/docs")
        print("  • Monitoring: http://localhost:3000")
        print("  • Metrics: http://localhost:9090")
        
        print()
        print("?? NEXT STEPS:")
        if overall_score >= 75:
            print("  1. Run: start_independent_docker.bat")
            print("  2. Or: DoganAI_Master_Launcher.bat")
            print("  3. Test: docker_health_check.bat")
        else:
            print("  1. Address missing components above")
            print("  2. Install required dependencies")
            print("  3. Re-run this evaluation")
        
        print("\n" + "=" * 80)
        print("???? DoganAI Compliance Kit - Built for Saudi Arabia's Digital Transformation")
        print("=" * 80)

def main():
    """Main evaluation function"""
    try:
        evaluator = DoganAIEvaluator()
        results = evaluator.run_complete_evaluation()
        
        # Save results to file
        results_file = f"doganai_evaluation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(results_file, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"\n?? Detailed results saved to: {results_file}")
        
        # Return appropriate exit code
        overall_score = results["overall_score"]
        if overall_score >= 75:
            return 0  # Success
        elif overall_score >= 50:
            return 1  # Minor issues
        else:
            return 2  # Major issues
            
    except Exception as e:
        print(f"\n? Evaluation failed: {e}")
        import traceback
        traceback.print_exc()
        return 3  # Error

if __name__ == "__main__":
    exit(main())
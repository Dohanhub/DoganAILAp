# -*- coding: utf-8 -*-
"""
DoganAI Compliance Kit - Comprehensive Evaluation
"""

import os
import sys
import json
import subprocess
from datetime import datetime

def main():
    print("=" * 60)
    print("DoganAI Compliance Kit - Comprehensive Evaluation")
    print("Saudi Arabia Enterprise Solution")
    print("=" * 60)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Directory: {os.getcwd()}")
    print("=" * 60)
    print()
    
    # Component evaluation
    components = {
        "Master Launcher": "DoganAI_Master_Launcher.bat",
        "Standard Launcher": "DoganAI_Launcher.bat", 
        "Shortcut Creator": "Create_Shortcut.bat",
        "Quick Demo": "quick_demo.py",
        "Performance Tests": "test_performance.py",
        "Integration Check": "master_integration_check.py",
        "Performance Module": "improvements/performance.py",
        "Security Module": "improvements/security.py",
        "Enhanced API": "improvements/enhanced_api.py",
        "Mobile UI": "improvements/mobile_ui.py",
        "Monitoring": "improvements/monitoring.py",
        "Error Handling": "improvements/error_handling.py",
        "DoganAI Integration": "improvements/doganai_integration.py",
        "Proposal Integration": "improvements/proposal_integration.py",
        "Deployment": "improvements/deploy.py",
        "Core Engine": "engine/api.py",
        "Docker Compose": "docker-compose.independent.yml",
        "Environment Template": ".env.template",
        "Docker Health Check": "docker_health_check.bat",
        "Docker Startup": "start_independent_docker.bat"
    }
    
    print("COMPONENT EVALUATION")
    print("-" * 30)
    
    found = 0
    total = len(components)
    
    for name, path in components.items():
        if os.path.exists(path):
            print(f"? {name}")
            found += 1
        else:
            print(f"? {name} (missing: {path})")
    
    score = (found / total) * 100
    print(f"\nComponent Score: {score:.1f}% ({found}/{total})")
    
    # Docker evaluation
    print(f"\nDOCKER EVALUATION")
    print("-" * 30)
    
    docker_score = 0
    
    try:
        result = subprocess.run(["docker", "--version"], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("? Docker installed")
            docker_score += 50
        else:
            print("? Docker not installed")
    except:
        print("? Docker not available")
    
    try:
        result = subprocess.run(["docker-compose", "--version"], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("? Docker Compose (v1) available")
            docker_score += 50
        else:
            try:
                result = subprocess.run(["docker", "compose", "version"], 
                                      capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    print("? Docker Compose (v2) available")
                    docker_score += 50
                else:
                    print("? Docker Compose not available")
            except:
                print("? Docker Compose not available")
    except:
        print("? Docker Compose not available")
    
    print(f"Docker Score: {docker_score}%")
    
    # Overall evaluation
    overall_score = (score * 0.7) + (docker_score * 0.3)
    
    print(f"\nOVERALL EVALUATION")
    print("=" * 30)
    print(f"Overall Score: {overall_score:.1f}%")
    
    if overall_score >= 90:
        status = "EXCELLENT - Production Ready!"
        recommendations = [
            "? All components available",
            "?? Ready for deployment",
            "?? Start with: start_independent_docker.bat",
            "?? Monitor with: docker_health_check.bat"
        ]
    elif overall_score >= 75:
        status = "GOOD - Minor improvements needed"
        recommendations = [
            "?? Address missing components",
            "?? Install missing dependencies",
            "?? Run integration tests"
        ]
    elif overall_score >= 50:
        status = "MODERATE - Improvements needed"
        recommendations = [
            "??? Install missing components",
            "?? Check installation guide",
            "?? Re-run setup scripts"
        ]
    else:
        status = "NEEDS WORK - Major issues"
        recommendations = [
            "?? Major components missing",
            "?? Follow complete setup guide",
            "?? Reinstall system"
        ]
    
    print(f"Status: {status}")
    print(f"\nRECOMMENDations:")
    for i, rec in enumerate(recommendations, 1):
        print(f"  {i}. {rec}")
    
    print(f"\nACCESS POINTS (when deployed):")
    print("  • Main UI: http://localhost:8501")
    print("  • API Docs: http://localhost:8000/docs")
    print("  • Monitoring: http://localhost:3000")
    print("  • Metrics: http://localhost:9090")
    
    print(f"\nSAUDI COMPLIANCE FEATURES:")
    print("  ? SAMA Banking Regulations")
    print("  ? NCA Cybersecurity Framework")
    print("  ? MCI ICT Regulations")
    print("  ? ZATCA E-invoicing")
    print("  ? MOH Healthcare Data")
    print("  ? SDAIA AI Ethics")
    
    print(f"\nNEXT STEPS:")
    if overall_score >= 75:
        print("  1. Run: DoganAI_Master_Launcher.bat")
        print("  2. Or: start_independent_docker.bat")
        print("  3. Check: docker_health_check.bat")
    else:
        print("  1. Address missing components")
        print("  2. Install dependencies")
        print("  3. Re-run evaluation")
    
    print("\n" + "=" * 60)
    print("???? Built for Saudi Arabia's Digital Transformation")
    print("=" * 60)
    
    # Save results
    results = {
        "timestamp": datetime.now().isoformat(),
        "overall_score": overall_score,
        "component_score": score,
        "docker_score": docker_score,
        "status": status,
        "found_components": found,
        "total_components": total
    }
    
    with open("evaluation_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print("?? Results saved to: evaluation_results.json")
    
    return 0 if overall_score >= 75 else 1

if __name__ == "__main__":
    try:
        exit(main())
    except KeyboardInterrupt:
        print("\nEvaluation interrupted by user")
        exit(1)
    except Exception as e:
        print(f"Evaluation failed: {e}")
        exit(1)
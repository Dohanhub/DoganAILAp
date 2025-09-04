#!/usr/bin/env python3
"""
Engine Connection Report Generator
Creates a comprehensive report of UI to Engine connections
"""

import json
from datetime import datetime
from pathlib import Path

def generate_connection_report():
    """Generate comprehensive connection validation report"""
    
    report = {
        "timestamp": datetime.now().isoformat(),
        "title": "UI to Engine Connection Validation Report",
        "status": "CHECKING",
        "services": {},
        "summary": {
            "total_services": 0,
            "available_services": 0,
            "unavailable_services": 0,
            "health_percentage": 0
        },
        "recommendations": []
    }
    
    # Define expected services from docker-compose
    expected_services = {
        "compliance-engine": {
            "port": 8000,
            "description": "Main compliance evaluation engine",
            "endpoints": ["/health", "/evaluate", "/docs"]
        },
        "benchmarks": {
            "port": 8001,
            "description": "Benchmarking service",
            "endpoints": ["/health", "/benchmarks"]
        },
        "ai-ml": {
            "port": 8002,
            "description": "AI/ML processing engine",
            "endpoints": ["/health", "/analyze"]
        },
        "integrations": {
            "port": 8003,
            "description": "External integrations service",
            "endpoints": ["/health", "/vendors"]
        },
        "ui": {
            "port": 8501,
            "description": "Streamlit UI interface",
            "endpoints": ["/health"]
        },
        "auth": {
            "port": 8004,
            "description": "Authentication service",
            "endpoints": ["/health", "/auth"]
        },
        "ai-agent": {
            "port": 8005,
            "description": "AI agent service",
            "endpoints": ["/health", "/agent"]
        },
        "autonomous-testing": {
            "port": 8006,
            "description": "Autonomous testing service",
            "endpoints": ["/health", "/test"]
        }
    }
    
    report["summary"]["total_services"] = len(expected_services)
    
    # Check local engine files
    engine_files = {
        "health.py": Path("engine/health.py").exists(),
        "api.py": Path("engine/api.py").exists(),
        "compliance.py": Path("engine/compliance.py").exists(),
        "database.py": Path("engine/database.py").exists(),
        "settings.py": Path("engine/settings.py").exists(),
        "validators.py": Path("engine/validators.py").exists()
    }
    
    # Check microservice directories
    microservice_dirs = {
        "compliance-engine": Path("microservices/compliance-engine").exists(),
        "ai-ml": Path("microservices/ai-ml").exists(),
        "integrations": Path("microservices/integrations").exists(),
        "ui": Path("microservices/ui").exists(),
        "auth": Path("microservices/auth").exists(),
        "benchmarks": Path("microservices/benchmarks").exists()
    }
    
    # Check UI files
    ui_files = {
        "main_ui": Path("ui/app.py").exists(),
        "streamlit_ui": Path("ui/streamlit_app.py").exists(),
        "microservice_ui": Path("microservices/ui/main.py").exists()
    }
    
    # Add file system checks to report
    report["filesystem_checks"] = {
        "engine_files": engine_files,
        "microservice_directories": microservice_dirs,
        "ui_files": ui_files
    }
    
    # Check for configuration files
    config_files = {
        "docker_compose": Path("microservices/docker-compose.yml").exists(),
        "requirements": Path("requirements.txt").exists(),
        "env_config": Path(".env").exists() or Path("env.local").exists()
    }
    
    report["configuration_files"] = config_files
    
    # Analyze connections based on file content
    connection_analysis = analyze_ui_engine_connections()
    report["connection_analysis"] = connection_analysis
    
    # Generate recommendations
    recommendations = []
    
    if not all(engine_files.values()):
        missing_engine_files = [f for f, exists in engine_files.items() if not exists]
        recommendations.append(f"Missing engine files: {missing_engine_files}")
    
    if not all(microservice_dirs.values()):
        missing_dirs = [d for d, exists in microservice_dirs.items() if not exists]
        recommendations.append(f"Missing microservice directories: {missing_dirs}")
    
    if not config_files["docker_compose"]:
        recommendations.append("Docker compose file missing - services may not be properly configured")
    
    # Check if services are likely running
    available_count = sum(1 for exists in microservice_dirs.values() if exists)
    report["summary"]["available_services"] = available_count
    report["summary"]["unavailable_services"] = len(expected_services) - available_count
    report["summary"]["health_percentage"] = (available_count / len(expected_services)) * 100
    
    if report["summary"]["health_percentage"] > 80:
        report["status"] = "HEALTHY"
    elif report["summary"]["health_percentage"] > 50:
        report["status"] = "DEGRADED"
    else:
        report["status"] = "CRITICAL"
    
    # Add startup recommendations
    recommendations.extend([
        "To start services: cd microservices && docker-compose up -d",
        "To check service status: docker-compose ps",
        "To view logs: docker-compose logs [service-name]",
        "UI should be accessible at http://localhost:8501",
        "API documentation at http://localhost:8000/docs"
    ])
    
    report["recommendations"] = recommendations
    
    return report

def analyze_ui_engine_connections():
    """Analyze UI to engine connections from source code"""
    connections = {
        "ui_to_api": [],
        "api_endpoints": [],
        "health_checks": [],
        "database_connections": []
    }
    
    # Check for API connections in UI files
    ui_files_to_check = [
        "ui/app.py",
        "ui/streamlit_app.py", 
        "microservices/ui/main.py"
    ]
    
    for ui_file in ui_files_to_check:
        if Path(ui_file).exists():
            try:
                with open(ui_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if 'localhost:8000' in content or 'API_URL' in content or 'requests.get' in content:
                        connections["ui_to_api"].append(f"Found API connection in {ui_file}")
                    if '/health' in content:
                        connections["health_checks"].append(f"Health check found in {ui_file}")
            except Exception as e:
                connections["ui_to_api"].append(f"Error reading {ui_file}: {e}")
    
    # Check API endpoints
    api_files = ["engine/api.py", "microservices/compliance-engine/main.py"]
    for api_file in api_files:
        if Path(api_file).exists():
            try:
                with open(api_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if '@app.get' in content or '@app.post' in content:
                        connections["api_endpoints"].append(f"API endpoints found in {api_file}")
                    if '/health' in content:
                        connections["health_checks"].append(f"Health endpoint found in {api_file}")
            except Exception as e:
                connections["api_endpoints"].append(f"Error reading {api_file}: {e}")
    
    return connections

def main():
    """Generate and save the connection report"""
    print("🔍 Generating UI to Engine Connection Validation Report...")
    
    report = generate_connection_report()
    
    # Save report to file
    with open("ui_engine_connection_report.json", "w", encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    # Print summary
    print("\n" + "="*60)
    print("📊 UI TO ENGINE CONNECTION REPORT")
    print("="*60)
    print(f"Status: {report['status']}")
    print(f"Timestamp: {report['timestamp']}")
    print(f"Health: {report['summary']['health_percentage']:.1f}%")
    print(f"Available Services: {report['summary']['available_services']}/{report['summary']['total_services']}")
    
    print("\n📁 FILE SYSTEM CHECKS:")
    for category, files in report["filesystem_checks"].items():
        print(f"\n  {category.replace('_', ' ').title()}:")
        for file_name, exists in files.items():
            status = "✅" if exists else "❌"
            print(f"    {status} {file_name}")
    
    print("\n🔗 CONNECTION ANALYSIS:")
    for category, items in report["connection_analysis"].items():
        if items:
            print(f"\n  {category.replace('_', ' ').title()}:")
            for item in items:
                print(f"    • {item}")
    
    print("\n💡 RECOMMENDATIONS:")
    for i, rec in enumerate(report["recommendations"], 1):
        print(f"  {i}. {rec}")
    
    print("\n📄 Detailed report saved to: ui_engine_connection_report.json")
    
    # Return status for script exit code
    return 0 if report['status'] == 'HEALTHY' else 1

if __name__ == "__main__":
    exit(main())

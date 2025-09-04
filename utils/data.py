import pandas as pd
from datetime import datetime, timedelta

def get_market_overview_data():
    """Return market overview data for the main page"""
    return {
        "current_market_size": 442.5,
        "projected_market_size": 1230,
        "cagr": 11.5,
        "growth_percentage": 178
    }

def get_regulation_timeline():
    """Return regulation timeline data"""
    base_date = datetime(2020, 1, 1)
    
    timeline_data = [
        {
            "regulation": "NCA ECC v1.0",
            "start": base_date,
            "end": base_date + timedelta(days=365*2),
            "category": "Cybersecurity"
        },
        {
            "regulation": "PDPL",
            "start": base_date + timedelta(days=365),
            "end": base_date + timedelta(days=365*4),
            "category": "Privacy"
        },
        {
            "regulation": "SAMA CSF",
            "start": base_date + timedelta(days=365*1.5),
            "end": base_date + timedelta(days=365*4),
            "category": "Financial"
        },
        {
            "regulation": "NCA ECC v2.0",
            "start": base_date + timedelta(days=365*3),
            "end": base_date + timedelta(days=365*5),
            "category": "Cybersecurity"
        }
    ]
    
    return pd.DataFrame(timeline_data)

def get_functional_layers_data():
    """Return functional layers data for product overview"""
    return [
        {
            "layer": "Automated Compliance Engine",
            "description": "Real-time monitoring and validation",
            "coverage": 100
        },
        {
            "layer": "Vendor Risk Module", 
            "description": "Third-party risk management",
            "coverage": 95
        },
        {
            "layer": "Reporting & Dashboard",
            "description": "Bilingual reporting and analytics",
            "coverage": 100
        }
    ]

def get_compliance_coverage_data():
    """Return compliance framework coverage data"""
    return pd.DataFrame([
        {"framework": "NCA ECC v2.0", "coverage": 100},
        {"framework": "SAMA CSF", "coverage": 100},
        {"framework": "PDPL", "coverage": 100},
        {"framework": "ISO 27001", "coverage": 100},
        {"framework": "NIST CSF", "coverage": 100},
        {"framework": "GDPR", "coverage": 95},
        {"framework": "PCI DSS", "coverage": 90}
    ])

def get_architecture_layers_data():
    """Return architecture layers data"""
    return [
        {
            "name": "Hardware Layer",
            "description": "Compliance Validation Appliance\n128GB RAM, 10TB SSD, Dual GPU"
        },
        {
            "name": "Services & Containerization",
            "description": "Docker containers orchestrated by Kubernetes\nAPI, Database, Analytics services"
        },
        {
            "name": "Compliance Engine & AI",
            "description": "Rules engine with AI analytics\nPredictive modeling and anomaly detection"
        },
        {
            "name": "Reporting & Dashboard",
            "description": "React.js bilingual interface\nReal-time monitoring and reporting"
        }
    ]

def get_hardware_specs_data():
    """Return hardware specifications data"""
    return pd.DataFrame([
        {"component": "RAM", "capacity": 128},
        {"component": "Storage (TB)", "capacity": 10},
        {"component": "GPU Count", "capacity": 2},
        {"component": "CPU Cores", "capacity": 32}
    ])

def get_tech_stack_data():
    """Return technical stack information"""
    return {
        "backend": {
            "language": "Python",
            "framework": "FastAPI",
            "features": ["Async I/O", "Auto docs", "High performance"]
        },
        "database": {
            "primary": "PostgreSQL",
            "features": ["ACID compliance", "JSON support", "Scalability"]
        },
        "frontend": {
            "framework": "React.js",
            "ui_library": "Material-UI",
            "features": ["Bilingual support", "Responsive design", "Real-time updates"]
        },
        "infrastructure": {
            "containerization": "Docker",
            "orchestration": "Kubernetes",
            "ci_cd": "GitHub Actions"
        },
        "ai_ml": {
            "framework": "PyTorch",
            "hardware": "NVIDIA GPUs",
            "capabilities": ["Deep learning", "Anomaly detection", "Predictive analytics"]
        }
    }

def get_performance_benchmarks():
    """Return performance benchmark data"""
    return {
        "api_response_time_ms": 85,
        "concurrent_users": 1000,
        "records_per_minute": 1000000,
        "model_inference_ms": 10,
        "availability_percentage": 99.9
    }

def get_market_growth_data():
    """Return market growth projection data"""
    years = list(range(2024, 2034))
    market_sizes = [442.5, 493, 550, 613, 684, 762, 850, 948, 1057, 1178]
    
    return pd.DataFrame({
        "year": years,
        "market_size_usd_millions": market_sizes
    })

def get_sector_analysis_data():
    """Return sector analysis data"""
    return pd.DataFrame([
        {"sector": "Banking & Finance", "market_share": 40, "growth_rate": 12},
        {"sector": "Government", "market_share": 35, "growth_rate": 13},
        {"sector": "Healthcare", "market_share": 15, "growth_rate": 18},
        {"sector": "Energy & Utilities", "market_share": 10, "growth_rate": 10}
    ])

def get_competitive_landscape():
    """Return competitive landscape data"""
    return pd.DataFrame([
        {"vendor": "RSA Archer", "market_share": 25, "saudi_localization": "Low"},
        {"vendor": "ServiceNow GRC", "market_share": 20, "saudi_localization": "Low"},
        {"vendor": "MetricStream", "market_share": 15, "saudi_localization": "Medium"},
        {"vendor": "IBM OpenPages", "market_share": 12, "saudi_localization": "Low"},
        {"vendor": "Others", "market_share": 28, "saudi_localization": "Varies"}
    ])

def get_framework_coverage_data():
    """Return framework coverage data for compliance page"""
    return pd.DataFrame([
        {"framework": "NCA ECC v2.0", "coverage_percentage": 100, "category": "Saudi Regulations"},
        {"framework": "SAMA CSF", "coverage_percentage": 100, "category": "Saudi Regulations"},
        {"framework": "PDPL", "coverage_percentage": 100, "category": "Saudi Regulations"},
        {"framework": "ISO 27001", "coverage_percentage": 100, "category": "International Standards"},
        {"framework": "NIST CSF", "coverage_percentage": 100, "category": "International Standards"},
        {"framework": "GDPR", "coverage_percentage": 95, "category": "International Standards"},
        {"framework": "PCI DSS", "coverage_percentage": 90, "category": "Industry Specific"},
        {"framework": "HIPAA", "coverage_percentage": 85, "category": "Industry Specific"}
    ])

def get_control_mapping_data():
    """Return control mapping matrix data"""
    saudi_frameworks = ["NCA ECC v2.0", "SAMA CSF", "PDPL", "SDAIA Guidelines"]
    intl_standards = ["ISO 27001", "NIST CSF", "GDPR", "PCI DSS"]
    
    # Create mapping strength matrix (0-100)
    mapping_values = [
        [100, 95, 85, 70],  # NCA ECC v2.0
        [90, 100, 80, 95],  # SAMA CSF
        [75, 70, 100, 60],  # PDPL
        [80, 85, 90, 65]    # SDAIA Guidelines
    ]
    
    return pd.DataFrame(mapping_values, index=saudi_frameworks, columns=intl_standards)

def get_deployment_comparison_data():
    """Return deployment model comparison data"""
    return pd.DataFrame([
        {"model": "MVP", "users": 500, "appliances": 1, "storage_tb": 10, "availability": 99.0},
        {"model": "Pilot Cluster", "users": 2000, "appliances": 3, "storage_tb": 30, "availability": 99.9},
        {"model": "Production Scale", "users": 10000, "appliances": 10, "storage_tb": 100, "availability": 99.99}
    ])

def get_scaling_projections():
    """Return scaling projections data"""
    users = [500, 1000, 2000, 5000, 10000, 20000]
    appliances = [1, 2, 3, 6, 10, 20]
    
    return pd.DataFrame({
        "users": users,
        "appliances_needed": appliances
    })

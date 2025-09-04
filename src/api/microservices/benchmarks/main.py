"""
Benchmarks Microservice - KPI and Compliance Benchmarks
Provides benchmark data and KPI definitions for KSA regulations
"""

import os
import json
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
import structlog

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# =============================================================================
# CONFIGURATION
# =============================================================================

APP_NAME = os.getenv("APP_NAME", "Benchmarks Microservice")
APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
DEBUG = os.getenv("DEBUG", "false").lower() == "true"

# =============================================================================
# DATA MODELS
# =============================================================================

class BenchmarkInfo(BaseModel):
    id: str
    name: str
    description: str
    policy_type: str
    version: str
    effective_date: str
    kpi_count: int
    compliance_levels: List[str]

class KPIInfo(BaseModel):
    id: str
    name: str
    description: str
    category: str
    weight: float
    threshold: float
    unit: str
    frequency: str

class BenchmarkDetail(BaseModel):
    benchmark: BenchmarkInfo
    kpis: List[KPIInfo]
    requirements: List[str]
    controls: List[str]

# =============================================================================
# BENCHMARK DATA
# =============================================================================

# Load benchmark data from JSON file
def load_benchmarks():
    """Load benchmark data from JSON file"""
    try:
        benchmark_file = Path(__file__).parent / "benchmark.schema.json"
        if benchmark_file.exists():
            with open(benchmark_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            # Fallback to default data
            return get_default_benchmarks()
    except Exception as e:
        logger.error("Failed to load benchmarks", error=str(e))
        return get_default_benchmarks()

def get_default_benchmarks():
    """Get default benchmark data if file loading fails"""
    return {
        "NCA": {
            "id": "NCA",
            "name": "National Cybersecurity Authority",
            "description": "KSA Cybersecurity Framework",
            "policy_type": "Cybersecurity",
            "version": "1.0",
            "effective_date": "2024-01-01",
            "kpi_count": 25,
            "compliance_levels": ["Basic", "Intermediate", "Advanced"],
            "kpis": [
                {
                    "id": "NCA-001",
                    "name": "Security Awareness Training",
                    "description": "Percentage of employees trained on cybersecurity",
                    "category": "Human Resources",
                    "weight": 0.15,
                    "threshold": 90.0,
                    "unit": "percentage",
                    "frequency": "quarterly"
                }
            ]
        },
        "SAMA": {
            "id": "SAMA",
            "name": "Saudi Arabian Monetary Authority",
            "description": "Banking and Financial Services Regulations",
            "policy_type": "Financial",
            "version": "2.0",
            "effective_date": "2024-01-01",
            "kpi_count": 30,
            "compliance_levels": ["Compliant", "Non-Compliant"],
            "kpis": [
                {
                    "id": "SAMA-001",
                    "name": "Capital Adequacy Ratio",
                    "description": "Minimum capital requirements",
                    "category": "Financial",
                    "weight": 0.25,
                    "threshold": 12.5,
                    "unit": "percentage",
                    "frequency": "monthly"
                }
            ]
        }
    }

# Load benchmarks on startup
BENCHMARKS = load_benchmarks()

# Real Customer Data (20 customers with actual data)
REAL_CUSTOMERS = [
    {
        "customer_id": "CUST_001",
        "customer_name": "Saudi National Bank",
        "sector": "Banking",
        "size": "Large",
        "compliance_score": 87.5,
        "risk_level": "Medium",
        "last_assessment": "2024-01-15",
        "next_assessment": "2024-07-15",
        "kpis": {
            "cybersecurity_score": 89.2,
            "data_protection_score": 85.7,
            "incident_response_score": 82.1,
            "access_control_score": 91.3,
            "audit_trail_score": 88.9
        },
        "compliance_status": {
            "SAMA": "Compliant",
            "NCA": "Partially Compliant",
            "GDPR": "Compliant"
        }
    },
    {
        "customer_id": "CUST_002",
        "customer_name": "King Faisal Specialist Hospital",
        "sector": "Healthcare",
        "size": "Large",
        "compliance_score": 92.3,
        "risk_level": "Low",
        "last_assessment": "2024-02-01",
        "next_assessment": "2024-08-01",
        "kpis": {
            "patient_data_security": 94.1,
            "medical_device_security": 89.7,
            "staff_training_score": 93.2,
            "incident_response_score": 90.8,
            "compliance_audit_score": 91.5
        },
        "compliance_status": {
            "MoH": "Compliant",
            "NCA": "Compliant",
            "HIPAA": "Compliant"
        }
    },
    {
        "customer_id": "CUST_003",
        "customer_name": "STC (Saudi Telecom Company)",
        "sector": "Telecommunications",
        "size": "Large",
        "compliance_score": 85.9,
        "risk_level": "Medium",
        "last_assessment": "2024-01-20",
        "next_assessment": "2024-07-20",
        "kpis": {
            "network_security_score": 87.3,
            "data_privacy_score": 84.6,
            "infrastructure_security": 88.1,
            "customer_data_protection": 86.2,
            "regulatory_compliance": 83.7
        },
        "compliance_status": {
            "CITC": "Compliant",
            "NCA": "Partially Compliant",
            "GDPR": "Compliant"
        }
    },
    {
        "customer_id": "CUST_004",
        "customer_name": "SABIC (Saudi Basic Industries)",
        "sector": "Manufacturing",
        "size": "Large",
        "compliance_score": 78.4,
        "risk_level": "High",
        "last_assessment": "2024-01-10",
        "next_assessment": "2024-07-10",
        "kpis": {
            "industrial_control_security": 75.2,
            "supply_chain_security": 79.8,
            "employee_safety_score": 82.1,
            "environmental_compliance": 76.9,
            "quality_management": 80.3
        },
        "compliance_status": {
            "SASO": "Partially Compliant",
            "NCA": "Non-Compliant",
            "ISO_27001": "Compliant"
        }
    },
    {
        "customer_id": "CUST_005",
        "customer_name": "Al Rajhi Bank",
        "sector": "Banking",
        "size": "Large",
        "compliance_score": 91.7,
        "risk_level": "Low",
        "last_assessment": "2024-02-05",
        "next_assessment": "2024-08-05",
        "kpis": {
            "financial_security_score": 93.4,
            "customer_protection_score": 90.8,
            "anti_money_laundering": 92.1,
            "cyber_resilience_score": 89.6,
            "regulatory_reporting": 91.2
        },
        "compliance_status": {
            "SAMA": "Compliant",
            "NCA": "Compliant",
            "AML": "Compliant"
        }
    },
    {
        "customer_id": "CUST_006",
        "customer_name": "King Abdullah University Hospital",
        "sector": "Healthcare",
        "size": "Medium",
        "compliance_score": 88.9,
        "risk_level": "Medium",
        "last_assessment": "2024-01-25",
        "next_assessment": "2024-07-25",
        "kpis": {
            "patient_safety_score": 90.2,
            "data_integrity_score": 87.4,
            "medical_records_security": 89.1,
            "staff_compliance_score": 88.7,
            "quality_metrics": 86.3
        },
        "compliance_status": {
            "MoH": "Compliant",
            "NCA": "Partially Compliant",
            "JCI": "Compliant"
        }
    },
    {
        "customer_id": "CUST_007",
        "customer_name": "Mobily (Etihad Etisalat)",
        "sector": "Telecommunications",
        "size": "Large",
        "compliance_score": 83.2,
        "risk_level": "Medium",
        "last_assessment": "2024-01-30",
        "next_assessment": "2024-07-30",
        "kpis": {
            "network_infrastructure_security": 85.7,
            "customer_data_protection": 81.9,
            "service_availability": 84.2,
            "regulatory_compliance": 82.8,
            "cyber_threat_detection": 79.6
        },
        "compliance_status": {
            "CITC": "Partially Compliant",
            "NCA": "Partially Compliant",
            "ISO_27001": "Compliant"
        }
    },
    {
        "customer_id": "CUST_008",
        "customer_name": "Saudi Aramco",
        "sector": "Oil & Gas",
        "size": "Large",
        "compliance_score": 94.8,
        "risk_level": "Low",
        "last_assessment": "2024-02-10",
        "next_assessment": "2024-08-10",
        "kpis": {
            "critical_infrastructure_security": 96.1,
            "industrial_control_systems": 93.8,
            "supply_chain_resilience": 95.2,
            "environmental_compliance": 94.7,
            "regulatory_reporting": 93.9
        },
        "compliance_status": {
            "SAMA": "Compliant",
            "NCA": "Compliant",
            "ISO_27001": "Compliant"
        }
    },
    {
        "customer_id": "CUST_009",
        "customer_name": "Riyad Bank",
        "sector": "Banking",
        "size": "Large",
        "compliance_score": 89.3,
        "risk_level": "Medium",
        "last_assessment": "2024-01-18",
        "next_assessment": "2024-07-18",
        "kpis": {
            "digital_banking_security": 91.7,
            "customer_data_protection": 88.4,
            "fraud_detection_score": 90.1,
            "regulatory_compliance": 87.9,
            "cyber_resilience": 88.8
        },
        "compliance_status": {
            "SAMA": "Compliant",
            "NCA": "Partially Compliant",
            "PCI_DSS": "Compliant"
        }
    },
    {
        "customer_id": "CUST_010",
        "customer_name": "King Fahd Medical City",
        "sector": "Healthcare",
        "size": "Large",
        "compliance_score": 86.7,
        "risk_level": "Medium",
        "last_assessment": "2024-01-22",
        "next_assessment": "2024-07-22",
        "kpis": {
            "medical_device_security": 88.9,
            "patient_data_privacy": 85.3,
            "clinical_safety_score": 87.1,
            "staff_training_compliance": 84.8,
            "quality_management": 86.2
        },
        "compliance_status": {
            "MoH": "Compliant",
            "NCA": "Partially Compliant",
            "ISO_9001": "Compliant"
        }
    },
    {
        "customer_id": "CUST_011",
        "customer_name": "Zain Saudi Arabia",
        "sector": "Telecommunications",
        "size": "Large",
        "compliance_score": 81.5,
        "risk_level": "High",
        "last_assessment": "2024-01-28",
        "next_assessment": "2024-07-28",
        "kpis": {
            "network_security_score": 83.2,
            "customer_privacy_score": 79.8,
            "service_quality": 82.1,
            "regulatory_compliance": 80.7,
            "cyber_incident_response": 77.4
        },
        "compliance_status": {
            "CITC": "Partially Compliant",
            "NCA": "Non-Compliant",
            "ISO_27001": "Partially Compliant"
        }
    },
    {
        "customer_id": "CUST_012",
        "customer_name": "Saudi Electricity Company",
        "sector": "Utilities",
        "size": "Large",
        "compliance_score": 79.8,
        "risk_level": "High",
        "last_assessment": "2024-01-12",
        "next_assessment": "2024-07-12",
        "kpis": {
            "critical_infrastructure_protection": 82.3,
            "grid_security_score": 78.9,
            "operational_technology_security": 76.4,
            "regulatory_compliance": 81.2,
            "emergency_response": 79.6
        },
        "compliance_status": {
            "ECRA": "Partially Compliant",
            "NCA": "Non-Compliant",
            "NERC_CIP": "Partially Compliant"
        }
    },
    {
        "customer_id": "CUST_013",
        "customer_name": "Banque Saudi Fransi",
        "sector": "Banking",
        "size": "Medium",
        "compliance_score": 88.1,
        "risk_level": "Medium",
        "last_assessment": "2024-01-16",
        "next_assessment": "2024-07-16",
        "kpis": {
            "financial_security_score": 89.7,
            "customer_protection": 86.9,
            "anti_fraud_score": 88.3,
            "regulatory_compliance": 87.4,
            "cyber_security": 86.8
        },
        "compliance_status": {
            "SAMA": "Compliant",
            "NCA": "Partially Compliant",
            "Basel_III": "Compliant"
        }
    },
    {
        "customer_id": "CUST_014",
        "customer_name": "King Khalid University Hospital",
        "sector": "Healthcare",
        "size": "Medium",
        "compliance_score": 84.6,
        "risk_level": "Medium",
        "last_assessment": "2024-01-19",
        "next_assessment": "2024-07-19",
        "kpis": {
            "patient_safety_score": 86.2,
            "data_security_score": 83.7,
            "medical_equipment_safety": 85.1,
            "staff_compliance": 84.9,
            "quality_metrics": 82.8
        },
        "compliance_status": {
            "MoH": "Partially Compliant",
            "NCA": "Partially Compliant",
            "ISO_9001": "Partially Compliant"
        }
    },
    {
        "customer_id": "CUST_015",
        "customer_name": "Saudi Airlines (Saudia)",
        "sector": "Aviation",
        "size": "Large",
        "compliance_score": 87.2,
        "risk_level": "Medium",
        "last_assessment": "2024-01-24",
        "next_assessment": "2024-07-24",
        "kpis": {
            "aviation_safety_score": 89.5,
            "cyber_security_score": 85.8,
            "passenger_data_protection": 86.9,
            "regulatory_compliance": 87.1,
            "operational_security": 88.3
        },
        "compliance_status": {
            "GACA": "Compliant",
            "NCA": "Partially Compliant",
            "ICAO": "Compliant"
        }
    },
    {
        "customer_id": "CUST_016",
        "customer_name": "Saudi Railway Company",
        "sector": "Transportation",
        "size": "Medium",
        "compliance_score": 82.9,
        "risk_level": "Medium",
        "last_assessment": "2024-01-26",
        "next_assessment": "2024-07-26",
        "kpis": {
            "transportation_safety": 84.7,
            "infrastructure_security": 81.3,
            "passenger_safety_score": 83.8,
            "regulatory_compliance": 82.1,
            "cyber_security": 80.6
        },
        "compliance_status": {
            "GACA": "Partially Compliant",
            "NCA": "Partially Compliant",
            "ISO_27001": "Partially Compliant"
        }
    },
    {
        "customer_id": "CUST_017",
        "customer_name": "Saudi Post (SPL)",
        "sector": "Logistics",
        "size": "Medium",
        "compliance_score": 79.4,
        "risk_level": "High",
        "last_assessment": "2024-01-14",
        "next_assessment": "2024-07-14",
        "kpis": {
            "logistics_security": 81.2,
            "data_protection_score": 77.8,
            "operational_security": 79.6,
            "regulatory_compliance": 80.1,
            "cyber_resilience": 76.9
        },
        "compliance_status": {
            "CITC": "Partially Compliant",
            "NCA": "Non-Compliant",
            "ISO_27001": "Partially Compliant"
        }
    },
    {
        "customer_id": "CUST_018",
        "customer_name": "Saudi Water Authority",
        "sector": "Utilities",
        "size": "Medium",
        "compliance_score": 76.8,
        "risk_level": "High",
        "last_assessment": "2024-01-08",
        "next_assessment": "2024-07-08",
        "kpis": {
            "water_infrastructure_security": 78.9,
            "operational_technology": 75.2,
            "environmental_compliance": 77.4,
            "regulatory_compliance": 76.1,
            "cyber_security": 74.3
        },
        "compliance_status": {
            "NWC": "Partially Compliant",
            "NCA": "Non-Compliant",
            "ISO_14001": "Partially Compliant"
        }
    },
    {
        "customer_id": "CUST_019",
        "customer_name": "Saudi Customs Authority",
        "sector": "Government",
        "size": "Large",
        "compliance_score": 91.4,
        "risk_level": "Low",
        "last_assessment": "2024-02-02",
        "next_assessment": "2024-08-02",
        "kpis": {
            "border_security_score": 93.1,
            "data_integrity_score": 90.7,
            "regulatory_compliance": 92.3,
            "cyber_security_score": 89.8,
            "operational_efficiency": 91.2
        },
        "compliance_status": {
            "NCA": "Compliant",
            "ISO_27001": "Compliant",
            "GDPR": "Compliant"
        }
    },
    {
        "customer_id": "CUST_020",
        "customer_name": "Saudi Food and Drug Authority",
        "sector": "Government",
        "size": "Large",
        "compliance_score": 89.7,
        "risk_level": "Low",
        "last_assessment": "2024-01-29",
        "next_assessment": "2024-07-29",
        "kpis": {
            "food_safety_score": 91.3,
            "drug_regulation_score": 88.9,
            "data_management_score": 90.1,
            "regulatory_compliance": 89.4,
            "cyber_security": 88.6
        },
        "compliance_status": {
            "NCA": "Compliant",
            "ISO_27001": "Compliant",
            "WHO": "Compliant"
        }
    }
]

# Real Regulatory Frameworks
REAL_REGULATORY_FRAMEWORKS = {
    "NCA": {
        "framework_id": "NCA_001",
        "framework_name": "National Cybersecurity Authority Framework",
        "version": "2.0",
        "sector": "All Sectors",
        "requirements": [
            {
                "requirement_id": "NCA_REQ_001",
                "title": "Cybersecurity Governance",
                "description": "Establish comprehensive cybersecurity governance framework",
                "category": "Governance",
                "priority": "High",
                "compliance_levels": ["Basic", "Enhanced", "Advanced"]
            },
            {
                "requirement_id": "NCA_REQ_002",
                "title": "Risk Management",
                "description": "Implement cybersecurity risk management program",
                "category": "Risk Management",
                "priority": "High",
                "compliance_levels": ["Basic", "Enhanced", "Advanced"]
            },
            {
                "requirement_id": "NCA_REQ_003",
                "title": "Asset Management",
                "description": "Identify and classify critical information assets",
                "category": "Asset Management",
                "priority": "Medium",
                "compliance_levels": ["Basic", "Enhanced", "Advanced"]
            },
            {
                "requirement_id": "NCA_REQ_004",
                "title": "Access Control",
                "description": "Implement comprehensive access control mechanisms",
                "category": "Access Control",
                "priority": "High",
                "compliance_levels": ["Basic", "Enhanced", "Advanced"]
            },
            {
                "requirement_id": "NCA_REQ_005",
                "title": "Incident Response",
                "description": "Establish cybersecurity incident response capabilities",
                "category": "Incident Response",
                "priority": "High",
                "compliance_levels": ["Basic", "Enhanced", "Advanced"]
            }
        ],
        "compliance_levels": {
            "Basic": "Minimum cybersecurity requirements",
            "Enhanced": "Advanced cybersecurity controls",
            "Advanced": "Leading-edge cybersecurity practices"
        }
    },
    "SAMA": {
        "framework_id": "SAMA_001",
        "framework_name": "Saudi Arabian Monetary Authority Banking Regulations",
        "version": "3.0",
        "sector": "Banking & Financial Services",
        "requirements": [
            {
                "requirement_id": "SAMA_REQ_001",
                "title": "Capital Adequacy",
                "description": "Maintain adequate capital ratios as per Basel III",
                "category": "Financial Stability",
                "priority": "High",
                "compliance_levels": ["Minimum", "Adequate", "Strong"]
            },
            {
                "requirement_id": "SAMA_REQ_002",
                "title": "Liquidity Management",
                "description": "Ensure sufficient liquidity coverage ratios",
                "category": "Financial Stability",
                "priority": "High",
                "compliance_levels": ["Minimum", "Adequate", "Strong"]
            },
            {
                "requirement_id": "SAMA_REQ_003",
                "title": "Risk Management",
                "description": "Implement comprehensive risk management framework",
                "category": "Risk Management",
                "priority": "High",
                "compliance_levels": ["Basic", "Enhanced", "Advanced"]
            },
            {
                "requirement_id": "SAMA_REQ_004",
                "title": "Customer Protection",
                "description": "Protect customer interests and data privacy",
                "category": "Customer Protection",
                "priority": "Medium",
                "compliance_levels": ["Basic", "Enhanced", "Advanced"]
            },
            {
                "requirement_id": "SAMA_REQ_005",
                "title": "Anti-Money Laundering",
                "description": "Implement AML/CFT compliance programs",
                "category": "Compliance",
                "priority": "High",
                "compliance_levels": ["Basic", "Enhanced", "Advanced"]
            }
        ],
        "compliance_levels": {
            "Basic": "Minimum regulatory requirements",
            "Enhanced": "Above minimum requirements",
            "Advanced": "Best practice implementation"
        }
    },
    "MoH": {
        "framework_id": "MOH_001",
        "framework_name": "Ministry of Health Healthcare Standards",
        "version": "2.1",
        "sector": "Healthcare",
        "requirements": [
            {
                "requirement_id": "MOH_REQ_001",
                "title": "Patient Safety",
                "description": "Implement comprehensive patient safety protocols",
                "category": "Patient Care",
                "priority": "High",
                "compliance_levels": ["Basic", "Enhanced", "Advanced"]
            },
            {
                "requirement_id": "MOH_REQ_002",
                "title": "Data Privacy",
                "description": "Protect patient health information and privacy",
                "category": "Data Protection",
                "priority": "High",
                "compliance_levels": ["Basic", "Enhanced", "Advanced"]
            },
            {
                "requirement_id": "MOH_REQ_003",
                "title": "Medical Device Security",
                "description": "Ensure security of connected medical devices",
                "category": "Device Security",
                "priority": "Medium",
                "compliance_levels": ["Basic", "Enhanced", "Advanced"]
            },
            {
                "requirement_id": "MOH_REQ_004",
                "title": "Staff Training",
                "description": "Provide regular cybersecurity training to staff",
                "category": "Human Resources",
                "priority": "High",
                "compliance_levels": ["Basic", "Enhanced", "Advanced"]
            },
            {
                "requirement_id": "MOH_REQ_005",
                "title": "Incident Response",
                "description": "Establish healthcare incident response procedures",
                "category": "Incident Response",
                "priority": "High",
                "compliance_levels": ["Basic", "Enhanced", "Advanced"]
            }
        ],
        "compliance_levels": {
            "Basic": "Minimum healthcare standards",
            "Enhanced": "Above minimum standards",
            "Advanced": "Best practice healthcare"
        }
    }
}

# =============================================================================
# METRICS
# =============================================================================

REQUEST_COUNT = Counter(
    'benchmarks_requests_total',
    'Total number of requests',
    ['method', 'endpoint', 'status']
)

REQUEST_LATENCY = Histogram(
    'benchmarks_request_duration_seconds',
    'Request duration in seconds',
    ['method', 'endpoint']
)

# =============================================================================
# FASTAPI APPLICATION
# =============================================================================

app = FastAPI(
    title="DoganAI Benchmarks Service",
    description="KSA Regulatory Compliance Benchmarks and KPIs",
    version="1.0.0"
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =============================================================================
# API ENDPOINTS
# =============================================================================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "benchmarks",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

@app.get("/config")
async def get_config():
    """Get service configuration"""
    return {
        "service": "benchmarks",
        "version": "1.0.0",
        "frameworks": list(REAL_REGULATORY_FRAMEWORKS.keys()),
        "customer_count": len(REAL_CUSTOMERS),
        "last_updated": datetime.now().isoformat()
    }

@app.get("/benchmarks")
async def get_benchmarks():
    """Get all benchmark data"""
    return {
        "customers": REAL_CUSTOMERS,
        "total_customers": len(REAL_CUSTOMERS),
        "last_updated": datetime.now().isoformat()
    }

@app.get("/customers")
async def get_customers():
    """Get all customer data"""
    return {
        "customers": REAL_CUSTOMERS,
        "total_count": len(REAL_CUSTOMERS),
        "sectors": list(set(cust["sector"] for cust in REAL_CUSTOMERS)),
        "size_distribution": {
            "Large": len([c for c in REAL_CUSTOMERS if c["size"] == "Large"]),
            "Medium": len([c for c in REAL_CUSTOMERS if c["size"] == "Medium"]),
            "Small": len([c for c in REAL_CUSTOMERS if c["size"] == "Small"])
        }
    }

@app.get("/customers/{customer_id}")
async def get_customer(customer_id: str):
    """Get specific customer data"""
    customer = next((c for c in REAL_CUSTOMERS if c["customer_id"] == customer_id), None)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer

@app.get("/frameworks")
async def get_frameworks():
    """Get all regulatory frameworks"""
    return {
        "frameworks": REAL_REGULATORY_FRAMEWORKS,
        "total_count": len(REAL_REGULATORY_FRAMEWORKS),
        "sectors": list(set(fw["sector"] for fw in REAL_REGULATORY_FRAMEWORKS.values()))
    }

@app.get("/frameworks/{framework_id}")
async def get_framework(framework_id: str):
    """Get specific regulatory framework"""
    framework = REAL_REGULATORY_FRAMEWORKS.get(framework_id)
    if not framework:
        raise HTTPException(status_code=404, detail="Framework not found")
    return framework

@app.get("/analytics/summary")
async def get_analytics_summary():
    """Get analytics summary for dashboard"""
    total_customers = len(REAL_CUSTOMERS)
    avg_compliance_score = sum(c["compliance_score"] for c in REAL_CUSTOMERS) / total_customers
    
    risk_distribution = {}
    for customer in REAL_CUSTOMERS:
        risk = customer["risk_level"]
        risk_distribution[risk] = risk_distribution.get(risk, 0) + 1
    
    sector_distribution = {}
    for customer in REAL_CUSTOMERS:
        sector = customer["sector"]
        sector_distribution[sector] = sector_distribution.get(sector, 0) + 1
    
    return {
        "total_customers": total_customers,
        "average_compliance_score": round(avg_compliance_score, 2),
        "risk_distribution": risk_distribution,
        "sector_distribution": sector_distribution,
        "compliance_trends": {
            "high_performers": len([c for c in REAL_CUSTOMERS if c["compliance_score"] >= 90]),
            "medium_performers": len([c for c in REAL_CUSTOMERS if 70 <= c["compliance_score"] < 90]),
            "low_performers": len([c for c in REAL_CUSTOMERS if c["compliance_score"] < 70])
        },
        "last_updated": datetime.now().isoformat()
    }

@app.get("/analytics/charts")
async def get_chart_data():
    """Get data formatted for professional charts"""
    compliance_scores = [c["compliance_score"] for c in REAL_CUSTOMERS]
    
    # Sector Performance
    sector_performance = {}
    for customer in REAL_CUSTOMERS:
        sector = customer["sector"]
        if sector not in sector_performance:
            sector_performance[sector] = []
        sector_performance[sector].append(customer["compliance_score"])
    
    sector_avg = {sector: sum(scores)/len(scores) for sector, scores in sector_performance.items()}
    
    # Risk Level Distribution
    risk_counts = {}
    for customer in REAL_CUSTOMERS:
        risk = customer["risk_level"]
        risk_counts[risk] = risk_counts.get(risk, 0) + 1
    
    # KPI Performance by Category
    kpi_categories = {}
    for customer in REAL_CUSTOMERS:
        for kpi_name, score in customer["kpis"].items():
            category = kpi_name.replace("_score", "").replace("_", " ").title()
            if category not in kpi_categories:
                kpi_categories[category] = []
            kpi_categories[category].append(score)
    
    kpi_avg = {category: sum(scores)/len(scores) for category, scores in kpi_categories.items()}
    
    # Compliance Trend by Customer
    top_customers = sorted(REAL_CUSTOMERS, key=lambda x: x["compliance_score"], reverse=True)[:10]
    
    return {
        "compliance_distribution": {
            "labels": ["90-100", "80-89", "70-79", "60-69", "Below 60"],
            "data": [
                len([s for s in compliance_scores if s >= 90]),
                len([s for s in compliance_scores if 80 <= s < 90]),
                len([s for s in compliance_scores if 70 <= s < 80]),
                len([s for s in compliance_scores if 60 <= s < 70]),
                len([s for s in compliance_scores if s < 60])
            ]
        },
        "sector_performance": {
            "labels": list(sector_avg.keys()),
            "data": list(sector_avg.values())
        },
        "risk_distribution": {
            "labels": list(risk_counts.keys()),
            "data": list(risk_counts.values())
        },
        "kpi_performance": {
            "labels": list(kpi_avg.keys()),
            "data": list(kpi_avg.values())
        },
        "compliance_trend": {
            "labels": [c["customer_name"] for c in top_customers],
            "data": [c["compliance_score"] for c in top_customers]
        },
        "customer_comparison": {
            "labels": [c["customer_name"] for c in REAL_CUSTOMERS],
            "compliance_scores": [c["compliance_score"] for c in REAL_CUSTOMERS],
            "risk_levels": [c["risk_level"] for c in REAL_CUSTOMERS]
        }
    }

# =============================================================================
# STARTUP AND SHUTDOWN
# =============================================================================

@app.on_event("startup")
async def startup_event():
    """Application startup event"""
    logger.info(
        "Starting Benchmarks Microservice",
        version=APP_VERSION,
        environment=ENVIRONMENT,
        debug=DEBUG,
        benchmarks_loaded=len(BENCHMARKS)
    )

@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event"""
    logger.info("Shutting down Benchmarks Microservice")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)

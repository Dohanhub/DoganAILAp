#!/usr/bin/env python3
"""
Vendor Management Service
Manages technology vendors, solutions, and compliance offerings
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json
import os

app = FastAPI(title="Vendor Management Service", description="Technology Vendors & Solutions")

# Technology Vendors Data
TECHNOLOGY_VENDORS = {
    "IBM": {
        "name": "IBM Corporation",
        "website": "https://www.ibm.com",
        "headquarters": "Armonk, NY, USA",
        "saudi_office": "Riyadh, Saudi Arabia",
        "compliance_certifications": [
            "ISO 27001",
            "SOC 2 Type II",
            "GDPR Compliance",
            "Saudi Data Protection"
        ],
        "solutions": [
            {
                "id": "IBM-WATSON-001",
                "name": "IBM Watson AI for Compliance",
                "category": "Artificial Intelligence",
                "description": "AI-powered compliance monitoring and risk assessment",
                "features": [
                    "Natural language processing for regulatory documents",
                    "Automated compliance scoring",
                    "Risk prediction and alerting",
                    "Multi-language support (Arabic/English)"
                ],
                "compliance_areas": [
                    "AML/KYC",
                    "Data Protection",
                    "Regulatory Reporting",
                    "Risk Management"
                ],
                "pricing": {
                    "starter": "50,000 SAR/month",
                    "enterprise": "200,000 SAR/month",
                    "custom": "Contact sales"
                },
                "implementation_time": "8-12 weeks",
                "saudi_compliance": "Fully compliant with SAMA, NCA, and MoH requirements"
            },
            {
                "id": "IBM-CLOUD-001",
                "name": "IBM Cloud Pak for Security",
                "category": "Cloud Security",
                "description": "Integrated security platform for hybrid cloud environments",
                "features": [
                    "Unified security dashboard",
                    "Threat intelligence",
                    "Identity and access management",
                    "Compliance reporting"
                ],
                "compliance_areas": [
                    "Cybersecurity",
                    "Data Protection",
                    "Network Security",
                    "Access Control"
                ],
                "pricing": {
                    "starter": "75,000 SAR/month",
                    "enterprise": "300,000 SAR/month",
                    "custom": "Contact sales"
                },
                "implementation_time": "6-10 weeks",
                "saudi_compliance": "Meets CITC data localization requirements"
            }
        ]
    },
    "Microsoft": {
        "name": "Microsoft Corporation",
        "website": "https://www.microsoft.com",
        "headquarters": "Redmond, WA, USA",
        "saudi_office": "Riyadh, Saudi Arabia",
        "compliance_certifications": [
            "ISO 27001",
            "SOC 2 Type II",
            "GDPR Compliance",
            "Saudi Cloud Compliance"
        ],
        "solutions": [
            {
                "id": "MS-AZURE-001",
                "name": "Microsoft Azure Cognitive Services",
                "category": "AI & Machine Learning",
                "description": "Cloud-based AI services for compliance automation",
                "features": [
                    "Document analysis and classification",
                    "Sentiment analysis for compliance monitoring",
                    "Language understanding",
                    "Custom model training"
                ],
                "compliance_areas": [
                    "Document Processing",
                    "Regulatory Analysis",
                    "Risk Assessment",
                    "Compliance Monitoring"
                ],
                "pricing": {
                    "pay_per_use": "0.50 SAR per 1,000 transactions",
                    "enterprise": "Volume discounts available",
                    "custom": "Contact sales"
                },
                "implementation_time": "4-8 weeks",
                "saudi_compliance": "Azure Saudi Cloud regions available"
            },
            {
                "id": "MS-365-001",
                "name": "Microsoft 365 Compliance Center",
                "category": "Productivity & Compliance",
                "description": "Integrated compliance and governance platform",
                "features": [
                    "Data loss prevention",
                    "Information governance",
                    "eDiscovery and legal hold",
                    "Compliance score tracking"
                ],
                "compliance_areas": [
                    "Data Protection",
                    "Information Governance",
                    "Legal Compliance",
                    "Audit and Reporting"
                ],
                "pricing": {
                    "basic": "25 SAR/user/month",
                    "premium": "45 SAR/user/month",
                    "enterprise": "Contact sales"
                },
                "implementation_time": "2-4 weeks",
                "saudi_compliance": "Local data residency in Saudi Arabia"
            }
        ]
    },
    "AWS": {
        "name": "Amazon Web Services",
        "website": "https://aws.amazon.com",
        "headquarters": "Seattle, WA, USA",
        "saudi_office": "Riyadh, Saudi Arabia",
        "compliance_certifications": [
            "ISO 27001",
            "SOC 2 Type II",
            "GDPR Compliance",
            "Saudi Cloud Compliance"
        ],
        "solutions": [
            {
                "id": "AWS-COMPREHEND-001",
                "name": "Amazon Comprehend",
                "category": "Natural Language Processing",
                "description": "AI-powered text analysis for compliance documents",
                "features": [
                    "Entity recognition",
                    "Key phrase extraction",
                    "Sentiment analysis",
                    "Language detection"
                ],
                "compliance_areas": [
                    "Document Analysis",
                    "Regulatory Compliance",
                    "Risk Assessment",
                    "Compliance Monitoring"
                ],
                "pricing": {
                    "pay_per_use": "0.40 SAR per 1,000 characters",
                    "batch_processing": "0.20 SAR per 1,000 characters",
                    "custom": "Contact sales"
                },
                "implementation_time": "3-6 weeks",
                "saudi_compliance": "AWS Middle East (Bahrain) region available"
            },
            {
                "id": "AWS-GUARDDUTY-001",
                "name": "Amazon GuardDuty",
                "category": "Security & Threat Detection",
                "description": "Intelligent threat detection for AWS accounts",
                "features": [
                    "Continuous security monitoring",
                    "Threat intelligence",
                    "Anomaly detection",
                    "Automated response"
                ],
                "compliance_areas": [
                    "Cybersecurity",
                    "Threat Detection",
                    "Incident Response",
                    "Security Monitoring"
                ],
                "pricing": {
                    "basic": "0.30 SAR per 1,000,000 events",
                    "enterprise": "Volume discounts available",
                    "custom": "Contact sales"
                },
                "implementation_time": "2-4 weeks",
                "saudi_compliance": "Meets Saudi cybersecurity requirements"
            }
        ]
    },
    "Oracle": {
        "name": "Oracle Corporation",
        "website": "https://www.oracle.com",
        "headquarters": "Austin, TX, USA",
        "saudi_office": "Riyadh, Saudi Arabia",
        "compliance_certifications": [
            "ISO 27001",
            "SOC 2 Type II",
            "GDPR Compliance",
            "Saudi Data Protection"
        ],
        "solutions": [
            {
                "id": "ORACLE-GRCC-001",
                "name": "Oracle Governance, Risk and Compliance",
                "category": "GRC Platform",
                "description": "Comprehensive governance, risk, and compliance management",
                "features": [
                    "Policy management",
                    "Risk assessment",
                    "Compliance monitoring",
                    "Audit management"
                ],
                "compliance_areas": [
                    "Governance",
                    "Risk Management",
                    "Compliance",
                    "Audit"
                ],
                "pricing": {
                    "starter": "100,000 SAR/month",
                    "enterprise": "500,000 SAR/month",
                    "custom": "Contact sales"
                },
                "implementation_time": "12-16 weeks",
                "saudi_compliance": "Local deployment available in Saudi Arabia"
            }
        ]
    },
    "SAP": {
        "name": "SAP SE",
        "website": "https://www.sap.com",
        "headquarters": "Walldorf, Germany",
        "saudi_office": "Riyadh, Saudi Arabia",
        "compliance_certifications": [
            "ISO 27001",
            "SOC 2 Type II",
            "GDPR Compliance",
            "Saudi Business Compliance"
        ],
        "solutions": [
            {
                "id": "SAP-GRC-001",
                "name": "SAP Governance, Risk and Compliance",
                "category": "Enterprise GRC",
                "description": "Integrated GRC solution for enterprise organizations",
                "features": [
                    "Unified risk management",
                    "Compliance automation",
                    "Policy enforcement",
                    "Real-time monitoring"
                ],
                "compliance_areas": [
                    "Enterprise Risk",
                    "Compliance Management",
                    "Policy Governance",
                    "Audit Automation"
                ],
                "pricing": {
                    "starter": "150,000 SAR/month",
                    "enterprise": "750,000 SAR/month",
                    "custom": "Contact sales"
                },
                "implementation_time": "16-20 weeks",
                "saudi_compliance": "Local SAP support and deployment available"
            }
        ]
    }
}

@app.get("/")
async def root():
    """Service root endpoint"""
    return {
        "service": "Vendor Management Service",
        "version": "1.0.0",
        "status": "active",
        "vendors_count": len(TECHNOLOGY_VENDORS),
        "total_solutions": sum(len(vendor["solutions"]) for vendor in TECHNOLOGY_VENDORS.values())
    }

@app.get("/api/vendors")
async def get_vendors():
    """Get list of all technology vendors"""
    return {
        "vendors": TECHNOLOGY_VENDORS,
        "count": len(TECHNOLOGY_VENDORS),
        "last_updated": datetime.now().isoformat()
    }

@app.get("/api/vendors/{vendor_id}")
async def get_vendor(vendor_id: str):
    """Get specific vendor details"""
    if vendor_id.upper() not in TECHNOLOGY_VENDORS:
        raise HTTPException(status_code=404, detail="Vendor not found")
    
    return {
        "vendor": TECHNOLOGY_VENDORS[vendor_id.upper()],
        "last_updated": datetime.now().isoformat()
    }

@app.get("/api/solutions")
async def get_all_solutions():
    """Get all solutions from all vendors"""
    all_solutions = []
    
    for vendor_id, vendor in TECHNOLOGY_VENDORS.items():
        for solution in vendor["solutions"]:
            solution_copy = solution.copy()
            solution_copy["vendor"] = vendor_id
            solution_copy["vendor_name"] = vendor["name"]
            all_solutions.append(solution_copy)
    
    return {
        "solutions": all_solutions,
        "count": len(all_solutions),
        "last_updated": datetime.now().isoformat()
    }

@app.get("/api/solutions/{solution_id}")
async def get_solution(solution_id: str):
    """Get specific solution details"""
    for vendor_id, vendor in TECHNOLOGY_VENDORS.items():
        for solution in vendor["solutions"]:
            if solution["id"] == solution_id:
                solution_copy = solution.copy()
                solution_copy["vendor"] = vendor_id
                solution_copy["vendor_name"] = vendor["name"]
                return solution_copy
    
    raise HTTPException(status_code=404, detail="Solution not found")

@app.get("/api/solutions/category/{category}")
async def get_solutions_by_category(category: str):
    """Get solutions by category"""
    solutions = []
    
    for vendor_id, vendor in TECHNOLOGY_VENDORS.items():
        for solution in vendor["solutions"]:
            if category.lower() in solution["category"].lower():
                solution_copy = solution.copy()
                solution_copy["vendor"] = vendor_id
                solution_copy["vendor_name"] = vendor["name"]
                solutions.append(solution_copy)
    
    return {
        "category": category,
        "solutions": solutions,
        "count": len(solutions),
        "last_updated": datetime.now().isoformat()
    }

@app.get("/api/solutions/compliance/{compliance_area}")
async def get_solutions_by_compliance(compliance_area: str):
    """Get solutions by compliance area"""
    solutions = []
    
    for vendor_id, vendor in TECHNOLOGY_VENDORS.items():
        for solution in vendor["solutions"]:
            if any(area.lower() in compliance_area.lower() for area in solution["compliance_areas"]):
                solution_copy = solution.copy()
                solution_copy["vendor"] = vendor_id
                solution_copy["vendor_name"] = vendor["name"]
                solutions.append(solution_copy)
    
    return {
        "compliance_area": compliance_area,
        "solutions": solutions,
        "count": len(solutions),
        "last_updated": datetime.now().isoformat()
    }

@app.get("/api/pricing-comparison")
async def get_pricing_comparison():
    """Get pricing comparison across vendors"""
    pricing_data = {}
    
    for vendor_id, vendor in TECHNOLOGY_VENDORS.items():
        pricing_data[vendor_id] = {
            "vendor_name": vendor["name"],
            "solutions": []
        }
        
        for solution in vendor["solutions"]:
            pricing_data[vendor_id]["solutions"].append({
                "solution_name": solution["name"],
                "pricing": solution["pricing"],
                "implementation_time": solution["implementation_time"]
            })
    
    return {
        "pricing_comparison": pricing_data,
        "last_updated": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8008)


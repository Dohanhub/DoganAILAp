#!/usr/bin/env python3
"""
Customer Data Mapping Service
Manages customer profiles, data flows, and compliance mapping
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json
import os

app = FastAPI(title="Customer Data Mapping Service", description="Customer Profiles & Data Flow Mapping")

# Customer Data Mapping Structure
CUSTOMER_DATA_MAPPING = {
    "customer_profiles": {
        "financial_services": {
            "name": "Financial Services Sector",
            "description": "Banks, insurance companies, and financial institutions",
            "data_categories": [
                "Personal Identifiable Information (PII)",
                "Financial Transaction Data",
                "KYC Documentation",
                "Risk Assessment Data",
                "Compliance Reports"
            ],
            "regulatory_requirements": [
                "SAMA AML/KYC",
                "Data Protection Laws",
                "Financial Reporting Standards",
                "Cybersecurity Requirements"
            ],
            "data_flows": [
                {
                    "flow_id": "FF-001",
                    "name": "Customer Onboarding",
                    "description": "New customer registration and verification process",
                    "data_sources": ["Customer Application", "ID Documents", "Financial Statements"],
                    "data_destinations": ["KYC Database", "Risk Assessment Engine", "Compliance System"],
                    "data_retention": "7 years minimum",
                    "compliance_checks": ["AML Screening", "Identity Verification", "Risk Scoring"]
                },
                {
                    "flow_id": "FF-002",
                    "name": "Transaction Processing",
                    "description": "Daily financial transaction processing and monitoring",
                    "data_sources": ["Transaction Systems", "Customer Accounts", "External Feeds"],
                    "data_destinations": ["Transaction Database", "AML Monitoring", "Reporting Systems"],
                    "data_retention": "10 years minimum",
                    "compliance_checks": ["Transaction Limits", "Suspicious Activity", "Regulatory Reporting"]
                }
            ]
        },
        "healthcare": {
            "name": "Healthcare Sector",
            "description": "Hospitals, clinics, and medical service providers",
            "data_categories": [
                "Patient Health Records",
                "Medical Device Data",
                "Treatment Information",
                "Billing and Insurance",
                "Staff Credentials"
            ],
            "regulatory_requirements": [
                "MoH Healthcare Standards",
                "Patient Data Protection",
                "Medical Device Regulations",
                "Clinical Trial Requirements"
            ],
            "data_flows": [
                {
                    "flow_id": "HF-001",
                    "name": "Patient Registration",
                    "description": "Patient admission and record creation",
                    "data_sources": ["Patient Forms", "ID Documents", "Insurance Information"],
                    "data_destinations": ["Patient Database", "Medical Records System", "Billing System"],
                    "data_retention": "Lifetime + 10 years",
                    "compliance_checks": ["Identity Verification", "Insurance Validation", "Consent Management"]
                },
                {
                    "flow_id": "HF-002",
                    "name": "Medical Treatment",
                    "description": "Treatment delivery and record keeping",
                    "data_sources": ["Medical Devices", "Staff Input", "Lab Results"],
                    "data_destinations": ["Medical Records", "Treatment Database", "Quality Assurance"],
                    "data_retention": "Lifetime + 10 years",
                    "compliance_checks": ["Treatment Authorization", "Quality Standards", "Safety Protocols"]
                }
            ]
        },
        "technology": {
            "name": "Technology Sector",
            "description": "Software companies, IT services, and digital platforms",
            "data_categories": [
                "User Account Data",
                "Application Usage Data",
                "System Logs",
                "API Transaction Data",
                "Customer Support Records"
            ],
            "regulatory_requirements": [
                "NCA Data Protection",
                "CITC Telecommunications",
                "Cybersecurity Standards",
                "Consumer Protection Laws"
            ],
            "data_flows": [
                {
                    "flow_id": "TF-001",
                    "name": "User Registration",
                    "description": "New user account creation and verification",
                    "data_sources": ["User Input", "Email Verification", "Social Media"],
                    "data_destinations": ["User Database", "Authentication System", "Analytics Platform"],
                    "data_retention": "Account lifetime + 3 years",
                    "compliance_checks": ["Age Verification", "Terms Acceptance", "Privacy Consent"]
                },
                {
                    "flow_id": "TF-002",
                    "name": "Service Usage",
                    "description": "User interaction with platform services",
                    "data_sources": ["User Actions", "System Events", "Performance Metrics"],
                    "data_destinations": ["Usage Analytics", "Performance Monitoring", "Customer Insights"],
                    "data_retention": "3 years",
                    "compliance_checks": ["Data Minimization", "Purpose Limitation", "User Control"]
                }
            ]
        },
        "retail": {
            "name": "Retail Sector",
            "description": "E-commerce platforms, retail stores, and consumer services",
            "data_categories": [
                "Customer Purchase History",
                "Payment Information",
                "Customer Preferences",
                "Service Interactions",
                "Marketing Data"
            ],
            "regulatory_requirements": [
                "Consumer Protection Laws",
                "Payment Security Standards",
                "Data Protection Regulations",
                "E-commerce Regulations"
            ],
            "data_flows": [
                {
                    "flow_id": "RF-001",
                    "name": "Customer Purchase",
                    "description": "Product/service purchase and payment processing",
                    "data_sources": ["Product Selection", "Payment Methods", "Shipping Information"],
                    "data_destinations": ["Order Database", "Payment Processor", "Inventory System"],
                    "data_retention": "7 years",
                    "compliance_checks": ["Payment Security", "Age Verification", "Fraud Detection"]
                },
                {
                    "flow_id": "RF-002",
                    "name": "Customer Support",
                    "description": "Customer service and support interactions",
                    "data_sources": ["Support Tickets", "Chat Logs", "Phone Records"],
                    "data_destinations": ["Support Database", "Customer History", "Quality Metrics"],
                    "data_retention": "3 years",
                    "compliance_checks": ["Data Privacy", "Service Quality", "Response Time"]
                }
            ]
        }
    },
    "data_classification": {
        "public": {
            "description": "Information that can be freely shared",
            "examples": ["Company website content", "Public announcements", "Marketing materials"],
            "handling_requirements": "No special protection required"
        },
        "internal": {
            "description": "Information for internal use only",
            "examples": ["Employee directories", "Internal procedures", "Meeting minutes"],
            "handling_requirements": "Internal access controls, no external sharing"
        },
        "confidential": {
            "description": "Sensitive business information",
            "examples": ["Business plans", "Financial projections", "Customer lists"],
            "handling_requirements": "Access controls, encryption, audit logging"
        },
        "restricted": {
            "description": "Highly sensitive information with legal protection",
            "examples": ["Personal data", "Financial records", "Health information"],
            "handling_requirements": "Strong encryption, access controls, compliance monitoring"
        }
    },
    "compliance_mapping": {
        "data_protection": {
            "regulations": ["Saudi Data Protection Law", "GDPR", "CCPA"],
            "requirements": [
                "Data minimization",
                "Purpose limitation",
                "User consent",
                "Data subject rights",
                "Breach notification"
            ],
            "implementation": [
                "Privacy by design",
                "Data inventory",
                "Consent management",
                "Data subject request handling"
            ]
        },
        "cybersecurity": {
            "regulations": ["Saudi Cybersecurity Framework", "ISO 27001", "NIST"],
            "requirements": [
                "Access controls",
                "Encryption",
                "Incident response",
                "Security monitoring",
                "Vulnerability management"
            ],
            "implementation": [
                "Security architecture",
                "Identity management",
                "Threat detection",
                "Security awareness training"
            ]
        },
        "financial_compliance": {
            "regulations": ["SAMA Guidelines", "Basel III", "AML/CFT"],
            "requirements": [
                "Customer due diligence",
                "Transaction monitoring",
                "Risk assessment",
                "Regulatory reporting",
                "Audit trails"
            ],
            "implementation": [
                "KYC processes",
                "AML systems",
                "Risk management framework",
                "Compliance monitoring"
            ]
        }
    }
}

@app.get("/")
async def root():
    """Service root endpoint"""
    return {
        "service": "Customer Data Mapping Service",
        "version": "1.0.0",
        "status": "active",
        "sectors_count": len(CUSTOMER_DATA_MAPPING["customer_profiles"]),
        "data_flows_count": sum(len(sector["data_flows"]) for sector in CUSTOMER_DATA_MAPPING["customer_profiles"].values())
    }

@app.get("/api/customer-profiles")
async def get_customer_profiles():
    """Get all customer profile sectors"""
    return {
        "customer_profiles": CUSTOMER_DATA_MAPPING["customer_profiles"],
        "count": len(CUSTOMER_DATA_MAPPING["customer_profiles"]),
        "last_updated": datetime.now().isoformat()
    }

@app.get("/api/customer-profiles/{sector}")
async def get_customer_profile(sector: str):
    """Get specific customer profile sector"""
    if sector not in CUSTOMER_DATA_MAPPING["customer_profiles"]:
        raise HTTPException(status_code=404, detail="Sector not found")
    
    return {
        "sector": CUSTOMER_DATA_MAPPING["customer_profiles"][sector],
        "last_updated": datetime.now().isoformat()
    }

@app.get("/api/data-flows")
async def get_all_data_flows():
    """Get all data flows across all sectors"""
    all_flows = []
    
    for sector, profile in CUSTOMER_DATA_MAPPING["customer_profiles"].items():
        for flow in profile["data_flows"]:
            flow_copy = flow.copy()
            flow_copy["sector"] = sector
            flow_copy["sector_name"] = profile["name"]
            all_flows.append(flow_copy)
    
    return {
        "data_flows": all_flows,
        "count": len(all_flows),
        "last_updated": datetime.now().isoformat()
    }

@app.get("/api/data-flows/{sector}")
async def get_sector_data_flows(sector: str):
    """Get data flows for specific sector"""
    if sector not in CUSTOMER_DATA_MAPPING["customer_profiles"]:
        raise HTTPException(status_code=404, detail="Sector not found")
    
    return {
        "sector": sector,
        "data_flows": CUSTOMER_DATA_MAPPING["customer_profiles"][sector]["data_flows"],
        "count": len(CUSTOMER_DATA_MAPPING["customer_profiles"][sector]["data_flows"]),
        "last_updated": datetime.now().isoformat()
    }

@app.get("/api/data-classification")
async def get_data_classification():
    """Get data classification levels"""
    return {
        "data_classification": CUSTOMER_DATA_MAPPING["data_classification"],
        "count": len(CUSTOMER_DATA_MAPPING["data_classification"]),
        "last_updated": datetime.now().isoformat()
    }

@app.get("/api/compliance-mapping")
async def get_compliance_mapping():
    """Get compliance mapping information"""
    return {
        "compliance_mapping": CUSTOMER_DATA_MAPPING["compliance_mapping"],
        "count": len(CUSTOMER_DATA_MAPPING["compliance_mapping"]),
        "last_updated": datetime.now().isoformat()
    }

@app.get("/api/compliance-mapping/{area}")
async def get_compliance_area(area: str):
    """Get specific compliance area mapping"""
    if area not in CUSTOMER_DATA_MAPPING["compliance_mapping"]:
        raise HTTPException(status_code=404, detail="Compliance area not found")
    
    return {
        "compliance_area": area,
        "mapping": CUSTOMER_DATA_MAPPING["compliance_mapping"][area],
        "last_updated": datetime.now().isoformat()
    }

@app.get("/api/data-inventory")
async def get_data_inventory():
    """Get comprehensive data inventory across all sectors"""
    inventory = {}
    
    for sector, profile in CUSTOMER_DATA_MAPPING["customer_profiles"].items():
        inventory[sector] = {
            "sector_name": profile["name"],
            "data_categories": profile["data_categories"],
            "regulatory_requirements": profile["regulatory_requirements"],
            "data_flows_count": len(profile["data_flows"]),
            "data_flows": [flow["name"] for flow in profile["data_flows"]]
        }
    
    return {
        "data_inventory": inventory,
        "total_sectors": len(inventory),
        "last_updated": datetime.now().isoformat()
    }

@app.get("/api/regulatory-impact/{sector}")
async def get_regulatory_impact(sector: str):
    """Get regulatory impact analysis for specific sector"""
    if sector not in CUSTOMER_DATA_MAPPING["customer_profiles"]:
        raise HTTPException(status_code=404, detail="Sector not found")
    
    profile = CUSTOMER_DATA_MAPPING["customer_profiles"][sector]
    
    # Map regulations to compliance areas
    impact_mapping = {}
    for req in profile["regulatory_requirements"]:
        if "SAMA" in req:
            impact_mapping[req] = "Financial Compliance"
        elif "MoH" in req:
            impact_mapping[req] = "Healthcare Standards"
        elif "NCA" in req:
            impact_mapping[req] = "Business Registration"
        elif "CITC" in req:
            impact_mapping[req] = "Telecommunications"
        else:
            impact_mapping[req] = "General Compliance"
    
    return {
        "sector": sector,
        "sector_name": profile["name"],
        "regulatory_impact": impact_mapping,
        "compliance_priority": "High" if len(profile["regulatory_requirements"]) > 3 else "Medium",
        "last_updated": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8009)


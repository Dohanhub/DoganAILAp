#!/usr/bin/env python3
"""
Regulatory Management Service
Manages Saudi regulatory authorities, regulations, and compliance requirements
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json
import os

app = FastAPI(title="Regulatory Management Service", description="Saudi Regulatory Authorities & Regulations")

# Saudi Regulatory Authorities Data
SAUDI_REGULATORS = {
    "NCA": {
        "name": "National Commercial Authority",
        "full_name": "الهيئة العامة للتجارة",
        "website": "https://nca.gov.sa",
        "api_endpoint": "https://api.nca.gov.sa",
        "jurisdiction": "Commercial & Business Registration",
        "compliance_areas": [
            "Company Registration",
            "Commercial Licenses", 
            "Data Protection",
            "Cybersecurity",
            "Consumer Protection"
        ],
        "regulations": [
            {
                "id": "NCA-REG-001",
                "title": "Data Protection and Privacy Regulations",
                "arabic_title": "لوائح حماية البيانات والخصوصية",
                "effective_date": "2024-01-01",
                "compliance_deadline": "2024-06-30",
                "scope": "All registered companies",
                "requirements": [
                    "Data encryption at rest and in transit",
                    "User consent management",
                    "Data breach notification within 72 hours",
                    "Regular privacy impact assessments"
                ],
                "penalties": {
                    "minor": "Warning and corrective action plan",
                    "major": "Fine up to 500,000 SAR",
                    "critical": "License suspension and legal action"
                }
            },
            {
                "id": "NCA-REG-002", 
                "title": "Cybersecurity Framework Requirements",
                "arabic_title": "متطلبات إطار العمل للأمن السيبراني",
                "effective_date": "2024-03-01",
                "compliance_deadline": "2024-09-30",
                "scope": "Technology and financial companies",
                "requirements": [
                    "Multi-factor authentication",
                    "Regular security audits",
                    "Incident response plan",
                    "Employee security training"
                ],
                "penalties": {
                    "minor": "Security improvement plan required",
                    "major": "Fine up to 1,000,000 SAR",
                    "critical": "Business suspension"
                }
            }
        ]
    },
    "SAMA": {
        "name": "Saudi Arabian Monetary Authority", 
        "full_name": "مؤسسة النقد العربي السعودي",
        "website": "https://sama.gov.sa",
        "api_endpoint": "https://api.sama.gov.sa",
        "jurisdiction": "Banking & Financial Services",
        "compliance_areas": [
            "Anti-Money Laundering (AML)",
            "Know Your Customer (KYC)",
            "Capital Adequacy",
            "Risk Management",
            "Digital Banking"
        ],
        "regulations": [
            {
                "id": "SAMA-REG-001",
                "title": "Anti-Money Laundering and Counter-Terrorism Financing",
                "arabic_title": "مكافحة غسل الأموال وتمويل الإرهاب",
                "effective_date": "2023-12-01",
                "compliance_deadline": "2024-03-31",
                "scope": "All financial institutions",
                "requirements": [
                    "Customer due diligence procedures",
                    "Suspicious transaction reporting",
                    "Risk-based approach implementation",
                    "Regular AML training for staff"
                ],
                "penalties": {
                    "minor": "Corrective action plan",
                    "major": "Fine up to 5,000,000 SAR",
                    "critical": "License revocation"
                }
            },
            {
                "id": "SAMA-REG-002",
                "title": "Digital Banking Security Standards",
                "arabic_title": "معايير أمان الخدمات المصرفية الرقمية",
                "effective_date": "2024-02-01",
                "compliance_deadline": "2024-08-31",
                "scope": "Digital banking services",
                "requirements": [
                    "End-to-end encryption",
                    "Biometric authentication",
                    "Fraud detection systems",
                    "24/7 monitoring"
                ],
                "penalties": {
                    "minor": "Security enhancement required",
                    "major": "Fine up to 2,000,000 SAR",
                    "critical": "Service suspension"
                }
            }
        ]
    },
    "MoH": {
        "name": "Ministry of Health",
        "full_name": "وزارة الصحة",
        "website": "https://moh.gov.sa",
        "api_endpoint": "https://api.moh.gov.sa",
        "jurisdiction": "Healthcare & Medical Services",
        "compliance_areas": [
            "Patient Data Protection",
            "Medical Device Standards",
            "Clinical Trial Regulations",
            "Healthcare Facility Licensing",
            "Medical Staff Certification"
        ],
        "regulations": [
            {
                "id": "MOH-REG-001",
                "title": "Healthcare Data Protection and Privacy",
                "arabic_title": "حماية خصوصية البيانات الصحية",
                "effective_date": "2024-01-15",
                "compliance_deadline": "2024-07-15",
                "scope": "All healthcare facilities",
                "requirements": [
                    "Patient consent management",
                    "Secure data storage",
                    "Access control and audit trails",
                    "Data breach response plan"
                ],
                "penalties": {
                    "minor": "Privacy improvement plan",
                    "major": "Fine up to 300,000 SAR",
                    "critical": "License suspension"
                }
            },
            {
                "id": "MOH-REG-002",
                "title": "Medical Device Cybersecurity Standards",
                "arabic_title": "معايير الأمن السيبراني للأجهزة الطبية",
                "effective_date": "2024-04-01",
                "compliance_deadline": "2024-10-01",
                "scope": "Connected medical devices",
                "requirements": [
                    "Device authentication",
                    "Secure communication protocols",
                    "Regular security updates",
                    "Vulnerability management"
                ],
                "penalties": {
                    "minor": "Security assessment required",
                    "major": "Fine up to 500,000 SAR",
                    "critical": "Device recall"
                }
            }
        ]
    },
    "CITC": {
        "name": "Communications and Information Technology Commission",
        "full_name": "هيئة الاتصالات وتقنية المعلومات",
        "website": "https://citc.gov.sa",
        "api_endpoint": "https://api.citc.gov.sa",
        "jurisdiction": "Telecommunications & IT",
        "compliance_areas": [
            "Telecom Licensing",
            "Data Localization",
            "Network Security",
            "Digital Services",
            "5G Infrastructure"
        ],
        "regulations": [
            {
                "id": "CITC-REG-001",
                "title": "Data Localization Requirements",
                "arabic_title": "متطلبات توطين البيانات",
                "effective_date": "2024-01-01",
                "compliance_deadline": "2024-12-31",
                "scope": "All telecom operators",
                "requirements": [
                    "Local data centers",
                    "Data sovereignty compliance",
                    "Cross-border data transfer restrictions",
                    "Regular compliance reporting"
                ],
                "penalties": {
                    "minor": "Compliance plan required",
                    "major": "Fine up to 3,000,000 SAR",
                    "critical": "Service restriction"
                }
            }
        ]
    }
}

@app.get("/")
async def root():
    """Service root endpoint"""
    return {
        "service": "Regulatory Management Service",
        "version": "1.0.0",
        "status": "active",
        "regulators_count": len(SAUDI_REGULATORS),
        "total_regulations": sum(len(reg["regulations"]) for reg in SAUDI_REGULATORS.values())
    }

@app.get("/api/regulators")
async def get_regulators():
    """Get list of all Saudi regulatory authorities"""
    return {
        "regulators": SAUDI_REGULATORS,
        "count": len(SAUDI_REGULATORS),
        "last_updated": datetime.now().isoformat()
    }

@app.get("/api/regulators/{regulator_id}")
async def get_regulator(regulator_id: str):
    """Get specific regulator details"""
    if regulator_id.upper() not in SAUDI_REGULATORS:
        raise HTTPException(status_code=404, detail="Regulator not found")
    
    return {
        "regulator": SAUDI_REGULATORS[regulator_id.upper()],
        "last_updated": datetime.now().isoformat()
    }

@app.get("/api/regulations")
async def get_all_regulations():
    """Get all regulations from all authorities"""
    all_regulations = []
    
    for regulator_id, regulator in SAUDI_REGULATORS.items():
        for regulation in regulator["regulations"]:
            regulation_copy = regulation.copy()
            regulation_copy["authority"] = regulator_id
            regulation_copy["authority_name"] = regulator["name"]
            all_regulations.append(regulation_copy)
    
    return {
        "regulations": all_regulations,
        "count": len(all_regulations),
        "last_updated": datetime.now().isoformat()
    }

@app.get("/api/regulations/{regulation_id}")
async def get_regulation(regulation_id: str):
    """Get specific regulation details"""
    for regulator_id, regulator in SAUDI_REGULATORS.items():
        for regulation in regulator["regulations"]:
            if regulation["id"] == regulation_id:
                regulation_copy = regulation.copy()
                regulation_copy["authority"] = regulator_id
                regulation_copy["authority_name"] = regulator["name"]
                return regulation_copy
    
    raise HTTPException(status_code=404, detail="Regulation not found")

@app.get("/api/compliance-areas")
async def get_compliance_areas():
    """Get all compliance areas across regulators"""
    compliance_areas = {}
    
    for regulator_id, regulator in SAUDI_REGULATORS.items():
        for area in regulator["compliance_areas"]:
            if area not in compliance_areas:
                compliance_areas[area] = []
            compliance_areas[area].append(regulator_id)
    
    return {
        "compliance_areas": compliance_areas,
        "count": len(compliance_areas),
        "last_updated": datetime.now().isoformat()
    }

@app.get("/api/upcoming-deadlines")
async def get_upcoming_deadlines(days: int = 90):
    """Get upcoming compliance deadlines"""
    upcoming = []
    cutoff_date = datetime.now() + timedelta(days=days)
    
    for regulator_id, regulator in SAUDI_REGULATORS.items():
        for regulation in regulator["regulations"]:
            deadline = datetime.fromisoformat(regulation["compliance_deadline"])
            if deadline <= cutoff_date:
                upcoming.append({
                    "regulation_id": regulation["id"],
                    "title": regulation["title"],
                    "authority": regulator_id,
                    "authority_name": regulator["name"],
                    "deadline": regulation["compliance_deadline"],
                    "days_remaining": (deadline - datetime.now()).days,
                    "urgency": "critical" if (deadline - datetime.now()).days <= 30 else "high" if (deadline - datetime.now()).days <= 60 else "medium"
                })
    
    # Sort by urgency and deadline
    upcoming.sort(key=lambda x: (x["urgency"] == "critical", x["days_remaining"]))
    
    return {
        "upcoming_deadlines": upcoming,
        "count": len(upcoming),
        "period_days": days,
        "last_updated": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8007)


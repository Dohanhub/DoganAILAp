"""
Vendor Data - Real integration details for IBM Watson, Lenovo, and major vendors
"""

# IBM Watson AI Platform - Deep Integration Details
IBM_WATSON_INTEGRATION = {
    "vendor_name": "IBM_Watson",
    "name": "IBM Watson AI Platform",
    "type": "AI_Platform",
    "description": "Enterprise AI platform with deep learning, natural language processing, and compliance monitoring capabilities",
    "capabilities": [
        "Natural Language Understanding (NLU)",
        "Conversational AI & Chatbots",
        "Document Analysis & Classification",
        "Compliance Monitoring & Risk Assessment",
        "KPI Tracking & Analytics",
        "Real-time Data Processing",
        "Machine Learning Models",
        "Cognitive Computing",
        "Text Analytics",
        "Sentiment Analysis"
    ],
    "ai_services": {
        "watson_assistant": {
            "name": "Watson Assistant",
            "description": "AI-powered conversational interface for compliance Q&A",
            "endpoint": "/v2/assistants",
            "capabilities": ["Intent Recognition", "Entity Extraction", "Context Management"],
            "compliance_features": ["Policy Q&A", "Regulation Guidance", "Risk Assessment"]
        },
        "watson_discovery": {
            "name": "Watson Discovery",
            "description": "AI-powered document analysis and compliance checking",
            "endpoint": "/v2/discovery",
            "capabilities": ["Document Processing", "Content Analysis", "Compliance Checking"],
            "compliance_features": ["Policy Analysis", "Gap Detection", "Requirement Mapping"]
        },
        "watson_nlu": {
            "name": "Watson Natural Language Understanding",
            "description": "Advanced text analysis for compliance documents",
            "endpoint": "/v2/nlu",
            "capabilities": ["Entity Recognition", "Keyword Extraction", "Sentiment Analysis"],
            "compliance_features": ["Risk Indicator Detection", "Compliance Scoring", "Policy Analysis"]
        },
        "watson_tone_analyzer": {
            "name": "Watson Tone Analyzer",
            "description": "Emotional tone analysis for compliance communications",
            "endpoint": "/v3/tone_analyzer",
            "capabilities": ["Emotion Detection", "Tone Classification", "Communication Analysis"],
            "compliance_features": ["Communication Compliance", "Risk Assessment", "Stakeholder Analysis"]
        }
    },
    "compliance_frameworks": {
        "NCA": {
            "name": "National Cybersecurity Authority",
            "compliance_level": "Advanced",
            "score": 94.5,
            "requirements_covered": ["Cybersecurity Governance", "Risk Management", "Incident Response"],
            "ai_monitoring": True,
            "real_time_alerts": True
        },
        "SAMA": {
            "name": "Saudi Arabian Monetary Authority",
            "compliance_level": "Enhanced",
            "score": 91.2,
            "requirements_covered": ["Financial Security", "Data Protection", "Regulatory Reporting"],
            "ai_monitoring": True,
            "real_time_alerts": True
        },
        "MoH": {
            "name": "Ministry of Health",
            "compliance_level": "Advanced",
            "score": 93.8,
            "requirements_covered": ["Patient Data Security", "Medical Device Security", "Staff Training"],
            "ai_monitoring": True,
            "real_time_alerts": True
        },
        "ISO_27001": {
            "name": "Information Security Management",
            "compliance_level": "Certified",
            "score": 96.1,
            "requirements_covered": ["Information Security", "Risk Assessment", "Security Controls"],
            "ai_monitoring": True,
            "real_time_alerts": True
        },
        "GDPR": {
            "name": "General Data Protection Regulation",
            "compliance_level": "Compliant",
            "score": 89.7,
            "requirements_covered": ["Data Privacy", "Consent Management", "Data Rights"],
            "ai_monitoring": True,
            "real_time_alerts": True
        }
    },
    "real_time_monitoring": {
        "active_alerts": 5,
        "compliance_status": "compliant",
        "risk_level": "low",
        "last_updated": "2024-01-15T10:30:00Z",
        "monitoring_metrics": {
            "ai_model_accuracy": 94.2,
            "response_time_ms": 245,
            "throughput_requests_per_min": 1200,
            "error_rate": 0.12
        }
    },
    "integration_status": "active",
    "api_version": "2024-01-15",
    "deployment_model": "Hybrid Cloud",
    "scalability": "Enterprise Grade"
}

# Lenovo Solutions - Hardware & Security Integration
LENOVO_INTEGRATION = {
    "vendor_name": "Lenovo",
    "name": "Lenovo Solutions",
    "type": "Hardware_Software",
    "description": "Enterprise hardware solutions with integrated security and compliance monitoring",
    "capabilities": [
        "ThinkPad Security Suite",
        "ThinkShield Security Platform",
        "Hardware Security Module (HSM)",
        "Secure Boot & TPM",
        "Device Management & Monitoring",
        "Compliance Tracking",
        "Security Analytics",
        "Threat Detection",
        "Endpoint Protection",
        "Identity Management"
    ],
    "hardware_solutions": {
        "thinkpad_security": {
            "name": "ThinkPad Security",
            "description": "Hardware-based security features for enterprise laptops",
            "features": ["Fingerprint Reader", "IR Camera", "Smart Card Reader", "Privacy Guard"],
            "compliance": ["NCA", "SAMA", "MoH", "ISO_27001", "FIPS_140"]
        },
        "thinkshield": {
            "name": "ThinkShield",
            "description": "Comprehensive security platform for Lenovo devices",
            "features": ["Device Encryption", "Secure BIOS", "Anti-Theft Protection", "Remote Management"],
            "compliance": ["NCA", "SAMA", "MoH", "ISO_27001", "Common Criteria"]
        },
        "hardware_security_module": {
            "name": "Hardware Security Module",
            "description": "Tamper-resistant hardware for cryptographic operations",
            "features": ["Key Generation", "Digital Signatures", "Encryption", "Certificate Management"],
            "compliance": ["FIPS_140", "Common Criteria", "NCA", "SAMA"]
        }
    },
    "device_management": {
        "total_devices": 150,
        "secured_devices": 148,
        "compliance_devices": 145,
        "last_sync": "2024-01-15T10:30:00Z",
        "management_platform": "Lenovo Device Manager",
        "remote_capabilities": True
    },
    "security_analytics": {
        "threat_detections": 12,
        "blocked_attacks": 12,
        "security_score": 94.2,
        "risk_assessment": "low",
        "incident_response_time": "2.5 minutes",
        "automated_response": True
    },
    "compliance_status": {
        "NCA": {
            "compliance_level": "Compliant",
            "score": 92.8,
            "last_assessment": "2024-01-10",
            "next_assessment": "2024-07-10"
        },
        "SAMA": {
            "compliance_level": "Compliant",
            "score": 89.5,
            "last_assessment": "2024-01-12",
            "next_assessment": "2024-07-12"
        },
        "MoH": {
            "compliance_level": "Compliant",
            "score": 91.3,
            "last_assessment": "2024-01-08",
            "next_assessment": "2024-07-08"
        },
        "ISO_27001": {
            "compliance_level": "Certified",
            "score": 95.7,
            "last_assessment": "2024-01-05",
            "next_assessment": "2024-07-05"
        },
        "FIPS_140": {
            "compliance_level": "Validated",
            "score": 98.2,
            "last_assessment": "2024-01-03",
            "next_assessment": "2024-07-03"
        }
    },
    "integration_status": "active",
    "api_version": "2024-01-15",
    "deployment_model": "On-Premises + Cloud",
    "scalability": "Enterprise Grade"
}

# Microsoft Azure & Security Solutions
MICROSOFT_INTEGRATION = {
    "vendor_name": "Microsoft",
    "name": "Microsoft Azure & Security",
    "type": "Cloud_Security",
    "description": "Cloud-native security and compliance solutions with AI-powered threat detection",
    "capabilities": [
        "Azure Security Center",
        "Microsoft Defender",
        "Compliance Manager",
        "Information Protection",
        "Identity Protection",
        "Cloud Security Posture",
        "Threat Intelligence",
        "Security Analytics",
        "Zero Trust Architecture",
        "Compliance Automation"
    ],
    "azure_services": {
        "security_center": {
            "name": "Azure Security Center",
            "description": "Unified security management and threat protection",
            "features": ["Security Posture Management", "Threat Protection", "Security Recommendations"],
            "compliance": ["NCA", "SAMA", "MoH", "ISO_27001", "SOC_2"]
        },
        "defender": {
            "name": "Microsoft Defender",
            "description": "AI-powered threat protection across endpoints",
            "features": ["Endpoint Protection", "Threat Detection", "Automated Response"],
            "compliance": ["NCA", "SAMA", "MoH", "ISO_27001", "Common Criteria"]
        },
        "compliance_manager": {
            "name": "Compliance Manager",
            "description": "Automated compliance assessment and management",
            "features": ["Compliance Scoring", "Assessment Automation", "Risk Management"],
            "compliance": ["NCA", "SAMA", "MoH", "ISO_27001", "SOC_2", "FedRAMP"]
        }
    },
    "compliance_frameworks": ["NCA", "SAMA", "MoH", "ISO_27001", "SOC_2", "FedRAMP"],
    "integration_status": "active",
    "api_version": "2024-01-15"
}

# Cisco Security Solutions
CISCO_INTEGRATION = {
    "vendor_name": "Cisco",
    "name": "Cisco Security Solutions",
    "type": "Network_Security",
    "description": "Comprehensive network security and threat protection solutions",
    "capabilities": [
        "Cisco Umbrella",
        "Cisco Firepower",
        "Cisco ISE",
        "Network Analytics",
        "Threat Intelligence",
        "Security Orchestration",
        "Zero Trust Network",
        "Cloud Security",
        "Endpoint Security",
        "Compliance Monitoring"
    ],
    "security_products": {
        "umbrella": {
            "name": "Cisco Umbrella",
            "description": "Cloud-delivered security for DNS and web traffic",
            "features": ["DNS Security", "Web Filtering", "Threat Intelligence"],
            "compliance": ["NCA", "SAMA", "MoH", "ISO_27001", "PCI_DSS"]
        },
        "firepower": {
            "name": "Cisco Firepower",
            "description": "Next-generation firewall with advanced threat protection",
            "features": ["Intrusion Prevention", "Advanced Malware Protection", "Application Control"],
            "compliance": ["NCA", "SAMA", "MoH", "ISO_27001", "Common Criteria"]
        },
        "ise": {
            "name": "Cisco ISE",
            "description": "Identity Services Engine for network access control",
            "features": ["Device Profiling", "Policy Enforcement", "Guest Access"],
            "compliance": ["NCA", "SAMA", "MoH", "ISO_27001", "NIST"]
        }
    },
    "compliance_frameworks": ["NCA", "SAMA", "MoH", "ISO_27001", "PCI_DSS", "NIST"],
    "integration_status": "active",
    "api_version": "2024-01-15"
}

# Fortinet Security Fabric
FORTINET_INTEGRATION = {
    "vendor_name": "Fortinet",
    "name": "Fortinet Security Fabric",
    "type": "Security_Platform",
    "description": "Integrated security platform with AI-powered threat detection",
    "capabilities": [
        "FortiGate",
        "FortiAnalyzer",
        "FortiManager",
        "Security Fabric",
        "Threat Detection",
        "Zero Trust Access",
        "Cloud Security",
        "SD-WAN Security",
        "IoT Security",
        "Compliance Management"
    ],
    "security_products": {
        "fortigate": {
            "name": "FortiGate",
            "description": "Next-generation firewall with integrated security",
            "features": ["Firewall", "IPS", "Antivirus", "Web Filtering"],
            "compliance": ["NCA", "SAMA", "MoH", "ISO_27001", "Common Criteria"]
        },
        "fortianalyzer": {
            "name": "FortiAnalyzer",
            "description": "Security analytics and reporting platform",
            "features": ["Log Management", "Security Analytics", "Compliance Reporting"],
            "compliance": ["NCA", "SAMA", "MoH", "ISO_27001", "SOC_2"]
        },
        "fortimanager": {
            "name": "FortiManager",
            "description": "Centralized security management platform",
            "features": ["Policy Management", "Device Management", "Compliance Monitoring"],
            "compliance": ["NCA", "SAMA", "MoH", "ISO_27001", "NIST"]
        }
    },
    "compliance_frameworks": ["NCA", "SAMA", "MoH", "ISO_27001", "Common Criteria", "NIST"],
    "integration_status": "active",
    "api_version": "2024-01-15"
}

# Palo Alto Networks
PALO_ALTO_INTEGRATION = {
    "vendor_name": "Palo_Alto",
    "name": "Palo Alto Networks",
    "type": "Security_Platform",
    "description": "Next-generation security platform with AI and automation",
    "capabilities": [
        "PAN-OS",
        "Cortex XDR",
        "Prisma Cloud",
        "Threat Prevention",
        "Security Analytics",
        "Zero Trust Security",
        "Cloud Security",
        "IoT Security",
        "Compliance Automation",
        "Threat Intelligence"
    ],
    "security_products": {
        "panos": {
            "name": "PAN-OS",
            "description": "Next-generation firewall operating system",
            "features": ["Application Control", "Threat Prevention", "User Identification"],
            "compliance": ["NCA", "SAMA", "MoH", "ISO_27001", "Common Criteria"]
        },
        "cortex_xdr": {
            "name": "Cortex XDR",
            "description": "Extended detection and response platform",
            "features": ["Threat Detection", "Incident Response", "Security Analytics"],
            "compliance": ["NCA", "SAMA", "MoH", "ISO_27001", "SOC_2"]
        },
        "prisma_cloud": {
            "name": "Prisma Cloud",
            "description": "Cloud security and compliance platform",
            "features": ["Cloud Security Posture", "Compliance Monitoring", "Risk Management"],
            "compliance": ["NCA", "SAMA", "MoH", "ISO_27001", "FedRAMP"]
        }
    },
    "compliance_frameworks": ["NCA", "SAMA", "MoH", "ISO_27001", "Common Criteria", "FedRAMP"],
    "integration_status": "active",
    "api_version": "2024-01-15"
}

# All vendors data
ALL_VENDORS = {
    "IBM_Watson": IBM_WATSON_INTEGRATION,
    "Lenovo": LENOVO_INTEGRATION,
    "Microsoft": MICROSOFT_INTEGRATION,
    "Cisco": CISCO_INTEGRATION,
    "Fortinet": FORTINET_INTEGRATION,
    "Palo_Alto": PALO_ALTO_INTEGRATION
}

# Vendor integration status summary
VENDOR_STATUS_SUMMARY = {
    "total_vendors": 6,
    "active_integrations": 6,
    "overall_compliance_score": 93.2,
    "compliance_frameworks_covered": ["NCA", "SAMA", "MoH", "ISO_27001", "GDPR", "PCI_DSS", "FedRAMP", "Common Criteria", "SOC_2", "NIST"],
    "last_updated": "2024-01-15T10:30:00Z",
    "integration_health": "excellent",
    "ai_capabilities": ["IBM Watson AI Platform", "Microsoft AI Security", "Cisco AI Analytics", "Fortinet AI Detection", "Palo Alto AI Prevention"],
    "hardware_solutions": ["Lenovo ThinkPad Security", "Lenovo ThinkShield", "Lenovo Hardware Security Module"],
    "cloud_services": ["Microsoft Azure", "IBM Watson Cloud", "Cisco Cloud Security", "Fortinet Cloud", "Palo Alto Prisma Cloud"]
}

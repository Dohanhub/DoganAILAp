#!/usr/bin/env python3
"""
DoganAI Compliance Kit - Workflow Simulator Web App
Serves the dual-screen workflow simulator as a web application
"""

import os
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# Initialize FastAPI app for workflow simulator
workflow_app = FastAPI(
    title="DoganAI Workflow Simulator",
    description="Interactive dual-screen workflow simulator for DoganAI Compliance Kit",
    version="1.0.0"
)

# Get the directory paths
CURRENT_DIR = Path(__file__).parent
STATIC_DIR = CURRENT_DIR / "static"
TEMPLATES_DIR = CURRENT_DIR / "templates"

# Create directories if they don't exist
STATIC_DIR.mkdir(exist_ok=True)
TEMPLATES_DIR.mkdir(exist_ok=True)

# Mount static files
workflow_app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Initialize templates
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

@workflow_app.get("/", response_class=HTMLResponse)
async def workflow_simulator_home(request: Request):
    """
    Serve the main workflow simulator page
    """
    # Read the HTML content from the existing file
    html_file = CURRENT_DIR / "workflow_simulator.html"
    
    if html_file.exists():
        with open(html_file, 'r', encoding='utf-8') as f:
            content = f.read()
        return HTMLResponse(content=content)
    else:
        return HTMLResponse(
            content="<h1>Workflow Simulator Not Found</h1><p>Please ensure workflow_simulator.html exists.</p>",
            status_code=404
        )

@workflow_app.get("/health")
async def health_check():
    """
    Health check endpoint for the workflow simulator
    """
    return {
        "status": "healthy",
        "service": "DoganAI Workflow Simulator",
        "version": "1.0.0"
    }

@workflow_app.get("/api/demo-data")
async def get_demo_data():
    """
    Provide demo data for the workflow simulator
    """
    return {
        "demo_projects": [
            {
                "id": "demo-1",
                "name": "GDPR Compliance Assessment",
                "type": "gdpr",
                "status": "completed",
                "progress": 100
            },
            {
                "id": "demo-2",
                "name": "ISO 27001 Certification",
                "type": "iso27001",
                "status": "in_progress",
                "progress": 65
            },
            {
                "id": "demo-3",
                "name": "SOX Compliance Review",
                "type": "sox",
                "status": "pending",
                "progress": 0
            }
        ],
        "system_metrics": {
            "api_status": "online",
            "database_status": "online",
            "ai_engine_status": "processing",
            "payment_gateway_status": "ready",
            "active_sessions": 42,
            "completed_assessments": 1247,
            "success_rate": 98.5
        },
        "recent_activities": [
            {
                "timestamp": "2024-01-20T10:30:00Z",
                "type": "assessment_completed",
                "user": "john.doe@company.com",
                "project": "GDPR Compliance Assessment"
            },
            {
                "timestamp": "2024-01-20T10:25:00Z",
                "type": "payment_processed",
                "user": "jane.smith@enterprise.com",
                "amount": "$299.00"
            },
            {
                "timestamp": "2024-01-20T10:20:00Z",
                "type": "ai_analysis_started",
                "user": "admin@startup.io",
                "project": "Custom Compliance Framework"
            }
        ]
    }

@workflow_app.get("/api/translations/{language}")
async def get_translations(language: str):
    """
    Get translations for the specified language
    """
    translations = {
        "en": {
            "title": "DoganAI Compliance Kit - Workflow Simulator",
            "userScreen": "User Screen - Mobile",
            "systemView": "System & Team View",
            "compactMode": "Compact Mode",
            "language": "Language",
            "welcome": "Welcome to DoganAI",
            "signUp": "Sign Up",
            "projectIntake": "Project Intake",
            "aiAssistant": "AI Assistant",
            "reviewPolicies": "Review & Policies",
            "payment": "Payment",
            "completion": "Completion",
            "getStarted": "Get Started",
            "next": "Next",
            "previous": "Previous",
            "complete": "Complete",
            "eventLog": "Event Log",
            "systemStatus": "System Status",
            "journeyMap": "Journey Map",
            "online": "Online",
            "processing": "Processing",
            "ready": "Ready",
            "downloadReceipt": "Download Receipt",
            "escalateToHuman": "Escalate to Human",
            "welcomeDesc": "Your AI-powered compliance solution",
            "signUpDesc": "Create your account to get started",
            "projectDesc": "Tell us about your compliance needs",
            "aiDesc": "Our AI assistant will guide you",
            "reviewDesc": "Review policies and recommendations",
            "paymentDesc": "Secure payment processing",
            "completionDesc": "Your compliance journey is complete"
        },
        "ar": {
            "title": "مجموعة دوجان للامتثال الذكي - محاكي سير العمل",
            "userScreen": "شاشة المستخدم - الهاتف المحمول",
            "systemView": "عرض النظام والفريق",
            "compactMode": "الوضع المضغوط",
            "language": "اللغة",
            "welcome": "مرحباً بك في دوجان الذكي",
            "signUp": "إنشاء حساب",
            "projectIntake": "استقبال المشروع",
            "aiAssistant": "المساعد الذكي",
            "reviewPolicies": "مراجعة السياسات",
            "payment": "الدفع",
            "completion": "الإنجاز",
            "getStarted": "ابدأ الآن",
            "next": "التالي",
            "previous": "السابق",
            "complete": "إكمال",
            "eventLog": "سجل الأحداث",
            "systemStatus": "حالة النظام",
            "journeyMap": "خريطة الرحلة",
            "online": "متصل",
            "processing": "قيد المعالجة",
            "ready": "جاهز",
            "downloadReceipt": "تحميل الإيصال",
            "escalateToHuman": "تصعيد لمشغل بشري",
            "welcomeDesc": "حلول الامتثال المدعومة بالذكاء الاصطناعي",
            "signUpDesc": "أنشئ حسابك للبدء",
            "projectDesc": "أخبرنا عن احتياجات الامتثال الخاصة بك",
            "aiDesc": "سيقوم مساعدنا الذكي بإرشادك",
            "reviewDesc": "مراجعة السياسات والتوصيات",
            "paymentDesc": "معالجة دفع آمنة",
            "completionDesc": "رحلة الامتثال الخاصة بك مكتملة"
        }
    }
    
    return translations.get(language, translations["en"])

@workflow_app.post("/api/submit-form")
async def submit_form(request: Request):
    """
    Handle form submissions from the workflow simulator
    """
    data = await request.json()
    
    # Process the form data (in a real app, this would save to database)
    response = {
        "success": True,
        "message": "Form submitted successfully",
        "data": data,
        "next_step": data.get("current_step", 0) + 1
    }
    
    return response

@workflow_app.post("/api/generate-receipt")
async def generate_receipt(request: Request):
    """
    Generate a receipt for completed workflow
    """
    data = await request.json()
    
    receipt_data = {
        "receipt_id": f"DOG-{int(__import__('time').time())}",
        "date": __import__('datetime').datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "customer_name": data.get("name", "Customer"),
        "company": data.get("company", "Company"),
        "service": "AI Compliance Consultation",
        "amount": "$299.00",
        "payment_method": data.get("payment_method", "Credit Card"),
        "status": "Completed",
        "items": [
            {
                "description": "Risk Analysis & Assessment",
                "amount": "$99.00"
            },
            {
                "description": "Policy Recommendations",
                "amount": "$100.00"
            },
            {
                "description": "Implementation Support",
                "amount": "$100.00"
            }
        ]
    }
    
    return receipt_data

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "workflow_app:workflow_app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    )
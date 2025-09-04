"""
AI Agent Microservice - Production Ready
Intelligent user guidance and system assistance
"""

import os
import json
import logging
import time
import uuid
import asyncio
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional, Union
from pathlib import Path
import yaml
from fastapi import FastAPI, HTTPException, Depends, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
# from fastapi.middleware.trustedhost import TrustedHostMiddleware  # Removed for development
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field, ValidationError
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
import structlog
import redis
import jwt
import requests
import aiohttp

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
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

logger = structlog.get_logger(__name__)

# =============================================================================
# CONFIGURATION
# =============================================================================

# Environment variables
APP_NAME = os.getenv("APP_NAME", "AI Agent Microservice")
APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
DEBUG = os.getenv("DEBUG", "false").lower() == "true"

# Security configuration
SECRET_KEY = os.getenv("SECRET_KEY", "7bBxUxlAEQjNKLYw_lzR3dzBxjtEZVwu-QWd9zyeImI")
API_KEY_HEADER = os.getenv("API_KEY_HEADER", "X-API-Key")

# Redis configuration
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "")
REDIS_DB = int(os.getenv("REDIS_DB", "4"))

# Service URLs
COMPLIANCE_ENGINE_URL = os.getenv("COMPLIANCE_ENGINE_URL", "http://localhost:8000")
BENCHMARKS_URL = os.getenv("BENCHMARKS_URL", "http://localhost:8001")
AI_ML_URL = os.getenv("AI_ML_URL", "http://localhost:8002")
INTEGRATIONS_URL = os.getenv("INTEGRATIONS_URL", "http://localhost:8003")
AUTH_URL = os.getenv("AUTH_URL", "http://localhost:8004")

# =============================================================================
# REDIS SETUP
# =============================================================================

def get_redis_client():
    """Get Redis client for conversation and guidance data storage"""
    try:
        redis_client = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            password=REDIS_PASSWORD if REDIS_PASSWORD else None,
            db=REDIS_DB,
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5
        )
        redis_client.ping()
        return redis_client
    except Exception as e:
        logger.warning("Redis connection failed, using in-memory storage", error=str(e))
        return None

# =============================================================================
# AI AGENT KNOWLEDGE BASE
# =============================================================================

# System guidance and help content
SYSTEM_GUIDANCE = {
    "welcome": {
        "title": "Welcome to DoganAI Compliance Kit",
        "message": "I'm your AI assistant, here to guide you through KSA regulatory compliance. How can I help you today?",
        "suggestions": [
            "Run a compliance test",
            "View vendor integrations",
            "Generate compliance reports",
            "Get AI analysis",
            "Learn about KSA regulations"
        ]
    },
    "compliance_testing": {
        "title": "Compliance Testing Guide",
        "steps": [
            "1. Select your organization type (Banking, Healthcare, etc.)",
            "2. Choose the regulatory framework (NCA, SAMA, MoH)",
            "3. Upload or input your compliance evidence",
            "4. Review the automated assessment results",
            "5. Get detailed recommendations for improvement"
        ],
        "tips": [
            "Ensure all evidence documents are up-to-date",
            "Include both technical and procedural documentation",
            "Review previous assessment results for trends"
        ]
    },
    "vendor_integrations": {
        "title": "Vendor Integration Guide",
        "description": "We integrate with leading vendors to provide comprehensive compliance solutions:",
        "vendors": {
            "IBM Watson": "AI-powered compliance monitoring and risk assessment",
            "Lenovo": "Hardware security and device management",
            "Microsoft": "Cloud security and compliance automation",
            "Cisco": "Network security and threat protection",
            "Fortinet": "Unified security platform",
            "Palo Alto": "Next-generation security solutions"
        },
        "benefits": [
            "Real-time compliance monitoring",
            "Automated risk assessment",
            "Integrated security solutions",
            "Comprehensive reporting"
        ]
    },
    "ksa_regulations": {
        "title": "KSA Regulatory Framework Overview",
        "frameworks": {
            "NCA": {
                "name": "National Cybersecurity Authority",
                "scope": "All sectors in Saudi Arabia",
                "focus": "Cybersecurity governance, risk management, incident response",
                "compliance_levels": ["Basic", "Enhanced", "Advanced"]
            },
            "SAMA": {
                "name": "Saudi Arabian Monetary Authority",
                "scope": "Financial institutions",
                "focus": "Financial security, data protection, regulatory reporting",
                "compliance_levels": ["Compliant", "Partially Compliant", "Non-Compliant"]
            },
            "MoH": {
                "name": "Ministry of Health",
                "scope": "Healthcare organizations",
                "focus": "Patient data security, medical device security, staff training",
                "compliance_levels": ["Compliant", "Partially Compliant", "Non-Compliant"]
            }
        }
    },
    "ai_analysis": {
        "title": "AI/ML Analysis Guide",
        "capabilities": [
            "Risk Assessment: Identify and quantify compliance risks",
            "Gap Analysis: Find compliance gaps and provide recommendations",
            "Trend Analysis: Track compliance improvements over time",
            "Anomaly Detection: Identify unusual patterns in compliance data"
        ],
        "use_cases": [
            "Automated compliance scoring",
            "Predictive risk modeling",
            "Intelligent recommendation engine",
            "Real-time compliance monitoring"
        ]
    },
    "reports": {
        "title": "Reporting and Analytics Guide",
        "report_types": [
            "Compliance Summary: High-level compliance status",
            "Detailed Assessment: Comprehensive compliance analysis",
            "Risk Report: Risk assessment and mitigation strategies",
            "Trend Analysis: Historical compliance performance"
        ],
        "features": [
            "Automated report generation",
            "Customizable templates",
            "Export to PDF/Excel",
            "Scheduled reporting"
        ]
    }
}

# User journey guidance
USER_JOURNEYS = {
    "new_user": {
        "title": "Getting Started",
        "steps": [
            "Complete your profile and organization setup",
            "Take a guided tour of the platform",
            "Run your first compliance assessment",
            "Review results and recommendations",
            "Set up vendor integrations as needed"
        ]
    },
    "compliance_officer": {
        "title": "Compliance Officer Workflow",
        "steps": [
            "Review current compliance status",
            "Identify gaps and risks",
            "Implement recommended controls",
            "Monitor progress and improvements",
            "Generate reports for stakeholders"
        ]
    },
    "vendor_partner": {
        "title": "Vendor Partner Workflow",
        "steps": [
            "Review vendor integration status",
            "Test integration capabilities",
            "Monitor compliance performance",
            "Generate vendor-specific reports",
            "Collaborate with customers on solutions"
        ]
    },
    "auditor": {
        "title": "Auditor Workflow",
        "steps": [
            "Review compliance assessments",
            "Validate evidence and controls",
            "Generate audit reports",
            "Track compliance trends",
            "Provide recommendations"
        ]
    }
}

# =============================================================================
# PYDANTIC MODELS
# =============================================================================

class UserQuery(BaseModel):
    """User query for AI guidance"""
    query: str = Field(..., description="User's question or request")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context")
    user_role: Optional[str] = Field(None, description="User's role in the system")
    user_organization: Optional[str] = Field(None, description="User's organization")

class AIResponse(BaseModel):
    """AI agent response"""
    response_id: str
    query: str
    answer: str
    guidance_type: str
    suggestions: List[str]
    related_topics: List[str]
    confidence_score: float
    timestamp: datetime

class GuidanceRequest(BaseModel):
    """Request for specific guidance"""
    guidance_type: str = Field(..., description="Type of guidance needed")
    user_context: Optional[Dict[str, Any]] = Field(None, description="User context")
    specific_question: Optional[str] = Field(None, description="Specific question")

class SystemStatus(BaseModel):
    """System status information"""
    service: str
    status: str
    response_time: float
    last_check: datetime

# =============================================================================
# AI AGENT ENGINE
# =============================================================================

class AIAgentEngine:
    """Core AI agent engine for user guidance"""
    
    def __init__(self):
        self.redis_client = get_redis_client()
        self.conversation_history = {}
        self.system_status = {}
        
    async def process_user_query(self, query: str, context: Optional[Dict[str, Any]] = None) -> AIResponse:
        """Process user query and provide intelligent guidance"""
        try:
            response_id = str(uuid.uuid4())
            
            # Analyze query intent
            intent = self._analyze_query_intent(query)
            
            # Generate appropriate response
            answer, guidance_type, suggestions, related_topics = await self._generate_response(
                query, intent, context
            )
            
            # Calculate confidence score
            confidence_score = self._calculate_confidence(query, intent, context)
            
            # Store conversation
            self._store_conversation(response_id, query, answer, context)
            
            return AIResponse(
                response_id=response_id,
                query=query,
                answer=answer,
                guidance_type=guidance_type,
                suggestions=suggestions,
                related_topics=related_topics,
                confidence_score=confidence_score,
                timestamp=datetime.now(timezone.utc)
            )
            
        except Exception as e:
            logger.error("Failed to process user query", error=str(e))
            raise
    
    def _analyze_query_intent(self, query: str) -> str:
        """Analyze user query to determine intent"""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ["compliance", "test", "assessment", "audit"]):
            return "compliance_testing"
        elif any(word in query_lower for word in ["vendor", "integration", "partner"]):
            return "vendor_integrations"
        elif any(word in query_lower for word in ["regulation", "ksa", "nca", "sama", "moh"]):
            return "ksa_regulations"
        elif any(word in query_lower for word in ["ai", "analysis", "machine learning", "ml"]):
            return "ai_analysis"
        elif any(word in query_lower for word in ["report", "analytics", "dashboard"]):
            return "reports"
        elif any(word in query_lower for word in ["help", "guide", "how to", "tutorial"]):
            return "general_guidance"
        elif any(word in query_lower for word in ["welcome", "start", "begin"]):
            return "welcome"
        else:
            return "general_guidance"
    
    async def _generate_response(self, query: str, intent: str, context: Optional[Dict[str, Any]]) -> tuple:
        """Generate response based on intent and context"""
        try:
            if intent == "welcome":
                return self._get_welcome_response()
            elif intent == "compliance_testing":
                return self._get_compliance_guidance()
            elif intent == "vendor_integrations":
                return self._get_vendor_guidance()
            elif intent == "ksa_regulations":
                return self._get_regulation_guidance()
            elif intent == "ai_analysis":
                return self._get_ai_guidance()
            elif intent == "reports":
                return self._get_report_guidance()
            else:
                return self._get_general_guidance(query)
                
        except Exception as e:
            logger.error("Failed to generate response", error=str(e))
            return (
                "I apologize, but I'm having trouble processing your request. Please try rephrasing your question.",
                "general_guidance",
                ["Try a different approach", "Contact support if the issue persists"],
                ["general_help", "support"]
            )
    
    def _get_welcome_response(self) -> tuple:
        """Get welcome response"""
        guidance = SYSTEM_GUIDANCE["welcome"]
        return (
            guidance["message"],
            "welcome",
            guidance["suggestions"],
            ["compliance_testing", "vendor_integrations", "ai_analysis", "reports"]
        )
    
    def _get_compliance_guidance(self) -> tuple:
        """Get compliance testing guidance"""
        guidance = SYSTEM_GUIDANCE["compliance_testing"]
        answer = f"{guidance['title']}\n\n"
        answer += "\n".join(guidance["steps"])
        answer += "\n\nTips:\n" + "\n".join(guidance["tips"])
        
        return (
            answer,
            "compliance_testing",
            ["Run compliance test", "View previous results", "Get recommendations"],
            ["compliance_testing", "reports", "ai_analysis"]
        )
    
    def _get_vendor_guidance(self) -> tuple:
        """Get vendor integration guidance"""
        guidance = SYSTEM_GUIDANCE["vendor_integrations"]
        answer = f"{guidance['title']}\n\n{guidance['description']}\n\n"
        
        for vendor, description in guidance["vendors"].items():
            answer += f"• {vendor}: {description}\n"
        
        answer += "\nBenefits:\n" + "\n".join([f"• {benefit}" for benefit in guidance["benefits"]])
        
        return (
            answer,
            "vendor_integrations",
            ["View vendor status", "Test integrations", "Get vendor reports"],
            ["vendor_integrations", "compliance_testing", "reports"]
        )
    
    def _get_regulation_guidance(self) -> tuple:
        """Get KSA regulation guidance"""
        guidance = SYSTEM_GUIDANCE["ksa_regulations"]
        answer = f"{guidance['title']}\n\n"
        
        for framework_id, framework in guidance["frameworks"].items():
            answer += f"{framework['name']} ({framework_id}):\n"
            answer += f"Scope: {framework['scope']}\n"
            answer += f"Focus: {framework['focus']}\n"
            answer += f"Compliance Levels: {', '.join(framework['compliance_levels'])}\n\n"
        
        return (
            answer,
            "ksa_regulations",
            ["Learn more about NCA", "Understand SAMA requirements", "Explore MoH standards"],
            ["ksa_regulations", "compliance_testing", "ai_analysis"]
        )
    
    def _get_ai_guidance(self) -> tuple:
        """Get AI/ML analysis guidance"""
        guidance = SYSTEM_GUIDANCE["ai_analysis"]
        answer = f"{guidance['title']}\n\nCapabilities:\n"
        answer += "\n".join([f"• {capability}" for capability in guidance["capabilities"]])
        answer += "\n\nUse Cases:\n"
        answer += "\n".join([f"• {use_case}" for use_case in guidance["use_cases"]])
        
        return (
            answer,
            "ai_analysis",
            ["Run AI analysis", "View AI insights", "Get recommendations"],
            ["ai_analysis", "compliance_testing", "reports"]
        )
    
    def _get_report_guidance(self) -> tuple:
        """Get reporting guidance"""
        guidance = SYSTEM_GUIDANCE["reports"]
        answer = f"{guidance['title']}\n\nReport Types:\n"
        answer += "\n".join([f"• {report_type}" for report_type in guidance["report_types"]])
        answer += "\n\nFeatures:\n"
        answer += "\n".join([f"• {feature}" for feature in guidance["features"]])
        
        return (
            answer,
            "reports",
            ["Generate report", "View report history", "Schedule reports"],
            ["reports", "compliance_testing", "ai_analysis"]
        )
    
    def _get_general_guidance(self, query: str) -> tuple:
        """Get general guidance for unclear queries"""
        return (
            "I understand you're asking about the DoganAI Compliance Kit. To better assist you, could you please specify what you'd like to know? You can ask about:\n\n"
            "• Compliance testing and assessments\n"
            "• Vendor integrations\n"
            "• KSA regulations (NCA, SAMA, MoH)\n"
            "• AI/ML analysis capabilities\n"
            "• Reporting and analytics\n"
            "• Getting started with the platform",
            "general_guidance",
            ["Learn about compliance testing", "Explore vendor integrations", "Understand KSA regulations"],
            ["compliance_testing", "vendor_integrations", "ksa_regulations"]
        )
    
    def _calculate_confidence(self, query: str, intent: str, context: Optional[Dict[str, Any]]) -> float:
        """Calculate confidence score for the response"""
        base_score = 0.7
        
        # Increase confidence for clear intent
        if intent != "general_guidance":
            base_score += 0.2
        
        # Increase confidence for longer, more specific queries
        if len(query.split()) > 5:
            base_score += 0.1
        
        # Increase confidence if context is provided
        if context:
            base_score += 0.1
        
        return min(1.0, base_score)
    
    def _store_conversation(self, response_id: str, query: str, answer: str, context: Optional[Dict[str, Any]]):
        """Store conversation in Redis for learning and analytics"""
        try:
            conversation_data = {
                "response_id": response_id,
                "query": query,
                "answer": answer,
                "context": context,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            if self.redis_client:
                self.redis_client.setex(
                    f"conversation:{response_id}",
                    86400,  # 24 hours TTL
                    json.dumps(conversation_data)
                )
            
            # Store in memory as backup
            self.conversation_history[response_id] = conversation_data
            
        except Exception as e:
            logger.error("Failed to store conversation", error=str(e))
    
    async def get_system_status(self) -> Dict[str, SystemStatus]:
        """Get status of all system services"""
        try:
            services = {
                "compliance_engine": COMPLIANCE_ENGINE_URL,
                "benchmarks": BENCHMARKS_URL,
                "ai_ml": AI_ML_URL,
                "integrations": INTEGRATIONS_URL,
                "auth": AUTH_URL
            }
            
            status_results = {}
            
            for service_name, service_url in services.items():
                try:
                    start_time = time.time()
                    async with aiohttp.ClientSession() as session:
                        async with session.get(f"{service_url}/health", timeout=5) as response:
                            response_time = time.time() - start_time
                            if response.status == 200:
                                status_results[service_name] = SystemStatus(
                                    service=service_name,
                                    status="healthy",
                                    response_time=response_time,
                                    last_check=datetime.now(timezone.utc)
                                )
                            else:
                                status_results[service_name] = SystemStatus(
                                    service=service_name,
                                    status="unhealthy",
                                    response_time=response_time,
                                    last_check=datetime.now(timezone.utc)
                                )
                except Exception as e:
                    logger.warning(f"Failed to check {service_name} status", error=str(e))
                    status_results[service_name] = SystemStatus(
                        service=service_name,
                        status="unreachable",
                        response_time=0.0,
                        last_check=datetime.now(timezone.utc)
                    )
            
            return status_results
            
        except Exception as e:
            logger.error("Failed to get system status", error=str(e))
            return {}
    
    def get_user_journey(self, user_type: str) -> Optional[Dict[str, Any]]:
        """Get user journey guidance for specific user type"""
        return USER_JOURNEYS.get(user_type)
    
    def get_guidance_topic(self, topic: str) -> Optional[Dict[str, Any]]:
        """Get specific guidance topic"""
        return SYSTEM_GUIDANCE.get(topic)

# =============================================================================
# FASTAPI APPLICATION
# =============================================================================

app = FastAPI(
    title="DoganAI Agent Service",
    description="AI Agent service for intelligent user guidance and system assistance",
    version="1.0.0"
)

# Add middleware
# TrustedHostMiddleware removed for development - ENABLE FOR PRODUCTION
# app.add_middleware(
#     TrustedHostMiddleware,
#     allowed_hosts=["*"]  # Allow all hosts for development - CONFIGURE FOR PRODUCTION
# )

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if DEBUG else ["https://www.dogan-ai.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize AI agent engine
ai_agent = AIAgentEngine()

# =============================================================================
# PROMETHEUS METRICS
# =============================================================================

AGENT_REQUESTS = Counter(
    "ai_agent_requests_total",
    "Total AI agent requests",
    ["method", "endpoint", "status"]
)

AGENT_LATENCY = Histogram(
    "ai_agent_request_duration_seconds",
    "AI agent request latency in seconds",
    ["method", "endpoint"]
)

# =============================================================================
# API ENDPOINTS
# =============================================================================

@app.post("/agent/query", response_model=AIResponse)
async def process_user_query(user_query: UserQuery):
    """Process user query and provide AI guidance"""
    try:
        response = await ai_agent.process_user_query(
            user_query.query,
            user_query.context
        )
        
        # Record metrics
        AGENT_REQUESTS.labels(method="POST", endpoint="/agent/query", status="success").inc()
        
        return response
        
    except Exception as e:
        logger.error("Failed to process user query", error=str(e))
        AGENT_REQUESTS.labels(method="POST", endpoint="/agent/query", status="error").inc()
        raise HTTPException(
            status_code=500,
            detail="Failed to process user query"
        )

@app.get("/agent/guidance/{guidance_type}")
async def get_guidance(guidance_type: str):
    """Get specific guidance topic"""
    try:
        guidance = ai_agent.get_guidance_topic(guidance_type)
        if not guidance:
            raise HTTPException(
                status_code=404,
                detail=f"Guidance topic '{guidance_type}' not found"
            )
        
        return guidance
        
    except Exception as e:
        logger.error("Failed to get guidance", error=str(e))
        raise HTTPException(
            status_code=500,
            detail="Failed to get guidance"
        )

@app.get("/agent/journey/{user_type}")
async def get_user_journey(user_type: str):
    """Get user journey guidance for specific user type"""
    try:
        journey = ai_agent.get_user_journey(user_type)
        if not journey:
            raise HTTPException(
                status_code=404,
                detail=f"User journey for '{user_type}' not found"
            )
        
        return journey
        
    except Exception as e:
        logger.error("Failed to get user journey", error=str(e))
        raise HTTPException(
            status_code=500,
            detail="Failed to get user journey"
        )

@app.get("/agent/status")
async def get_system_status():
    """Get system status for all services"""
    try:
        status = await ai_agent.get_system_status()
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "services": status
        }
        
    except Exception as e:
        logger.error("Failed to get system status", error=str(e))
        raise HTTPException(
            status_code=500,
            detail="Failed to get system status"
        )

@app.get("/agent/topics")
async def get_available_topics():
    """Get list of available guidance topics"""
    try:
        return {
            "topics": list(SYSTEM_GUIDANCE.keys()),
            "user_journeys": list(USER_JOURNEYS.keys()),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        logger.error("Failed to get available topics", error=str(e))
        raise HTTPException(
            status_code=500,
            detail="Failed to get available topics"
        )

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": APP_NAME,
        "version": APP_VERSION,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "conversations_stored": len(ai_agent.conversation_history)
    }

@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    from fastapi.responses import Response
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )

# =============================================================================
# STARTUP AND SHUTDOWN
# =============================================================================

@app.on_event("startup")
async def startup_event():
    """Application startup event"""
    logger.info(
        "Starting AI Agent Microservice",
        version=APP_VERSION,
        environment=ENVIRONMENT,
        debug=DEBUG
    )

@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event"""
    logger.info("Shutting down AI Agent Microservice")

# =============================================================================
# ERROR HANDLERS
# =============================================================================

@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    return {
        "detail": "Validation error",
        "errors": exc.errors()
    }

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error("Unhandled exception", error=str(exc), exc_info=True)
    return {
        "detail": "Internal server error"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8005)

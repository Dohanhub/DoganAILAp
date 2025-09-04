"""
AI-ML Microservice - Production Ready
Local LLM inference, compliance Q&A, risk prediction, and natural language processing
"""

import os
import json
import logging
import time
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Union
from pathlib import Path
import yaml
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, Request, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
# from fastapi.middleware.trustedhost import TrustedHostMiddleware  # Removed for development
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field, ValidationError
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
import structlog
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import joblib
import redis
import jwt
from cryptography.fernet import Fernet
import hashlib
import pickle
import psutil
import asyncio

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
APP_NAME = os.getenv("APP_NAME", "AI-ML Microservice")
APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
DEBUG = os.getenv("DEBUG", "false").lower() == "true"

# Security configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
API_KEY_HEADER = os.getenv("API_KEY_HEADER", "X-API-Key")
ENABLE_HTTPS = os.getenv("ENABLE_HTTPS", "false").lower() == "true"

# Redis configuration
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "")
REDIS_DB = int(os.getenv("REDIS_DB", "1"))

# Model configuration
MODEL_PATH = os.getenv("MODEL_PATH", "./models")
ENABLE_LOCAL_LLM = os.getenv("ENABLE_LOCAL_LLM", "false").lower() == "true"
LLM_MODEL_PATH = os.getenv("LLM_MODEL_PATH", "./llm_models")

# =============================================================================
# HARDWARE MONITORING & LOAD TESTING
# =============================================================================

def get_hardware_metrics():
    """Get comprehensive real-time hardware utilization metrics"""
    try:
        # CPU metrics
        cpu_usage = psutil.cpu_percent(interval=1)
        cpu_count = psutil.cpu_count()
        cpu_freq = psutil.cpu_freq()
        cpu_stats = psutil.cpu_stats()
        
        # Memory metrics
        memory = psutil.virtual_memory()
        swap = psutil.swap_memory()
        
        # Disk metrics
        disk = psutil.disk_usage('/')
        disk_io = psutil.disk_io_counters()
        
        # Network metrics
        network = psutil.net_io_counters()
        network_connections = len(psutil.net_connections())
        
        # GPU usage (if available)
        gpu_usage = None
        gpu_memory = None
        gpu_temp = None
        try:
            import GPUtil
            gpus = GPUtil.getGPUs()
            if gpus:
                gpu = gpus[0]
                gpu_usage = gpu.load * 100
                gpu_memory = gpu.memoryUtil * 100
                gpu_temp = gpu.temperature
        except:
            pass
        
        # Temperature (if available)
        temperature = None
        try:
            if os.name == 'nt':  # Windows
                import wmi
                w = wmi.WMI(namespace="root\\OpenHardwareMonitor")
                temperature_infos = w.Sensor()
                for sensor in temperature_infos:
                    if sensor.SensorType == 'Temperature':
                        temperature = sensor.Value
                        break
        except:
            pass
        
        # Process metrics
        processes = len(psutil.pids())
        
        # System uptime
        boot_time = datetime.fromtimestamp(psutil.boot_time())
        uptime = datetime.now() - boot_time
        
        return {
            "timestamp": datetime.now().isoformat(),
            "cpu": {
                "usage_percent": round(cpu_usage, 2),
                "count": cpu_count,
                "frequency_mhz": round(cpu_freq.current, 2) if cpu_freq else None,
                "ctx_switches": cpu_stats.ctx_switches,
                "interrupts": cpu_stats.interrupts,
                "soft_interrupts": cpu_stats.soft_interrupts,
                "syscalls": cpu_stats.syscalls
            },
            "memory": {
                "total_gb": round(memory.total / (1024**3), 2),
                "available_gb": round(memory.available / (1024**3), 2),
                "used_gb": round(memory.used / (1024**3), 2),
                "usage_percent": round(memory.percent, 2),
                "swap_total_gb": round(swap.total / (1024**3), 2),
                "swap_used_gb": round(swap.used / (1024**3), 2),
                "swap_usage_percent": round(swap.percent, 2)
            },
            "disk": {
                "total_gb": round(disk.total / (1024**3), 2),
                "used_gb": round(disk.used / (1024**3), 2),
                "free_gb": round(disk.free / (1024**3), 2),
                "usage_percent": round(disk.percent, 2),
                "read_bytes": disk_io.read_bytes,
                "write_bytes": disk_io.write_bytes,
                "read_count": disk_io.read_count,
                "write_count": disk_io.write_count
            },
            "network": {
                "bytes_sent": network.bytes_sent,
                "bytes_recv": network.bytes_recv,
                "packets_sent": network.packets_sent,
                "packets_recv": network.packets_recv,
                "connections": network_connections
            },
            "gpu": {
                "usage_percent": round(gpu_usage, 2) if gpu_usage else None,
                "memory_percent": round(gpu_memory, 2) if gpu_memory else None,
                "temperature_c": round(gpu_temp, 2) if gpu_temp else None
            },
            "system": {
                "temperature_c": round(temperature, 2) if temperature else None,
                "processes": processes,
                "uptime_seconds": int(uptime.total_seconds()),
                "boot_time": boot_time.isoformat()
            }
        }
        
    except Exception as e:
        logger.error("Failed to get hardware metrics", error=str(e))
        return {
            "timestamp": datetime.now().isoformat(),
            "error": str(e),
            "cpu": {"usage_percent": 0.0},
            "memory": {"usage_percent": 0.0},
            "disk": {"usage_percent": 0.0},
            "network": {"bytes_sent": 0, "bytes_recv": 0},
            "gpu": {"usage_percent": None},
            "system": {"temperature_c": None, "processes": 0}
        }

def get_performance_metrics():
    """Get performance metrics for AI operations"""
    try:
        # Get current hardware state
        hw_metrics = get_hardware_metrics()
        
        # Calculate performance scores
        cpu_score = max(0, 100 - hw_metrics["cpu"]["usage_percent"])
        memory_score = max(0, 100 - hw_metrics["memory"]["usage_percent"])
        disk_score = max(0, 100 - hw_metrics["disk"]["usage_percent"])
        
        # Overall performance score
        overall_score = (cpu_score + memory_score + disk_score) / 3
        
        return {
            "timestamp": datetime.now().isoformat(),
            "overall_score": round(overall_score, 2),
            "cpu_score": round(cpu_score, 2),
            "memory_score": round(memory_score, 2),
            "disk_score": round(disk_score, 2),
            "recommendations": get_performance_recommendations(hw_metrics),
            "hardware_metrics": hw_metrics
        }
        
    except Exception as e:
        logger.error("Failed to get performance metrics", error=str(e))
        return {"error": str(e)}

def get_performance_recommendations(metrics):
    """Get performance improvement recommendations"""
    recommendations = []
    
    if metrics["cpu"]["usage_percent"] > 80:
        recommendations.append("High CPU usage detected. Consider reducing concurrent AI operations.")
    
    if metrics["memory"]["usage_percent"] > 85:
        recommendations.append("High memory usage. Consider clearing cache or reducing batch sizes.")
    
    if metrics["disk"]["usage_percent"] > 90:
        recommendations.append("Disk space running low. Consider cleanup or expansion.")
    
    if metrics["gpu"]["usage_percent"] and metrics["gpu"]["usage_percent"] > 95:
        recommendations.append("GPU utilization very high. Consider reducing model complexity.")
    
    if not recommendations:
        recommendations.append("System performance is optimal for AI operations.")
    
    return recommendations

# =============================================================================
# LOAD TESTING FOR AI SCENARIOS
# =============================================================================

class LoadTestEngine:
    """Engine for testing hardware performance under various AI workloads"""
    
    def __init__(self):
        self.test_results = {}
        self.current_tests = {}
    
    async def run_comprehensive_load_test(self, test_config: Dict[str, Any]) -> Dict[str, Any]:
        """Run comprehensive load test with multiple AI scenarios"""
        test_id = str(uuid.uuid4())
        start_time = time.time()
        
        try:
            # Baseline metrics
            baseline_metrics = get_hardware_metrics()
            
            # Run different AI workload tests
            test_results = {
                "baseline": baseline_metrics,
                "text_processing": await self._test_text_processing(test_config.get("text_volume", 1000)),
                "image_processing": await self._test_image_processing(test_config.get("image_count", 100)),
                "model_inference": await self._test_model_inference(test_config.get("inference_requests", 500)),
                "data_analysis": await self._test_data_analysis(test_config.get("data_size", 10000)),
                "concurrent_operations": await self._test_concurrent_operations(test_config.get("concurrent_users", 50))
            }
            
            # Final metrics
            final_metrics = get_hardware_metrics()
            
            # Calculate performance impact
            performance_impact = self._calculate_performance_impact(baseline_metrics, final_metrics)
            
            # Generate recommendations
            recommendations = self._generate_load_test_recommendations(test_results, performance_impact)
            
            test_summary = {
                "test_id": test_id,
                "start_time": datetime.fromtimestamp(start_time).isoformat(),
                "duration_seconds": round(time.time() - start_time, 2),
                "test_config": test_config,
                "test_results": test_results,
                "final_metrics": final_metrics,
                "performance_impact": performance_impact,
                "recommendations": recommendations,
                "hardware_capacity_assessment": self._assess_hardware_capacity(test_results, performance_impact)
            }
            
            self.test_results[test_id] = test_summary
            return test_summary
            
        except Exception as e:
            logger.error("Load test failed", error=str(e))
            return {
                "test_id": test_id,
                "error": str(e),
                "duration_seconds": round(time.time() - start_time, 2)
            }
    
    async def _test_text_processing(self, text_volume: int) -> Dict[str, Any]:
        """Test text processing performance"""
        start_time = time.time()
        start_metrics = get_hardware_metrics()
        
        # Simulate text processing workload
        texts = [f"Sample text {i} for processing test" * 10 for i in range(text_volume)]
        processed = []
        
        for text in texts:
            # Simulate NLP processing
            processed.append(text.upper().split())
            if len(processed) % 100 == 0:
                await asyncio.sleep(0.01)  # Small delay to prevent overwhelming
        
        end_metrics = get_hardware_metrics()
        
        return {
            "texts_processed": len(processed),
            "duration_seconds": round(time.time() - start_time, 2),
            "start_metrics": start_metrics,
            "end_metrics": end_metrics,
            "throughput": round(len(processed) / (time.time() - start_time), 2)
        }
    
    async def _test_image_processing(self, image_count: int) -> Dict[str, Any]:
        """Test image processing performance"""
        start_time = time.time()
        start_metrics = get_hardware_metrics()
        
        # Simulate image processing workload
        for i in range(image_count):
            # Simulate image operations
            dummy_image = np.random.rand(224, 224, 3)
            processed = np.mean(dummy_image)
            if i % 50 == 0:
                await asyncio.sleep(0.01)
        
        end_metrics = get_hardware_metrics()
        
        return {
            "images_processed": image_count,
            "duration_seconds": round(time.time() - start_time, 2),
            "start_metrics": start_metrics,
            "end_metrics": end_metrics,
            "throughput": round(image_count / (time.time() - start_time), 2)
        }
    
    async def _test_model_inference(self, inference_requests: int) -> Dict[str, Any]:
        """Test model inference performance"""
        start_time = time.time()
        start_metrics = get_hardware_metrics()
        
        # Simulate model inference workload
        for i in range(inference_requests):
            # Simulate inference
            input_data = np.random.rand(1, 100)
            result = np.sum(input_data)
            if i % 100 == 0:
                await asyncio.sleep(0.01)
        
        end_metrics = get_hardware_metrics()
        
        return {
            "inferences_performed": inference_requests,
            "duration_seconds": round(time.time() - start_time, 2),
            "start_metrics": start_metrics,
            "end_metrics": end_metrics,
            "throughput": round(inference_requests / (time.time() - start_time), 2)
        }
    
    async def _test_data_analysis(self, data_size: int) -> Dict[str, Any]:
        """Test data analysis performance"""
        start_time = time.time()
        start_metrics = get_hardware_metrics()
        
        # Simulate data analysis workload
        data = np.random.rand(data_size, 10)
        
        # Perform various analyses
        mean_values = np.mean(data, axis=0)
        std_values = np.std(data, axis=0)
        correlation_matrix = np.corrcoef(data.T)
        
        end_metrics = get_hardware_metrics()
        
        return {
            "data_points_analyzed": data_size,
            "duration_seconds": round(time.time() - start_time, 2),
            "start_metrics": start_metrics,
            "end_metrics": end_metrics,
            "throughput": round(data_size / (time.time() - start_time), 2)
        }
    
    async def _test_concurrent_operations(self, concurrent_users: int) -> Dict[str, Any]:
        """Test concurrent operations performance"""
        start_time = time.time()
        start_metrics = get_hardware_metrics()
        
        # Simulate concurrent user operations
        async def simulate_user_operation(user_id: int):
            await asyncio.sleep(0.1)  # Simulate operation time
            return f"User {user_id} operation completed"
        
        # Run concurrent operations
        tasks = [simulate_user_operation(i) for i in range(concurrent_users)]
        results = await asyncio.gather(*tasks)
        
        end_metrics = get_hardware_metrics()
        
        return {
            "concurrent_users": concurrent_users,
            "duration_seconds": round(time.time() - start_time, 2),
            "start_metrics": start_metrics,
            "end_metrics": end_metrics,
            "operations_completed": len(results)
        }
    
    def _calculate_performance_impact(self, baseline: Dict, final: Dict) -> Dict[str, Any]:
        """Calculate performance impact of load testing"""
        try:
            cpu_impact = final["cpu"]["usage_percent"] - baseline["cpu"]["usage_percent"]
            memory_impact = final["memory"]["usage_percent"] - baseline["memory"]["usage_percent"]
            disk_impact = final["disk"]["usage_percent"] - baseline["disk"]["usage_percent"]
            
            return {
                "cpu_impact_percent": round(cpu_impact, 2),
                "memory_impact_percent": round(memory_impact, 2),
                "disk_impact_percent": round(disk_impact, 2),
                "overall_impact": round((cpu_impact + memory_impact + disk_impact) / 3, 2)
            }
        except:
            return {"error": "Could not calculate performance impact"}
    
    def _generate_load_test_recommendations(self, test_results: Dict, performance_impact: Dict) -> List[str]:
        """Generate recommendations based on load test results"""
        recommendations = []
        
        if performance_impact.get("cpu_impact_percent", 0) > 30:
            recommendations.append("High CPU impact detected. Consider CPU upgrade or workload distribution.")
        
        if performance_impact.get("memory_impact_percent", 0) > 25:
            recommendations.append("Significant memory pressure. Consider RAM upgrade or memory optimization.")
        
        if performance_impact.get("disk_impact_percent", 0) > 20:
            recommendations.append("Disk I/O bottleneck detected. Consider SSD upgrade or I/O optimization.")
        
        # Add specific recommendations based on test results
        if test_results.get("text_processing", {}).get("throughput", 0) < 100:
            recommendations.append("Text processing throughput is low. Consider optimizing NLP pipelines.")
        
        if test_results.get("image_processing", {}).get("throughput", 0) < 50:
            recommendations.append("Image processing throughput is low. Consider GPU acceleration.")
        
        if not recommendations:
            recommendations.append("Hardware performance is adequate for current AI workloads.")
        
        return recommendations
    
    def _assess_hardware_capacity(self, test_results: Dict, performance_impact: Dict) -> Dict[str, Any]:
        """Assess hardware capacity for AI workloads"""
        try:
            # Calculate capacity scores
            cpu_capacity = max(0, 100 - performance_impact.get("cpu_impact_percent", 0))
            memory_capacity = max(0, 100 - performance_impact.get("memory_impact_percent", 0))
            disk_capacity = max(0, 100 - performance_impact.get("disk_impact_percent", 0))
            
            overall_capacity = (cpu_capacity + memory_capacity + disk_capacity) / 3
            
            # Determine capacity level
            if overall_capacity >= 80:
                capacity_level = "Excellent"
                capacity_description = "Hardware can handle significantly more AI workloads"
            elif overall_capacity >= 60:
                capacity_level = "Good"
                capacity_description = "Hardware can handle current workloads with room for growth"
            elif overall_capacity >= 40:
                capacity_level = "Moderate"
                capacity_description = "Hardware is at moderate capacity, consider optimization"
            else:
                capacity_level = "Limited"
                capacity_description = "Hardware is near capacity, upgrade recommended"
            
            return {
                "overall_capacity_percent": round(overall_capacity, 2),
                "cpu_capacity_percent": round(cpu_capacity, 2),
                "memory_capacity_percent": round(memory_capacity, 2),
                "disk_capacity_percent": round(disk_capacity, 2),
                "capacity_level": capacity_level,
                "capacity_description": capacity_description,
                "recommended_actions": self._get_capacity_recommendations(overall_capacity)
            }
            
        except Exception as e:
            return {"error": f"Could not assess capacity: {str(e)}"}
    
    def _get_capacity_recommendations(self, capacity_percent: float) -> List[str]:
        """Get recommendations based on capacity assessment"""
        if capacity_percent >= 80:
            return [
                "System can handle increased AI workloads",
                "Consider adding more AI models or services",
                "Monitor for any performance degradation"
            ]
        elif capacity_percent >= 60:
            return [
                "System has good capacity for current workloads",
                "Consider gradual workload increases",
                "Monitor resource usage trends"
            ]
        elif capacity_percent >= 40:
            return [
                "Optimize existing AI workloads",
                "Consider hardware upgrades if workloads increase",
                "Implement resource monitoring and alerts"
            ]
        else:
            return [
                "Immediate hardware upgrade recommended",
                "Reduce current AI workloads",
                "Implement aggressive resource optimization"
            ]

# Initialize load test engine
load_test_engine = LoadTestEngine()

# =============================================================================
# REDIS SETUP
# =============================================================================

def get_redis_client():
    """Get Redis client for caching and model storage"""
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
# SECURITY
# =============================================================================

class APIKeyAuth:
    """API Key authentication"""
    def __init__(self):
        self.scheme = HTTPBearer(auto_error=False)
    
    async def __call__(self, request: Request) -> Optional[str]:
        # Check API key header first
        api_key = request.headers.get(API_KEY_HEADER)
        if api_key:
            if await self.validate_api_key(api_key):
                return api_key
        
        # Fall back to Bearer token
        credentials: HTTPAuthorizationCredentials = await self.scheme(request)
        if credentials:
            if await self.validate_jwt_token(credentials.credentials):
                return credentials.credentials
        
        return None
    
    async def validate_api_key(self, api_key: str) -> bool:
        """Validate API key"""
        valid_keys = os.getenv("VALID_API_KEYS", "").split(",")
        return api_key in valid_keys
    
    async def validate_jwt_token(self, token: str) -> bool:
        """Validate JWT token"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            return True
        except jwt.ExpiredSignatureError:
            return False
        except jwt.InvalidTokenError:
            return False

# Authentication dependency
auth_handler = APIKeyAuth()

async def get_current_user(api_key: Optional[str] = Depends(auth_handler)):
    if not api_key:
        raise HTTPException(
            status_code=401,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return api_key

# =============================================================================
# PROMETHEUS METRICS
# =============================================================================

REQUEST_COUNT = Counter(
    "ai_ml_requests_total",
    "Total AI-ML requests",
    ["method", "endpoint", "status"]
)

REQUEST_LATENCY = Histogram(
    "ai_ml_request_duration_seconds",
    "AI-ML request latency in seconds",
    ["method", "endpoint"]
)

PREDICTION_COUNT = Counter(
    "ai_ml_predictions_total",
    "Total AI-ML predictions",
    ["model_type", "prediction_type"]
)

# =============================================================================
# PYDANTIC MODELS
# =============================================================================

class ComplianceQuestion(BaseModel):
    """Compliance question for Q&A"""
    question: str = Field(..., description="Compliance-related question")
    context: Optional[str] = Field(None, description="Additional context for the question")
    policy_type: Optional[str] = Field(None, description="Type of policy (NCA, SAMA, MoH, etc.)")
    language: str = Field("en", description="Language for the answer (en, ar)")
    
    class Config:
        schema_extra = {
            "example": {
                "question": "What are the cybersecurity requirements for financial institutions?",
                "context": "NCA compliance for banking sector",
                "policy_type": "NCA",
                "language": "en"
            }
        }

class ComplianceAnswer(BaseModel):
    """Compliance answer with confidence score"""
    question: str = Field(..., description="Original question")
    answer: str = Field(..., description="Generated answer")
    confidence_score: float = Field(..., description="Confidence score (0-1)")
    sources: List[str] = Field(..., description="Sources used for the answer")
    policy_references: List[str] = Field(..., description="Referenced policies")
    timestamp: datetime = Field(..., description="When the answer was generated")
    
    class Config:
        schema_extra = {
            "example": {
                "question": "What are the cybersecurity requirements for financial institutions?",
                "answer": "Financial institutions must implement comprehensive cybersecurity measures...",
                "confidence_score": 0.85,
                "sources": ["NCA Cybersecurity Framework", "SAMA Guidelines"],
                "policy_references": ["NCA-CYB-2024", "SAMA-SEC-2024"],
                "timestamp": "2024-01-15T10:30:00Z"
            }
        }

class RiskPredictionRequest(BaseModel):
    """Risk prediction request"""
    vendor_id: str = Field(..., description="Vendor identifier")
    compliance_data: Dict[str, Any] = Field(..., description="Compliance assessment data")
    historical_data: Optional[Dict[str, Any]] = Field(None, description="Historical compliance data")
    risk_factors: List[str] = Field(..., description="Risk factors to consider")
    
    class Config:
        schema_extra = {
            "example": {
                "vendor_id": "vendor_123",
                "compliance_data": {
                    "cybersecurity_score": 85,
                    "data_protection_score": 90,
                    "regulatory_score": 75
                },
                "risk_factors": ["cybersecurity", "data_protection", "regulatory"]
            }
        }

class RiskPrediction(BaseModel):
    """Risk prediction result"""
    vendor_id: str = Field(..., description="Vendor identifier")
    overall_risk_score: float = Field(..., description="Overall risk score (0-100)")
    risk_level: str = Field(..., description="Risk level (low, medium, high, critical)")
    risk_factors: Dict[str, float] = Field(..., description="Risk scores by factor")
    recommendations: List[str] = Field(..., description="Risk mitigation recommendations")
    confidence_score: float = Field(..., description="Prediction confidence (0-1)")
    timestamp: datetime = Field(..., description="When the prediction was made")
    
    class Config:
        schema_extra = {
            "example": {
                "vendor_id": "vendor_123",
                "overall_risk_score": 65.5,
                "risk_level": "medium",
                "risk_factors": {
                    "cybersecurity": 70.0,
                    "data_protection": 45.0,
                    "regulatory": 80.0
                },
                "recommendations": [
                    "Improve data protection measures",
                    "Enhance regulatory compliance"
                ],
                "confidence_score": 0.82,
                "timestamp": "2024-01-15T10:30:00Z"
            }
        }

class DocumentAnalysisRequest(BaseModel):
    """Document analysis request"""
    document_type: str = Field(..., description="Type of document to analyze")
    content: str = Field(..., description="Document content for analysis")
    analysis_type: List[str] = Field(..., description="Types of analysis to perform")
    language: str = Field("en", description="Document language")
    
    class Config:
        schema_extra = {
            "example": {
                "document_type": "policy_document",
                "content": "This policy outlines the cybersecurity requirements...",
                "analysis_type": ["compliance_check", "risk_assessment", "keyword_extraction"],
                "language": "en"
            }
        }

class DocumentAnalysis(BaseModel):
    """Document analysis result"""
    document_type: str = Field(..., description="Type of document analyzed")
    analysis_results: Dict[str, Any] = Field(..., description="Analysis results by type")
    compliance_score: Optional[float] = Field(None, description="Overall compliance score")
    risk_indicators: List[str] = Field(..., description="Identified risk indicators")
    keywords: List[str] = Field(..., description="Extracted keywords")
    sentiment_score: Optional[float] = Field(None, description="Document sentiment score")
    timestamp: datetime = Field(..., description="When the analysis was performed")
    
    class Config:
        schema_extra = {
            "example": {
                "document_type": "policy_document",
                "analysis_results": {
                    "compliance_check": {"score": 85, "issues": ["missing_encryption"]},
                    "risk_assessment": {"risk_level": "medium", "factors": ["data_exposure"]},
                    "keyword_extraction": ["cybersecurity", "encryption", "compliance"]
                },
                "compliance_score": 85.0,
                "risk_indicators": ["data_exposure", "missing_encryption"],
                "keywords": ["cybersecurity", "encryption", "compliance"],
                "sentiment_score": 0.7,
                "timestamp": "2024-01-15T10:30:00Z"
            }
        }

# =============================================================================
# AI-ML ENGINE CORE
# =============================================================================

class AIMLEngine:
    """Core AI-ML engine for compliance and risk analysis"""
    
    def __init__(self):
        self.redis_client = get_redis_client()
        self.models = {}
        self.vectorizer = None
        self.compliance_knowledge_base = {}
        self._load_models()
        self._load_knowledge_base()
        self._initialize_vectorizer()
    
    def _load_models(self):
        """Load pre-trained models"""
        try:
            model_dir = Path(MODEL_PATH)
            if model_dir.exists():
                # Load risk prediction model
                risk_model_path = model_dir / "risk_prediction_model.pkl"
                if risk_model_path.exists():
                    self.models['risk_prediction'] = joblib.load(risk_model_path)
                    logger.info("Risk prediction model loaded successfully")
                
                # Load anomaly detection model
                anomaly_model_path = model_dir / "anomaly_detection_model.pkl"
                if anomaly_model_path.exists():
                    self.models['anomaly_detection'] = joblib.load(anomaly_model_path)
                    logger.info("Anomaly detection model loaded successfully")
                
                # Load text classification model
                text_model_path = model_dir / "text_classification_model.pkl"
                if text_model_path.exists():
                    self.models['text_classification'] = joblib.load(text_model_path)
                    logger.info("Text classification model loaded successfully")
            
            logger.info(f"Loaded {len(self.models)} models")
            
        except Exception as e:
            logger.error("Failed to load models", error=str(e))
    
    def _load_knowledge_base(self):
        """Load compliance knowledge base"""
        try:
            # Load from policies directory
            policies_dir = Path(__file__).parent.parent.parent / "policies"
            if policies_dir.exists():
                for policy_file in policies_dir.glob("*.yaml"):
                    try:
                        with open(policy_file, 'r', encoding='utf-8') as f:
                            policy_data = yaml.safe_load(f)
                            if 'id' in policy_data:
                                self.compliance_knowledge_base[policy_data['id']] = policy_data
                    except Exception as e:
                        logger.warning(f"Failed to load policy {policy_file}", error=str(e))
            
            # Load from benchmarks directory
            benchmarks_dir = Path(__file__).parent.parent.parent / "benchmarks"
            if benchmarks_dir.exists():
                for benchmark_file in benchmarks_dir.glob("*.json"):
                    try:
                        with open(benchmark_file, 'r', encoding='utf-8') as f:
                            benchmark_data = json.load(f)
                            if 'id' in benchmark_data:
                                self.compliance_knowledge_base[benchmark_data['id']] = benchmark_data
                    except Exception as e:
                        logger.warning(f"Failed to load benchmark {benchmark_file}", error=str(e))
            
            logger.info(f"Loaded {len(self.compliance_knowledge_base)} knowledge base items")
            
        except Exception as e:
            logger.error("Failed to load knowledge base", error=str(e))
    
    def _initialize_vectorizer(self):
        """Initialize text vectorizer for similarity search"""
        try:
            # Create TF-IDF vectorizer from knowledge base
            documents = []
            for item in self.compliance_knowledge_base.values():
                if 'description' in item:
                    documents.append(item['description'])
                if 'requirements' in item:
                    for req in item['requirements']:
                        if isinstance(req, dict) and 'description' in req:
                            documents.append(req['description'])
                        elif isinstance(req, str):
                            documents.append(req)
            
            if documents:
                self.vectorizer = TfidfVectorizer(
                    max_features=1000,
                    stop_words='english',
                    ngram_range=(1, 2)
                )
                self.vectorizer.fit(documents)
                logger.info("Text vectorizer initialized successfully")
            
        except Exception as e:
            logger.error("Failed to initialize vectorizer", error=str(e))
    
    def answer_compliance_question(self, question: ComplianceQuestion) -> ComplianceAnswer:
        """Answer compliance questions using knowledge base and similarity search"""
        try:
            # Vectorize the question
            if self.vectorizer:
                question_vector = self.vectorizer.transform([question.question])
                
                # Find similar documents
                best_matches = []
                for item_id, item in self.compliance_knowledge_base.items():
                    if 'description' in item:
                        item_vector = self.vectorizer.transform([item['description']])
                        similarity = cosine_similarity(question_vector, item_vector)[0][0]
                        if similarity > 0.1:  # Threshold for relevance
                            best_matches.append((item_id, item, similarity))
                
                # Sort by similarity
                best_matches.sort(key=lambda x: x[2], reverse=True)
                
                if best_matches:
                    # Generate answer from best matches
                    best_match = best_matches[0]
                    answer = self._generate_answer_from_knowledge(question, best_match[1])
                    confidence_score = min(best_match[2] * 1.2, 1.0)  # Boost confidence slightly
                    
                    sources = [best_match[0]]
                    policy_references = [best_match[0]]
                    
                    return ComplianceAnswer(
                        question=question.question,
                        answer=answer,
                        confidence_score=confidence_score,
                        sources=sources,
                        policy_references=policy_references,
                        timestamp=datetime.now(timezone.utc)
                    )
            
            # Fallback answer
            return ComplianceAnswer(
                question=question.question,
                answer="I don't have enough information to provide a specific answer. Please consult the relevant policy documents or contact compliance experts.",
                confidence_score=0.1,
                sources=[],
                policy_references=[],
                timestamp=datetime.now(timezone.utc)
            )
            
        except Exception as e:
            logger.error("Failed to answer compliance question", error=str(e))
            raise
    
    def _generate_answer_from_knowledge(self, question: ComplianceQuestion, knowledge_item: Dict[str, Any]) -> str:
        """Generate answer from knowledge base item"""
        answer_parts = []
        
        if 'description' in knowledge_item:
            answer_parts.append(f"Based on {knowledge_item.get('name', 'the policy')}: {knowledge_item['description']}")
        
        if 'requirements' in knowledge_item:
            answer_parts.append("Key requirements include:")
            for req in knowledge_item['requirements'][:3]:  # Limit to first 3 requirements
                if isinstance(req, dict) and 'description' in req:
                    answer_parts.append(f"- {req['description']}")
                elif isinstance(req, str):
                    answer_parts.append(f"- {req}")
        
        if 'risk_level' in knowledge_item:
            answer_parts.append(f"Risk level: {knowledge_item['risk_level']}")
        
        return " ".join(answer_parts)
    
    def predict_risk(self, request: RiskPredictionRequest) -> RiskPrediction:
        """Predict vendor risk based on compliance data"""
        try:
            # Extract features from compliance data
            features = self._extract_risk_features(request.compliance_data)
            
            # Use risk prediction model if available
            if 'risk_prediction' in self.models:
                risk_score = self.models['risk_prediction'].predict([features])[0]
            else:
                # Simple rule-based risk scoring
                risk_score = self._calculate_rule_based_risk(request.compliance_data)
            
            # Calculate risk level
            risk_level = self._determine_risk_level(risk_score)
            
            # Calculate individual factor risks
            risk_factors = self._calculate_factor_risks(request.compliance_data, request.risk_factors)
            
            # Generate recommendations
            recommendations = self._generate_risk_recommendations(risk_factors, risk_level)
            
            # Calculate confidence score
            confidence_score = self._calculate_prediction_confidence(request.compliance_data)
            
            return RiskPrediction(
                vendor_id=request.vendor_id,
                overall_risk_score=risk_score,
                risk_level=risk_level,
                risk_factors=risk_factors,
                recommendations=recommendations,
                confidence_score=confidence_score,
                timestamp=datetime.now(timezone.utc)
            )
            
        except Exception as e:
            logger.error("Failed to predict risk", error=str(e))
            raise
    
    def _extract_risk_features(self, compliance_data: Dict[str, Any]) -> List[float]:
        """Extract numerical features for risk prediction"""
        features = []
        
        # Extract scores
        for key, value in compliance_data.items():
            if isinstance(value, (int, float)):
                features.append(float(value))
            elif isinstance(value, str) and value.isdigit():
                features.append(float(value))
            else:
                features.append(0.0)  # Default value for non-numeric
        
        # Pad or truncate to expected length
        expected_length = 10
        if len(features) < expected_length:
            features.extend([0.0] * (expected_length - len(features)))
        else:
            features = features[:expected_length]
        
        return features
    
    def _calculate_rule_based_risk(self, compliance_data: Dict[str, Any]) -> float:
        """Calculate risk using rule-based approach"""
        total_score = 0
        count = 0
        
        for key, value in compliance_data.items():
            if isinstance(value, (int, float)):
                # Convert score to risk (higher score = lower risk)
                risk_score = max(0, 100 - value)
                total_score += risk_score
                count += 1
        
        return total_score / count if count > 0 else 50.0
    
    def _determine_risk_level(self, risk_score: float) -> str:
        """Determine risk level from score"""
        if risk_score < 25:
            return "low"
        elif risk_score < 50:
            return "medium"
        elif risk_score < 75:
            return "high"
        else:
            return "critical"
    
    def _calculate_factor_risks(self, compliance_data: Dict[str, Any], risk_factors: List[str]) -> Dict[str, float]:
        """Calculate risk scores for individual factors"""
        factor_risks = {}
        
        for factor in risk_factors:
            if factor in compliance_data:
                value = compliance_data[factor]
                if isinstance(value, (int, float)):
                    factor_risks[factor] = max(0, 100 - value)
                else:
                    factor_risks[factor] = 50.0  # Default risk
            else:
                factor_risks[factor] = 75.0  # High risk for missing factors
        
        return factor_risks
    
    def _generate_risk_recommendations(self, risk_factors: Dict[str, float], risk_level: str) -> List[str]:
        """Generate risk mitigation recommendations"""
        recommendations = []
        
        # High-risk factor recommendations
        high_risk_factors = [factor for factor, score in risk_factors.items() if score > 70]
        for factor in high_risk_factors:
            recommendations.append(f"Immediately address {factor} vulnerabilities")
        
        # General recommendations based on risk level
        if risk_level == "critical":
            recommendations.append("Conduct comprehensive security audit and risk assessment")
            recommendations.append("Implement emergency security measures")
        elif risk_level == "high":
            recommendations.append("Prioritize high-risk factor remediation")
            recommendations.append("Increase monitoring and oversight")
        elif risk_level == "medium":
            recommendations.append("Develop risk mitigation plan")
            recommendations.append("Enhance compliance monitoring")
        else:
            recommendations.append("Maintain current security posture")
            recommendations.append("Regular compliance reviews")
        
        return recommendations
    
    def _calculate_prediction_confidence(self, compliance_data: Dict[str, Any]) -> float:
        """Calculate confidence in the prediction"""
        # More data = higher confidence
        data_completeness = len(compliance_data) / 10.0  # Normalize to 0-1
        confidence = min(data_completeness, 1.0)
        
        # Boost confidence if we have models
        if self.models:
            confidence = min(confidence + 0.2, 1.0)
        
        return round(confidence, 2)
    
    def analyze_document(self, request: DocumentAnalysisRequest) -> DocumentAnalysis:
        """Analyze document for compliance and risk"""
        try:
            analysis_results = {}
            
            # Compliance check
            if "compliance_check" in request.analysis_type:
                compliance_score = self._check_document_compliance(request.content)
                analysis_results["compliance_check"] = {
                    "score": compliance_score,
                    "issues": self._identify_compliance_issues(request.content)
                }
            
            # Risk assessment
            if "risk_assessment" in request.analysis_type:
                risk_level = self._assess_document_risk(request.content)
                analysis_results["risk_assessment"] = {
                    "risk_level": risk_level,
                    "factors": self._identify_risk_factors(request.content)
                }
            
            # Keyword extraction
            if "keyword_extraction" in request.analysis_type:
                keywords = self._extract_keywords(request.content)
                analysis_results["keyword_extraction"] = keywords
            
            # Sentiment analysis
            if "sentiment_analysis" in request.analysis_type:
                sentiment_score = self._analyze_sentiment(request.content)
                analysis_results["sentiment_analysis"] = {"score": sentiment_score}
            
            # Calculate overall compliance score
            compliance_score = None
            if "compliance_check" in analysis_results:
                compliance_score = analysis_results["compliance_check"]["score"]
            
            # Extract risk indicators
            risk_indicators = []
            if "risk_assessment" in analysis_results:
                risk_indicators = analysis_results["risk_assessment"]["factors"]
            
            # Extract keywords
            keywords = []
            if "keyword_extraction" in analysis_results:
                keywords = analysis_results["keyword_extraction"]
            
            # Calculate sentiment score
            sentiment_score = None
            if "sentiment_analysis" in analysis_results:
                sentiment_score = analysis_results["sentiment_analysis"]["score"]
            
            return DocumentAnalysis(
                document_type=request.document_type,
                analysis_results=analysis_results,
                compliance_score=compliance_score,
                risk_indicators=risk_indicators,
                keywords=keywords,
                sentiment_score=sentiment_score,
                timestamp=datetime.now(timezone.utc)
            )
            
        except Exception as e:
            logger.error("Failed to analyze document", error=str(e))
            raise
    
    def _check_document_compliance(self, content: str) -> float:
        """Check document compliance score"""
        # Simple keyword-based compliance scoring
        compliance_keywords = [
            "encryption", "authentication", "authorization", "audit", "monitoring",
            "security", "compliance", "policy", "procedure", "standard"
        ]
        
        content_lower = content.lower()
        found_keywords = sum(1 for keyword in compliance_keywords if keyword in content_lower)
        
        # Score based on keyword coverage
        return min(100, (found_keywords / len(compliance_keywords)) * 100)
    
    def _identify_compliance_issues(self, content: str) -> List[str]:
        """Identify compliance issues in document"""
        issues = []
        
        # Check for common compliance issues
        if "password" in content.lower() and "encryption" not in content.lower():
            issues.append("password_storage_without_encryption")
        
        if "personal data" in content.lower() and "consent" not in content.lower():
            issues.append("personal_data_without_consent")
        
        if "financial" in content.lower() and "audit" not in content.lower():
            issues.append("financial_data_without_audit")
        
        return issues
    
    def _assess_document_risk(self, content: str) -> str:
        """Assess document risk level"""
        risk_score = 0
        
        # Risk indicators
        high_risk_terms = ["confidential", "secret", "restricted", "internal"]
        medium_risk_terms = ["sensitive", "private", "personal", "financial"]
        
        content_lower = content.lower()
        
        for term in high_risk_terms:
            if term in content_lower:
                risk_score += 3
        
        for term in medium_risk_terms:
            if term in content_lower:
                risk_score += 2
        
        if risk_score >= 6:
            return "high"
        elif risk_score >= 3:
            return "medium"
        else:
            return "low"
    
    def _identify_risk_factors(self, content: str) -> List[str]:
        """Identify risk factors in document"""
        risk_factors = []
        
        # Check for risk indicators
        if "confidential" in content.lower():
            risk_factors.append("confidential_information")
        
        if "personal" in content.lower():
            risk_factors.append("personal_data")
        
        if "financial" in content.lower():
            risk_factors.append("financial_data")
        
        if "password" in content.lower():
            risk_factors.append("credential_exposure")
        
        return risk_factors
    
    def _extract_keywords(self, content: str) -> List[str]:
        """Extract keywords from document"""
        # Simple keyword extraction
        words = content.lower().split()
        
        # Filter out common words
        stop_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by"}
        keywords = [word for word in words if word not in stop_words and len(word) > 3]
        
        # Count frequency and return top keywords
        from collections import Counter
        keyword_counts = Counter(keywords)
        return [keyword for keyword, count in keyword_counts.most_common(10)]
    
    def _analyze_sentiment(self, content: str) -> float:
        """Analyze document sentiment"""
        # Simple sentiment analysis
        positive_words = ["good", "excellent", "secure", "safe", "compliant", "approved"]
        negative_words = ["bad", "poor", "insecure", "unsafe", "non-compliant", "rejected"]
        
        content_lower = content.lower()
        
        positive_count = sum(1 for word in positive_words if word in content_lower)
        negative_count = sum(1 for word in negative_words if word in content_lower)
        
        if positive_count == 0 and negative_count == 0:
            return 0.5  # Neutral
        
        return positive_count / (positive_count + negative_count)

# =============================================================================
# FASTAPI APPLICATION
# =============================================================================

app = FastAPI(
    title="DoganAI ML Service",
    description="Local LLM inference, compliance Q&A, risk prediction, and natural language processing",
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
    allow_origins=["*"] if DEBUG else ["https://your-domain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize AI-ML engine
ai_ml_engine = AIMLEngine()

# =============================================================================
# MIDDLEWARE FOR METRICS
# =============================================================================

@app.middleware("http")
async def add_metrics(request: Request, call_next):
    start_time = time.time()
    
    response = await call_next(request)
    
    # Record metrics
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code
    ).inc()
    
    REQUEST_LATENCY.labels(
        method=request.method,
        endpoint=request.url.path
    ).observe(time.time() - start_time)
    
    return response

# =============================================================================
# API ENDPOINTS
# =============================================================================

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": APP_NAME,
        "version": APP_VERSION,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "models_loaded": len(ai_ml_engine.models),
        "knowledge_base_size": len(ai_ml_engine.compliance_knowledge_base)
    }

@app.get("/config")
async def config():
    """Return current configuration"""
    return {
        "version": APP_VERSION,
        "environment": ENVIRONMENT,
        "debug": DEBUG,
        "models_available": list(ai_ml_engine.models.keys()),
        "local_llm_enabled": ENABLE_LOCAL_LLM,
        "vectorizer_initialized": ai_ml_engine.vectorizer is not None
    }

@app.post("/qa/compliance", response_model=ComplianceAnswer)
async def answer_compliance_question(
    question: ComplianceQuestion,
    current_user: str = Depends(get_current_user)
):
    """Answer compliance questions using AI"""
    try:
        answer = ai_ml_engine.answer_compliance_question(question)
        
        # Record metrics
        PREDICTION_COUNT.labels(
            model_type="qa",
            prediction_type="compliance_answer"
        ).inc()
        
        return answer
        
    except Exception as e:
        logger.error("Failed to answer compliance question", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to generate answer")

@app.post("/predict/risk", response_model=RiskPrediction)
async def predict_risk(
    request: RiskPredictionRequest,
    current_user: str = Depends(get_current_user)
):
    """Predict vendor risk based on compliance data"""
    try:
        prediction = ai_ml_engine.predict_risk(request)
        
        # Record metrics
        PREDICTION_COUNT.labels(
            model_type="risk_prediction",
            prediction_type="vendor_risk"
        ).inc()
        
        return prediction
        
    except Exception as e:
        logger.error("Failed to predict risk", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to generate risk prediction")

@app.post("/analyze/document", response_model=DocumentAnalysis)
async def analyze_document(
    request: DocumentAnalysisRequest,
    current_user: str = Depends(get_current_user)
):
    """Analyze document for compliance and risk"""
    try:
        analysis = ai_ml_engine.analyze_document(request)
        
        # Record metrics
        PREDICTION_COUNT.labels(
            model_type="document_analysis",
            prediction_type="compliance_risk"
        ).inc()
        
        return analysis
        
    except Exception as e:
        logger.error("Failed to analyze document", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to analyze document")

@app.get("/models/status")
async def get_models_status():
    """Get status of loaded models"""
    model_status = {}
    
    for model_name, model in ai_ml_engine.models.items():
        model_status[model_name] = {
            "loaded": True,
            "type": type(model).__name__,
            "parameters": getattr(model, 'n_estimators', 'N/A') if hasattr(model, 'n_estimators') else 'N/A'
        }
    
    return {
        "models": model_status,
        "vectorizer": ai_ml_engine.vectorizer is not None,
        "knowledge_base_size": len(ai_ml_engine.compliance_knowledge_base)
    }

@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )

# =============================================================================
# ENHANCED HARDWARE MONITORING ENDPOINTS
# =============================================================================

@app.get("/hardware/comprehensive")
async def get_comprehensive_hardware_metrics():
    """Get comprehensive hardware metrics with detailed analysis"""
    try:
        metrics = get_hardware_metrics()
        performance = get_performance_metrics()
        
        return {
            "hardware_metrics": metrics,
            "performance_analysis": performance,
            "timestamp": datetime.now().isoformat(),
            "status": "success"
        }
    except Exception as e:
        logger.error("Failed to get comprehensive hardware metrics", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/hardware/realtime")
async def get_realtime_hardware_metrics():
    """Get real-time hardware metrics for live monitoring"""
    try:
        metrics = get_hardware_metrics()
        
        # Add real-time alerts
        alerts = []
        if metrics["cpu"]["usage_percent"] > 90:
            alerts.append({"level": "critical", "message": "CPU usage critical (>90%)"})
        elif metrics["cpu"]["usage_percent"] > 80:
            alerts.append({"level": "warning", "message": "CPU usage high (>80%)"})
            
        if metrics["memory"]["usage_percent"] > 95:
            alerts.append({"level": "critical", "message": "Memory usage critical (>95%)"})
        elif metrics["memory"]["usage_percent"] > 85:
            alerts.append({"level": "warning", "message": "Memory usage high (>85%)"})
            
        if metrics["disk"]["usage_percent"] > 95:
            alerts.append({"level": "critical", "message": "Disk usage critical (>95%)"})
        elif metrics["disk"]["usage_percent"] > 90:
            alerts.append({"level": "warning", "message": "Disk usage high (>90%)"})
        
        return {
            "metrics": metrics,
            "alerts": alerts,
            "timestamp": datetime.now().isoformat(),
            "status": "success"
        }
    except Exception as e:
        logger.error("Failed to get real-time hardware metrics", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/hardware/trends")
async def get_hardware_trends():
    """Get hardware usage trends over time"""
    try:
        # This would typically come from a time-series database
        # For now, we'll simulate trend data
        current_metrics = get_hardware_metrics()
        
        trends = {
            "cpu_trend": "stable",  # stable, increasing, decreasing
            "memory_trend": "stable",
            "disk_trend": "stable",
            "gpu_trend": "stable" if current_metrics["gpu"]["usage_percent"] else "n/a",
            "recommendations": get_performance_recommendations(current_metrics)
        }
        
        return {
            "current_metrics": current_metrics,
            "trends": trends,
            "timestamp": datetime.now().isoformat(),
            "status": "success"
        }
    except Exception as e:
        logger.error("Failed to get hardware trends", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

# =============================================================================
# LOAD TESTING ENDPOINTS
# =============================================================================

@app.post("/load-test/comprehensive")
async def run_comprehensive_load_test(test_config: Dict[str, Any]):
    """Run comprehensive load test for AI scenarios"""
    try:
        logger.info("Starting comprehensive load test", config=test_config)
        
        # Run the load test
        test_result = await load_test_engine.run_comprehensive_load_test(test_config)
        
        return {
            "status": "success",
            "test_result": test_result,
            "message": "Load test completed successfully"
        }
    except Exception as e:
        logger.error("Load test failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"Load test failed: {str(e)}")

@app.post("/load-test/quick")
async def run_quick_load_test():
    """Run a quick load test with default parameters"""
    try:
        default_config = {
            "text_volume": 100,
            "image_count": 50,
            "inference_requests": 100,
            "data_size": 1000,
            "concurrent_users": 10
        }
        
        test_result = await load_test_engine.run_comprehensive_load_test(default_config)
        
        return {
            "status": "success",
            "test_result": test_result,
            "message": "Quick load test completed successfully"
        }
    except Exception as e:
        logger.error("Quick load test failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"Quick load test failed: {str(e)}")

@app.get("/load-test/status")
async def get_load_test_status():
    """Get status of current and completed load tests"""
    try:
        return {
            "current_tests": len(load_test_engine.current_tests),
            "completed_tests": len(load_test_engine.test_results),
            "recent_tests": list(load_test_engine.test_results.keys())[-5:],  # Last 5 test IDs
            "status": "success"
        }
    except Exception as e:
        logger.error("Failed to get load test status", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/load-test/results/{test_id}")
async def get_load_test_results(test_id: str):
    """Get results of a specific load test"""
    try:
        if test_id not in load_test_engine.test_results:
            raise HTTPException(status_code=404, detail="Test not found")
        
        return {
            "status": "success",
            "test_result": load_test_engine.test_results[test_id]
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get load test results", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/load-test/ai-scenario")
async def test_ai_scenario(scenario_config: Dict[str, Any]):
    """Test specific AI scenario workload"""
    try:
        scenario_type = scenario_config.get("type", "general")
        
        if scenario_type == "text_processing":
            result = await load_test_engine._test_text_processing(
                scenario_config.get("text_volume", 1000)
            )
        elif scenario_type == "image_processing":
            result = await load_test_engine._test_image_processing(
                scenario_config.get("image_count", 100)
            )
        elif scenario_type == "model_inference":
            result = await load_test_engine._test_model_inference(
                scenario_config.get("inference_requests", 500)
            )
        elif scenario_type == "data_analysis":
            result = await load_test_engine._test_data_analysis(
                scenario_config.get("data_size", 10000)
            )
        elif scenario_type == "concurrent_operations":
            result = await load_test_engine._test_concurrent_operations(
                scenario_config.get("concurrent_users", 50)
            )
        else:
            raise HTTPException(status_code=400, detail="Invalid scenario type")
        
        return {
            "status": "success",
            "scenario_type": scenario_type,
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error("AI scenario test failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"AI scenario test failed: {str(e)}")

@app.get("/hardware/capacity-assessment")
async def get_hardware_capacity_assessment():
    """Get comprehensive hardware capacity assessment"""
    try:
        # Get current hardware state
        current_metrics = get_hardware_metrics()
        
        # Run a quick capacity test
        capacity_test_config = {
            "text_volume": 50,
            "image_count": 25,
            "inference_requests": 50,
            "data_size": 500,
            "concurrent_users": 5
        }
        
        capacity_test = await load_test_engine.run_comprehensive_load_test(capacity_test_config)
        
        # Extract capacity assessment
        capacity_assessment = capacity_test.get("hardware_capacity_assessment", {})
        
        return {
            "status": "success",
            "current_metrics": current_metrics,
            "capacity_assessment": capacity_assessment,
            "recommendations": capacity_assessment.get("recommended_actions", []),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error("Failed to get capacity assessment", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

# =============================================================================
# STARTUP AND SHUTDOWN
# =============================================================================

@app.on_event("startup")
async def startup_event():
    """Application startup event"""
    logger.info(
        "Starting AI-ML Microservice",
        version=APP_VERSION,
        environment=ENVIRONMENT,
        debug=DEBUG
    )

@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event"""
    logger.info("Shutting down AI-ML Microservice")

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

# Import Response for metrics endpoint
from fastapi.responses import Response

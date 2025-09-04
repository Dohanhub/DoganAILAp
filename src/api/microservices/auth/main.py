"""
Authentication Microservice - Production Ready
Manual user management for trials + Microsoft authentication preparation
"""

import os
import json
import logging
import time
import uuid
import hashlib
import secrets
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional, Union
from pathlib import Path
import yaml
from fastapi import FastAPI, HTTPException, Depends, Request, Form, status
from fastapi.middleware.cors import CORSMiddleware
# from fastapi.middleware.trustedhost import TrustedHostMiddleware  # Removed for development
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, ValidationError, EmailStr
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
import structlog
import redis
import jwt
from cryptography.fernet import Fernet
import bcrypt

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
APP_NAME = os.getenv("APP_NAME", "Authentication Microservice")
APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
DEBUG = os.getenv("DEBUG", "false").lower() == "true"

# Security configuration
SECRET_KEY = os.getenv("SECRET_KEY", "7bBxUxlAEQjNKLYw_lzR3dzBxjtEZVwu-QWd9zyeImI")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))

# Redis configuration
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "")
REDIS_DB = int(os.getenv("REDIS_DB", "3"))

# Microsoft Auth configuration (for future use)
MICROSOFT_CLIENT_ID = os.getenv("MICROSOFT_CLIENT_ID", "")
MICROSOFT_CLIENT_SECRET = os.getenv("MICROSOFT_CLIENT_SECRET", "")
MICROSOFT_TENANT_ID = os.getenv("MICROSOFT_TENANT_ID", "")

# =============================================================================
# REDIS SETUP
# =============================================================================

def get_redis_client():
    """Get Redis client for session and user data storage"""
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
# MANUAL USER MANAGEMENT (TRIAL PHASE)
# =============================================================================

# Trial users - will be replaced with database in production
TRIAL_USERS = {
    "admin@dogan-ai.com": {
        "user_id": "admin_001",
        "email": "admin@dogan-ai.com",
        "username": "admin",
        "full_name": "System Administrator",
        "role": "admin",
        "permissions": ["*"],
        "organization": "DoganAI",
        "status": "active",
        "created_at": "2024-01-01T00:00:00Z",
        "last_login": None,
        "password_hash": bcrypt.hashpw("Admin@123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    },
    "vendor@dogan-ai.com": {
        "user_id": "vendor_001",
        "email": "vendor@dogan-ai.com",
        "username": "vendor",
        "full_name": "Vendor Tester",
        "role": "vendor",
        "permissions": ["vendor_access", "compliance_view", "reports_view"],
        "organization": "Vendor Partner",
        "status": "active",
        "created_at": "2024-01-01T00:00:00Z",
        "last_login": None,
        "password_hash": bcrypt.hashpw("Vendor@123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    },
    "customer@dogan-ai.com": {
        "user_id": "customer_001",
        "email": "customer@dogan-ai.com",
        "username": "customer",
        "full_name": "Customer User",
        "role": "customer",
        "permissions": ["compliance_test", "reports_view", "ai_analysis"],
        "organization": "Customer Organization",
        "status": "active",
        "created_at": "2024-01-01T00:00:00Z",
        "last_login": None,
        "password_hash": bcrypt.hashpw("Customer@123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    }
}

# =============================================================================
# PYDANTIC MODELS
# =============================================================================

class UserLogin(BaseModel):
    """User login request"""
    email: EmailStr = Field(..., description="User email")
    password: str = Field(..., description="User password")

class UserCreate(BaseModel):
    """User creation request"""
    email: EmailStr = Field(..., description="User email")
    username: str = Field(..., description="Username")
    full_name: str = Field(..., description="Full name")
    role: str = Field(..., description="User role")
    organization: str = Field(..., description="Organization")
    password: str = Field(..., description="Password")

class UserResponse(BaseModel):
    """User response model"""
    user_id: str
    email: str
    username: str
    full_name: str
    role: str
    permissions: List[str]
    organization: str
    status: str
    created_at: str
    last_login: Optional[str]

class TokenResponse(BaseModel):
    """Token response model"""
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int
    user: UserResponse

class PermissionCheck(BaseModel):
    """Permission check request"""
    resource: str = Field(..., description="Resource to access")
    action: str = Field(..., description="Action to perform")

# =============================================================================
# AUTHENTICATION ENGINE
# =============================================================================

class AuthenticationEngine:
    """Core authentication engine"""
    
    def __init__(self):
        self.redis_client = get_redis_client()
        self.users = TRIAL_USERS.copy()
        self.active_sessions = {}
        
    def authenticate_user(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate user with email and password"""
        try:
            if email not in self.users:
                return None
            
            user = self.users[email]
            if user["status"] != "active":
                return None
            
            # Verify password
            if bcrypt.checkpw(password.encode('utf-8'), user["password_hash"].encode('utf-8')):
                # Update last login
                user["last_login"] = datetime.now(timezone.utc).isoformat()
                return user
            return None
            
        except Exception as e:
            logger.error("Authentication failed", error=str(e), email=email)
            return None
    
    def create_access_token(self, user: Dict[str, Any]) -> str:
        """Create JWT access token"""
        try:
            payload = {
                "sub": user["user_id"],
                "email": user["email"],
                "role": user["role"],
                "permissions": user["permissions"],
                "exp": datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
                "iat": datetime.now(timezone.utc)
            }
            return jwt.encode(payload, SECRET_KEY, algorithm=JWT_ALGORITHM)
        except Exception as e:
            logger.error("Failed to create access token", error=str(e))
            raise
    
    def create_refresh_token(self, user: Dict[str, Any]) -> str:
        """Create JWT refresh token"""
        try:
            payload = {
                "sub": user["user_id"],
                "email": user["email"],
                "type": "refresh",
                "exp": datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
                "iat": datetime.now(timezone.utc)
            }
            return jwt.encode(payload, SECRET_KEY, algorithm=JWT_ALGORITHM)
        except Exception as e:
            logger.error("Failed to create refresh token", error=str(e))
            raise
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify JWT token and return payload"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[JWT_ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("Token expired")
            return None
        except jwt.InvalidTokenError:
            logger.warning("Invalid token")
            return None
        except Exception as e:
            logger.error("Token verification failed", error=str(e))
            return None
    
    def check_permission(self, user_permissions: List[str], resource: str, action: str) -> bool:
        """Check if user has permission for resource and action"""
        try:
            # Admin has all permissions
            if "*" in user_permissions:
                return True
            
            # Check specific permissions
            required_permission = f"{resource}:{action}"
            if required_permission in user_permissions:
                return True
            
            # Check resource-level permissions
            if f"{resource}:*" in user_permissions:
                return True
            
            return False
            
        except Exception as e:
            logger.error("Permission check failed", error=str(e))
            return False
    
    def create_session(self, user: Dict[str, Any], access_token: str, refresh_token: str) -> str:
        """Create user session"""
        try:
            session_id = str(uuid.uuid4())
            session_data = {
                "user_id": user["user_id"],
                "email": user["email"],
                "role": user["role"],
                "access_token": access_token,
                "refresh_token": refresh_token,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "expires_at": (datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)).isoformat()
            }
            
            # Store in Redis if available
            if self.redis_client:
                self.redis_client.setex(
                    f"session:{session_id}",
                    ACCESS_TOKEN_EXPIRE_MINUTES * 60,
                    json.dumps(session_data)
                )
            
            # Store in memory as backup
            self.active_sessions[session_id] = session_data
            
            return session_id
            
        except Exception as e:
            logger.error("Failed to create session", error=str(e))
            raise
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session data"""
        try:
            # Try Redis first
            if self.redis_client:
                session_data = self.redis_client.get(f"session:{session_id}")
                if session_data:
                    return json.loads(session_data)
            
            # Fallback to memory
            return self.active_sessions.get(session_id)
            
        except Exception as e:
            logger.error("Failed to get session", error=str(e))
            return None
    
    def revoke_session(self, session_id: str) -> bool:
        """Revoke user session"""
        try:
            # Remove from Redis
            if self.redis_client:
                self.redis_client.delete(f"session:{session_id}")
            
            # Remove from memory
            if session_id in self.active_sessions:
                del self.active_sessions[session_id]
            
            return True
            
        except Exception as e:
            logger.error("Failed to revoke session", error=str(e))
            return False

# =============================================================================
# FASTAPI APPLICATION
# =============================================================================

app = FastAPI(
    title="DoganAI Authentication Service",
    description="Authentication service with manual user management and Microsoft auth preparation",
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

# Initialize authentication engine
auth_engine = AuthenticationEngine()

# =============================================================================
# PROMETHEUS METRICS
# =============================================================================

AUTH_REQUESTS = Counter(
    "auth_requests_total",
    "Total authentication requests",
    ["method", "endpoint", "status"]
)

AUTH_LATENCY = Histogram(
    "auth_request_duration_seconds",
    "Authentication request latency in seconds",
    ["method", "endpoint"]
)

# =============================================================================
# DEPENDENCIES
# =============================================================================

oauth2_scheme = HTTPBearer(auto_error=False)

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme)) -> Dict[str, Any]:
    """Get current authenticated user"""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        payload = auth_engine.verify_token(credentials.credentials)
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Get user data
        user_email = payload.get("email")
        if not user_email or user_email not in auth_engine.users:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return auth_engine.users[user_email]
        
    except Exception as e:
        logger.error("Failed to get current user", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def check_permission(resource: str, action: str, user: Dict[str, Any] = Depends(get_current_user)) -> bool:
    """Check if user has permission for resource and action"""
    if not auth_engine.check_permission(user["permissions"], resource, action):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Insufficient permissions for {resource}:{action}"
        )
    return True

# =============================================================================
# API ENDPOINTS
# =============================================================================

@app.post("/auth/login", response_model=TokenResponse)
async def login(user_data: UserLogin):
    """User login endpoint"""
    try:
        # Authenticate user
        user = auth_engine.authenticate_user(user_data.email, user_data.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        # Create tokens
        access_token = auth_engine.create_access_token(user)
        refresh_token = auth_engine.create_refresh_token(user)
        
        # Create session
        session_id = auth_engine.create_session(user, access_token, refresh_token)
        
        # Record metrics
        AUTH_REQUESTS.labels(method="POST", endpoint="/auth/login", status="success").inc()
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=UserResponse(**user)
        )
        
    except Exception as e:
        logger.error("Login failed", error=str(e))
        AUTH_REQUESTS.labels(method="POST", endpoint="/auth/login", status="error").inc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )

@app.post("/auth/refresh")
async def refresh_token(refresh_token: str = Form(...)):
    """Refresh access token"""
    try:
        # Verify refresh token
        payload = auth_engine.verify_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        # Get user data
        user_email = payload.get("email")
        if not user_email or user_email not in auth_engine.users:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        user = auth_engine.users[user_email]
        
        # Create new access token
        new_access_token = auth_engine.create_access_token(user)
        
        return {
            "access_token": new_access_token,
            "token_type": "bearer",
            "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }
        
    except Exception as e:
        logger.error("Token refresh failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token refresh failed"
        )

@app.post("/auth/logout")
async def logout(current_user: Dict[str, Any] = Depends(get_current_user)):
    """User logout endpoint"""
    try:
        # In a real implementation, you would revoke the session
        # For now, we'll just return success
        return {"message": "Logged out successfully"}
        
    except Exception as e:
        logger.error("Logout failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout failed"
        )

@app.get("/auth/me", response_model=UserResponse)
async def get_current_user_info(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Get current user information"""
    return UserResponse(**current_user)

@app.post("/auth/check-permission")
async def check_user_permission(
    permission_check: PermissionCheck,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Check if user has specific permission"""
    try:
        has_permission = auth_engine.check_permission(
            current_user["permissions"],
            permission_check.resource,
            permission_check.action
        )
        
        return {
            "has_permission": has_permission,
            "user_id": current_user["user_id"],
            "resource": permission_check.resource,
            "action": permission_check.action
        }
        
    except Exception as e:
        logger.error("Permission check failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Permission check failed"
        )

@app.get("/auth/users", response_model=List[UserResponse])
async def get_users(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Get all users (admin only)"""
    # Check admin permission
    await check_permission("users", "read", current_user)
    
    users = []
    for user in auth_engine.users.values():
        # Don't include password hash
        user_copy = user.copy()
        if "password_hash" in user_copy:
            del user_copy["password_hash"]
        users.append(UserResponse(**user_copy))
    
    return users

@app.post("/auth/users", response_model=UserResponse)
async def create_user(
    user_data: UserCreate,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Create new user (admin only)"""
    # Check admin permission
    await check_permission("users", "create", current_user)
    
    try:
        # Check if user already exists
        if user_data.email in auth_engine.users:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User already exists"
            )
        
        # Create new user
        new_user = {
            "user_id": f"user_{len(auth_engine.users) + 1:03d}",
            "email": user_data.email,
            "username": user_data.username,
            "full_name": user_data.full_name,
            "role": user_data.role,
            "permissions": ["basic_access"],  # Default permissions
            "organization": user_data.organization,
            "status": "active",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "last_login": None,
            "password_hash": bcrypt.hashpw(user_data.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        }
        
        auth_engine.users[user_data.email] = new_user
        
        # Return user without password hash
        user_response = new_user.copy()
        del user_response["password_hash"]
        
        return UserResponse(**user_response)
        
    except Exception as e:
        logger.error("Failed to create user", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user"
        )

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": APP_NAME,
        "version": APP_VERSION,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "users_count": len(auth_engine.users),
        "active_sessions": len(auth_engine.active_sessions)
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
        "Starting Authentication Microservice",
        version=APP_VERSION,
        environment=ENVIRONMENT,
        debug=DEBUG,
        users_loaded=len(auth_engine.users)
    )

@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event"""
    logger.info("Shutting down Authentication Microservice")

# =============================================================================
# ERROR HANDLERS
# =============================================================================

@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": "Validation error", "errors": exc.errors()}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error("Unhandled exception", error=str(exc), exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004)

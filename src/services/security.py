"""
Enhanced Security and Authentication Improvements
"""
import hashlib
import hmac
import secrets
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Set
from enum import Enum
import jwt
from passlib.context import CryptContext
from passlib.hash import argon2
from pydantic import BaseModel, Field, validator
from fastapi import HTTPException, Request, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import redis
import ipaddress
from cryptography.fernet import Fernet
import logging


class UserRole(str, Enum):
    """User roles for RBAC"""
    ADMIN = "admin"
    AUDITOR = "auditor"
    COMPLIANCE_OFFICER = "compliance_officer"
    READ_ONLY = "read_only"
    GUEST = "guest"


class Permission(str, Enum):
    """Granular permissions"""
    READ_COMPLIANCE = "read:compliance"
    WRITE_COMPLIANCE = "write:compliance"
    READ_REPORTS = "read:reports"
    WRITE_REPORTS = "write:reports"
    ADMIN_USERS = "admin:users"
    ADMIN_SYSTEM = "admin:system"
    AUDIT_LOGS = "audit:logs"


# Role-Permission Mapping
ROLE_PERMISSIONS: Dict[UserRole, Set[Permission]] = {
    UserRole.ADMIN: {
        Permission.READ_COMPLIANCE, Permission.WRITE_COMPLIANCE,
        Permission.READ_REPORTS, Permission.WRITE_REPORTS,
        Permission.ADMIN_USERS, Permission.ADMIN_SYSTEM,
        Permission.AUDIT_LOGS
    },
    UserRole.COMPLIANCE_OFFICER: {
        Permission.READ_COMPLIANCE, Permission.WRITE_COMPLIANCE,
        Permission.READ_REPORTS, Permission.WRITE_REPORTS,
        Permission.AUDIT_LOGS
    },
    UserRole.AUDITOR: {
        Permission.READ_COMPLIANCE, Permission.READ_REPORTS,
        Permission.AUDIT_LOGS
    },
    UserRole.READ_ONLY: {
        Permission.READ_COMPLIANCE, Permission.READ_REPORTS
    },
    UserRole.GUEST: {
        Permission.READ_COMPLIANCE
    }
}


class User(BaseModel):
    """User model with security features"""
    id: str
    username: str
    email: str
    role: UserRole
    is_active: bool = True
    is_mfa_enabled: bool = False
    last_login: Optional[datetime] = None
    failed_login_attempts: int = 0
    locked_until: Optional[datetime] = None
    password_changed_at: Optional[datetime] = None
    
    def has_permission(self, permission: Permission) -> bool:
        """Check if user has specific permission"""
        return permission in ROLE_PERMISSIONS.get(self.role, set())
    
    def is_locked(self) -> bool:
        """Check if account is locked"""
        return (
            self.locked_until and 
            self.locked_until > datetime.utcnow()
        )


class SecurityConfig(BaseModel):
    """Security configuration"""
    secret_key: str = Field(..., min_length=32)
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    max_failed_attempts: int = 5
    lockout_duration_minutes: int = 15
    password_min_length: int = 12
    password_require_uppercase: bool = True
    password_require_lowercase: bool = True
    password_require_numbers: bool = True
    password_require_symbols: bool = True
    session_timeout_minutes: int = 120
    enable_rate_limiting: bool = True
    rate_limit_requests: int = 100
    rate_limit_window_minutes: int = 15
    allowed_ip_ranges: List[str] = []
    enable_audit_logging: bool = True


class SecurityManager:
    """Comprehensive security manager"""
    
    def __init__(self, config: SecurityConfig, redis_client: Optional[redis.Redis] = None):
        self.config = config
        self.redis_client = redis_client
        self.pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
        self.fernet = Fernet(Fernet.generate_key())  # For encrypting sensitive data
        
    def hash_password(self, password: str) -> str:
        """Hash password with Argon2"""
        return self.pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        return self.pwd_context.verify(plain_password, hashed_password)
    
    def validate_password_strength(self, password: str) -> Dict[str, bool]:
        """Validate password strength"""
        checks = {
            "min_length": len(password) >= self.config.password_min_length,
            "has_uppercase": any(c.isupper() for c in password) if self.config.password_require_uppercase else True,
            "has_lowercase": any(c.islower() for c in password) if self.config.password_require_lowercase else True,
            "has_numbers": any(c.isdigit() for c in password) if self.config.password_require_numbers else True,
            "has_symbols": any(not c.isalnum() for c in password) if self.config.password_require_symbols else True,
        }
        
        checks["is_valid"] = all(checks.values())
        return checks
    
    def create_access_token(self, data: Dict[str, Any]) -> str:
        """Create JWT access token"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=self.config.access_token_expire_minutes)
        to_encode.update({"exp": expire, "type": "access"})
        
        return jwt.encode(to_encode, self.config.secret_key, algorithm=self.config.algorithm)
    
    def create_refresh_token(self, data: Dict[str, Any]) -> str:
        """Create JWT refresh token"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=self.config.refresh_token_expire_days)
        to_encode.update({"exp": expire, "type": "refresh"})
        
        return jwt.encode(to_encode, self.config.secret_key, algorithm=self.config.algorithm)
    
    def verify_token(self, token: str, token_type: str = "access") -> Dict[str, Any]:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(token, self.config.secret_key, algorithms=[self.config.algorithm])
            
            if payload.get("type") != token_type:
                raise HTTPException(status_code=401, detail="Invalid token type")
            
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token expired")
        except jwt.JWTError:
            raise HTTPException(status_code=401, detail="Invalid token")
    
    def encrypt_sensitive_data(self, data: str) -> str:
        """Encrypt sensitive data"""
        return self.fernet.encrypt(data.encode()).decode()
    
    def decrypt_sensitive_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data"""
        return self.fernet.decrypt(encrypted_data.encode()).decode()


class RateLimiter:
    """Advanced rate limiter with multiple strategies"""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis_client = redis_client
    
    async def is_rate_limited(
        self, 
        key: str, 
        limit: int, 
        window_seconds: int,
        strategy: str = "sliding_window"
    ) -> bool:
        """Check if request should be rate limited"""
        
        if strategy == "sliding_window":
            return await self._sliding_window_rate_limit(key, limit, window_seconds)
        elif strategy == "token_bucket":
            return await self._token_bucket_rate_limit(key, limit, window_seconds)
        else:
            return await self._fixed_window_rate_limit(key, limit, window_seconds)
    
    async def _sliding_window_rate_limit(self, key: str, limit: int, window_seconds: int) -> bool:
        """Sliding window rate limiting"""
        now = time.time()
        pipeline = self.redis_client.pipeline()
        
        # Remove old entries
        pipeline.zremrangebyscore(key, 0, now - window_seconds)
        
        # Count current requests
        pipeline.zcard(key)
        
        # Add current request
        pipeline.zadd(key, {str(now): now})
        
        # Set expiration
        pipeline.expire(key, window_seconds)
        
        results = pipeline.execute()
        current_count = results[1]
        
        return current_count >= limit
    
    async def _token_bucket_rate_limit(self, key: str, limit: int, refill_period: int) -> bool:
        """Token bucket rate limiting"""
        bucket_key = f"{key}:bucket"
        last_refill_key = f"{key}:last_refill"
        
        now = time.time()
        
        # Get current bucket state
        current_tokens = self.redis_client.get(bucket_key)
        last_refill = self.redis_client.get(last_refill_key)
        
        if current_tokens is None:
            current_tokens = limit
            last_refill = now
        else:
            current_tokens = int(current_tokens)
            last_refill = float(last_refill)
        
        # Calculate tokens to add
        time_passed = now - last_refill
        tokens_to_add = int(time_passed / refill_period)
        current_tokens = min(limit, current_tokens + tokens_to_add)
        
        if current_tokens <= 0:
            return True
        
        # Consume token
        current_tokens -= 1
        
        # Update bucket state
        pipeline = self.redis_client.pipeline()
        pipeline.set(bucket_key, current_tokens, ex=refill_period * limit)
        pipeline.set(last_refill_key, now, ex=refill_period * limit)
        pipeline.execute()
        
        return False
    
    async def _fixed_window_rate_limit(self, key: str, limit: int, window_seconds: int) -> bool:
        """Fixed window rate limiting"""
        current_window = int(time.time()) // window_seconds
        window_key = f"{key}:{current_window}"
        
        current_count = self.redis_client.incr(window_key)
        if current_count == 1:
            self.redis_client.expire(window_key, window_seconds)
        
        return current_count > limit


class IPWhitelist:
    """IP address whitelist/blacklist management"""
    
    def __init__(self, allowed_ranges: List[str], blocked_ips: List[str] = None):
        self.allowed_networks = [ipaddress.ip_network(ip, strict=False) for ip in allowed_ranges]
        self.blocked_ips = set(blocked_ips or [])
    
    def is_allowed(self, ip_address: str) -> bool:
        """Check if IP address is allowed"""
        if ip_address in self.blocked_ips:
            return False
        
        if not self.allowed_networks:
            return True  # No restrictions
        
        client_ip = ipaddress.ip_address(ip_address)
        return any(client_ip in network for network in self.allowed_networks)


class AuditLogger:
    """Security audit logging"""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
    
    def log_authentication_attempt(
        self, 
        username: str, 
        ip_address: str, 
        user_agent: str,
        success: bool,
        failure_reason: Optional[str] = None
    ):
        """Log authentication attempt"""
        self.logger.info(
            "Authentication attempt",
            extra={
                "event_type": "authentication",
                "username": username,
                "ip_address": ip_address,
                "user_agent": user_agent,
                "success": success,
                "failure_reason": failure_reason,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
    
    def log_authorization_check(
        self, 
        user_id: str, 
        resource: str, 
        permission: str,
        granted: bool
    ):
        """Log authorization check"""
        self.logger.info(
            "Authorization check",
            extra={
                "event_type": "authorization",
                "user_id": user_id,
                "resource": resource,
                "permission": permission,
                "granted": granted,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
    
    def log_sensitive_operation(
        self, 
        user_id: str, 
        operation: str, 
        resource_id: str,
        details: Optional[Dict[str, Any]] = None
    ):
        """Log sensitive operation"""
        self.logger.warning(
            "Sensitive operation",
            extra={
                "event_type": "sensitive_operation",
                "user_id": user_id,
                "operation": operation,
                "resource_id": resource_id,
                "details": details or {},
                "timestamp": datetime.utcnow().isoformat()
            }
        )


# FastAPI Security Dependencies
class SecurityBearer(HTTPBearer):
    """Custom HTTP Bearer authentication"""
    
    def __init__(self, security_manager: SecurityManager):
        super().__init__()
        self.security_manager = security_manager
    
    async def __call__(self, request: Request) -> Dict[str, Any]:
        credentials: HTTPAuthorizationCredentials = await super().__call__(request)
        
        if credentials.scheme != "Bearer":
            raise HTTPException(status_code=401, detail="Invalid authentication scheme")
        
        payload = self.security_manager.verify_token(credentials.credentials)
        
        # Add user info to request state
        request.state.user_id = payload.get("sub")
        request.state.user_role = payload.get("role")
        
        return payload


def require_permission(permission: Permission):
    """Decorator to require specific permission"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Extract request from args/kwargs
            request = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break
            
            if not request:
                raise HTTPException(status_code=500, detail="Request not found")
            
            user_role = getattr(request.state, 'user_role', None)
            if not user_role:
                raise HTTPException(status_code=401, detail="Authentication required")
            
            user_permissions = ROLE_PERMISSIONS.get(UserRole(user_role), set())
            if permission not in user_permissions:
                raise HTTPException(
                    status_code=403, 
                    detail=f"Permission {permission} required"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator


async def get_current_user(
    request: Request,
    security: SecurityBearer = Depends()
) -> User:
    """Get current authenticated user"""
    user_id = getattr(request.state, 'user_id', None)
    user_role = getattr(request.state, 'user_role', None)
    
    if not user_id or not user_role:
        raise HTTPException(status_code=401, detail="Invalid authentication")
    
    # In a real implementation, you would fetch the user from database
    # For now, return a mock user
    return User(
        id=user_id,
        username=f"user_{user_id}",
        email=f"user_{user_id}@example.com",
        role=UserRole(user_role)
    )
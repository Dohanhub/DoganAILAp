import os
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, Union
from dotenv import load_dotenv
import logging
from pathlib import Path
import json
import pytz
from datetime import datetime, timezone

# Load .env if present
load_dotenv()

logger = logging.getLogger(__name__)

def _split_csv(value: str) -> List[str]:
    """Parse comma-separated values with enhanced validation"""
    if not value:
        return []
    return [v.strip() for v in value.split(",") if v.strip()]

def _get_bool_env(key: str, default: bool = False) -> bool:
    """Get boolean environment variable with enhanced validation"""
    value = os.getenv(key, "").lower().strip()
    if not value:
        return default
    
    true_values = {"true", "1", "yes", "on", "enabled"}
    false_values = {"false", "0", "no", "off", "disabled"}
    
    if value in true_values:
        return True
    elif value in false_values:
        return False
    else:
        logger.warning(f"Invalid boolean value for {key}: '{value}', using default: {default}")
        return default

def _get_int_env(key: str, default: int, min_val: Optional[int] = None, max_val: Optional[int] = None) -> int:
    """Get integer environment variable with validation and bounds checking"""
    try:
        value = int(os.getenv(key, str(default)))
        
        if min_val is not None and value < min_val:
            logger.warning(f"Value for {key} ({value}) below minimum ({min_val}), using minimum")
            return min_val
        
        if max_val is not None and value > max_val:
            logger.warning(f"Value for {key} ({value}) above maximum ({max_val}), using maximum")
            return max_val
            
        return value
    except ValueError:
        logger.warning(f"Invalid integer value for {key}: '{os.getenv(key)}', using default: {default}")
        return default

def _get_path_env(key: str, default: str, must_exist: bool = False) -> str:
    """Get path environment variable with validation"""
    path = os.getenv(key, default)
    
    if must_exist and not os.path.exists(path):
        logger.warning(f"Path for {key} does not exist: {path}")
    
    return path

def _get_timezone_env(key: str, default: str = "UTC") -> str:
    """Get timezone environment variable with validation"""
    tz_name = os.getenv(key, default)
    try:
        # Validate timezone
        pytz.timezone(tz_name)
        return tz_name
    except pytz.exceptions.UnknownTimeZoneError:
        logger.warning(f"Invalid timezone '{tz_name}' for {key}, using UTC")
        return "UTC"

@dataclass
class DatabaseConfig:
    """Database configuration with validation"""
    host: str = field(default_factory=lambda: os.getenv("POSTGRES_HOST", "localhost"))
    port: int = field(default_factory=lambda: _get_int_env("POSTGRES_PORT", 5432, 1, 65535))
    database: str = field(default_factory=lambda: os.getenv("POSTGRES_DB", "ksa"))
    user: str = field(default_factory=lambda: os.getenv("POSTGRES_USER", "postgres"))
    password: str = field(default_factory=lambda: os.getenv("POSTGRES_PASSWORD", "postgres"))
    pool_size: int = field(default_factory=lambda: _get_int_env("POSTGRES_POOL_SIZE", 5, 1, 50))
    max_overflow: int = field(default_factory=lambda: _get_int_env("POSTGRES_MAX_OVERFLOW", 10, 0, 100))
    echo: bool = field(default_factory=lambda: _get_bool_env("POSTGRES_ECHO", False))
    # Fix timezone handling
    timezone: str = field(default_factory=lambda: _get_timezone_env("POSTGRES_TIMEZONE", "UTC"))
    ssl_mode: str = field(default_factory=lambda: os.getenv("POSTGRES_SSL_MODE", "prefer"))
    ssl_cert: Optional[str] = field(default_factory=lambda: os.getenv("POSTGRES_SSL_CERT"))
    ssl_key: Optional[str] = field(default_factory=lambda: os.getenv("POSTGRES_SSL_KEY"))
    ssl_ca: Optional[str] = field(default_factory=lambda: os.getenv("POSTGRES_SSL_CA"))
    
    @property
    def url(self) -> str:
        """Get PostgreSQL connection URL with timezone setting"""
        base_url = f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"
        # Add timezone parameter to ensure consistent timezone handling
        return f"{base_url}?timezone={self.timezone}&sslmode={self.ssl_mode}"
    
    def validate(self) -> List[str]:
        """Validate database configuration"""
        errors = []
        
        if not self.host:
            errors.append("Database host cannot be empty")
        
        if not self.database:
            errors.append("Database name cannot be empty")
        
        if not self.user:
            errors.append("Database user cannot be empty")
        
        if not self.password:
            errors.append("Database password cannot be empty")
        
        return errors

@dataclass
class TimezoneConfig:
    """Timezone configuration to fix time-related issues"""
    application_timezone: str = field(default_factory=lambda: _get_timezone_env("APP_TIMEZONE", "UTC"))
    display_timezone: str = field(default_factory=lambda: _get_timezone_env("DISPLAY_TIMEZONE", "Asia/Riyadh"))  # KSA timezone
    force_utc: bool = field(default_factory=lambda: _get_bool_env("FORCE_UTC_TIMESTAMPS", True))
    auto_detect_client_timezone: bool = field(default_factory=lambda: _get_bool_env("AUTO_DETECT_CLIENT_TZ", False))
    
    def get_application_tz(self):
        """Get application timezone object"""
        return pytz.timezone(self.application_timezone)
    
    def get_display_tz(self):
        """Get display timezone object"""
        return pytz.timezone(self.display_timezone)
    
    def now_utc(self) -> datetime:
        """Get current UTC time"""
        return datetime.now(timezone.utc)
    
    def now_local(self) -> datetime:
        """Get current time in application timezone"""
        return datetime.now(self.get_application_tz())
    
    def to_utc(self, dt: datetime) -> datetime:
        """Convert datetime to UTC"""
        if dt.tzinfo is None:
            # Assume it's in application timezone
            dt = self.get_application_tz().localize(dt)
        return dt.astimezone(timezone.utc)
    
    def to_display_timezone(self, dt: datetime) -> datetime:
        """Convert datetime to display timezone"""
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(self.get_display_tz())
    
    def validate(self) -> List[str]:
        """Validate timezone configuration"""
        errors = []
        
        try:
            pytz.timezone(self.application_timezone)
        except pytz.exceptions.UnknownTimeZoneError:
            errors.append(f"Invalid application timezone: {self.application_timezone}")
        
        try:
            pytz.timezone(self.display_timezone)
        except pytz.exceptions.UnknownTimeZoneError:
            errors.append(f"Invalid display timezone: {self.display_timezone}")
        
        return errors

@dataclass
class SecurityConfig:
    """Security configuration"""
    secret_key: Optional[str] = field(default_factory=lambda: os.getenv("SECRET_KEY"))
    api_key_header: str = field(default_factory=lambda: os.getenv("API_KEY_HEADER", "X-API-Key"))
    enable_https: bool = field(default_factory=lambda: _get_bool_env("ENABLE_HTTPS", False))
    session_timeout: int = field(default_factory=lambda: _get_int_env("SESSION_TIMEOUT", 3600, 300, 86400))
    max_login_attempts: int = field(default_factory=lambda: _get_int_env("MAX_LOGIN_ATTEMPTS", 5, 1, 20))
    jwt_algorithm: str = field(default_factory=lambda: os.getenv("JWT_ALGORITHM", "HS256"))
    jwt_expiry: int = field(default_factory=lambda: _get_int_env("JWT_EXPIRY", 3600, 300, 86400))
    bcrypt_rounds: int = field(default_factory=lambda: _get_int_env("BCRYPT_ROUNDS", 12, 10, 16))
    rate_limit_enabled: bool = field(default_factory=lambda: _get_bool_env("RATE_LIMIT_ENABLED", True))
    rate_limit_requests: int = field(default_factory=lambda: _get_int_env("RATE_LIMIT_REQUESTS", 100, 10, 1000))
    rate_limit_window: int = field(default_factory=lambda: _get_int_env("RATE_LIMIT_WINDOW", 60, 10, 3600))
    
    def validate(self) -> List[str]:
        """Validate security configuration"""
        errors = []
        
        if not self.secret_key:
            errors.append("SECRET_KEY is required for production")
        elif len(self.secret_key) < 32:
            errors.append("SECRET_KEY should be at least 32 characters long")
        
        if not self.api_key_header:
            errors.append("API_KEY_HEADER cannot be empty")
        
        return errors

@dataclass
class LoggingConfig:
    """Logging configuration"""
    level: str = field(default_factory=lambda: os.getenv("LOG_LEVEL", "INFO"))
    format: str = field(default_factory=lambda: os.getenv(
        "LOG_FORMAT", 
        "%(asctime)s %(levelname)s %(name)s - %(message)s"
    ))
    use_utc: bool = field(default_factory=lambda: _get_bool_env("LOG_USE_UTC", True))
    file_path: Optional[str] = field(default_factory=lambda: os.getenv("LOG_FILE_PATH"))
    max_file_size: int = field(default_factory=lambda: _get_int_env("LOG_MAX_FILE_SIZE", 10485760, 1048576, 104857600))  # 10MB default
    backup_count: int = field(default_factory=lambda: _get_int_env("LOG_BACKUP_COUNT", 5, 1, 20))
    enable_json: bool = field(default_factory=lambda: _get_bool_env("LOG_ENABLE_JSON", False))
    enable_syslog: bool = field(default_factory=lambda: _get_bool_env("LOG_ENABLE_SYSLOG", False))
    syslog_host: Optional[str] = field(default_factory=lambda: os.getenv("SYSLOG_HOST"))
    syslog_port: int = field(default_factory=lambda: _get_int_env("SYSLOG_PORT", 514, 1, 65535))
    
    def validate(self) -> List[str]:
        """Validate logging configuration"""
        errors = []
        
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if self.level.upper() not in valid_levels:
            errors.append(f"Invalid log level: {self.level}. Must be one of {valid_levels}")
        
        if self.file_path and not os.path.exists(os.path.dirname(self.file_path)):
            errors.append(f"Log file directory does not exist: {os.path.dirname(self.file_path)}")
        
        return errors

@dataclass
class CacheConfig:
    """Cache configuration"""
    enable_caching: bool = field(default_factory=lambda: _get_bool_env("ENABLE_CACHING", True))
    cache_ttl: int = field(default_factory=lambda: _get_int_env("CACHE_TTL", 300, 60, 86400))
    cache_type: str = field(default_factory=lambda: os.getenv("CACHE_TYPE", "memory"))
    redis_host: Optional[str] = field(default_factory=lambda: os.getenv("REDIS_HOST"))
    redis_port: int = field(default_factory=lambda: _get_int_env("REDIS_PORT", 6379, 1, 65535))
    redis_password: Optional[str] = field(default_factory=lambda: os.getenv("REDIS_PASSWORD"))
    redis_db: int = field(default_factory=lambda: _get_int_env("REDIS_DB", 0, 0, 15))
    redis_ssl: bool = field(default_factory=lambda: _get_bool_env("REDIS_SSL", False))
    
    def validate(self) -> List[str]:
        """Validate cache configuration"""
        errors = []
        
        if self.cache_type not in ["memory", "redis"]:
            errors.append(f"Invalid cache type: {self.cache_type}. Must be 'memory' or 'redis'")
        
        if self.cache_type == "redis" and not self.redis_host:
            errors.append("Redis host is required when using Redis cache")
        
        return errors

@dataclass
class MonitoringConfig:
    """Monitoring configuration"""
    enable_metrics: bool = field(default_factory=lambda: _get_bool_env("ENABLE_METRICS", True))
    metrics_port: int = field(default_factory=lambda: _get_int_env("METRICS_PORT", 9090, 1024, 65535))
    enable_health_checks: bool = field(default_factory=lambda: _get_bool_env("ENABLE_HEALTH_CHECKS", True))
    health_check_interval: int = field(default_factory=lambda: _get_int_env("HEALTH_CHECK_INTERVAL", 30, 5, 300))
    enable_tracing: bool = field(default_factory=lambda: _get_bool_env("ENABLE_TRACING", False))
    jaeger_host: Optional[str] = field(default_factory=lambda: os.getenv("JAEGER_HOST"))
    jaeger_port: int = field(default_factory=lambda: _get_int_env("JAEGER_PORT", 6831, 1, 65535))
    enable_alerting: bool = field(default_factory=lambda: _get_bool_env("ENABLE_ALERTING", False))
    alert_webhook_url: Optional[str] = field(default_factory=lambda: os.getenv("ALERT_WEBHOOK_URL"))
    
    def validate(self) -> List[str]:
        """Validate monitoring configuration"""
        errors = []
        
        if self.enable_tracing and not self.jaeger_host:
            errors.append("Jaeger host is required when tracing is enabled")
        
        if self.enable_alerting and not self.alert_webhook_url:
            errors.append("Alert webhook URL is required when alerting is enabled")
        
        return errors

@dataclass
class APIConfig:
    """API configuration"""
    host: str = field(default_factory=lambda: os.getenv("API_HOST", "0.0.0.0"))
    port: int = field(default_factory=lambda: _get_int_env("API_PORT", 8000, 1024, 65535))
    workers: int = field(default_factory=lambda: _get_int_env("API_WORKERS", 4, 1, 32))
    timeout: int = field(default_factory=lambda: _get_int_env("API_TIMEOUT", 30, 5, 300))
    max_request_size: int = field(default_factory=lambda: _get_int_env("API_MAX_REQUEST_SIZE", 10485760, 1048576, 104857600))  # 10MB
    enable_docs: bool = field(default_factory=lambda: _get_bool_env("API_ENABLE_DOCS", True))
    enable_redoc: bool = field(default_factory=lambda: _get_bool_env("API_ENABLE_REDOC", True))
    cors_origins: List[str] = field(default_factory=lambda: _split_csv(os.getenv("CORS_ORIGINS", "http://localhost:8501")))
    cors_allow_credentials: bool = field(default_factory=lambda: _get_bool_env("CORS_ALLOW_CREDENTIALS", True))
    
    def validate(self) -> List[str]:
        """Validate API configuration"""
        errors = []
        
        if not self.host:
            errors.append("API host cannot be empty")
        
        if self.workers < 1:
            errors.append("API workers must be at least 1")
        
        return errors

@dataclass
class UIConfig:
    """UI configuration"""
    host: str = field(default_factory=lambda: os.getenv("UI_HOST", "0.0.0.0"))
    port: int = field(default_factory=lambda: _get_int_env("UI_PORT", 8501, 1024, 65535))
    enable_telemetry: bool = field(default_factory=lambda: _get_bool_env("UI_ENABLE_TELEMETRY", False))
    theme: str = field(default_factory=lambda: os.getenv("UI_THEME", "light"))
    language: str = field(default_factory=lambda: os.getenv("UI_LANGUAGE", "en"))
    supported_languages: List[str] = field(default_factory=lambda: _split_csv(os.getenv("UI_SUPPORTED_LANGUAGES", "en,ar")))
    
    def validate(self) -> List[str]:
        """Validate UI configuration"""
        errors = []
        
        if self.theme not in ["light", "dark", "auto"]:
            errors.append(f"Invalid UI theme: {self.theme}. Must be 'light', 'dark', or 'auto'")
        
        if self.language not in self.supported_languages:
            errors.append(f"UI language {self.language} not in supported languages: {self.supported_languages}")
        
        return errors

@dataclass
class Settings:
    """Main application settings"""
    # Basic app info
    app_name: str = field(default_factory=lambda: os.getenv("APP_NAME", "DoganAI Compliance Kit"))
    app_version: str = field(default_factory=lambda: os.getenv("APP_VERSION", "1.0.0"))
    environment: str = field(default_factory=lambda: os.getenv("ENVIRONMENT", "development"))
    debug: bool = field(default_factory=lambda: _get_bool_env("DEBUG", False))
    
    # Component configurations
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    timezone: TimezoneConfig = field(default_factory=TimezoneConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    cache: CacheConfig = field(default_factory=CacheConfig)
    monitoring: MonitoringConfig = field(default_factory=MonitoringConfig)
    api: APIConfig = field(default_factory=APIConfig)
    ui: UIConfig = field(default_factory=UIConfig)
    
    # Computed properties
    @property
    def is_production(self) -> bool:
        """Check if running in production"""
        return self.environment.lower() in ["production", "prod"]
    
    @property
    def is_development(self) -> bool:
        """Check if running in development"""
        return self.environment.lower() in ["development", "dev"]
    
    @property
    def is_testing(self) -> bool:
        """Check if running in testing"""
        return self.environment.lower() in ["testing", "test"]
    
    @property
    def rate_limit_enabled(self) -> bool:
        """Check if rate limiting is enabled"""
        return self.security.rate_limit_enabled
    
    def get_current_time(self) -> datetime:
        """Get current time in application timezone"""
        return self.timezone.now_local()
    
    def validate(self) -> List[str]:
        """Validate all configuration"""
        errors = []
        
        # Validate each component
        errors.extend(self.database.validate())
        errors.extend(self.timezone.validate())
        errors.extend(self.security.validate())
        errors.extend(self.logging.validate())
        errors.extend(self.cache.validate())
        errors.extend(self.monitoring.validate())
        errors.extend(self.api.validate())
        errors.extend(self.ui.validate())
        
        # Production-specific validations
        if self.is_production:
            if self.debug:
                errors.append("Debug mode should be disabled in production")
            
            if not self.security.secret_key:
                errors.append("SECRET_KEY is required in production")
            
            if not self.security.enable_https:
                errors.append("HTTPS should be enabled in production")
        
        return errors
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert settings to dictionary (excluding sensitive data)"""
        return {
            "app_name": self.app_name,
            "app_version": self.app_version,
            "environment": self.environment,
            "debug": self.debug,
            "database": {
                "host": self.database.host,
                "port": self.database.port,
                "database": self.database.database,
                "user": self.database.user,
                "ssl_mode": self.database.ssl_mode,
                "timezone": self.database.timezone
            },
            "timezone": {
                "application_timezone": self.timezone.application_timezone,
                "display_timezone": self.timezone.display_timezone,
                "force_utc": self.timezone.force_utc
            },
            "security": {
                "enable_https": self.security.enable_https,
                "session_timeout": self.security.session_timeout,
                "max_login_attempts": self.security.max_login_attempts,
                "rate_limit_enabled": self.security.rate_limit_enabled
            },
            "logging": {
                "level": self.logging.level,
                "use_utc": self.logging.use_utc,
                "enable_json": self.logging.enable_json
            },
            "cache": {
                "enable_caching": self.cache.enable_caching,
                "cache_type": self.cache.cache_type,
                "cache_ttl": self.cache.cache_ttl
            },
            "monitoring": {
                "enable_metrics": self.monitoring.enable_metrics,
                "enable_health_checks": self.monitoring.enable_health_checks,
                "enable_tracing": self.monitoring.enable_tracing
            },
            "api": {
                "host": self.api.host,
                "port": self.api.port,
                "workers": self.api.workers,
                "timeout": self.api.timeout
            },
            "ui": {
                "host": self.ui.host,
                "port": self.ui.port,
                "theme": self.ui.theme,
                "language": self.ui.language
            }
        }

# Global settings instance
settings = Settings()

# Validate settings on import
if __name__ == "__main__":
    errors = settings.validate()
    if errors:
        print("Configuration validation errors:")
        for error in errors:
            print(f"  - {error}")
        exit(1)
    else:
        print("Configuration validation passed!")
        print(f"App: {settings.app_name} v{settings.app_version}")
        print(f"Environment: {settings.environment}")
        print(f"Debug: {settings.debug}")

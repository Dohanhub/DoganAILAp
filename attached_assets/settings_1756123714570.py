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
    
    @property
    def url(self) -> str:
        """Get PostgreSQL connection URL with timezone setting"""
        base_url = f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"
        # Add timezone parameter to ensure consistent timezone handling
        return f"{base_url}?timezone={self.timezone}"
    
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
    file_path: Optional[str] = field(default_factory=lambda: os.getenv("LOG_FILE_PATH"))
    max_file_size: int = field(default_factory=lambda: _get_int_env("LOG_MAX_FILE_SIZE", 10485760, 1048576))  # 10MB default
    backup_count: int = field(default_factory=lambda: _get_int_env("LOG_BACKUP_COUNT", 5, 1, 10))
    enable_json: bool = field(default_factory=lambda: _get_bool_env("LOG_ENABLE_JSON", False))
    # Add timezone to logging
    use_utc: bool = field(default_factory=lambda: _get_bool_env("LOG_USE_UTC", True))
    
    def validate(self) -> List[str]:
        """Validate logging configuration"""
        errors = []
        
        valid_log_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        if self.level.upper() not in valid_log_levels:
            errors.append(f"Invalid log level '{self.level}', must be one of: {valid_log_levels}")
        
        return errors

@dataclass
class Settings:
    """Enhanced application settings with validation and type safety"""
    
    # App metadata
    app_name: str = field(default_factory=lambda: os.getenv("APP_NAME", "KSA Compliance API"))
    app_version: str = field(default_factory=lambda: os.getenv("APP_VERSION", "0.1.0"))
    environment: str = field(default_factory=lambda: os.getenv("ENVIRONMENT", "development"))
    debug: bool = field(default_factory=lambda: _get_bool_env("DEBUG", False))
    
    # API configuration
    api_url: str = field(default_factory=lambda: os.getenv("API_URL", "http://localhost:8000"))
    api_host: str = field(default_factory=lambda: os.getenv("API_HOST", "0.0.0.0"))
    api_port: int = field(default_factory=lambda: _get_int_env("API_PORT", 8000, 1, 65535))
    
    # CORS configuration
    cors_origins: List[str] = field(default_factory=list)
    cors_allow_credentials: bool = field(default_factory=lambda: _get_bool_env("CORS_ALLOW_CREDENTIALS", True))
    cors_max_age: int = field(default_factory=lambda: _get_int_env("CORS_MAX_AGE", 86400))
    
    # Database configuration
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    
    # Timezone configuration (NEW - to fix the 5-hour delay)
    timezone: TimezoneConfig = field(default_factory=TimezoneConfig)
    
    # Security configuration
    security: SecurityConfig = field(default_factory=SecurityConfig)
    
    # Logging configuration
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    
    # Performance settings (Fixed cache TTL defaults)
    max_workers: int = field(default_factory=lambda: _get_int_env("MAX_WORKERS", 4, 1, 32))
    request_timeout: int = field(default_factory=lambda: _get_int_env("REQUEST_TIMEOUT", 30, 5, 300))
    cache_ttl: int = field(default_factory=lambda: _get_int_env("CACHE_TTL", 300, 60, 3600))  # 5 minutes default
    
    # Rate limiting
    rate_limit_enabled: bool = field(default_factory=lambda: _get_bool_env("RATE_LIMIT_ENABLED", True))
    rate_limit_requests: int = field(default_factory=lambda: _get_int_env("RATE_LIMIT_REQUESTS", 100, 10, 10000))
    rate_limit_window: int = field(default_factory=lambda: _get_int_env("RATE_LIMIT_WINDOW", 3600, 60, 86400))
    
    # File paths
    mappings_dir: str = field(default_factory=lambda: _get_path_env("MAPPINGS_DIR", "mappings"))
    policies_dir: str = field(default_factory=lambda: _get_path_env("POLICIES_DIR", "policies"))
    vendors_dir: str = field(default_factory=lambda: _get_path_env("VENDORS_DIR", "vendors"))
    benchmarks_dir: str = field(default_factory=lambda: _get_path_env("BENCHMARKS_DIR", "benchmarks"))
    
    # Monitoring and observability
    enable_metrics: bool = field(default_factory=lambda: _get_bool_env("ENABLE_METRICS", True))
    metrics_path: str = field(default_factory=lambda: os.getenv("METRICS_PATH", "/metrics"))
    health_check_interval: int = field(default_factory=lambda: _get_int_env("HEALTH_CHECK_INTERVAL", 60, 10, 300))
    
    # Feature flags
    enable_caching: bool = field(default_factory=lambda: _get_bool_env("ENABLE_CACHING", True))
    enable_audit_logging: bool = field(default_factory=lambda: _get_bool_env("ENABLE_AUDIT_LOGGING", True))
    enable_async_evaluation: bool = field(default_factory=lambda: _get_bool_env("ENABLE_ASYNC_EVALUATION", False))
    
    def __post_init__(self):
        """Post-initialization validation and setup"""
        # Parse CORS origins
        cors_origins_str = os.getenv(
            "CORS_ORIGINS", 
            "http://localhost:8501,http://127.0.0.1:8501"
        )
        self.cors_origins = _split_csv(cors_origins_str)
        
        # Environment-specific adjustments
        if self.environment.lower() in ("production", "prod"):
            self.debug = False
            if not self.security.secret_key:
                logger.error("SECRET_KEY is required in production environment")
        
        # Validate directory paths
        self._validate_directories()
        
        # Log timezone configuration for debugging
        logger.info(f"Timezone configuration - App: {self.timezone.application_timezone}, "
                   f"Display: {self.timezone.display_timezone}, Force UTC: {self.timezone.force_utc}")
    
    def _validate_directories(self):
        """Validate that required directories exist or can be created"""
        base_dir = Path(__file__).parent.parent
        
        for dir_name in [self.mappings_dir, self.policies_dir, self.vendors_dir, self.benchmarks_dir]:
            dir_path = base_dir / dir_name
            try:
                dir_path.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                logger.warning(f"Cannot create/access directory {dir_path}: {e}")
    
    @property
    def database_url(self) -> str:
        """Get database URL"""
        return self.database.url
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment"""
        return self.environment.lower() in ("production", "prod")
    
    @property
    def is_development(self) -> bool:
        """Check if running in development environment"""
        return self.environment.lower() in ("development", "dev", "debug")
    
    def get_current_time(self, use_utc: bool = None) -> datetime:
        """Get current time with proper timezone handling"""
        if use_utc is None:
            use_utc = self.timezone.force_utc
        
        if use_utc or self.timezone.force_utc:
            return self.timezone.now_utc()
        else:
            return self.timezone.now_local()
    
    def validate(self) -> List[str]:
        """Validate all configuration settings"""
        errors = []
        
        # Basic validation
        if not self.app_name:
            errors.append("APP_NAME cannot be empty")
        
        if not self.app_version:
            errors.append("APP_VERSION cannot be empty")
        
        # Environment-specific validation
        if self.is_production:
            if self.debug:
                errors.append("DEBUG should be disabled in production")
            
            if not self.cors_origins:
                errors.append("CORS_ORIGINS should be configured in production")
        
        # Validate sub-configurations
        errors.extend(self.database.validate())
        errors.extend(self.timezone.validate())  # NEW timezone validation
        errors.extend(self.security.validate())
        errors.extend(self.logging.validate())
        
        # Cross-configuration validation
        if self.rate_limit_enabled and self.rate_limit_requests <= 0:
            errors.append("RATE_LIMIT_REQUESTS must be greater than 0 when rate limiting is enabled")
        
        return errors

    def to_dict(self) -> Dict[str, Any]:
        """Convert settings to dictionary (excluding sensitive data)"""
        return {
            "app_name": self.app_name,
            "app_version": self.app_version,
            "environment": self.environment,
            "debug": self.debug,
            "api_host": self.api_host,
            "api_port": self.api_port,
            "cors_origins": self.cors_origins,
            "database_host": self.database.host,
            "database_port": self.database.port,
            "database_name": self.database.database,
            "enable_metrics": self.enable_metrics,
            "enable_caching": self.enable_caching,
            "max_workers": self.max_workers,
            "request_timeout": self.request_timeout,
            # Exclude sensitive information like passwords and keys
        }
    
    def save_to_file(self, file_path: str, include_sensitive: bool = False):
        """Save configuration to file"""
        try:
            config_data = self.to_dict()
            
            if include_sensitive:
                config_data.update({
                    "database_user": self.database.user,
                    "database_password": "***REDACTED***",  # Never save actual password
                    "secret_key": "***REDACTED***",
                })
            
            with open(file_path, 'w') as f:
                json.dump(config_data, f, indent=2)
            
            logger.info(f"Configuration saved to {file_path}")
            
        except Exception as e:
            logger.error(f"Failed to save configuration to {file_path}: {e}")
    
    @classmethod
    def load_from_file(cls, file_path: str) -> 'Settings':
        """Load configuration from file"""
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            # Create new instance with loaded data
            # This would require more complex logic to map back to environment variables
            logger.info(f"Configuration loaded from {file_path}")
            return cls()  # For now, return default instance
            
        except Exception as e:
            logger.error(f"Failed to load configuration from {file_path}: {e}")
            return cls()

# Global settings instance
settings = Settings()

# Validate settings on import
validation_errors = settings.validate()
if validation_errors:
    for error in validation_errors:
        logger.error(f"Configuration error: {error}")
    
    if settings.is_production and validation_errors:
        raise ValueError(f"Configuration validation failed in production: {validation_errors}")
    elif validation_errors:
        logger.warning("Configuration validation failed, but continuing in development mode")

# Configure logging based on settings
def configure_logging():
    """Configure logging based on settings"""
    import logging.handlers
    
    log_level = getattr(logging, settings.logging.level.upper(), logging.INFO)
    
    # Remove existing handlers
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    
    # Configure format
    formatter = logging.Formatter(settings.logging.format)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logging.root.addHandler(console_handler)
    
    # File handler if specified
    if settings.logging.file_path:
        try:
            file_handler = logging.handlers.RotatingFileHandler(
                settings.logging.file_path,
                maxBytes=settings.logging.max_file_size,
                backupCount=settings.logging.backup_count,
                encoding='utf-8'
            )
            file_handler.setFormatter(formatter)
            logging.root.addHandler(file_handler)
        except Exception as e:
            logger.error(f"Failed to setup file logging: {e}")
    
    # Set log level
    logging.root.setLevel(log_level)
    
    logger.info(f"Logging configured: level={settings.logging.level}, format=custom")

# Configure logging on import
if not settings.debug:  # Only auto-configure in production
    configure_logging()

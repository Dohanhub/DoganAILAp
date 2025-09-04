import os
from dataclasses import dataclass, field
from typing import List, Optional
from dotenv import load_dotenv
import logging
import pytz
from datetime import datetime, timezone

# Load .env if present
load_dotenv()

logger = logging.getLogger(__name__)

def _get_bool_env(key: str, default: bool = False) -> bool:
    """Get boolean environment variable"""
    value = os.getenv(key, "").lower().strip()
    return value in {"true", "1", "yes", "on", "enabled"} if value else default

def _get_int_env(key: str, default: int, min_val: Optional[int] = None, max_val: Optional[int] = None) -> int:
    """Get integer environment variable with validation"""
    try:
        value = int(os.getenv(key, str(default)))
        if min_val is not None and value < min_val:
            return min_val
        if max_val is not None and value > max_val:
            return max_val
        return value
    except ValueError:
        return default

def _split_csv(value: str) -> List[str]:
    """Parse comma-separated values"""
    if not value:
        return []
    return [v.strip() for v in value.split(",") if v.strip()]

@dataclass
class DatabaseConfig:
    """PostgreSQL database configuration"""
    host: str = field(default_factory=lambda: os.getenv("PGHOST", "localhost"))
    port: int = field(default_factory=lambda: _get_int_env("PGPORT", 5432, 1, 65535))
    database: str = field(default_factory=lambda: os.getenv("PGDATABASE", "postgres"))
    user: str = field(default_factory=lambda: os.getenv("PGUSER", "postgres"))
    password: str = field(default_factory=lambda: os.getenv("PGPASSWORD", "postgres"))
    pool_size: int = field(default_factory=lambda: _get_int_env("POSTGRES_POOL_SIZE", 5, 1, 50))
    max_overflow: int = field(default_factory=lambda: _get_int_env("POSTGRES_MAX_OVERFLOW", 10, 0, 100))
    echo: bool = field(default_factory=lambda: _get_bool_env("POSTGRES_ECHO", False))
    timezone: str = field(default_factory=lambda: os.getenv("POSTGRES_TIMEZONE", "UTC"))

@dataclass
class RedisConfig:
    """Redis configuration for caching and session management"""
    host: str = field(default_factory=lambda: os.getenv("REDIS_HOST", "localhost"))
    port: int = field(default_factory=lambda: _get_int_env("REDIS_PORT", 6379, 1, 65535))
    password: Optional[str] = field(default_factory=lambda: os.getenv("REDIS_PASSWORD"))
    database: int = field(default_factory=lambda: _get_int_env("REDIS_DATABASE", 0, 0, 15))
    max_connections: int = field(default_factory=lambda: _get_int_env("REDIS_MAX_CONNECTIONS", 10, 1, 100))
    socket_timeout: int = field(default_factory=lambda: _get_int_env("REDIS_SOCKET_TIMEOUT", 5, 1, 60))
    socket_connect_timeout: int = field(default_factory=lambda: _get_int_env("REDIS_SOCKET_CONNECT_TIMEOUT", 2, 1, 30))
    retry_on_timeout: bool = field(default_factory=lambda: _get_bool_env("REDIS_RETRY_ON_TIMEOUT", True))
    health_check_interval: int = field(default_factory=lambda: _get_int_env("REDIS_HEALTH_CHECK_INTERVAL", 30, 10, 300))

@dataclass
class TimescaleDBConfig:
    """TimescaleDB configuration (PostgreSQL extension)"""
    # Uses same configuration as PostgreSQL since TimescaleDB is an extension
    host: str = field(default_factory=lambda: os.getenv("TIMESCALEDB_HOST", "localhost"))
    port: int = field(default_factory=lambda: _get_int_env("TIMESCALEDB_PORT", 5432, 1, 65535))
    database: str = field(default_factory=lambda: os.getenv("TIMESCALEDB_DATABASE", "postgres"))
    user: str = field(default_factory=lambda: os.getenv("TIMESCALEDB_USER", "postgres"))
    password: str = field(default_factory=lambda: os.getenv("TIMESCALEDB_PASSWORD", "postgres"))
    chunk_time_interval: str = field(default_factory=lambda: os.getenv("TIMESCALEDB_CHUNK_TIME_INTERVAL", "1 day"))
    compression_enabled: bool = field(default_factory=lambda: _get_bool_env("TIMESCALEDB_COMPRESSION_ENABLED", True))
    retention_policy_days: int = field(default_factory=lambda: _get_int_env("TIMESCALEDB_RETENTION_DAYS", 90, 1, 3650))

@dataclass
class ElasticsearchConfig:
    """Elasticsearch configuration for search and analytics"""
    host: str = field(default_factory=lambda: os.getenv("ELASTICSEARCH_HOST", "localhost"))
    port: int = field(default_factory=lambda: _get_int_env("ELASTICSEARCH_PORT", 9200, 1, 65535))
    username: Optional[str] = field(default_factory=lambda: os.getenv("ELASTICSEARCH_USERNAME"))
    password: Optional[str] = field(default_factory=lambda: os.getenv("ELASTICSEARCH_PASSWORD"))
    use_ssl: bool = field(default_factory=lambda: _get_bool_env("ELASTICSEARCH_USE_SSL", False))
    verify_certs: bool = field(default_factory=lambda: _get_bool_env("ELASTICSEARCH_VERIFY_CERTS", True))
    ca_certs: Optional[str] = field(default_factory=lambda: os.getenv("ELASTICSEARCH_CA_CERTS"))
    timeout: int = field(default_factory=lambda: _get_int_env("ELASTICSEARCH_TIMEOUT", 30, 5, 300))
    max_retries: int = field(default_factory=lambda: _get_int_env("ELASTICSEARCH_MAX_RETRIES", 3, 1, 10))
    retry_on_timeout: bool = field(default_factory=lambda: _get_bool_env("ELASTICSEARCH_RETRY_ON_TIMEOUT", True))
    sniff_on_start: bool = field(default_factory=lambda: _get_bool_env("ELASTICSEARCH_SNIFF_ON_START", True))
    sniff_on_connection_fail: bool = field(default_factory=lambda: _get_bool_env("ELASTICSEARCH_SNIFF_ON_CONNECTION_FAIL", True))
    sniffer_timeout: int = field(default_factory=lambda: _get_int_env("ELASTICSEARCH_SNIFFER_TIMEOUT", 60, 10, 300))

@dataclass
class TimezoneConfig:
    """Timezone configuration"""
    application_timezone: str = field(default_factory=lambda: os.getenv("APP_TIMEZONE", "UTC"))
    display_timezone: str = field(default_factory=lambda: os.getenv("DISPLAY_TIMEZONE", "Asia/Riyadh"))
    force_utc: bool = field(default_factory=lambda: _get_bool_env("FORCE_UTC_TIMESTAMPS", True))
    
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
    
    def to_display_timezone(self, dt: datetime) -> datetime:
        """Convert datetime to display timezone"""
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(self.get_display_tz())

@dataclass
class SecurityConfig:
    """Security configuration"""
    secret_key: Optional[str] = field(default_factory=lambda: os.getenv("SECRET_KEY"))
    api_key_header: str = field(default_factory=lambda: os.getenv("API_KEY_HEADER", "X-API-Key"))
    session_timeout: int = field(default_factory=lambda: _get_int_env("SESSION_TIMEOUT", 3600, 300, 86400))

@dataclass
class ObservabilityConfig:
    """Observability and monitoring configuration"""
    enable_metrics: bool = field(default_factory=lambda: _get_bool_env("ENABLE_METRICS", True))
    enable_structured_logging: bool = field(default_factory=lambda: _get_bool_env("ENABLE_STRUCTURED_LOGGING", True))
    enable_tracing: bool = field(default_factory=lambda: _get_bool_env("ENABLE_TRACING", True))
    metrics_port: int = field(default_factory=lambda: _get_int_env("METRICS_PORT", 9090, 1024, 65535))
    log_level: str = field(default_factory=lambda: os.getenv("LOG_LEVEL", "INFO"))
    log_format: str = field(default_factory=lambda: os.getenv("LOG_FORMAT", "json"))
    correlation_id_header: str = field(default_factory=lambda: os.getenv("CORRELATION_ID_HEADER", "X-Correlation-ID"))
    health_check_interval: int = field(default_factory=lambda: _get_int_env("HEALTH_CHECK_INTERVAL", 60, 10, 300))
    metrics_retention_days: int = field(default_factory=lambda: _get_int_env("METRICS_RETENTION_DAYS", 30, 1, 365))

@dataclass
class Settings:
    """Application settings"""
    
    # App metadata
    app_name: str = field(default_factory=lambda: os.getenv("APP_NAME", "Dogan AI 'Shahin KSA'"))
    app_version: str = field(default_factory=lambda: os.getenv("APP_VERSION", "0.1.0"))
    environment: str = field(default_factory=lambda: os.getenv("ENVIRONMENT", "development"))
    debug: bool = field(default_factory=lambda: _get_bool_env("DEBUG", False))
    
    # API configuration
    api_host: str = field(default_factory=lambda: os.getenv("API_HOST", "0.0.0.0"))
    api_port: int = field(default_factory=lambda: _get_int_env("API_PORT", 8000, 1, 65535))
    
    # CORS configuration
    cors_origins: List[str] = field(default_factory=list)
    cors_allow_credentials: bool = field(default_factory=lambda: _get_bool_env("CORS_ALLOW_CREDENTIALS", True))
    cors_max_age: int = field(default_factory=lambda: _get_int_env("CORS_MAX_AGE", 86400))
    
    # Database configurations
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    redis: RedisConfig = field(default_factory=RedisConfig)
    timescaledb: TimescaleDBConfig = field(default_factory=TimescaleDBConfig)
    elasticsearch: ElasticsearchConfig = field(default_factory=ElasticsearchConfig)
    
    # Timezone configuration
    timezone: TimezoneConfig = field(default_factory=TimezoneConfig)
    
    # Security configuration
    security: SecurityConfig = field(default_factory=SecurityConfig)

    # Observability configuration
    observability: ObservabilityConfig = field(default_factory=ObservabilityConfig)

    # Performance settings
    cache_ttl: int = field(default_factory=lambda: _get_int_env("CACHE_TTL", 300, 60, 3600))
    request_timeout: int = field(default_factory=lambda: _get_int_env("REQUEST_TIMEOUT", 30, 5, 300))

    # Feature flags
    enable_caching: bool = field(default_factory=lambda: _get_bool_env("ENABLE_CACHING", True))
    enable_audit_logging: bool = field(default_factory=lambda: _get_bool_env("ENABLE_AUDIT_LOGGING", True))
    
    def __post_init__(self):
        """Post-initialization setup"""
        # Parse CORS origins
        cors_origins_str = os.getenv("CORS_ORIGINS", "http://localhost:5000,http://localhost:8501")
        self.cors_origins = _split_csv(cors_origins_str)
        
        # Environment-specific adjustments
        if self.environment.lower() in ("production", "prod"):
            self.debug = False
    
    @property
    def is_production(self) -> bool:
        """Check if running in production"""
        return self.environment.lower() in ("production", "prod")
    
    def get_current_time(self) -> datetime:
        """Get current time with proper timezone handling"""
        if self.timezone.force_utc:
            return self.timezone.now_utc()
        return self.timezone.now_local()
    
    def validate(self) -> List[str]:
        """Validate settings"""
        errors = []
        
        if self.is_production and not self.security.secret_key:
            errors.append("SECRET_KEY is required in production")
        
        return errors

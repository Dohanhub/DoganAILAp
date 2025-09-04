from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

# Get database URL from environment or use SQLite as default (dev)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./compliance.db")

env_name = (os.getenv('ENV') or os.getenv('ENVIRONMENT') or 'production').lower()

# Guard against SQLite by default unless explicitly allowed for dev/test
if DATABASE_URL.startswith("sqlite") and env_name not in {'development', 'dev', 'test', 'testing'}:
    # Allow override only with explicit ALLOW_SQLITE=true for non-production testing
    if os.getenv('ALLOW_SQLITE', 'false').lower() not in {'1','true','yes'}:
        raise RuntimeError("SQLite is disabled outside development/test environments. Set ALLOW_SQLITE=true to override for local use.")
    # Enforce SSL for Postgres in production
    if DATABASE_URL.startswith("postgresql") and 'sslmode=' not in DATABASE_URL:
        auto_append = os.getenv('AUTO_APPEND_SSLMODE', 'true').lower() in {'1','true','yes'}
        if auto_append:
            sep = '&' if ('?' in DATABASE_URL) else '?'
            DATABASE_URL = f"{DATABASE_URL}{sep}sslmode=require"
        elif os.getenv('DB_SSLMODE', '').lower() != 'require':
            raise RuntimeError("PostgreSQL connection must enforce sslmode=require in production")

# Create SQLAlchemy engine
_connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
_engine_kwargs = {}
if not DATABASE_URL.startswith("sqlite"):
    # Basic, tunable pooling for non-SQLite DBs
    _engine_kwargs.update({
        "pool_pre_ping": True,
        "pool_size": int(os.getenv("DB_POOL_SIZE", "5")),
        "max_overflow": int(os.getenv("DB_MAX_OVERFLOW", "10")),
    })

engine = create_engine(
    DATABASE_URL,
    connect_args=_connect_args,
    **_engine_kwargs,
)

# Create session local class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

def get_db():
    """Dependency to get DB session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

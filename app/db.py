from sqlalchemy.orm import sessionmaker
import os

try:
    # Reuse existing engine/session from app.database if available
    from .database import engine, SessionLocal as _SessionLocal  # type: ignore
    SessionLocal = _SessionLocal
except Exception:  # fallback (should not be used in normal flow)
    from sqlalchemy import create_engine
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./compliance.db")
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        pool_size=int(os.getenv("DB_POOL_SIZE", "5")),
        max_overflow=int(os.getenv("DB_MAX_OVERFLOW", "10")),
        pool_timeout=int(os.getenv("DB_POOL_TIMEOUT", "30")),
        connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
    )
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def healthcheck(conn_timeout: int = 2) -> bool:
    try:
        with engine.connect() as conn:
            conn.exec_driver_sql("SELECT 1")
        return True
    except Exception:
        return False


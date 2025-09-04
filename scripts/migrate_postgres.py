"""
Create/upgrade Postgres schema using SQLAlchemy metadata.

Usage:
  DATABASE_URL=postgresql+psycopg2://user:pass@host:5432/db python scripts/migrate_postgres.py
"""
import os
from app.database import Base
from app import models  # noqa: F401 ensures models are imported
from sqlalchemy import create_engine


def main() -> None:
    url = os.getenv('DATABASE_URL')
    if not url:
        print('DATABASE_URL not set')
        raise SystemExit(2)
    engine = create_engine(url)
    Base.metadata.create_all(bind=engine)
    print('Schema ensured for Postgres')


if __name__ == '__main__':
    main()


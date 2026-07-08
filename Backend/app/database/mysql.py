"""
MySQL database engine and session factory (SQLAlchemy sync).

Pool settings:
  pool_pre_ping  — discard stale connections before use (safe behind load balancers)
  pool_size=10   — baseline connections kept open per worker process
  max_overflow=20 — burst capacity above pool_size under load
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

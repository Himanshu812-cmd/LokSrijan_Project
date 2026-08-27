"""Database engine, session factory, and declarative base.

Synchronous SQLAlchemy 2.x is used deliberately: it is simpler to reason
about for a small team and fast enough for the MVP. No models are defined
yet — the schema arrives in a later task.

Note: `create_engine` does not open a connection at import time, so the
application starts cleanly even when PostgreSQL is not running.
"""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import settings

engine = create_engine(
    settings.database_url,
    echo=settings.debug,
    pool_pre_ping=True,  # transparently recycle connections dropped by the server
    future=True,
    # Fail fast when PostgreSQL is not running. Without this, a connection
    # attempt can block for a long time and hang /health/db.
    connect_args={"connect_timeout": 3},
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    """Base class every ORM model will inherit from."""


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency yielding a database session per request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

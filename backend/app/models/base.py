"""SQLAlchemy declarative base, engine, and session setup.

Other leads: define models in new files under app/models/ that import
`Base` from here, e.g.

    from app.models.base import Base

    class Timeline(Base):
        __tablename__ = "timeline_events"
        ...

Then use `get_db` as a FastAPI dependency to obtain a session.
"""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import settings

# SQLite needs this connect_arg when used with FastAPI's threaded requests;
# it's a no-op for Postgres.
connect_args = (
    {"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}
)

engine = create_engine(settings.DATABASE_URL, connect_args=connect_args)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Base class all ORM models should inherit from."""

    pass


def get_db() -> Generator:
    """FastAPI dependency that yields a DB session and closes it afterward."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

"""Shared fixtures for API tests: in-memory DB, test client, admin tokens."""

import time

import jwt
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import settings
from app.main import app
from app.models.base import Base, get_db

TEST_SECRET = "test-nextauth-secret-not-used-anywhere-real"


@pytest.fixture
def db_session():
    # StaticPool keeps one connection so every session sees the same
    # in-memory database, including those opened by the test client.
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client(db_session, monkeypatch):
    monkeypatch.setattr(settings, "CLOUDINARY_CLOUD_NAME", "ekiti-test")
    monkeypatch.setattr(settings, "CLOUDINARY_UPLOAD_PRESET", "ekiti30_member_unsigned")
    monkeypatch.setattr(settings, "NEXTAUTH_SECRET", TEST_SECRET)

    app.dependency_overrides[get_db] = lambda: db_session
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()


def _make_token(
    secret: str = TEST_SECRET,
    role: str = "admin",
    email: str = "admin@example.com",
    expires_in: int = 3600,
) -> str:
    now = int(time.time())
    return jwt.encode(
        {"sub": email, "email": email, "role": role, "iat": now, "exp": now + expires_in},
        secret,
        algorithm="HS256",
    )


@pytest.fixture
def make_token():
    """Mint a token shaped like the ones frontend/src/lib/auth.ts issues."""
    return _make_token


@pytest.fixture
def admin_headers() -> dict[str, str]:
    return {"Authorization": f"Bearer {_make_token()}"}

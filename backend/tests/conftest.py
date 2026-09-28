"""Shared fixtures for API tests: in-memory DB, test client, auth tokens, fake Cloudinary."""

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
from app.services import cloudinary_admin

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
def cloudinary_resources(monkeypatch) -> dict[str, dict]:
    """Fake Cloudinary account: public_id -> Admin API resource details.

    Replaces cloudinary_admin.get_resource so tests never call Cloudinary.
    Tests add entries (see tests/test_uploads.py:cloudinary_resource) for
    the uploads they want to exist.
    """
    resources: dict[str, dict] = {}

    def fake_get_resource(public_id: str, resource_type: str) -> dict | None:
        resource = resources.get(public_id)
        if resource is None or resource.get("resource_type") != resource_type:
            return None
        return resource

    monkeypatch.setattr(cloudinary_admin, "get_resource", fake_get_resource)
    return resources


@pytest.fixture
def client(db_session, monkeypatch, cloudinary_resources):
    monkeypatch.setattr(settings, "CLOUDINARY_CLOUD_NAME", "ekiti-test")
    monkeypatch.setattr(settings, "CLOUDINARY_UPLOAD_PRESET", "ekiti30_member_unsigned")
    monkeypatch.setattr(settings, "CLOUDINARY_API_KEY", "test-api-key")
    monkeypatch.setattr(settings, "CLOUDINARY_API_SECRET", "test-api-secret")
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
    name: str | None = None,
) -> str:
    now = int(time.time())
    claims = {"sub": email, "email": email, "role": role, "iat": now, "exp": now + expires_in}
    if name is not None:
        claims["name"] = name
    return jwt.encode(claims, secret, algorithm="HS256")


@pytest.fixture
def make_token():
    """Mint a token shaped like the ones frontend/src/lib/auth.ts issues."""
    return _make_token


@pytest.fixture
def admin_headers() -> dict[str, str]:
    return {"Authorization": f"Bearer {_make_token()}"}


@pytest.fixture
def contributor_headers() -> dict[str, str]:
    token = _make_token(role="contributor", email="contributor@example.com")
    return {"Authorization": f"Bearer {token}"}

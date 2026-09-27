"""Tests for the folder convention and the member upload init/complete flow."""

import pytest

from app.models.asset import Asset
from app.services.cloudinary_convention import (
    ALLOWED_FOLDERS,
    MAX_UPLOAD_BYTES,
    validate_folder,
)

CLOUD_URL = "https://res.cloudinary.com/ekiti-test/image/upload/v1/EKITI30/Historical/abc123.jpg"


def init_payload(**overrides) -> dict:
    payload = {
        "contributor": "Adebayo Ojo",
        "source": "Family archive",
        "location_lga": "Ado-Ekiti",
        "description": "Market square, 1970s",
        "rights_status": "owned",
        "related_content_id": "timeline-1996",
        "folder": "EKITI30/Historical",
    }
    payload.update(overrides)
    return payload


# --- validate_folder ------------------------------------------------------


@pytest.mark.parametrize("folder", ALLOWED_FOLDERS)
def test_validate_folder_accepts_every_allowed_folder(folder):
    assert validate_folder(folder) is True


@pytest.mark.parametrize(
    "folder",
    [
        "",
        "EKITI30",
        "EKITI30/Random",
        "ekiti30/historical",  # case matters
        "EKITI30/Historical/",  # trailing slash
        "EKITI30/Historical/sub",  # subfolders aren't allowed
        "EKITI30/Ekiti_2055",
        "../EKITI30/Historical",
    ],
)
def test_validate_folder_rejects_everything_else(folder):
    assert validate_folder(folder) is False


# --- POST /api/uploads/init -----------------------------------------------


def test_init_creates_pending_asset_and_returns_upload_config(client, db_session):
    response = client.post("/api/uploads/init", json=init_payload())

    assert response.status_code == 201
    body = response.json()
    assert body["cloud_name"] == "ekiti-test"
    assert body["upload_preset"] == "ekiti30_member_unsigned"
    assert body["folder"] == "EKITI30/Historical"
    assert body["max_file_bytes"] == MAX_UPLOAD_BYTES == 10 * 1024 * 1024
    assert body["allowed_formats"] == ["jpg", "png", "webp", "mp4"]

    asset = db_session.get(Asset, body["asset_id"])
    assert asset.status == "pending"
    assert asset.public_id is None
    assert asset.cloudinary_url is None
    assert asset.contributor == "Adebayo Ojo"
    assert asset.rights_status == "owned"
    assert asset.related_content_id == "timeline-1996"


def test_init_rejects_folder_outside_convention(client, db_session):
    response = client.post("/api/uploads/init", json=init_payload(folder="EKITI30/Other"))

    assert response.status_code == 422
    assert db_session.query(Asset).count() == 0


def test_init_requires_contributor_and_rights_status(client):
    response = client.post(
        "/api/uploads/init", json=init_payload(contributor="", rights_status="")
    )
    assert response.status_code == 422


def test_init_returns_503_when_cloudinary_not_configured(client, monkeypatch):
    from app.core.config import settings

    monkeypatch.setattr(settings, "CLOUDINARY_UPLOAD_PRESET", None)
    response = client.post("/api/uploads/init", json=init_payload())
    assert response.status_code == 503


# --- POST /api/uploads/{id}/complete --------------------------------------


def test_complete_saves_public_id_and_url(client, db_session):
    asset_id = client.post("/api/uploads/init", json=init_payload()).json()["asset_id"]

    response = client.post(
        f"/api/uploads/{asset_id}/complete",
        json={"public_id": "EKITI30/Historical/abc123", "secure_url": CLOUD_URL},
    )

    assert response.status_code == 200
    db_session.expire_all()
    asset = db_session.get(Asset, asset_id)
    assert asset.public_id == "EKITI30/Historical/abc123"
    assert asset.cloudinary_url == CLOUD_URL
    assert asset.status == "pending"  # still needs admin approval


def test_complete_unknown_asset_is_404(client):
    response = client.post(
        "/api/uploads/999/complete",
        json={"public_id": "EKITI30/Historical/abc123", "secure_url": CLOUD_URL},
    )
    assert response.status_code == 404


def test_complete_twice_is_409(client):
    asset_id = client.post("/api/uploads/init", json=init_payload()).json()["asset_id"]
    payload = {"public_id": "EKITI30/Historical/abc123", "secure_url": CLOUD_URL}

    assert client.post(f"/api/uploads/{asset_id}/complete", json=payload).status_code == 200
    assert client.post(f"/api/uploads/{asset_id}/complete", json=payload).status_code == 409


@pytest.mark.parametrize(
    "secure_url",
    [
        "https://res.cloudinary.com/someone-else/image/upload/v1/EKITI30/Historical/abc123.jpg",
        "http://res.cloudinary.com/ekiti-test/image/upload/v1/EKITI30/Historical/abc123.jpg",
        "https://evil.example.com/ekiti-test/EKITI30/Historical/abc123.jpg",
    ],
)
def test_complete_rejects_urls_outside_our_cloudinary_account(client, secure_url):
    asset_id = client.post("/api/uploads/init", json=init_payload()).json()["asset_id"]

    response = client.post(
        f"/api/uploads/{asset_id}/complete",
        json={"public_id": "EKITI30/Historical/abc123", "secure_url": secure_url},
    )
    assert response.status_code == 422


def test_complete_rejects_public_id_not_in_url(client):
    asset_id = client.post("/api/uploads/init", json=init_payload()).json()["asset_id"]

    response = client.post(
        f"/api/uploads/{asset_id}/complete",
        json={"public_id": "EKITI30/Historical/different", "secure_url": CLOUD_URL},
    )
    assert response.status_code == 422

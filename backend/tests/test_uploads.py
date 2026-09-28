"""Tests for the folder convention and the member upload init/complete flow."""

import httpx
import pytest

from app.core.config import settings
from app.models.asset import Asset
from app.services import cloudinary_admin
from app.services.cloudinary_convention import (
    ALLOWED_FOLDERS,
    MAX_UPLOAD_BYTES,
    validate_folder,
)

PUBLIC_ID = "EKITI30/Historical/abc123"
CLOUD_URL = f"https://res.cloudinary.com/ekiti-test/image/upload/v1/{PUBLIC_ID}.jpg"
COMPLETE_PAYLOAD = {"public_id": PUBLIC_ID, "secure_url": CLOUD_URL}


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


def cloudinary_resource(**overrides) -> dict:
    """Admin API details for PUBLIC_ID, uploaded where init_payload() says."""
    resource = {
        "public_id": PUBLIC_ID,
        "resource_type": "image",
        "type": "upload",
        "format": "jpg",
        "bytes": 250_000,
        "asset_folder": "EKITI30/Historical",
        "secure_url": CLOUD_URL,
    }
    resource.update(overrides)
    return resource


@pytest.fixture
def init_asset(client, contributor_headers):
    """POST /init as a contributor and return the new asset_id."""

    def _init(**overrides) -> int:
        response = client.post(
            "/api/uploads/init", json=init_payload(**overrides), headers=contributor_headers
        )
        assert response.status_code == 201
        return response.json()["asset_id"]

    return _init


def auth(make_token, role: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {make_token(role=role)}"}


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


# --- upload auth (require_contributor) ------------------------------------

UPLOAD_ROUTES = [
    ("/api/uploads/init", init_payload()),
    ("/api/uploads/1/complete", COMPLETE_PAYLOAD),
]


@pytest.mark.parametrize("path,body", UPLOAD_ROUTES)
def test_upload_routes_reject_missing_token(client, db_session, path, body):
    response = client.post(path, json=body)

    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"
    assert db_session.query(Asset).count() == 0


@pytest.mark.parametrize("path,body", UPLOAD_ROUTES)
@pytest.mark.parametrize(
    "token_kwargs",
    [
        {"secret": "wrong-secret-wrong-secret-wrong-secret"},
        {"expires_in": -60},
    ],
    ids=["wrong-secret", "expired"],
)
def test_upload_routes_reject_invalid_tokens(client, make_token, path, body, token_kwargs):
    headers = {"Authorization": f"Bearer {make_token(**token_kwargs)}"}
    assert client.post(path, json=body, headers=headers).status_code == 401


def test_upload_routes_reject_unknown_role(client, make_token):
    response = client.post(
        "/api/uploads/init", json=init_payload(), headers=auth(make_token, "member")
    )
    assert response.status_code == 403


def test_upload_routes_fail_closed_without_secret(client, contributor_headers, monkeypatch):
    monkeypatch.setattr(settings, "NEXTAUTH_SECRET", None)
    response = client.post("/api/uploads/init", json=init_payload(), headers=contributor_headers)
    assert response.status_code == 503


@pytest.mark.parametrize("role", ["contributor", "admin"])
def test_init_accepts_contributor_and_admin_tokens(client, make_token, role):
    response = client.post(
        "/api/uploads/init", json=init_payload(), headers=auth(make_token, role)
    )
    assert response.status_code == 201


@pytest.mark.parametrize("role", ["contributor", "admin"])
def test_valid_token_does_not_bypass_folder_check(client, db_session, make_token, role):
    response = client.post(
        "/api/uploads/init",
        json=init_payload(folder="EKITI30/Other"),
        headers=auth(make_token, role),
    )

    assert response.status_code == 422
    assert db_session.query(Asset).count() == 0


def test_contributor_token_cannot_use_admin_routes(client, contributor_headers):
    response = client.get("/api/admin/assets/pending", headers=contributor_headers)
    assert response.status_code == 403


# --- POST /api/uploads/init -----------------------------------------------


def test_init_creates_pending_asset_and_returns_upload_config(
    client, db_session, contributor_headers
):
    response = client.post("/api/uploads/init", json=init_payload(), headers=contributor_headers)

    assert response.status_code == 201
    body = response.json()
    assert body["cloud_name"] == "ekiti-test"
    assert body["upload_preset"] == "ekiti30_member_unsigned"
    assert body["folder"] == "EKITI30/Historical"
    assert body["max_file_bytes"] == MAX_UPLOAD_BYTES == 10 * 1024 * 1024
    assert body["allowed_formats"] == ["jpg", "png", "webp", "mp4"]
    # The Admin API credentials never leave the backend.
    assert "test-api-key" not in response.text
    assert "test-api-secret" not in response.text

    asset = db_session.get(Asset, body["asset_id"])
    assert asset.status == "pending"
    assert asset.public_id is None
    assert asset.cloudinary_url is None
    # Identity comes from the verified token, not the request body.
    assert asset.contributor == "contributor@example.com"
    assert asset.created_by == "contributor@example.com"
    assert asset.rights_status == "owned"
    assert asset.related_content_id == "timeline-1996"


def test_init_requires_rights_status(client, contributor_headers):
    response = client.post(
        "/api/uploads/init",
        json=init_payload(rights_status=""),
        headers=contributor_headers,
    )
    assert response.status_code == 422


def test_init_does_not_need_a_contributor_field(client, contributor_headers):
    payload = init_payload()
    del payload["contributor"]
    response = client.post("/api/uploads/init", json=payload, headers=contributor_headers)
    assert response.status_code == 201


def test_init_returns_503_when_cloudinary_not_configured(
    client, contributor_headers, monkeypatch
):
    monkeypatch.setattr(settings, "CLOUDINARY_UPLOAD_PRESET", None)
    response = client.post("/api/uploads/init", json=init_payload(), headers=contributor_headers)
    assert response.status_code == 503


# --- POST /api/uploads/{id}/complete --------------------------------------


def assert_not_completed(db_session, asset_id):
    db_session.expire_all()
    asset = db_session.get(Asset, asset_id)
    assert asset.public_id is None
    assert asset.cloudinary_url is None
    assert asset.status == "pending"


@pytest.mark.parametrize("role", ["contributor", "admin"])
def test_complete_saves_verified_public_id_and_url(
    client, db_session, cloudinary_resources, make_token, role
):
    cloudinary_resources[PUBLIC_ID] = cloudinary_resource()
    # The same account creates and completes the upload.
    owner = auth(make_token, role)
    init = client.post("/api/uploads/init", json=init_payload(), headers=owner)
    asset_id = init.json()["asset_id"]

    response = client.post(
        f"/api/uploads/{asset_id}/complete",
        json=COMPLETE_PAYLOAD,
        headers=owner,
    )

    assert response.status_code == 200
    db_session.expire_all()
    asset = db_session.get(Asset, asset_id)
    assert asset.public_id == PUBLIC_ID
    assert asset.cloudinary_url == CLOUD_URL
    assert asset.status == "pending"  # still needs admin approval


def test_complete_accepts_fixed_folder_mode_accounts(
    client, init_asset, cloudinary_resources, contributor_headers
):
    resource = cloudinary_resource(folder="EKITI30/Historical")
    del resource["asset_folder"]
    cloudinary_resources[PUBLIC_ID] = resource
    asset_id = init_asset()

    response = client.post(
        f"/api/uploads/{asset_id}/complete", json=COMPLETE_PAYLOAD, headers=contributor_headers
    )
    assert response.status_code == 200


def test_complete_accepts_video(client, init_asset, cloudinary_resources, contributor_headers):
    video_url = f"https://res.cloudinary.com/ekiti-test/video/upload/v1/{PUBLIC_ID}.mp4"
    cloudinary_resources[PUBLIC_ID] = cloudinary_resource(
        resource_type="video", format="mp4", secure_url=video_url
    )
    asset_id = init_asset()

    response = client.post(
        f"/api/uploads/{asset_id}/complete",
        json={"public_id": PUBLIC_ID, "secure_url": video_url},
        headers=contributor_headers,
    )
    assert response.status_code == 200


def test_complete_rejects_upload_missing_from_cloudinary(
    client, db_session, init_asset, contributor_headers
):
    asset_id = init_asset()  # nothing registered in the fake Cloudinary

    response = client.post(
        f"/api/uploads/{asset_id}/complete", json=COMPLETE_PAYLOAD, headers=contributor_headers
    )

    assert response.status_code == 422
    assert "No such upload" in response.json()["detail"]
    assert_not_completed(db_session, asset_id)


def test_complete_rejects_upload_in_wrong_folder(
    client, db_session, init_asset, cloudinary_resources, contributor_headers
):
    # Uploaded to a different allowed folder than the one recorded at init.
    cloudinary_resources[PUBLIC_ID] = cloudinary_resource(asset_folder="EKITI30/LGAs")
    asset_id = init_asset(folder="EKITI30/Historical")

    response = client.post(
        f"/api/uploads/{asset_id}/complete", json=COMPLETE_PAYLOAD, headers=contributor_headers
    )

    assert response.status_code == 422
    assert "folder" in response.json()["detail"]
    assert_not_completed(db_session, asset_id)


@pytest.mark.parametrize(
    "overrides",
    [
        {"format": "gif"},
        {"bytes": MAX_UPLOAD_BYTES + 1},
        {"bytes": None},
        {"public_id": "EKITI30/Historical/someone-else"},
    ],
    ids=["bad-format", "too-big", "no-size", "public-id-mismatch"],
)
def test_complete_rejects_resources_failing_sanity_checks(
    client, db_session, init_asset, cloudinary_resources, contributor_headers, overrides
):
    cloudinary_resources[PUBLIC_ID] = cloudinary_resource(**overrides)
    asset_id = init_asset()

    response = client.post(
        f"/api/uploads/{asset_id}/complete", json=COMPLETE_PAYLOAD, headers=contributor_headers
    )

    assert response.status_code == 422
    assert_not_completed(db_session, asset_id)


@pytest.mark.parametrize(
    "error,expected_status",
    [
        (cloudinary_admin.CloudinaryLookupError("HTTP 500"), 502),
        (cloudinary_admin.CloudinaryNotConfigured(), 503),
    ],
    ids=["cloudinary-down", "not-configured"],
)
def test_complete_fails_closed_when_cloudinary_cannot_verify(
    client, db_session, init_asset, contributor_headers, monkeypatch, error, expected_status
):
    def raise_error(public_id, resource_type):
        raise error

    monkeypatch.setattr(cloudinary_admin, "get_resource", raise_error)
    asset_id = init_asset()

    response = client.post(
        f"/api/uploads/{asset_id}/complete", json=COMPLETE_PAYLOAD, headers=contributor_headers
    )

    assert response.status_code == expected_status
    assert_not_completed(db_session, asset_id)


def test_complete_unknown_asset_is_404(client, contributor_headers):
    response = client.post(
        "/api/uploads/999/complete", json=COMPLETE_PAYLOAD, headers=contributor_headers
    )
    assert response.status_code == 404


def test_complete_twice_is_409(client, init_asset, cloudinary_resources, contributor_headers):
    cloudinary_resources[PUBLIC_ID] = cloudinary_resource()
    asset_id = init_asset()
    url = f"/api/uploads/{asset_id}/complete"

    assert client.post(url, json=COMPLETE_PAYLOAD, headers=contributor_headers).status_code == 200
    assert client.post(url, json=COMPLETE_PAYLOAD, headers=contributor_headers).status_code == 409


@pytest.mark.parametrize("review_status", ["approved", "rejected"])
def test_complete_reviewed_asset_is_409(
    client, db_session, init_asset, cloudinary_resources, contributor_headers, review_status
):
    cloudinary_resources[PUBLIC_ID] = cloudinary_resource()
    asset_id = init_asset()
    db_session.get(Asset, asset_id).status = review_status
    db_session.commit()

    response = client.post(
        f"/api/uploads/{asset_id}/complete", json=COMPLETE_PAYLOAD, headers=contributor_headers
    )
    assert response.status_code == 409


@pytest.mark.parametrize(
    "secure_url",
    [
        "https://res.cloudinary.com/someone-else/image/upload/v1/EKITI30/Historical/abc123.jpg",
        "http://res.cloudinary.com/ekiti-test/image/upload/v1/EKITI30/Historical/abc123.jpg",
        "https://evil.example.com/ekiti-test/EKITI30/Historical/abc123.jpg",
        "https://res.cloudinary.com/ekiti-test/raw/upload/v1/EKITI30/Historical/abc123.jpg",
    ],
)
def test_complete_rejects_urls_outside_our_cloudinary_account(
    client, init_asset, cloudinary_resources, contributor_headers, secure_url
):
    cloudinary_resources[PUBLIC_ID] = cloudinary_resource()
    asset_id = init_asset()

    response = client.post(
        f"/api/uploads/{asset_id}/complete",
        json={"public_id": PUBLIC_ID, "secure_url": secure_url},
        headers=contributor_headers,
    )
    assert response.status_code == 422


def test_complete_rejects_public_id_not_in_url(client, init_asset, contributor_headers):
    asset_id = init_asset()

    response = client.post(
        f"/api/uploads/{asset_id}/complete",
        json={"public_id": "EKITI30/Historical/different", "secure_url": CLOUD_URL},
        headers=contributor_headers,
    )
    assert response.status_code == 422


@pytest.mark.parametrize("public_id", ["EKITI30/../admin", "abc?x=1", "EKITI30//abc"])
def test_complete_rejects_unsafe_public_ids(client, init_asset, contributor_headers, public_id):
    asset_id = init_asset()

    response = client.post(
        f"/api/uploads/{asset_id}/complete",
        json={
            "public_id": public_id,
            "secure_url": f"https://res.cloudinary.com/ekiti-test/image/upload/{public_id}.jpg",
        },
        headers=contributor_headers,
    )
    assert response.status_code == 422


# --- cloudinary_admin.get_resource (HTTP layer, no real network) ----------


@pytest.fixture
def admin_api_settings(monkeypatch):
    monkeypatch.setattr(settings, "CLOUDINARY_CLOUD_NAME", "ekiti-test")
    monkeypatch.setattr(settings, "CLOUDINARY_API_KEY", "key")
    monkeypatch.setattr(settings, "CLOUDINARY_API_SECRET", "secret")


def fake_httpx_get(monkeypatch, response=None, error=None) -> list:
    calls = []

    def fake_get(url, auth, timeout):
        calls.append({"url": url, "auth": auth})
        if error:
            raise error
        return response

    monkeypatch.setattr(cloudinary_admin.httpx, "get", fake_get)
    return calls


def test_get_resource_calls_admin_api_with_credentials(admin_api_settings, monkeypatch):
    calls = fake_httpx_get(monkeypatch, httpx.Response(200, json=cloudinary_resource()))

    assert cloudinary_admin.get_resource(PUBLIC_ID, "image") == cloudinary_resource()
    assert calls == [
        {
            "url": "https://api.cloudinary.com/v1_1/ekiti-test/resources/image/upload/"
            "EKITI30/Historical/abc123",
            "auth": ("key", "secret"),
        }
    ]


def test_get_resource_returns_none_for_404(admin_api_settings, monkeypatch):
    fake_httpx_get(monkeypatch, httpx.Response(404, json={"error": {"message": "not found"}}))
    assert cloudinary_admin.get_resource(PUBLIC_ID, "image") is None


@pytest.mark.parametrize(
    "kwargs",
    [
        {"response": httpx.Response(401)},
        {"response": httpx.Response(500)},
        {"error": httpx.ConnectTimeout("timed out")},
    ],
    ids=["401", "500", "timeout"],
)
def test_get_resource_raises_lookup_error_on_failure(admin_api_settings, monkeypatch, kwargs):
    fake_httpx_get(monkeypatch, **kwargs)
    with pytest.raises(cloudinary_admin.CloudinaryLookupError):
        cloudinary_admin.get_resource(PUBLIC_ID, "image")


def test_get_resource_requires_credentials(admin_api_settings, monkeypatch):
    monkeypatch.setattr(settings, "CLOUDINARY_API_SECRET", None)
    calls = fake_httpx_get(monkeypatch)

    with pytest.raises(cloudinary_admin.CloudinaryNotConfigured):
        cloudinary_admin.get_resource(PUBLIC_ID, "image")
    assert calls == []


# --- identity comes from the verified login -------------------------------


def test_init_ignores_a_client_supplied_contributor(client, db_session, contributor_headers):
    response = client.post(
        "/api/uploads/init",
        json=init_payload(contributor="Governor of Ekiti", created_by="someone-else@example.com"),
        headers=contributor_headers,
    )

    assert response.status_code == 201
    asset = db_session.get(Asset, response.json()["asset_id"])
    assert asset.contributor == "contributor@example.com"
    assert asset.created_by == "contributor@example.com"


def test_init_labels_the_asset_with_the_verified_name(client, db_session, make_token):
    token = make_token(role="contributor", email="ada@example.com", name="Ada Obi")
    response = client.post(
        "/api/uploads/init",
        json=init_payload(contributor="Not Ada"),
        headers={"Authorization": f"Bearer {token}"},
    )

    asset = db_session.get(Asset, response.json()["asset_id"])
    assert asset.contributor == "Ada Obi"  # display label
    assert asset.created_by == "ada@example.com"  # the identity that matters


def test_owner_identity_ignores_email_case_and_spacing(
    client, db_session, cloudinary_resources, make_token
):
    cloudinary_resources[PUBLIC_ID] = cloudinary_resource()
    first = make_token(role="contributor", email="Ada@Example.com")
    second = make_token(role="contributor", email=" ada@example.com ")
    init = client.post(
        "/api/uploads/init", json=init_payload(), headers={"Authorization": f"Bearer {first}"}
    )
    asset_id = init.json()["asset_id"]
    assert db_session.get(Asset, asset_id).created_by == "ada@example.com"

    response = client.post(
        f"/api/uploads/{asset_id}/complete",
        json=COMPLETE_PAYLOAD,
        headers={"Authorization": f"Bearer {second}"},
    )
    assert response.status_code == 200


# --- ownership: nobody completes someone else's upload --------------------


@pytest.fixture
def two_contributors(make_token):
    def headers(email):
        return {"Authorization": f"Bearer {make_token(role='contributor', email=email)}"}

    return headers("alice@example.com"), headers("bob@example.com")


def test_contributor_cannot_complete_another_contributors_upload(
    client, db_session, cloudinary_resources, two_contributors
):
    alice, bob = two_contributors
    cloudinary_resources[PUBLIC_ID] = cloudinary_resource()
    asset_id = client.post("/api/uploads/init", json=init_payload(), headers=alice).json()[
        "asset_id"
    ]

    response = client.post(
        f"/api/uploads/{asset_id}/complete", json=COMPLETE_PAYLOAD, headers=bob
    )

    assert response.status_code == 403
    assert_not_completed(db_session, asset_id)

    # The rejected attempt did not disturb the real owner's upload.
    ok = client.post(f"/api/uploads/{asset_id}/complete", json=COMPLETE_PAYLOAD, headers=alice)
    assert ok.status_code == 200


def test_admin_cannot_complete_a_contributors_upload_either(
    client, db_session, cloudinary_resources, two_contributors, admin_headers
):
    alice, _ = two_contributors
    cloudinary_resources[PUBLIC_ID] = cloudinary_resource()
    asset_id = client.post("/api/uploads/init", json=init_payload(), headers=alice).json()[
        "asset_id"
    ]

    response = client.post(
        f"/api/uploads/{asset_id}/complete", json=COMPLETE_PAYLOAD, headers=admin_headers
    )

    assert response.status_code == 403
    assert_not_completed(db_session, asset_id)


def test_non_owner_learns_nothing_about_a_completed_asset(
    client, cloudinary_resources, two_contributors
):
    alice, bob = two_contributors
    cloudinary_resources[PUBLIC_ID] = cloudinary_resource()
    asset_id = client.post("/api/uploads/init", json=init_payload(), headers=alice).json()[
        "asset_id"
    ]
    assert (
        client.post(
            f"/api/uploads/{asset_id}/complete", json=COMPLETE_PAYLOAD, headers=alice
        ).status_code
        == 200
    )

    # The owner sees "already completed" (409); a stranger only sees 403.
    again_owner = client.post(
        f"/api/uploads/{asset_id}/complete", json=COMPLETE_PAYLOAD, headers=alice
    )
    again_stranger = client.post(
        f"/api/uploads/{asset_id}/complete", json=COMPLETE_PAYLOAD, headers=bob
    )
    assert again_owner.status_code == 409
    assert again_stranger.status_code == 403


def test_asset_with_no_recorded_owner_cannot_be_completed(
    client, db_session, cloudinary_resources, contributor_headers, admin_headers
):
    cloudinary_resources[PUBLIC_ID] = cloudinary_resource()
    legacy = Asset(
        folder="EKITI30/Historical",
        contributor="legacy row",
        rights_status="owned",
        status="pending",
        created_by=None,
    )
    db_session.add(legacy)
    db_session.commit()

    for headers in (contributor_headers, admin_headers):
        response = client.post(
            f"/api/uploads/{legacy.id}/complete", json=COMPLETE_PAYLOAD, headers=headers
        )
        assert response.status_code == 403
    assert_not_completed(db_session, legacy.id)


def test_unauthenticated_caller_cannot_complete_anyones_upload(
    client, db_session, cloudinary_resources, contributor_headers
):
    cloudinary_resources[PUBLIC_ID] = cloudinary_resource()
    asset_id = client.post(
        "/api/uploads/init", json=init_payload(), headers=contributor_headers
    ).json()["asset_id"]

    response = client.post(f"/api/uploads/{asset_id}/complete", json=COMPLETE_PAYLOAD)

    assert response.status_code == 401
    assert_not_completed(db_session, asset_id)

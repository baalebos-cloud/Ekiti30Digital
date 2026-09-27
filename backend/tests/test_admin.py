"""Tests for admin auth (require_admin), asset review, and the approved-only helper."""

import pytest

from app.models.asset import Asset
from app.services.assets import get_approved_assets_query

ADMIN_ROUTES = [
    ("get", "/api/admin/assets/pending", None),
    ("post", "/api/admin/assets/1/approve", None),
    ("post", "/api/admin/assets/1/reject", {"rejection_reason": "Blurry"}),
]


def add_asset(db_session, status="pending", **fields) -> Asset:
    asset = Asset(
        folder="EKITI30/LGAs",
        contributor="Member",
        rights_status="owned",
        status=status,
        **fields,
    )
    db_session.add(asset)
    db_session.commit()
    return asset


# --- require_admin --------------------------------------------------------


@pytest.mark.parametrize("method,path,body", ADMIN_ROUTES)
def test_admin_routes_reject_missing_token(client, method, path, body):
    response = client.request(method, path, json=body)
    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"


@pytest.mark.parametrize("method,path,body", ADMIN_ROUTES)
@pytest.mark.parametrize(
    "token_kwargs",
    [
        {"secret": "wrong-secret-wrong-secret-wrong-secret"},
        {"expires_in": -60},
    ],
    ids=["wrong-secret", "expired"],
)
def test_admin_routes_reject_invalid_tokens(client, make_token, method, path, body, token_kwargs):
    headers = {"Authorization": f"Bearer {make_token(**token_kwargs)}"}
    assert client.request(method, path, json=body, headers=headers).status_code == 401


def test_admin_routes_reject_garbage_token(client):
    headers = {"Authorization": "Bearer not-a-jwt"}
    assert client.get("/api/admin/assets/pending", headers=headers).status_code == 401


def test_admin_routes_reject_non_admin_role(client, make_token):
    headers = {"Authorization": f"Bearer {make_token(role='member')}"}
    assert client.get("/api/admin/assets/pending", headers=headers).status_code == 403


def test_admin_routes_fail_closed_without_secret(client, admin_headers, monkeypatch):
    from app.core.config import settings

    monkeypatch.setattr(settings, "NEXTAUTH_SECRET", None)
    assert client.get("/api/admin/assets/pending", headers=admin_headers).status_code == 503


# --- review flow ----------------------------------------------------------


def test_list_pending_returns_only_pending(client, db_session, admin_headers):
    pending = add_asset(db_session)
    add_asset(db_session, status="approved")
    add_asset(db_session, status="rejected")

    response = client.get("/api/admin/assets/pending", headers=admin_headers)

    assert response.status_code == 200
    assert [a["id"] for a in response.json()] == [pending.id]


def test_approve_sets_status_and_reviewer(client, db_session, admin_headers):
    asset = add_asset(db_session)

    response = client.post(f"/api/admin/assets/{asset.id}/approve", headers=admin_headers)

    assert response.status_code == 200
    db_session.expire_all()
    asset = db_session.get(Asset, asset.id)
    assert asset.status == "approved"
    assert asset.reviewed_by == "admin@example.com"
    assert asset.reviewed_at is not None
    assert asset.rejection_reason is None


def test_reject_sets_status_reason_and_reviewer(client, db_session, admin_headers):
    asset = add_asset(db_session)

    response = client.post(
        f"/api/admin/assets/{asset.id}/reject",
        json={"rejection_reason": "No evidence of rights"},
        headers=admin_headers,
    )

    assert response.status_code == 200
    db_session.expire_all()
    asset = db_session.get(Asset, asset.id)
    assert asset.status == "rejected"
    assert asset.rejection_reason == "No evidence of rights"
    assert asset.reviewed_by == "admin@example.com"
    assert asset.reviewed_at is not None


def test_reject_requires_reason(client, db_session, admin_headers):
    asset = add_asset(db_session)
    response = client.post(
        f"/api/admin/assets/{asset.id}/reject",
        json={"rejection_reason": ""},
        headers=admin_headers,
    )
    assert response.status_code == 422


def test_reviewing_an_already_reviewed_asset_is_409(client, db_session, admin_headers):
    asset = add_asset(db_session, status="approved")
    response = client.post(f"/api/admin/assets/{asset.id}/approve", headers=admin_headers)
    assert response.status_code == 409


def test_reviewing_unknown_asset_is_404(client, admin_headers):
    response = client.post("/api/admin/assets/999/approve", headers=admin_headers)
    assert response.status_code == 404


# --- get_approved_assets_query --------------------------------------------


def test_approved_query_excludes_pending_and_rejected(db_session):
    approved = add_asset(db_session, status="approved")
    add_asset(db_session, status="pending")
    add_asset(db_session, status="rejected")

    assert [a.id for a in get_approved_assets_query(db_session).all()] == [approved.id]

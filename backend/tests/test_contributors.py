"""Tests for contributor signup/login and admin review of signups."""

import pytest

from app.core.passwords import hash_password, verify_password
from app.models.contributor import ContributorAccount

PASSWORD = "correct-horse-battery"

ADMIN_ROUTES = [
    ("get", "/api/admin/contributors/pending", None),
    ("post", "/api/admin/contributors/1/approve", None),
    ("post", "/api/admin/contributors/1/reject", {"rejection_reason": "Unknown"}),
]


def add_contributor(
    db_session, email="member@example.com", status="pending"
) -> ContributorAccount:
    account = ContributorAccount(
        name="Member",
        email=email,
        password_hash=hash_password(PASSWORD),
        status=status,
    )
    db_session.add(account)
    db_session.commit()
    return account


def signup(client, **overrides):
    body = {"name": "Ada Ekiti", "email": "ada@example.com", "password": PASSWORD}
    return client.post("/api/auth/signup", json=body | overrides)


# --- passwords ------------------------------------------------------------


def test_hash_password_round_trip():
    password_hash = hash_password(PASSWORD)
    assert password_hash != PASSWORD
    assert verify_password(PASSWORD, password_hash)
    assert not verify_password("wrong-password", password_hash)
    assert not verify_password(PASSWORD, None)


# --- signup ---------------------------------------------------------------


def test_signup_creates_pending_account(client, db_session):
    response = signup(client, email="  Ada@Example.COM ")

    assert response.status_code == 201
    assert response.json()["status"] == "pending"
    assert "password" not in response.text

    account = db_session.query(ContributorAccount).one()
    assert account.name == "Ada Ekiti"
    assert account.email == "ada@example.com"
    assert account.status == "pending"
    assert verify_password(PASSWORD, account.password_hash)


def test_signup_duplicate_email_returns_409(client, db_session):
    assert signup(client).status_code == 201

    response = signup(client, email="ADA@example.com", name="Someone Else")

    assert response.status_code == 409
    assert db_session.query(ContributorAccount).count() == 1


@pytest.mark.parametrize(
    "overrides",
    [
        {"email": "not-an-email"},
        {"password": "short"},
        {"password": "x" * 73},
        {"name": "   "},
    ],
    ids=["bad-email", "short-password", "long-password", "blank-name"],
)
def test_signup_rejects_invalid_input(client, db_session, overrides):
    assert signup(client, **overrides).status_code == 422
    assert db_session.query(ContributorAccount).count() == 0


# --- login ----------------------------------------------------------------


def login(client, email="member@example.com", password=PASSWORD):
    return client.post("/api/auth/login", json={"email": email, "password": password})


def test_login_wrong_password_returns_401(client, db_session):
    add_contributor(db_session, status="approved")
    response = login(client, password="wrong-password")
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password"


def test_login_unknown_email_returns_same_401(client, db_session):
    add_contributor(db_session, status="approved")
    unknown = login(client, email="nobody@example.com")
    wrong_password = login(client, password="wrong-password")
    assert unknown.status_code == wrong_password.status_code == 401
    assert unknown.json() == wrong_password.json()


def test_login_pending_account_returns_403(client, db_session):
    add_contributor(db_session, status="pending")
    response = login(client)
    assert response.status_code == 403
    assert response.json() == {"detail": "Account pending approval", "code": "pending"}


def test_login_rejected_account_returns_403(client, db_session):
    add_contributor(db_session, status="rejected")
    response = login(client)
    assert response.status_code == 403
    assert response.json() == {"detail": "Account not approved", "code": "rejected"}


def test_login_wrong_password_on_pending_account_returns_401(client, db_session):
    # Status must not leak without the right password.
    add_contributor(db_session, status="pending")
    assert login(client, password="wrong-password").status_code == 401


def test_login_approved_account_succeeds(client, db_session):
    account = add_contributor(db_session, status="approved")

    response = login(client, email="Member@Example.com")

    assert response.status_code == 200
    assert response.json() == {
        "id": account.id,
        "name": "Member",
        "email": "member@example.com",
    }


# --- admin auth -----------------------------------------------------------


@pytest.mark.parametrize("method,path,body", ADMIN_ROUTES)
def test_admin_contributor_routes_reject_missing_token(client, method, path, body):
    assert client.request(method, path, json=body).status_code == 401


@pytest.mark.parametrize("method,path,body", ADMIN_ROUTES)
def test_admin_contributor_routes_reject_non_admin(client, make_token, method, path, body):
    headers = {"Authorization": f"Bearer {make_token(role='contributor')}"}
    assert client.request(method, path, json=body, headers=headers).status_code == 403


# --- admin review flow ----------------------------------------------------


def test_list_pending_returns_only_pending_without_hash(client, db_session, admin_headers):
    pending = add_contributor(db_session, email="a@example.com")
    add_contributor(db_session, email="b@example.com", status="approved")
    add_contributor(db_session, email="c@example.com", status="rejected")

    response = client.get("/api/admin/contributors/pending", headers=admin_headers)

    assert response.status_code == 200
    assert [c["id"] for c in response.json()] == [pending.id]
    assert "password_hash" not in response.json()[0]


def test_approve_then_login_succeeds(client, db_session, admin_headers):
    account = add_contributor(db_session)
    assert login(client).status_code == 403

    response = client.post(
        f"/api/admin/contributors/{account.id}/approve", headers=admin_headers
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "approved"
    assert body["reviewed_by"] == "admin@example.com"
    assert body["reviewed_at"] is not None
    assert "password_hash" not in body
    assert login(client).status_code == 200


def test_reject_records_reason_and_blocks_login(client, db_session, admin_headers):
    account = add_contributor(db_session)

    response = client.post(
        f"/api/admin/contributors/{account.id}/reject",
        json={"rejection_reason": "Could not verify identity"},
        headers=admin_headers,
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "rejected"
    assert body["rejection_reason"] == "Could not verify identity"
    assert body["reviewed_by"] == "admin@example.com"
    db_session.refresh(account)
    assert account.status == "rejected"
    assert login(client).status_code == 403


def test_reject_requires_reason(client, db_session, admin_headers):
    account = add_contributor(db_session)
    response = client.post(
        f"/api/admin/contributors/{account.id}/reject", json={}, headers=admin_headers
    )
    assert response.status_code == 422


@pytest.mark.parametrize("action", ["approve", "reject"])
def test_review_unknown_contributor_returns_404(client, admin_headers, action):
    response = client.post(
        f"/api/admin/contributors/999/{action}",
        json={"rejection_reason": "x"},
        headers=admin_headers,
    )
    assert response.status_code == 404


@pytest.mark.parametrize("action", ["approve", "reject"])
def test_review_already_reviewed_returns_409(client, db_session, admin_headers, action):
    account = add_contributor(db_session, status="approved")
    response = client.post(
        f"/api/admin/contributors/{account.id}/{action}",
        json={"rejection_reason": "x"},
        headers=admin_headers,
    )
    assert response.status_code == 409

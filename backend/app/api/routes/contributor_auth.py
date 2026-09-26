"""Public contributor signup and login.

These endpoints only manage contributor accounts; they don't issue tokens.
The frontend's NextAuth calls /login server-side and, on success, issues
the contributor-role JWT itself. Admin login is separate and unaffected
(frontend/src/lib/auth.ts, app/core/auth.py:require_admin).

TODO(before launch): both endpoints are public and unthrottled. Add rate
limiting (per-IP and per-email, e.g. at the proxy/CDN or with a shared
store such as Redis) before real traffic — /login is otherwise open to
password guessing and /signup to spam accounts.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.passwords import hash_password, verify_password
from app.models.base import get_db
from app.models.contributor import ContributorAccount
from app.schemas.contributors import (
    LoginNotApprovedResponse,
    LoginRequest,
    LoginResponse,
    SignupRequest,
    SignupResponse,
)

router = APIRouter(prefix="/api/auth", tags=["auth"])

_EMAIL_TAKEN = "An account with this email already exists"


@router.post("/signup", response_model=SignupResponse, status_code=201)
def signup(body: SignupRequest, db: Session = Depends(get_db)):
    """Create a pending contributor account for an admin to review."""
    existing = (
        db.query(ContributorAccount.id)
        .filter(ContributorAccount.email == body.email)
        .first()
    )
    if existing is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=_EMAIL_TAKEN)

    db.add(
        ContributorAccount(
            name=body.name,
            email=body.email,
            password_hash=hash_password(body.password),
            status="pending",
        )
    )
    try:
        db.commit()
    except IntegrityError:
        # Lost a race with a concurrent signup for the same email.
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=_EMAIL_TAKEN
        ) from None

    return SignupResponse(
        message="Signup received. An admin will review your account.",
        status="pending",
    )


@router.post(
    "/login",
    response_model=LoginResponse,
    responses={status.HTTP_403_FORBIDDEN: {"model": LoginNotApprovedResponse}},
)
def login(body: LoginRequest, db: Session = Depends(get_db)):
    """Check a contributor's credentials and approval status.

    401 for an unknown email or wrong password (deliberately identical);
    403 only once the password is proven correct but the account isn't
    approved, with a `code` of "pending" or "rejected".
    """
    account = (
        db.query(ContributorAccount)
        .filter(ContributorAccount.email == body.email)
        .first()
    )
    password_hash = account.password_hash if account is not None else None
    if not verify_password(body.password, password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    if account.status != "approved":
        # A JSONResponse rather than HTTPException, whose body can only
        # carry `detail`.
        pending = account.status == "pending"
        body = LoginNotApprovedResponse(
            detail="Account pending approval" if pending else "Account not approved",
            code="pending" if pending else "rejected",
        )
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN, content=body.model_dump()
        )

    return LoginResponse(id=account.id, name=account.name, email=account.email)

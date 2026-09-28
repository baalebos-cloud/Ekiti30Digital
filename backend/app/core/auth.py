"""Authentication for protected API routes.

Users log in through NextAuth in the frontend (frontend/src/lib/auth.ts),
which is configured to issue HS256-signed JWTs using NEXTAUTH_SECRET. The
frontend's server side forwards that token to us as
`Authorization: Bearer <token>`, and the dependencies below verify it against
the same shared secret.

Every token carries a `role` claim, one of ROLES:
- require_admin accepts only "admin" (asset review).
- require_contributor accepts "contributor" or "admin" (media uploads) —
  admins can do everything contributors can.
"""

from dataclasses import dataclass

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.config import settings

# Must match the algorithm NextAuth's custom jwt.encode uses in the frontend.
_JWT_ALGORITHM = "HS256"

_bearer = HTTPBearer(auto_error=False)

ROLES = ("admin", "contributor")


@dataclass
class AdminUser:
    """The authenticated admin making the request."""

    email: str


@dataclass
class ContributorUser:
    """The authenticated contributor (or admin) making the request.

    Every field comes from the verified token, never from request data.
    """

    email: str
    role: str
    name: str | None = None

    @property
    def owner_id(self) -> str:
        """Stable identity used to record and check who owns an asset."""
        return self.email.strip().lower()

    @property
    def display_name(self) -> str:
        """Label shown to reviewers: the account's name, else its email."""
        return (self.name or "").strip() or self.owner_id


def _unauthorized(detail: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )


def _decode_token(credentials: HTTPAuthorizationCredentials | None) -> dict:
    """Verify the bearer token and return its claims.

    401 if the token is missing, malformed, expired, or signed with the
    wrong secret; 503 if the backend has no NEXTAUTH_SECRET configured
    (fail closed).
    """
    if not settings.NEXTAUTH_SECRET:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication is not configured",
        )

    if credentials is None:
        raise _unauthorized("Missing bearer token")

    try:
        return jwt.decode(
            credentials.credentials,
            settings.NEXTAUTH_SECRET,
            algorithms=[_JWT_ALGORITHM],
            options={"require": ["exp", "sub", "email"]},
        )
    except jwt.InvalidTokenError:
        raise _unauthorized("Invalid or expired token") from None


def require_admin(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
) -> AdminUser:
    """FastAPI dependency: reject the request unless it carries a valid admin JWT.

    401/503 as in _decode_token; 403 if the token is valid but not an admin
    token.
    """
    claims = _decode_token(credentials)

    if claims.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required"
        )

    return AdminUser(email=claims["email"])


def require_contributor(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
) -> ContributorUser:
    """FastAPI dependency: reject the request unless it carries a valid
    contributor or admin JWT.

    401/503 as in _decode_token; 403 if the token is valid but carries no
    recognized role.
    """
    claims = _decode_token(credentials)

    role = claims.get("role")
    if role not in ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Contributor access required"
        )

    name = claims.get("name")
    return ContributorUser(
        email=claims["email"], role=role, name=name if isinstance(name, str) else None
    )

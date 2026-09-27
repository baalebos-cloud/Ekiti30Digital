"""Admin authentication for protected API routes.

Admins log in through NextAuth in the frontend (frontend/src/lib/auth.ts),
which is configured to issue HS256-signed JWTs using NEXTAUTH_SECRET. The
frontend's server side forwards that token to us as
`Authorization: Bearer <token>`, and require_admin verifies it against the
same shared secret.
"""

from dataclasses import dataclass

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.config import settings

# Must match the algorithm NextAuth's custom jwt.encode uses in the frontend.
_JWT_ALGORITHM = "HS256"

_bearer = HTTPBearer(auto_error=False)


@dataclass
class AdminUser:
    """The authenticated admin making the request."""

    email: str


def _unauthorized(detail: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )


def require_admin(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
) -> AdminUser:
    """FastAPI dependency: reject the request unless it carries a valid admin JWT.

    401 if the token is missing, malformed, expired, or signed with the
    wrong secret; 403 if it's valid but not an admin token; 503 if the
    backend has no NEXTAUTH_SECRET configured (fail closed).
    """
    if not settings.NEXTAUTH_SECRET:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Admin authentication is not configured",
        )

    if credentials is None:
        raise _unauthorized("Missing bearer token")

    try:
        claims = jwt.decode(
            credentials.credentials,
            settings.NEXTAUTH_SECRET,
            algorithms=[_JWT_ALGORITHM],
            options={"require": ["exp", "sub", "email"]},
        )
    except jwt.InvalidTokenError:
        raise _unauthorized("Invalid or expired token") from None

    if claims.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required"
        )

    return AdminUser(email=claims["email"])

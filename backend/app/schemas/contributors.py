"""Request/response schemas for contributor signup, login, and admin review."""

import re
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

# Deliberately loose — one "@", something on both sides, a dot in the
# domain. Real verification would need an email round-trip anyway.
_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

# bcrypt ignores everything past 72 bytes.
_MAX_PASSWORD_BYTES = 72


def _normalize_email(value: str) -> str:
    value = value.strip().lower()
    if not _EMAIL_RE.fullmatch(value):
        raise ValueError("must be a valid email address")
    return value


class SignupRequest(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    email: str = Field(max_length=254)
    password: str = Field(min_length=8)

    @field_validator("name")
    @classmethod
    def _strip_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("must not be blank")
        return value

    @field_validator("email")
    @classmethod
    def _check_email(cls, value: str) -> str:
        return _normalize_email(value)

    @field_validator("password")
    @classmethod
    def _check_password_length(cls, value: str) -> str:
        if len(value.encode("utf-8")) > _MAX_PASSWORD_BYTES:
            raise ValueError(f"must be at most {_MAX_PASSWORD_BYTES} bytes")
        return value


class SignupResponse(BaseModel):
    message: str
    status: str


class LoginRequest(BaseModel):
    email: str
    password: str

    @field_validator("email")
    @classmethod
    def _lowercase_email(cls, value: str) -> str:
        # No format check: an invalid email just fails the lookup with the
        # same generic 401 as any other bad credentials.
        return value.strip().lower()


class LoginResponse(BaseModel):
    """What the frontend's NextAuth needs to issue a contributor JWT."""

    id: int
    name: str
    email: str


class LoginNotApprovedResponse(BaseModel):
    """403 body when the password is right but the account can't log in.

    `detail` is for people reading the response; clients should branch on
    `code` rather than matching the message text.
    """

    detail: str
    code: Literal["pending", "rejected"]


class ContributorOut(BaseModel):
    """An account as admins see it — never includes password_hash."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: str
    status: str
    rejection_reason: str | None
    reviewed_by: str | None
    reviewed_at: datetime | None
    created_at: datetime
    updated_at: datetime

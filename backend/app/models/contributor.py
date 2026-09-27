"""Contributor accounts: self-service signup with admin approval.

Separate from admin auth, which stays in the frontend's NextAuth config
(frontend/src/lib/auth.ts). A contributor signs up via POST /api/auth/signup,
starts as "pending", and can only log in once an admin approves them
(see app/api/routes/contributor_admin.py).
"""

from datetime import datetime

from sqlalchemy import DateTime, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base

CONTRIBUTOR_STATUSES = ("pending", "approved", "rejected")


class ContributorAccount(Base):
    """A contributor who has signed up, awaiting or past admin review."""

    __tablename__ = "contributor_accounts"

    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str]
    # Stored lowercased (see app/schemas/contributors.py) so uniqueness is
    # case-insensitive.
    email: Mapped[str] = mapped_column(unique=True)
    # bcrypt hash from app/core/passwords.py — never the plain password.
    password_hash: Mapped[str]

    # One of CONTRIBUTOR_STATUSES.
    status: Mapped[str] = mapped_column(
        default="pending", server_default="pending", index=True
    )
    rejection_reason: Mapped[str | None] = mapped_column(Text)
    reviewed_by: Mapped[str | None]
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime)

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

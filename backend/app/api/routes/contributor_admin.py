"""Admin review of contributor signups.

Every route here requires a valid admin JWT (see app/core/auth.py). Mirrors
the asset review routes in admin.py.
"""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.auth import AdminUser, require_admin
from app.models.base import get_db
from app.models.contributor import ContributorAccount
from app.schemas.assets import RejectRequest
from app.schemas.contributors import ContributorOut

router = APIRouter(
    prefix="/api/admin/contributors",
    tags=["admin"],
    dependencies=[Depends(require_admin)],
)


def _get_pending_contributor(contributor_id: int, db: Session) -> ContributorAccount:
    account = db.get(ContributorAccount, contributor_id)
    if account is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contributor not found"
        )
    if account.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Contributor has already been {account.status}",
        )
    return account


def _now() -> datetime:
    # Stored naive in UTC, matching the other DateTime columns.
    return datetime.now(timezone.utc).replace(tzinfo=None)


@router.get("/pending", response_model=list[ContributorOut])
def list_pending_contributors(db: Session = Depends(get_db)):
    """All signups awaiting review, oldest first."""
    return (
        db.query(ContributorAccount)
        .filter(ContributorAccount.status == "pending")
        .order_by(ContributorAccount.created_at, ContributorAccount.id)
        .all()
    )


@router.post("/{contributor_id}/approve", response_model=ContributorOut)
def approve_contributor(
    contributor_id: int,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(require_admin),
):
    account = _get_pending_contributor(contributor_id, db)
    account.status = "approved"
    account.reviewed_by = admin.email
    account.reviewed_at = _now()
    db.commit()
    db.refresh(account)
    return account


@router.post("/{contributor_id}/reject", response_model=ContributorOut)
def reject_contributor(
    contributor_id: int,
    body: RejectRequest,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(require_admin),
):
    account = _get_pending_contributor(contributor_id, db)
    account.status = "rejected"
    account.rejection_reason = body.rejection_reason
    account.reviewed_by = admin.email
    account.reviewed_at = _now()
    db.commit()
    db.refresh(account)
    return account

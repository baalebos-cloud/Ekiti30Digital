"""Query helpers for media assets."""

from sqlalchemy.orm import Query, Session

from app.models.asset import Asset


def get_approved_assets_query(db: Session) -> Query:
    """Base query for assets that are safe to show publicly.

    Every public-facing route that displays media (timeline, LGAs, stories,
    Ekiti 2056, ...) MUST start from this helper rather than querying Asset
    directly, so pending or rejected uploads can never leak into public
    output. Only admin routes (app/api/routes/admin.py) may query Asset
    without this filter.
    """
    return db.query(Asset).filter(Asset.status == "approved")

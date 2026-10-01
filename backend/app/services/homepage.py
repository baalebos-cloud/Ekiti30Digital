"""Homepage content: ordered lists, positions, and the public feed.

Used by the admin routes (app/api/routes/homepage_admin.py), the public
route (app/api/routes/homepage.py) and the seed script.
"""

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.homepage import HeroContent, HeroImage, Landmark, Leader, Moment
from app.schemas.homepage import (
    Cta,
    HeroImageOut,
    HeroOut,
    HomepageOut,
    LandmarkOut,
    LeaderOut,
    MomentOut,
)

HERO_ID = 1

# The models that are ordered lists, each with a `position` column.
OrderedModel = type[HeroImage] | type[Leader] | type[Landmark] | type[Moment]


class InvalidOrder(ValueError):
    """A reorder request that isn't exactly the current ids, once each."""


def ordered(db: Session, model: OrderedModel) -> list:
    return db.query(model).order_by(model.position, model.id).all()


def next_position(db: Session, model: OrderedModel) -> int:
    highest = db.query(func.max(model.position)).scalar()
    return 0 if highest is None else highest + 1


def renumber(items: list) -> None:
    """Positions 0, 1, 2, ... in the given order (after a delete or a reorder)."""
    for index, item in enumerate(items):
        item.position = index


def reorder(db: Session, model: OrderedModel, ids: list[int], updated_by: str) -> list:
    """Put the rows in `ids` order; the caller commits. Returns them in their new order.

    Only rows whose position changed get the new updated_by / updated_at.
    """
    items = {item.id: item for item in ordered(db, model)}
    if len(ids) != len(set(ids)):
        raise InvalidOrder("each id may appear only once")
    if set(ids) != set(items):
        missing = sorted(set(items) - set(ids))
        unknown = sorted(set(ids) - set(items))
        parts = []
        if missing:
            parts.append(f"missing ids: {', '.join(map(str, missing))}")
        if unknown:
            parts.append(f"unknown ids: {', '.join(map(str, unknown))}")
        raise InvalidOrder("the new order must list every item exactly once (" + "; ".join(parts) + ")")
    for index, item_id in enumerate(ids):
        item = items[item_id]
        if item.position != index:
            item.position = index
            item.updated_by = updated_by
    return [items[i] for i in ids]


def get_hero(db: Session) -> HeroContent | None:
    return db.get(HeroContent, HERO_ID)


def public_homepage(db: Session) -> HomepageOut:
    hero = get_hero(db)
    return HomepageOut(
        hero=None
        if hero is None
        else HeroOut(
            eyebrow=hero.eyebrow,
            headline=hero.headline,
            subtitle=hero.subtitle,
            primary_cta=Cta(label=hero.primary_cta_label, href=hero.primary_cta_href),
            secondary_cta=Cta(label=hero.secondary_cta_label, href=hero.secondary_cta_href),
            facts=hero.facts,
            images=[HeroImageOut.model_validate(i) for i in ordered(db, HeroImage)],
        ),
        leaders=[LeaderOut.model_validate(i) for i in ordered(db, Leader)],
        landmarks=[LandmarkOut.model_validate(i) for i in ordered(db, Landmark)],
        moments=[MomentOut.model_validate(i) for i in ordered(db, Moment)],
    )

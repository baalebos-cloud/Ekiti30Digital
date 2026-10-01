"""Homepage content an admin manages: the hero, leaders, landmarks and moments.

Loaded once from the homepage's original hardcoded content by
scripts/seed_homepage.py, then edited through /api/admin/homepage/*
(app/api/routes/homepage_admin.py) and served by GET /api/homepage.

Every table has created_at / updated_at and updated_by, the email from the
verified admin token of whoever last changed the row (never from the
request; "cli:<user>" for the seed script), as on app/models/lga.py.

Lists are shown in `position` order (ties by id). Section headings and
descriptions stay in the frontend components; they aren't content here.
"""

from datetime import datetime

from sqlalchemy import JSON, DateTime, Integer, Text, false, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base

# The homepage has three hero polaroids in a fixed layout.
MAX_HERO_IMAGES = 3

# Line-art icons a card shows until it has a real image (image_url). Drawn by
# the frontend (frontend/src/components/homepage/PlaceholderIcon.tsx).
PLACEHOLDER_ICONS: tuple[str, ...] = (
    "document",
    "person",
    "springs",
    "waterfall",
    "hill",
    "star",
    "house",
    "book",
    "pin",
    "celebration",
)


class _Audited:
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )
    updated_by: Mapped[str | None]


class HeroContent(_Audited, Base):
    """The hero's text: a single row (id 1)."""

    __tablename__ = "homepage_hero"

    id: Mapped[int] = mapped_column(primary_key=True)
    eyebrow: Mapped[str]
    # Minimal markup, never HTML: a newline is a line break and *text* is
    # emphasis (see app/schemas/homepage.py). Rendered as React elements.
    headline: Mapped[str] = mapped_column(Text)
    subtitle: Mapped[str] = mapped_column(Text)
    primary_cta_label: Mapped[str]
    primary_cta_href: Mapped[str]
    secondary_cta_label: Mapped[str]
    secondary_cta_href: Mapped[str]
    # The facts row: [{"label": "Created", "value": "1 Oct 1996"}, ...].
    facts: Mapped[list[dict[str, str]]] = mapped_column(JSON)


class HeroImage(_Audited, Base):
    """One hero polaroid (at most MAX_HERO_IMAGES)."""

    __tablename__ = "homepage_hero_images"

    id: Mapped[int] = mapped_column(primary_key=True)
    position: Mapped[int] = mapped_column(Integer, index=True)
    caption: Mapped[str]
    image_url: Mapped[str | None]
    placeholder_icon: Mapped[str]


class Leader(_Audited, Base):
    """A governor in "The people who led us home"."""

    __tablename__ = "homepage_leaders"

    id: Mapped[int] = mapped_column(primary_key=True)
    position: Mapped[int] = mapped_column(Integer, index=True)
    name: Mapped[str]
    # Free text, e.g. "2003–2006, 2014–2018" or "2022–present".
    term: Mapped[str]
    # Without a portrait the card shows the person icon.
    image_url: Mapped[str | None]


class Landmark(_Audited, Base):
    """A place in the landmarks strip."""

    __tablename__ = "homepage_landmarks"

    id: Mapped[int] = mapped_column(primary_key=True)
    position: Mapped[int] = mapped_column(Integer, index=True)
    name: Mapped[str]
    # The line under the name, e.g. "Ado-Ekiti, the state capital".
    description: Mapped[str] = mapped_column(Text)
    image_url: Mapped[str | None]
    placeholder_icon: Mapped[str]


class Moment(_Audited, Base):
    """A moment on the homepage's moments spine."""

    __tablename__ = "homepage_moments"

    id: Mapped[int] = mapped_column(primary_key=True)
    position: Mapped[int] = mapped_column(Integer, index=True)
    # Free text: a year ("1996") or a span ("2010s").
    year: Mapped[str]
    label: Mapped[str] = mapped_column(Text)
    # Anchors (the state's creation, its 30th) get the larger, gold treatment.
    is_anchor: Mapped[bool] = mapped_column(default=False, server_default=false())
    image_url: Mapped[str | None]
    placeholder_icon: Mapped[str]

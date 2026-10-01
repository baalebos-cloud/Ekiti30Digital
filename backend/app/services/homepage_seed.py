"""The homepage's original content, as it was hardcoded in the frontend components.

Loaded once by scripts/seed_homepage.py, so the homepage looks the same on
the day it switches to the database. Copied verbatim from Hero.tsx,
LeadersStrip.tsx, LandmarksStrip.tsx and MomentsSpine.tsx (en dashes, em
dashes and straight apostrophes included).

seed() only fills what's empty: a section that already has content is left
alone, so running it again never undoes an admin's edits.
"""

from dataclasses import dataclass, field

from sqlalchemy.orm import Session

from app.models.homepage import HeroContent, HeroImage, Landmark, Leader, Moment
from app.services import homepage

HERO = {
    "eyebrow": "Marking 30 years of Ekiti State, 1996–2026",
    "headline": "Welcome home.\nThirty years of *us*.",
    "subtitle": (
        "The leaders who guided us, the hills and springs that raised us, the moments we "
        "celebrated together — one place to remember where we've been, and imagine where "
        "we're going."
    ),
    "primary_cta_label": "Walk Through Our Journey",
    "primary_cta_href": "#moments",
    "secondary_cta_label": "Share Your Ekiti Story",
    "secondary_cta_href": "/my-ekiti-story",
    # From the sourced timeline (03_Timeline, EK-001).
    "facts": [
        {"label": "Created", "value": "1 Oct 1996"},
        {"label": "Local governments", "value": "16"},
        {"label": "Capital", "value": "Ado-Ekiti"},
        {"label": "Leaders since", "value": "7"},
    ],
}

HERO_IMAGES = [
    {"caption": "Fajuyi Park, Ado-Ekiti", "placeholder_icon": "document"},
    {"caption": "Governors, 1996–2026", "placeholder_icon": "person"},
    {"caption": "Ikogosi Warm Springs", "placeholder_icon": "springs"},
]

LEADERS = [
    {"name": "Mohammed Bawa", "term": "1996–1998"},
    {"name": "Atanda Yusuf", "term": "1998–1999"},
    {"name": "Niyi Adebayo", "term": "1999–2003"},
    {"name": "Ayodele Fayose", "term": "2003–2006, 2014–2018"},
    {"name": "Segun Oni", "term": "2007–2010"},
    {"name": "Kayode Fayemi", "term": "2010–2014, 2018–2022"},
    {"name": "Biodun Oyebanji", "term": "2022–present"},
]

LANDMARKS = [
    {
        "name": "Ikogosi Warm Springs",
        "description": "Ikogosi-Ekiti · where warm and cold waters meet",
        "placeholder_icon": "springs",
    },
    {"name": "Arinta Waterfalls", "description": "Ipole-Iloro, Ekiti West", "placeholder_icon": "waterfall"},
    {"name": "Fajuyi Memorial Park", "description": "Ado-Ekiti, the state capital", "placeholder_icon": "document"},
    {"name": "Olosunta Hill", "description": "Ikere-Ekiti · sacred hill and skyline", "placeholder_icon": "hill"},
]

# Note: unlike the timeline (03_Timeline), these labels carry no sources.
MOMENTS = [
    {"year": "1996", "label": "Ekiti State is created from Ondo State", "is_anchor": True, "placeholder_icon": "star"},
    {"year": "1999", "label": "First elected civilian governor takes office", "is_anchor": False, "placeholder_icon": "house"},
    {"year": "2010s", "label": "Growth in roads, schools and healthcare access", "is_anchor": False, "placeholder_icon": "book"},
    {"year": "2022", "label": "A new administration continues the journey", "is_anchor": False, "placeholder_icon": "pin"},
    {"year": "2026", "label": "Ekiti turns 30 — and we're building this, together", "is_anchor": True, "placeholder_icon": "celebration"},
]

_LISTS = (
    ("hero images", HeroImage, HERO_IMAGES),
    ("leaders", Leader, LEADERS),
    ("landmarks", Landmark, LANDMARKS),
    ("moments", Moment, MOMENTS),
)


@dataclass
class SeedResult:
    seeded: list[str] = field(default_factory=list)
    # Sections that already had content, left as they were.
    kept: list[str] = field(default_factory=list)


def seed(db: Session, *, updated_by: str) -> SeedResult:
    """Insert the original content into every empty section, and commit."""
    result = SeedResult()
    if homepage.get_hero(db) is None:
        db.add(HeroContent(id=homepage.HERO_ID, **HERO, updated_by=updated_by))
        result.seeded.append("hero")
    else:
        result.kept.append("hero")

    for name, model, rows in _LISTS:
        if db.query(model).first() is not None:
            result.kept.append(name)
            continue
        for position, row in enumerate(rows):
            db.add(model(**row, position=position, updated_by=updated_by))
        result.seeded.append(name)

    db.commit()
    return result

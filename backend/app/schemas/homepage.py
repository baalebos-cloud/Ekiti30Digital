"""Schemas for the homepage content: admin requests/responses and the public feed.

Admin request models forbid unknown fields, as in app/schemas/content_admin.py:
id, position, image_url, updated_by and updated_at are set by the server
(position through the reorder endpoints, image_url only by an image upload),
and a request that tries to send them is rejected rather than ignored.

The public response (GET /api/homepage) is camelCase, like app/schemas/lgas.py,
and carries only what the homepage renders.
"""

from datetime import datetime
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, field_validator, model_validator
from pydantic.alias_generators import to_camel

from app.models.homepage import PLACEHOLDER_ICONS

# Trimmed, non-empty text. Lengths are generous caps, not design limits.
_Short = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=200)]
_Long = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=1000)]
_Icon = Literal[*PLACEHOLDER_ICONS]

MAX_HERO_FACTS = 6


def _check_headline(value: str | None) -> str | None:
    """The headline is minimal markup, not HTML: a newline breaks the line, *text* is emphasis."""
    if value is None:
        return value
    value = "\n".join(line.strip() for line in value.strip().splitlines())
    if "<" in value or ">" in value:
        raise ValueError("the headline can't contain HTML; use a new line for a break and *text* for emphasis")
    if value.count("*") % 2:
        raise ValueError("every *emphasis* needs an opening and a closing *")
    if "**" in value:
        raise ValueError("*emphasis* can't be empty")
    return value


def _check_href(value: str | None) -> str | None:
    """A button link: a page on this site ("/..."), a section ("#..."), or an https:// URL."""
    if value is None:
        return value
    if value.startswith(("/", "#", "https://")) and not value.startswith("//"):
        return value
    raise ValueError('a link must start with "/", "#" or "https://"')


class _Request(BaseModel):
    model_config = ConfigDict(extra="forbid")


class _Update(_Request):
    """A partial update: leave a field out to keep it. Sending null isn't allowed; every field is required."""

    @model_validator(mode="after")
    def _no_nulls(self):
        nulls = sorted(name for name in self.model_fields_set if getattr(self, name) is None)
        if nulls:
            raise ValueError(f"these can't be empty: {', '.join(nulls)}")
        return self


# --- Hero ---


class HeroFact(_Request):
    label: _Short
    value: _Short


class HeroUpdate(_Update):
    """PATCH /api/admin/homepage/hero. Before the hero exists, every field is needed."""

    eyebrow: _Short | None = None
    headline: _Long | None = None
    subtitle: _Long | None = None
    primary_cta_label: _Short | None = None
    primary_cta_href: _Short | None = None
    secondary_cta_label: _Short | None = None
    secondary_cta_href: _Short | None = None
    facts: list[HeroFact] | None = Field(default=None, min_length=1, max_length=MAX_HERO_FACTS)

    _headline = field_validator("headline")(_check_headline)
    _hrefs = field_validator("primary_cta_href", "secondary_cta_href")(_check_href)


class HeroImageCreate(_Request):
    caption: _Short
    placeholder_icon: _Icon = "document"


class HeroImageUpdate(_Update):
    caption: _Short | None = None
    placeholder_icon: _Icon | None = None


# --- Leaders, landmarks, moments ---


class LeaderCreate(_Request):
    name: _Short
    term: _Short


class LeaderUpdate(_Update):
    name: _Short | None = None
    term: _Short | None = None


class LandmarkCreate(_Request):
    name: _Short
    description: _Long
    placeholder_icon: _Icon = "pin"


class LandmarkUpdate(_Update):
    name: _Short | None = None
    description: _Long | None = None
    placeholder_icon: _Icon | None = None


class MomentCreate(_Request):
    year: _Short
    label: _Long
    is_anchor: bool = False
    placeholder_icon: _Icon = "star"


class MomentUpdate(_Update):
    year: _Short | None = None
    label: _Long | None = None
    is_anchor: bool | None = None
    placeholder_icon: _Icon | None = None


class ReorderRequest(_Request):
    """Every id in the list, once each, in the new order."""

    ids: list[int]


# --- Admin responses ---


class _AdminOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
    updated_by: str | None


class HeroAdminOut(_AdminOut):
    eyebrow: str
    headline: str
    subtitle: str
    primary_cta_label: str
    primary_cta_href: str
    secondary_cta_label: str
    secondary_cta_href: str
    facts: list[HeroFact]


class HeroImageAdminOut(_AdminOut):
    position: int
    caption: str
    image_url: str | None
    placeholder_icon: str


class LeaderAdminOut(_AdminOut):
    position: int
    name: str
    term: str
    image_url: str | None


class LandmarkAdminOut(_AdminOut):
    position: int
    name: str
    description: str
    image_url: str | None
    placeholder_icon: str


class MomentAdminOut(_AdminOut):
    position: int
    year: str
    label: str
    is_anchor: bool
    image_url: str | None
    placeholder_icon: str


# --- Public: GET /api/homepage ---


class _CamelModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True, from_attributes=True)


class Cta(_CamelModel):
    label: str
    href: str


class Fact(_CamelModel):
    label: str
    value: str


class HeroImageOut(_CamelModel):
    id: int
    caption: str
    image_url: str | None
    placeholder_icon: str


class HeroOut(_CamelModel):
    eyebrow: str
    headline: str
    subtitle: str
    primary_cta: Cta
    secondary_cta: Cta
    facts: list[Fact]
    images: list[HeroImageOut]


class LeaderOut(_CamelModel):
    id: int
    name: str
    term: str
    image_url: str | None


class LandmarkOut(_CamelModel):
    id: int
    name: str
    description: str
    image_url: str | None
    placeholder_icon: str


class MomentOut(_CamelModel):
    id: int
    year: str
    label: str
    is_anchor: bool
    image_url: str | None
    placeholder_icon: str


class HomepageOut(_CamelModel):
    # None until the hero has been seeded or saved.
    hero: HeroOut | None
    leaders: list[LeaderOut]
    landmarks: list[LandmarkOut]
    moments: list[MomentOut]

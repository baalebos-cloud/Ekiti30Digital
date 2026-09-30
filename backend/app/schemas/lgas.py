"""Public response shape for GET /api/lgas.

Serialized with camelCase keys to match the frontend's `Lga` type
(frontend/src/data/lgas.ts); FastAPI emits response models by alias.
verification_status is passed through unchanged — every LGA is "Pending"
today, and the frontend labels it as such.
"""

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel

from app.models.lga import Lga

# Written in the source where research hasn't been done yet; shown as an
# empty list rather than as if it were a place called "To be researched".
_PLACEHOLDERS = {"to be researched"}


def _split_list(value: str | None) -> list[str]:
    items = [item.strip() for item in (value or "").split(";")]
    return [item for item in items if item and item.lower() not in _PLACEHOLDERS]


class _CamelModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)


class LgaSource(_CamelModel):
    name: str
    url: str | None
    type: str | None


class LgaOut(_CamelModel):
    slug: str
    name: str
    headquarters: str
    latitude: float
    longitude: float
    coordinate_type: str | None
    towns: list[str]
    notable_places: list[str]
    institutions: list[str]
    sources: list[LgaSource]
    source_date: str | None
    last_checked: str
    verification_status: str
    limitations: str | None
    owner: str | None
    # Serialized as imageUrl; null until an admin uploads one.
    image_url: str | None

    @classmethod
    def from_model(cls, lga: Lga) -> "LgaOut":
        sources = [
            LgaSource(
                name=getattr(lga, f"source_{n}_name"),
                url=getattr(lga, f"source_{n}_link"),
                type=getattr(lga, f"source_{n}_type"),
            )
            for n in (1, 2, 3)
            if getattr(lga, f"source_{n}_name")
        ]
        return cls(
            slug=lga.slug,
            name=lga.lga_name,
            headquarters=lga.headquarters,
            latitude=lga.latitude,
            longitude=lga.longitude,
            coordinate_type=lga.coordinate_type,
            towns=_split_list(lga.major_towns_communities),
            notable_places=_split_list(lga.notable_places),
            institutions=_split_list(lga.important_institutions),
            sources=sources,
            source_date=lga.source_date,
            last_checked=lga.last_checked,
            verification_status=lga.verification_status,
            limitations=lga.limitations,
            owner=lga.owner,
            image_url=lga.image_url,
        )


class LgaListResponse(BaseModel):
    lgas: list[LgaOut]

"""Ekiti's 16 Local Government Areas, loaded from 02_LGAs/ekiti_lgas.csv.

Columns mirror the CSV (see 02_LGAs/README.md) and are stored as the source
has them — list columns stay semicolon-separated text, "To be researched"
placeholders are kept, and last_checked / verification_status are not
reinterpreted. Loaded by app/services/lga_ingestion.py.
"""

from datetime import datetime

from sqlalchemy import DateTime, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Lga(Base):
    """One LGA row from the source dataset."""

    __tablename__ = "lgas"

    id: Mapped[int] = mapped_column(primary_key=True)

    # slugify(lga_name), e.g. "Ido/Osi" -> "ido-osi". The upsert key, and
    # matches the 02_LGAs/lga-<slug>.md filenames.
    slug: Mapped[str] = mapped_column(unique=True, index=True)

    lga_name: Mapped[str]
    headquarters: Mapped[str]

    # Approximate headquarters town-centre point (WGS84), not a boundary.
    latitude: Mapped[float]
    longitude: Mapped[float]
    coordinate_type: Mapped[str | None]

    # Semicolon-separated in the source.
    major_towns_communities: Mapped[str | None] = mapped_column(Text)
    notable_places: Mapped[str | None] = mapped_column(Text)
    important_institutions: Mapped[str | None] = mapped_column(Text)

    # Numbered source records: source_N_name/type/link describe one source.
    source_1_name: Mapped[str | None]
    source_1_type: Mapped[str | None]
    source_1_link: Mapped[str | None]
    source_2_name: Mapped[str | None]
    source_2_type: Mapped[str | None]
    source_2_link: Mapped[str | None]
    source_3_name: Mapped[str | None]
    source_3_type: Mapped[str | None]
    source_3_link: Mapped[str | None]

    # Free text in the source (e.g. "Not specified"), so not a date column.
    source_date: Mapped[str | None]
    # Stored exactly as the source has it (currently YYYY-MM-DD).
    last_checked: Mapped[str]
    # Stored exactly as the source has it (every row is "Pending" today).
    verification_status: Mapped[str] = mapped_column(index=True)

    limitations: Mapped[str | None] = mapped_column(Text)
    owner: Mapped[str | None]

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

"""SQLAlchemy models.

Import every model module here so Base.metadata is fully populated —
Alembic's autogenerate (see backend/alembic/env.py) relies on this.
"""

from app.models.asset import Asset  # noqa: F401
from app.models.contributor import ContributorAccount  # noqa: F401
from app.models.knowledge import Chunk, KnowledgeDocument  # noqa: F401

"""Load the homepage's original content into the homepage tables, once.

!! RUN THIS BY HAND. It writes to whatever database DATABASE_URL names.
!! DATABASE_URL must be set in your terminal session: this script deliberately
!! ignores backend/.env, so it can't write to a database by accident.

Usage, from backend/ (after `alembic upgrade head` on that database):

    python scripts/seed_homepage.py

Fills only the sections that are empty (the hero, hero images, leaders,
landmarks, moments) with the content the homepage had hardcoded before it
moved to the database (app/services/homepage_seed.py). A section that already
has content is left as it is, so running this again never undoes an admin's
edits. Seeded rows get updated_by = "cli:<your OS username>".

After this, the admin area (Manage content -> Homepage) is how the content changes.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine  # noqa: E402
from sqlalchemy.engine import make_url  # noqa: E402
from sqlalchemy.orm import sessionmaker  # noqa: E402

from app.services import homepage_seed  # noqa: E402
from app.services.attribution import cli_identity  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        print("DATABASE_URL is not set in this shell (backend/.env is ignored).", file=sys.stderr)
        return 1
    url = make_url(database_url)
    # Never print the password.
    print(f"Target database: {url.drivername}://{url.host or ''}:{url.port or ''}/{url.database}")
    identity = cli_identity()
    print(f"Seeded rows will be recorded as updated_by = {identity!r}")

    engine = create_engine(database_url)
    try:
        with sessionmaker(bind=engine)() as session:
            result = homepage_seed.seed(session, updated_by=identity)
    finally:
        engine.dispose()

    print(f"Seeded: {', '.join(result.seeded) or 'nothing'}")
    if result.kept:
        print(f"Already had content, left as is: {', '.join(result.kept)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

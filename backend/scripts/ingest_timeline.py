"""Load 03_Timeline/EKITI30_Timeline_Events_1996-2026.csv into timeline_events (upsert by id).

!! RUN THIS BY HAND. It writes to whatever database DATABASE_URL names.
!! DATABASE_URL must be set in your terminal session: this script deliberately
!! ignores backend/.env, so it can't write to a database by accident.

Usage, from backend/ (after `alembic upgrade head` on that database):

    python scripts/ingest_timeline.py --dry-run    # validate the CSV, write nothing
    python scripts/ingest_timeline.py              # validate and upsert
    python scripts/ingest_timeline.py --csv path/to/other.csv

Invalid rows are skipped and listed; the exit status is 1 if any were.
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine  # noqa: E402
from sqlalchemy.engine import make_url  # noqa: E402
from sqlalchemy.orm import sessionmaker  # noqa: E402

from app.services.timeline_ingestion import ingest_timeline, load_csv, validate_rows  # noqa: E402

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DEFAULT_CSV = os.path.join(REPO_ROOT, "03_Timeline", "EKITI30_Timeline_Events_1996-2026.csv")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--csv", default=DEFAULT_CSV, help="path to the timeline CSV")
    parser.add_argument(
        "--dry-run", action="store_true", help="validate the CSV without touching a database"
    )
    args = parser.parse_args()

    rows = load_csv(args.csv)
    print(f"Read {len(rows)} row(s) from {args.csv}")

    if args.dry_run:
        valid, skipped = validate_rows(rows)
        print(f"Valid: {len(valid)}")
    else:
        database_url = os.environ.get("DATABASE_URL")
        if not database_url:
            print("DATABASE_URL is not set in this shell (backend/.env is ignored).", file=sys.stderr)
            return 1
        url = make_url(database_url)
        # Never print the password.
        print(f"Target database: {url.drivername}://{url.host or ''}:{url.port or ''}/{url.database}")

        engine = create_engine(database_url)
        with sessionmaker(bind=engine)() as session:
            result = ingest_timeline(rows, session)
        engine.dispose()
        skipped = result.skipped
        print(f"Created: {result.created}  Updated: {result.updated}")

    print(f"Skipped: {len(skipped)}")
    for row in skipped:
        print(f"  line {row.line} ({row.event_id}): {row.reason}")
    return 1 if skipped else 0


if __name__ == "__main__":
    sys.exit(main())

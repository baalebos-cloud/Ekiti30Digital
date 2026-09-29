"""Load 03_Timeline/EKITI30_Timeline_Events_1996-2026.csv into timeline_events (upsert by id).

!! RUN THIS BY HAND. It writes to whatever database DATABASE_URL names.
!! DATABASE_URL must be set in your terminal session: this script deliberately
!! ignores backend/.env, so it can't write to a database by accident.

Usage, from backend/ (after `alembic upgrade head` on that database):

    python scripts/ingest_timeline.py --dry-run    # validate the CSV, write nothing
    python scripts/ingest_timeline.py              # validate and upsert
    python scripts/ingest_timeline.py --force      # ...including rows admins edited
    python scripts/ingest_timeline.py --csv path/to/other.csv

For initial loads and emergencies. The normal way to change this data is the
admin area (edits, or CSV import at POST /api/admin/timeline/import), which
records the admin's verified email as updated_by. Rows this script changes
get updated_by = "cli:<your OS username>".

Before writing, the script lists every row the CSV would change that was last
changed by an admin. Without --force those rows are left untouched (and
listed as held back); every other row is imported. With --force they are
overwritten with the CSV's values.

Exit status is 1 if any row was invalid or held back.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ingest_common import REPO_ROOT, run  # noqa: E402

from app.services import timeline_ingestion  # noqa: E402

DEFAULT_CSV = os.path.join(REPO_ROOT, "03_Timeline", "EKITI30_Timeline_Events_1996-2026.csv")


def main(argv: list[str] | None = None) -> int:
    return run(
        description=__doc__.splitlines()[0],
        default_csv=DEFAULT_CSV,
        service=timeline_ingestion,
        ingest=timeline_ingestion.ingest_timeline,
        key_attr="event_id",
        argv=argv,
    )


if __name__ == "__main__":
    sys.exit(main())

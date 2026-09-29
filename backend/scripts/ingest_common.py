"""Shared runner for scripts/ingest_lgas.py and scripts/ingest_timeline.py.

Both scripts behave identically; only the dataset differs. See either
script's docstring for usage.
"""

import argparse
import os
import sys
from collections.abc import Callable
from types import ModuleType

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine  # noqa: E402
from sqlalchemy.engine import make_url  # noqa: E402
from sqlalchemy.orm import sessionmaker  # noqa: E402

from app.services.attribution import cli_identity  # noqa: E402

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

BANNER = "!" * 72


def _print_skipped(skipped, key_attr: str) -> None:
    print(f"Skipped (invalid): {len(skipped)}")
    for row in skipped:
        print(f"  line {row.line} ({getattr(row, key_attr)}): {row.reason}")


def run(
    *,
    description: str,
    default_csv: str,
    service: ModuleType,
    ingest: Callable,
    key_attr: str,
    argv: list[str] | None = None,
) -> int:
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--csv", default=default_csv, help="path to the CSV")
    parser.add_argument(
        "--dry-run", action="store_true", help="validate the CSV without touching a database"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="also overwrite rows last changed by an admin in the admin UI",
    )
    args = parser.parse_args(argv)

    rows = service.read_csv(args.csv)
    print(f"Read {len(rows)} row(s) from {args.csv}")

    if args.dry_run:
        valid, skipped = service.validate_rows(rows)
        print(f"Valid: {len(valid)}")
        print("(Dry run: no database, so rows edited by admins aren't checked.)")
        _print_skipped(skipped, key_attr)
        return 1 if skipped else 0

    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        print("DATABASE_URL is not set in this shell (backend/.env is ignored).", file=sys.stderr)
        return 1
    url = make_url(database_url)
    # Never print the password.
    print(f"Target database: {url.drivername}://{url.host or ''}:{url.port or ''}/{url.database}")
    identity = cli_identity()
    print(f"Changes will be recorded as updated_by = {identity!r}")

    engine = create_engine(database_url)
    try:
        with sessionmaker(bind=engine)() as session:
            # Look first, write nothing: which admin edits would this undo?
            preview = ingest(rows, session, updated_by=identity, dry_run=True)
            if preview.admin_edited:
                print(BANNER)
                print(
                    f"!! WARNING: this CSV would overwrite {len(preview.admin_edited)} row(s) "
                    "last changed by an admin in the admin UI:"
                )
                for edit in preview.admin_edited:
                    print(f"!!   {edit.key}  (last changed by {edit.updated_by})")
                if args.force:
                    print("!! --force given: these rows WILL be overwritten with the CSV's values.")
                else:
                    print("!! Without --force these rows are skipped; every other row is imported.")
                print(BANNER)

            result = ingest(
                rows, session, updated_by=identity, protect_admin_edits=not args.force
            )
    finally:
        engine.dispose()

    print(
        f"Created: {len(result.created)}  Updated: {len(result.updated)}  "
        f"Unchanged: {len(result.unchanged)}  Held back: {len(result.held_back)}"
    )
    if result.held_back:
        print(f"Held back (last changed by an admin; re-run with --force to overwrite): {len(result.held_back)}")
        for edit in result.held_back:
            print(f"  {edit.key}: last changed by {edit.updated_by}")
    _print_skipped(result.skipped, key_attr)
    return 1 if result.skipped or result.held_back else 0

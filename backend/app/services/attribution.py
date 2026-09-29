"""Who changed a content row: an admin (verified email) or the CLI scripts.

updated_by on lgas / timeline_events holds either an admin's verified email
(set by the admin API from the token) or a CLI marker such as
"cli:ayobami" (set by scripts/ingest_*.py). The "cli:" prefix can't be
mistaken for an email, and it lets the CLI tell whether a row it is about
to overwrite was last changed by an admin.
"""

import getpass
import re

CLI_PREFIX = "cli:"


def cli_identity(username: str | None = None) -> str:
    """"cli:<OS username>", reduced to characters that can't form an email."""
    if username is None:
        try:
            username = getpass.getuser()
        except Exception:  # getuser raises if no username can be found
            username = ""
    safe = re.sub(r"[^A-Za-z0-9._-]+", "-", username).strip("-.") or "unknown"
    return f"{CLI_PREFIX}{safe}"


def is_admin_attribution(updated_by: str | None) -> bool:
    """True if the row was last changed through the admin API (a real email)."""
    return bool(updated_by) and not updated_by.startswith(CLI_PREFIX)

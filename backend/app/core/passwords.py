"""Password hashing for contributor accounts.

A thin wrapper around passlib's bcrypt so the rest of the app never touches
hashing details. Note bcrypt only uses the first 72 bytes of a password;
app/schemas/contributors.py rejects longer ones rather than letting them be
silently truncated.

passlib 1.7.4 is pinned alongside bcrypt 4.0.1 in requirements.txt: later
bcrypt releases break passlib's backend detection (5.x fails outright).
"""

from passlib.context import CryptContext

_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Return a salted bcrypt hash of `password`."""
    return _context.hash(password)


def verify_password(password: str, password_hash: str | None) -> bool:
    """Return True if `password` matches `password_hash`.

    Pass None when there's no account to check against: a dummy hash is
    still verified so the response takes as long as a real mismatch,
    which avoids revealing via timing whether an email is registered.
    """
    if password_hash is None:
        _context.dummy_verify()
        return False
    return _context.verify(password, password_hash)

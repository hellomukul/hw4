"""Password hashing and account auth for Campus Customs.

Passwords are never stored or compared in plain text. We keep a salted
PBKDF2-HMAC-SHA256 hash and verify by recomputing it — the raw password
exists only for the moment it takes to hash, and is never written anywhere.

Stored hash format (new accounts), four `$`-separated fields:

    pbkdf2_sha256$<iterations>$<salt_hex>$<digest_hex>

The database already contains seeded rows in an older three-field layout:

    pbkdf2_sha256$<salt>$<digest_hex>

which has no iteration field. `verify_password` understands both, so the
seeded users keep working while new sign-ups use the self-describing format.
"""

from __future__ import annotations

import hashlib
import hmac
import secrets

ALGORITHM = "pbkdf2_sha256"
ITERATIONS = 260_000  # cost for newly created accounts

# The seeded rows omit the iteration count. 120,000 is the value the fixtures
# were generated with — confirmed by reproducing the test user's stored hash
# from its known password and salt. New accounts use ITERATIONS above instead.
LEGACY_ITERATIONS = 120_000


def _pbkdf2(password: str, salt: str, iterations: int) -> str:
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), iterations)
    return dk.hex()


def hash_password(password: str) -> str:
    """Return a fresh salted hash for a new password."""
    salt = secrets.token_hex(16)
    digest = _pbkdf2(password, salt, ITERATIONS)
    return f"{ALGORITHM}${ITERATIONS}${salt}${digest}"


def verify_password(password: str, stored: str) -> bool:
    """Check a password against a stored hash, in constant time.

    Accepts both the new four-field format and the seeded three-field one.
    Never raises on a malformed hash — a bad record is simply a failed login.
    """
    if not stored:
        return False
    parts = stored.split("$")

    try:
        if len(parts) == 4:
            algorithm, iterations_s, salt, expected = parts
            iterations = int(iterations_s)
        elif len(parts) == 3:
            algorithm, salt, expected = parts
            iterations = LEGACY_ITERATIONS
        else:
            return False
    except (ValueError, TypeError):
        return False

    if algorithm != ALGORITHM:
        return False

    candidate = _pbkdf2(password, salt, iterations)
    # hmac.compare_digest avoids leaking match progress through timing.
    return hmac.compare_digest(candidate, expected)

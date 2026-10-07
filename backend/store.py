"""Chat history persistence for logged-in customers.

Reads and writes the `chat_messages` table (one row per turn). Only
logged-in users get history: the table's `user_id` is NOT NULL and references
`users`, so a guest simply has nothing written. A user is identified by the
email the signed-in website sends; we map it to a real `users` row and store
everything under that row's id, so memory is tied to the account.

Self-contained DB helpers (no import from main) to keep the import graph a
simple line.
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
DB_PATH = HERE.parent / "data" / "campus_customs.db"

# How many past turns to load / keep in view. Bounds tokens and query size.
HISTORY_LIMIT = 40


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def get_user_by_email(email: str | None) -> dict[str, Any] | None:
    """The user row for a signed-in email, or None for a guest / unknown email.

    This is what ties chat memory to a real account: no match, no history.
    """
    if not email or not email.strip():
        return None
    with _connect() as conn:
        row = conn.execute(
            "SELECT id, name, email, first_name, last_name FROM users "
            "WHERE lower(email) = ?",
            (email.strip().lower(),),
        ).fetchone()
    return dict(row) if row else None


def load_history(user_id: int, limit: int = HISTORY_LIMIT) -> list[dict[str, Any]]:
    """A user's past chat turns, oldest first, with any product cards decoded."""
    with _connect() as conn:
        rows = conn.execute(
            "SELECT role, content, products_json, created_at FROM chat_messages "
            "WHERE user_id = ? ORDER BY id DESC LIMIT ?",
            (user_id, limit),
        ).fetchall()
    rows = list(reversed(rows))  # fetched newest-first, show oldest-first
    history = []
    for r in rows:
        products = []
        if r["products_json"]:
            try:
                products = json.loads(r["products_json"])
            except (TypeError, ValueError):
                products = []
        history.append(
            {
                "role": r["role"],
                "content": r["content"],
                "products": products,
                "created_at": r["created_at"],
            }
        )
    return history


def save_message(
    user_id: int,
    role: str,
    content: str,
    products: list[dict[str, Any]] | None = None,
) -> None:
    """Append one turn for a logged-in user."""
    products_json = json.dumps(products) if products else None
    with _connect() as conn:
        conn.execute(
            "INSERT INTO chat_messages (user_id, role, content, products_json) "
            "VALUES (?, ?, ?, ?)",
            (user_id, role, content, products_json),
        )
        conn.commit()

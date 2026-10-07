"""Append-only audit trail for agent runs.

Every chat turn the agent handles adds one entry to output/audit_trail.json.
Entries are only ever appended — prior runs are preserved, never overwritten —
so the file is a complete, ordered history of what the agent did.

Each entry records: when it ran, the tools it called with short
arguments/results, a short preview of the reply, and why the agent stopped.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
AUDIT_PATH = HERE.parent / "output" / "audit_trail.json"

# Keep the file readable: long values are clipped to a short preview.
MAX_FIELD = 160


def clip(value: Any, limit: int = MAX_FIELD) -> Any:
    """Shorten a value for the log — long strings become a preview."""
    if isinstance(value, str):
        s = value.strip().replace("\n", " ")
        return s if len(s) <= limit else s[: limit - 1] + "…"
    if isinstance(value, dict):
        return {k: clip(v, 80) for k, v in value.items()}
    if isinstance(value, list):
        return [clip(v, 80) for v in value[:5]]
    return value


def _load() -> list[dict[str, Any]]:
    """The existing entries, or an empty list if the file is new/unreadable."""
    if not AUDIT_PATH.exists():
        return []
    try:
        data = json.loads(AUDIT_PATH.read_text(encoding="utf-8"))
    except (ValueError, OSError):
        return []
    return data if isinstance(data, list) else []


def append_entry(entry: dict[str, Any]) -> None:
    """Add one run to the trail, preserving everything already there.

    Never raises: an audit failure must not break a chat reply. The write is
    read-modify-write so the whole history is kept, never replaced.
    """
    try:
        AUDIT_PATH.parent.mkdir(parents=True, exist_ok=True)
        entries = _load()
        entries.append(entry)
        AUDIT_PATH.write_text(json.dumps(entries, indent=2) + "\n", encoding="utf-8")
    except OSError:
        pass


def build_entry(
    message: str,
    tool_calls: list[dict[str, Any]],
    reply: str,
    stop_reason: str,
    products_shown: int,
    signed_in: bool,
) -> dict[str, Any]:
    """Shape one audit entry from a finished run."""
    return {
        "time": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "signed_in": signed_in,
        "message": clip(message),
        "tools": [
            {
                "tool": call["tool"],
                "args": clip(call.get("args", {})),
                "result": clip(call.get("result", "")),
            }
            for call in tool_calls
        ],
        "reply_preview": clip(reply),
        "products_shown": products_shown,
        "stop_reason": stop_reason,
    }

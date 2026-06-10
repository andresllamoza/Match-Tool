"""SQLite-backed journey persistence + HTTP-only cookie helpers."""

from __future__ import annotations

import json
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from engine.models import JourneyContext, JourneyState

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = Path(os.environ.get("PB_SESSION_DB", ROOT / "data" / "pb_sessions.db"))
COOKIE_NAME = "pb_session"
COOKIE_MAX_AGE = 60 * 60 * 24 * 30  # 30 days

_TERMINAL_STATES = {JourneyState.COMPLETE, JourneyState.ESCALATED}


def is_resumable(ctx: JourneyContext) -> bool:
    return ctx.state not in _TERMINAL_STATES


def _connect() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with _connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS journey_sessions (
                journey_id TEXT PRIMARY KEY,
                context_json TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        conn.commit()


def save_context(ctx: JourneyContext) -> None:
    payload = ctx.model_dump_json()
    now = datetime.now(timezone.utc).isoformat()
    with _connect() as conn:
        conn.execute(
            """
            INSERT INTO journey_sessions (journey_id, context_json, updated_at)
            VALUES (?, ?, ?)
            ON CONFLICT(journey_id) DO UPDATE SET
                context_json = excluded.context_json,
                updated_at = excluded.updated_at
            """,
            (ctx.journey_id, payload, now),
        )
        conn.commit()


def load_context(journey_id: str) -> JourneyContext | None:
    with _connect() as conn:
        row = conn.execute(
            "SELECT context_json FROM journey_sessions WHERE journey_id = ?",
            (journey_id,),
        ).fetchone()
    if not row:
        return None
    return JourneyContext.model_validate_json(row["context_json"])


def delete_context(journey_id: str) -> None:
    with _connect() as conn:
        conn.execute("DELETE FROM journey_sessions WHERE journey_id = ?", (journey_id,))
        conn.commit()


def cookie_settings(*, secure: bool | None = None) -> dict[str, object]:
    if secure is None:
        secure = os.environ.get("PB_COOKIE_SECURE", "").lower() in {"1", "true", "yes"}
    return {
        "key": COOKIE_NAME,
        "httponly": True,
        "samesite": "lax",
        "max_age": COOKIE_MAX_AGE,
        "secure": secure,
    }

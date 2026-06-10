"""Session persistence — SQLite write-through survives Streamlit RAM purge."""

from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from engine.models import JourneyContext

DEFAULT_DB = Path(__file__).resolve().parent.parent / "data" / "rollover_sessions.db"

_SCHEMA = """
CREATE TABLE IF NOT EXISTS sessions (
    journey_id  TEXT PRIMARY KEY,
    state       TEXT NOT NULL,
    provider    TEXT,
    channel     TEXT,
    surface     TEXT NOT NULL DEFAULT 'customer',
    context_json TEXT NOT NULL,
    updated_at  TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_sessions_updated ON sessions (updated_at DESC);
"""


class SessionStore:
    def __init__(self, db_path: Path | str = DEFAULT_DB):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with self._conn() as conn:
            conn.executescript(_SCHEMA)

    def _conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, timeout=5)
        conn.execute("PRAGMA journal_mode=WAL")
        return conn

    def save(self, ctx: JourneyContext, surface: str = "customer") -> None:
        with self._conn() as conn:
            conn.execute(
                """INSERT INTO sessions
                   (journey_id, state, provider, channel, surface, context_json, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?)
                   ON CONFLICT(journey_id) DO UPDATE SET
                     state=excluded.state, provider=excluded.provider,
                     channel=excluded.channel, surface=excluded.surface,
                     context_json=excluded.context_json, updated_at=excluded.updated_at""",
                (
                    ctx.journey_id,
                    ctx.state.value if hasattr(ctx.state, "value") else str(ctx.state),
                    ctx.provider,
                    ctx.channel.value if ctx.channel else None,
                    surface,
                    ctx.model_dump_json(),
                    datetime.now(timezone.utc).isoformat(),
                ),
            )

    def load(self, journey_id: str) -> Optional[JourneyContext]:
        with self._conn() as conn:
            row = conn.execute(
                "SELECT context_json FROM sessions WHERE journey_id = ?", (journey_id,)
            ).fetchone()
        return JourneyContext.model_validate_json(row[0]) if row else None

    def recent(self, limit: int = 8) -> list[dict]:
        with self._conn() as conn:
            rows = conn.execute(
                """SELECT journey_id, state, provider, channel, updated_at
                   FROM sessions ORDER BY updated_at DESC LIMIT ?""",
                (limit,),
            ).fetchall()
        return [
            {
                "journey_id": r[0],
                "state": r[1],
                "provider": r[2],
                "channel": r[3],
                "updated_at": r[4],
            }
            for r in rows
        ]

    def delete(self, journey_id: str) -> None:
        with self._conn() as conn:
            conn.execute("DELETE FROM sessions WHERE journey_id = ?", (journey_id,))

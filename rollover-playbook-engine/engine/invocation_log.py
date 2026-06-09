from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path


def _log_path() -> Path:
    env = os.environ.get("ROLLOVER_LOG_PATH")
    if env:
        return Path(env)
    return Path(__file__).resolve().parent.parent / "data" / "invocations.jsonl"


def log_invocation(
    provider: str,
    funnel_stage: str,
    path_taken: str,
    outcome: str,
) -> None:
    """Append one JSON line per recommendation (no PII)."""
    path = _log_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    record = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "provider": provider,
        "funnel_stage": funnel_stage,
        "path_taken": path_taken,
        "outcome": outcome,
    }
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record) + "\n")

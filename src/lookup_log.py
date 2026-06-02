from datetime import datetime, timezone
import os
from pathlib import Path
from typing import Sequence

import pandas as pd

from src.matcher import DATA_DIR, MatchResult, canonicalize_employer


LOG_COLUMNS = [
    "timestamp_utc",
    "input_name",
    "normalized_input",
    "found",
    "candidate_count",
    "matched_employer",
    "recordkeeper",
    "confidence",
    "confidence_label",
    "match_method",
    "match_reason",
    "plan_name",
    "plan_year",
    "participants",
    "ein",
    "error",
]


def _log_path(log_path: Path | None = None) -> Path:
    if log_path is not None:
        return log_path

    configured_path = os.environ.get("LOOKUP_LOG_PATH")
    if configured_path:
        return Path(configured_path).expanduser()
    return DATA_DIR / "lookup_attempts_master.csv"


def append_lookup_attempt(
    input_name: str,
    results: Sequence[MatchResult],
    error: str | None = None,
    log_path: Path | None = None,
) -> dict[str, object]:
    """Append one user-entered lookup attempt to the inspection log."""
    top_result = results[0] if results else None
    row = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "input_name": input_name.strip(),
        "normalized_input": canonicalize_employer(input_name),
        "found": bool(top_result),
        "candidate_count": len(results),
        "matched_employer": top_result.matched_employer_name if top_result else "",
        "recordkeeper": top_result.recordkeeper if top_result else "",
        "confidence": round(top_result.confidence, 4) if top_result else "",
        "confidence_label": top_result.confidence_label if top_result else "",
        "match_method": top_result.match_method if top_result else "no_match",
        "match_reason": (
            top_result.match_reason
            if top_result
            else "No candidate cleared the matcher's exact, boundary, spacing, or fuzzy thresholds."
        ),
        "plan_name": top_result.plan_name if top_result else "",
        "plan_year": top_result.plan_year if top_result else "",
        "participants": top_result.plan_participants if top_result else "",
        "ein": top_result.ein if top_result else "",
        "error": error or "",
    }

    path = _log_path(log_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    write_header = not path.exists() or path.stat().st_size == 0
    pd.DataFrame([row], columns=LOG_COLUMNS).to_csv(
        path,
        mode="a",
        header=write_header,
        index=False,
    )
    return row


def read_lookup_attempts(log_path: Path | None = None) -> pd.DataFrame:
    """Read the persisted lookup attempts, newest first."""
    path = _log_path(log_path)
    if not path.exists() or path.stat().st_size == 0:
        return pd.DataFrame(columns=LOG_COLUMNS)

    attempts = pd.read_csv(path, dtype=str, keep_default_na=False)
    for column in LOG_COLUMNS:
        if column not in attempts.columns:
            attempts[column] = ""
    return attempts[LOG_COLUMNS].iloc[::-1].reset_index(drop=True)

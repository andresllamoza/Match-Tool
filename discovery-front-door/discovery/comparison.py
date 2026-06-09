from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path

from .models import ComparisonEvent, DiscoveryResult


def comparison_from_discovery(result: DiscoveryResult) -> ComparisonEvent:
    m = result.matcher_result.provider
    a = result.advizorpro_result.provider
    return ComparisonEvent(
        employer_query=result.employer_query,
        matcher_provider=m,
        advizorpro_provider=a,
        agreement=bool(m and a and m == a),
    )


def _log_path() -> Path:
    env = os.environ.get("DISCOVERY_LOG_PATH")
    if env:
        return Path(env)
    return Path(__file__).resolve().parent.parent / "data" / "comparisons.jsonl"


def log_comparison(event: ComparisonEvent) -> None:
    path = _log_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    record = {
        "ts": datetime.now(timezone.utc).isoformat(),
        **event.model_dump(),
    }
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record) + "\n")


def summarize(events: list[ComparisonEvent]) -> dict:
    n = len(events)
    if n == 0:
        return {"n": 0}
    agreements = sum(1 for e in events if e.agreement)
    matcher_hits = sum(1 for e in events if e.matcher_provider)
    adv_hits = sum(1 for e in events if e.advizorpro_provider)
    matcher_only = sum(
        1 for e in events if e.matcher_provider and not e.advizorpro_provider
    )
    adv_only = sum(
        1 for e in events if e.advizorpro_provider and not e.matcher_provider
    )
    return {
        "n": n,
        "agreement_rate": round(agreements / n, 2),
        "matcher_coverage": round(matcher_hits / n, 2),
        "advizorpro_coverage": round(adv_hits / n, 2),
        "matcher_only": matcher_only,
        "advizorpro_only": adv_only,
    }

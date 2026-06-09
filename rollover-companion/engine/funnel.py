from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path

from pydantic import BaseModel, Field

from .events import _journey_log_path


class StallPoint(BaseModel):
    state: str
    provider: str | None
    channel: str | None
    count: int


class FunnelSummary(BaseModel):
    total_journeys: int = 0
    by_state: dict[str, int] = Field(default_factory=dict)
    by_provider: dict[str, int] = Field(default_factory=dict)
    by_channel: dict[str, int] = Field(default_factory=dict)
    stall_points: list[StallPoint] = Field(default_factory=list)
    completion_rate: float = 0.0
    provider_not_covered_count: int = 0
    handoff_offered_count: int = 0
    handoff_taken_count: int = 0


STALL_STATES = {"stuck", "escalated", "access_blocked"}


def load_funnel_summary(log_path: Path | None = None) -> FunnelSummary:
    path = log_path or _journey_log_path()
    if not path.exists():
        return FunnelSummary()

    journeys: set[str] = set()
    by_state: Counter[str] = Counter()
    by_provider: Counter[str] = Counter()
    by_channel: Counter[str] = Counter()
    stall_counter: Counter[tuple[str, str | None, str | None]] = Counter()
    completed_journeys: set[str] = set()
    provider_not_covered_count = 0
    handoff_offered_count = 0
    handoff_taken_count = 0

    with path.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            record = json.loads(line)
            jid = record.get("metadata", {}).get("journey_id")
            state = record.get("state", "unknown")
            action = record.get("action", "")
            provider = record.get("provider")
            channel = record.get("channel")
            by_state[state] += 1
            if state == "provider_not_covered":
                provider_not_covered_count += 1
            if action == "handoff_offered":
                handoff_offered_count += 1
            if action == "handoff_taken":
                handoff_taken_count += 1
            if provider:
                by_provider[provider] += 1
            if channel:
                by_channel[channel] += 1
            if jid:
                journeys.add(jid)
                if state == "complete":
                    completed_journeys.add(jid)
            if state in STALL_STATES:
                stall_counter[(state, provider, channel)] += 1

    total = len(journeys)
    completion = len(completed_journeys) / total if total else 0.0
    stall_points = [
        StallPoint(state=s, provider=p, channel=c, count=n)
        for (s, p, c), n in stall_counter.most_common()
    ]

    return FunnelSummary(
        total_journeys=total,
        by_state=dict(by_state),
        by_provider=dict(by_provider),
        by_channel=dict(by_channel),
        stall_points=stall_points,
        completion_rate=round(completion, 3),
        provider_not_covered_count=provider_not_covered_count,
        handoff_offered_count=handoff_offered_count,
        handoff_taken_count=handoff_taken_count,
    )

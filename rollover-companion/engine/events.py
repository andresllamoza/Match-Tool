from __future__ import annotations

import json
import os
from pathlib import Path

from .models import (
    ComparisonEvent,
    ConfidenceTier,
    JourneyChannel,
    JourneyEvent,
    JourneyState,
    utc_now_iso,
)


def _journey_log_path() -> Path:
    env = os.environ.get("JOURNEY_LOG_PATH")
    if env:
        return Path(env)
    return Path(__file__).resolve().parent.parent / "data" / "journey_events.jsonl"


def _comparison_log_path() -> Path:
    env = os.environ.get("COMPARISON_LOG_PATH")
    if env:
        return Path(env)
    return Path(__file__).resolve().parent.parent / "data" / "comparison_events.jsonl"


class EventLogger:
    def __init__(
        self,
        journey_path: Path | None = None,
        comparison_path: Path | None = None,
    ):
        self.journey_path = journey_path or _journey_log_path()
        self.comparison_path = comparison_path or _comparison_log_path()

    def log_journey(
        self,
        state: JourneyState,
        provider: str | None,
        channel: JourneyChannel | None,
        action: str,
        outcome: str,
        metadata: dict | None = None,
        journey_id: str | None = None,
    ) -> JourneyEvent:
        event = JourneyEvent(
            timestamp=utc_now_iso(),
            state=state,
            provider=provider,
            channel=channel,
            action=action,
            outcome=outcome,
            metadata={**(metadata or {}), **({"journey_id": journey_id} if journey_id else {})},
        )
        self._append(self.journey_path, event.model_dump())
        return event

    def log_comparison(
        self,
        input_query: str,
        matcher_result: str | None,
        advizorpro_result: str | None,
        agreement: bool,
        confidence_tier: ConfidenceTier,
    ) -> ComparisonEvent:
        event = ComparisonEvent(
            timestamp=utc_now_iso(),
            input=input_query,
            matcher_result=matcher_result,
            advizorpro_result=advizorpro_result,
            agreement=agreement,
            confidence_tier=confidence_tier,
        )
        self._append(self.comparison_path, event.model_dump())
        return event

    @staticmethod
    def _append(path: Path, record: dict) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record) + "\n")

from __future__ import annotations

from adapters.factory import build_journey_engine
from engine.models import JourneyContext

_engine = build_journey_engine()
_sessions: dict[str, JourneyContext] = {}


def get_engine() -> JourneyEngine:
    return _engine


def create_session() -> JourneyContext:
    ctx = _engine.start()
    _sessions[ctx.journey_id] = ctx
    return ctx


def get_session(journey_id: str) -> JourneyContext:
    if journey_id not in _sessions:
        raise KeyError(f"Unknown journey: {journey_id}")
    return _sessions[journey_id]


def save_session(ctx: JourneyContext) -> None:
    _sessions[ctx.journey_id] = ctx

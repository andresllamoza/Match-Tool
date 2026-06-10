from __future__ import annotations

from engine.journey import JourneyEngine
from engine.models import JourneyContext

from api.persistence import delete_context, init_db, load_context, save_context

_engine = JourneyEngine()
_sessions: dict[str, JourneyContext] = {}

init_db()


def get_engine() -> JourneyEngine:
    return _engine


def create_session() -> JourneyContext:
    ctx = _engine.start()
    _sessions[ctx.journey_id] = ctx
    save_context(ctx)
    return ctx


def get_session(journey_id: str) -> JourneyContext:
    if journey_id in _sessions:
        return _sessions[journey_id]
    ctx = load_context(journey_id)
    if ctx is None:
        raise KeyError(f"Unknown journey: {journey_id}")
    _sessions[journey_id] = ctx
    return ctx


def save_session(ctx: JourneyContext) -> None:
    _sessions[ctx.journey_id] = ctx
    save_context(ctx)


def clear_session(journey_id: str) -> None:
    _sessions.pop(journey_id, None)
    delete_context(journey_id)

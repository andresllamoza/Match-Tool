"""Shared journey action dispatch for JSON and HTMX routes."""

from __future__ import annotations

from typing import Any

from fastapi import HTTPException

from api.sessions import get_engine, save_session
from engine.assistant import ScopedAssistant
from engine.journey import InvalidTransitionError
from engine.models import JourneyChannel, JourneyContext, JourneyScreen

_assistant = ScopedAssistant(get_engine().knowledge)


def dispatch_action(ctx: JourneyContext, body: dict[str, Any]) -> JourneyScreen | dict[str, Any]:
    """Apply a journey action. Returns JourneyScreen, or dict for assistant responses."""
    engine = get_engine()
    action_type = body.get("type")
    if not action_type:
        raise HTTPException(400, "type required")

    try:
        if action_type == "lookup":
            employer = body.get("employer")
            if not employer:
                raise HTTPException(400, "employer required")
            screen = engine.lookup_employer(ctx, employer)
        elif action_type == "provider_direct":
            provider = body.get("provider")
            if not provider:
                raise HTTPException(400, "provider required")
            screen = engine.set_provider_direct(ctx, provider)
        elif action_type == "disambiguate":
            answer = body.get("answer")
            if not answer:
                raise HTTPException(400, "answer required")
            screen = engine.disambiguate(ctx, answer)
        elif action_type == "access":
            if body.get("can_login") is None:
                raise HTTPException(400, "can_login required")
            screen = engine.submit_access(ctx, bool(body["can_login"]))
        elif action_type == "access_recovered":
            screen = engine.submit_access_recovered(ctx)
        elif action_type == "tax_type":
            tax_type = body.get("tax_type")
            if not tax_type:
                raise HTTPException(400, "tax_type required")
            screen = engine.submit_tax_type(ctx, tax_type)
        elif action_type == "channel":
            channel = body.get("channel")
            if not channel:
                raise HTTPException(400, "channel required")
            screen = engine.choose_channel(ctx, JourneyChannel(channel))
        elif action_type == "step":
            outcome = body.get("outcome")
            if not outcome:
                raise HTTPException(400, "outcome required")
            screen = engine.advance_step(ctx, outcome)
        elif action_type == "confirm_in_flight":
            screen = engine.confirm_in_flight(ctx)
        elif action_type == "mark_complete":
            screen = engine.mark_complete(ctx)
        elif action_type == "escalate":
            screen = engine.escalate(ctx, body.get("reason") or "user_requested")
        elif action_type == "handoff":
            screen = engine.take_handoff(ctx, body.get("reason") or "provider_not_covered")
        elif action_type == "resume":
            screen = engine.resume_from_stuck(ctx)
        elif action_type == "go_back":
            screen = engine.go_back(ctx)
        elif action_type == "ask":
            question = body.get("question")
            if not question:
                raise HTTPException(400, "question required")
            result = _assistant.answer(
                question,
                ctx.state,
                ctx.provider or ctx.uncovered_provider,
            )
            save_session(ctx)
            return {"assistant": result, "screen": engine.render(ctx)}
        else:
            raise HTTPException(400, "unknown action type")
    except InvalidTransitionError as exc:
        raise HTTPException(400, str(exc)) from exc

    save_session(ctx)
    return screen

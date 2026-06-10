"""Template context helpers for HTMX surfaces."""

from __future__ import annotations

from typing import Any, Literal

from api.journey_response import JourneyResponse, wrap_journey
from api.sessions import get_engine, get_session
from engine.models import JourneyContext, JourneyScreen, JourneyState

DecisionMode = Literal[
    "employer",
    "provider_pick",
    "disambiguation",
    "access",
    "tax",
    "channel",
    "channel_step",
    "stuck",
    "track",
    "confirm",
    "done",
]

SurfaceMode = Literal["customer", "agent", "embed"]


def resolve_decision_mode(
    data: JourneyResponse,
    *,
    show_provider_picker: bool = False,
) -> DecisionMode:
    screen = data.screen
    enrichment = data.enrichment

    in_channel = screen.state in {
        JourneyState.ONLINE_IN_PROGRESS,
        JourneyState.PHONE_IN_PROGRESS,
        JourneyState.FORMS_IN_PROGRESS,
    }

    if screen.state in {JourneyState.COMPLETE, JourneyState.ESCALATED}:
        return "done"
    if enrichment.requires_tax_selection:
        return "tax"
    if show_provider_picker:
        return "provider_pick"
    if screen.disambiguation_question and screen.disambiguation_options:
        return "disambiguation"
    if screen.state == JourneyState.PROVIDER_UNKNOWN:
        return "employer"
    if screen.state in {JourneyState.PROVIDER_IDENTIFIED, JourneyState.PROVIDER_NOT_COVERED}:
        return "access"
    if screen.state == JourneyState.ACCESS_RECOVERED and any(
        "phone" in a.lower() or "form" in a.lower() for a in screen.secondary_actions
    ):
        return "channel"
    if in_channel:
        return "channel_step"
    if screen.state == JourneyState.STUCK:
        return "stuck"
    if screen.state in {JourneyState.INITIATED, JourneyState.IN_FLIGHT}:
        return "track"
    if screen.state in {JourneyState.ACCESS_BLOCKED, JourneyState.ACCESS_RECOVERED}:
        return "confirm"
    return "confirm"


def build_view_context(
    ctx: JourneyContext,
    screen: JourneyScreen,
    *,
    mode: SurfaceMode = "customer",
    include_intel: bool = False,
    welcome_back: bool = False,
    show_provider_picker: bool = False,
    error: str | None = None,
    read_only: bool = False,
    embed_theme: str = "default",
) -> dict[str, Any]:
    data = wrap_journey(ctx, screen, include_intel=include_intel)
    decision = resolve_decision_mode(data, show_provider_picker=show_provider_picker)
    provider_name = ctx.provider or ctx.uncovered_provider or "your provider"
    step_number = max(data.step_index + 1, 1)

    return {
        "data": data,
        "ctx": ctx,
        "screen": screen,
        "enrichment": data.enrichment,
        "mode": mode,
        "decision": decision,
        "welcome_back": welcome_back,
        "show_provider_picker": show_provider_picker,
        "error": error,
        "read_only": read_only,
        "embed_theme": embed_theme,
        "providers": get_engine().knowledge.list_providers(),
        "provider_name": provider_name,
        "step_number": step_number,
        "journey_id": ctx.journey_id,
    }


def load_journey_response(
    journey_id: str,
    *,
    include_intel: bool = False,
) -> JourneyResponse:
    ctx = get_session(journey_id)
    screen = get_engine().render(ctx)
    return wrap_journey(ctx, screen, include_intel=include_intel)

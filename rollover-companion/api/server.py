from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Literal, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from api.sessions import create_session, get_engine, get_session, save_session  # noqa: E402
from engine.assistant import ScopedAssistant  # noqa: E402
from engine.funnel import load_funnel_summary  # noqa: E402
from engine.enrichment import build_enrichment  # noqa: E402
from engine.journey import InvalidTransitionError  # noqa: E402
from engine.models import (  # noqa: E402
    JourneyChannel,
    JourneyContext,
    JourneyScreen,
    JourneyState,
    ScreenEnrichment,
)

app = FastAPI(title="Rollover Companion API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

_assistant = ScopedAssistant(get_engine().knowledge)


class ActionRequest(BaseModel):
    type: Literal[
        "lookup",
        "provider_direct",
        "disambiguate",
        "access",
        "access_recovered",
        "channel",
        "step",
        "confirm_in_flight",
        "mark_complete",
        "escalate",
        "resume",
        "ask",
        "tax_type",
    ]
    tax_type: Optional[Literal["pre_tax", "roth", "both", "pre_tax_to_roth"]] = None
    employer: Optional[str] = None
    provider: Optional[str] = None
    answer: Optional[str] = None
    can_login: Optional[bool] = None
    channel: Optional[Literal["online", "phone", "forms"]] = None
    outcome: Optional[Literal["done", "stuck"]] = None
    reason: Optional[str] = None
    question: Optional[str] = None


class JourneyResponse(BaseModel):
    context: JourneyContext
    screen: JourneyScreen
    step_index: int = 0
    total_steps: int = 0
    enrichment: ScreenEnrichment = Field(default_factory=ScreenEnrichment)
    provider_intel: dict[str, Any] = Field(default_factory=dict)


def _enrich_intel(ctx: JourneyContext, screen: JourneyScreen) -> dict[str, Any]:
    if not ctx.provider:
        return {}
    engine = get_engine()
    pb = engine.knowledge.get(ctx.provider)
    intel: dict[str, Any] = {
        "mechanism": pb.mechanism.value,
        "check_destination": pb.check_destination,
        "forward_step_required": pb.forward_step_required,
        "portal": pb.portal,
        "flags_available": engine.knowledge.available_flags(ctx.provider),
        "rep_questions": [q.model_dump() for q in pb.call_script.rep_questions],
        "call_phone": pb.call_script.phone,
        "call_intro": pb.call_script.intro,
    }
    return intel


def _step_totals(ctx: JourneyContext) -> tuple[int, int]:
    if not ctx.provider:
        return ctx.step_index, 0
    pb = get_engine().knowledge.get(ctx.provider)
    if ctx.state == JourneyState.ONLINE_IN_PROGRESS:
        return ctx.step_index, len(pb.steps)
    if ctx.state == JourneyState.PHONE_IN_PROGRESS:
        return ctx.step_index, len(pb.call_script.steps)
    if ctx.state == JourneyState.FORMS_IN_PROGRESS:
        return ctx.step_index, len(pb.form_guidance.fields)
    return ctx.step_index, 0


def _wrap(ctx: JourneyContext, screen: JourneyScreen, include_intel: bool = False) -> JourneyResponse:
    engine = get_engine()
    step_index, total_steps = _step_totals(ctx)
    return JourneyResponse(
        context=ctx,
        screen=screen,
        step_index=step_index,
        total_steps=total_steps,
        enrichment=build_enrichment(engine.knowledge, ctx, screen),
        provider_intel=_enrich_intel(ctx, screen) if include_intel else {},
    )


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/providers")
def list_providers():
    return {"providers": get_engine().knowledge.list_providers()}


@app.get("/api/funnel")
def funnel():
    return load_funnel_summary().model_dump()


@app.post("/api/journey/start", response_model=JourneyResponse)
def start_journey(agent: bool = False):
    ctx = create_session()
    screen = get_engine().render(ctx)
    return _wrap(ctx, screen, include_intel=agent)


@app.get("/api/journey/{journey_id}", response_model=JourneyResponse)
def get_journey(journey_id: str, agent: bool = False):
    try:
        ctx = get_session(journey_id)
    except KeyError:
        raise HTTPException(404, "Journey not found")
    screen = get_engine().render(ctx)
    return _wrap(ctx, screen, include_intel=agent)


@app.post("/api/journey/{journey_id}/action")
def journey_action(journey_id: str, body: ActionRequest, agent: bool = False):
    try:
        ctx = get_session(journey_id)
    except KeyError:
        raise HTTPException(404, "Journey not found")

    engine = get_engine()
    try:
        if body.type == "lookup":
            if not body.employer:
                raise HTTPException(400, "employer required")
            screen = engine.lookup_employer(ctx, body.employer)
        elif body.type == "provider_direct":
            if not body.provider:
                raise HTTPException(400, "provider required")
            screen = engine.set_provider_direct(ctx, body.provider)
        elif body.type == "disambiguate":
            if not body.answer:
                raise HTTPException(400, "answer required")
            screen = engine.disambiguate(ctx, body.answer)
        elif body.type == "access":
            if body.can_login is None:
                raise HTTPException(400, "can_login required")
            screen = engine.submit_access(ctx, body.can_login)
        elif body.type == "access_recovered":
            screen = engine.submit_access_recovered(ctx)
        elif body.type == "tax_type":
            if not body.tax_type:
                raise HTTPException(400, "tax_type required")
            screen = engine.submit_tax_type(ctx, body.tax_type)
        elif body.type == "channel":
            if not body.channel:
                raise HTTPException(400, "channel required")
            screen = engine.choose_channel(ctx, JourneyChannel(body.channel))
        elif body.type == "step":
            if not body.outcome:
                raise HTTPException(400, "outcome required")
            screen = engine.advance_step(ctx, body.outcome)
        elif body.type == "confirm_in_flight":
            screen = engine.confirm_in_flight(ctx)
        elif body.type == "mark_complete":
            screen = engine.mark_complete(ctx)
        elif body.type == "escalate":
            screen = engine.escalate(ctx, body.reason or "user_requested")
        elif body.type == "resume":
            screen = engine.resume_from_stuck(ctx)
        elif body.type == "ask":
            if not body.question:
                raise HTTPException(400, "question required")
            result = _assistant.answer(body.question, ctx.state, ctx.provider)
            save_session(ctx)
            return {"assistant": result, **_wrap(ctx, engine.render(ctx), include_intel=agent).model_dump()}
        else:
            raise HTTPException(400, "unknown action type")
    except InvalidTransitionError as exc:
        raise HTTPException(400, str(exc))

    save_session(ctx)
    return _wrap(ctx, screen, include_intel=agent)

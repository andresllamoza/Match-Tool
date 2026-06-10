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

from api.journey_dispatch import dispatch_action  # noqa: E402
from api.journey_response import JourneyResponse, wrap_journey  # noqa: E402
from api.sessions import create_session, get_engine, get_session, save_session  # noqa: E402
from engine.funnel import load_funnel_summary  # noqa: E402
from engine.models import JourneyContext, JourneyScreen  # noqa: E402

app = FastAPI(title="Rollover Companion API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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
        "go_back",
        "ask",
        "tax_type",
        "handoff",
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


def _wrap(ctx: JourneyContext, screen: JourneyScreen, include_intel: bool = False) -> JourneyResponse:
    return wrap_journey(ctx, screen, include_intel=include_intel)


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

    result = dispatch_action(ctx, body.model_dump(exclude_none=True))
    if isinstance(result, dict):
        return {"assistant": result["assistant"], **_wrap(ctx, result["screen"], include_intel=agent).model_dump()}
    return _wrap(ctx, result, include_intel=agent)


from api.html_routes import router as html_router  # noqa: E402

app.include_router(html_router)

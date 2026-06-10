"""Thin bridge from Streamlit → rollover-companion JourneyEngine (same as the API)."""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any

import streamlit as st

_COMPANION = Path(__file__).resolve().parents[2] / "rollover-companion"
if not _COMPANION.exists():
    raise FileNotFoundError(f"rollover-companion not found at {_COMPANION}")
if str(_COMPANION) not in sys.path:
    sys.path.insert(0, str(_COMPANION))

from engine.enrichment import build_enrichment
from engine.journey import InvalidTransitionError, JourneyEngine
from engine.models import (
    JourneyChannel,
    JourneyContext,
    JourneyScreen,
    JourneyState,
    ScreenEnrichment,
)


def _build_engine() -> JourneyEngine:
    from adapters.advizorpro import AdvizorProAdapter
    from adapters.employer_index import EmployerIndexAdapter
    from adapters.hybrid5500 import Hybrid5500Adapter
    from adapters.matcher5500 import Local5500Adapter, master_cache_available
    from engine.knowledge import KnowledgeBase
    from engine.lookup import LookupService

    # Fast path for Streamlit Cloud: synthetic → bundled index (~6 MB, no DOL download).
    # Full 115 MB matcher only when recordkeeper_master.csv exists locally.
    repo = _COMPANION.parent
    adapters: list = [Local5500Adapter.from_synthetic()]
    index = EmployerIndexAdapter.from_csv(repo / "data" / "employer_rk_index.csv")
    if index is not None:
        adapters.append(index)
    if master_cache_available(repo):
        try:
            adapters.append(Local5500Adapter.from_matcher(repo))
        except Exception:
            pass
    matcher = Hybrid5500Adapter(adapters) if len(adapters) > 1 else adapters[0]

    knowledge = KnowledgeBase.from_dir(_COMPANION / "rollover-knowledge-layer")
    lookup = LookupService(knowledge, matcher, AdvizorProAdapter())
    return JourneyEngine(knowledge=knowledge, lookup_service=lookup)


@st.cache_resource
def get_engine() -> JourneyEngine:
    return _build_engine()


def load_context() -> JourneyContext:
    if "journey_ctx" not in st.session_state:
        engine = get_engine()
        ctx = engine.start()
        st.session_state.journey_ctx = ctx.model_dump(mode="json")
    return JourneyContext.model_validate(st.session_state.journey_ctx)


def save_context(ctx: JourneyContext) -> None:
    st.session_state.journey_ctx = ctx.model_dump(mode="json")


def step_totals(ctx: JourneyContext) -> tuple[int, int]:
    engine = get_engine()
    if not ctx.provider and not ctx.uncovered_provider:
        return ctx.step_index, 0
    pb = engine.knowledge.playbook_for(ctx)
    if ctx.state == JourneyState.ONLINE_IN_PROGRESS:
        return ctx.step_index, len(pb.steps)
    if ctx.state == JourneyState.PHONE_IN_PROGRESS:
        return ctx.step_index, len(pb.call_script.steps)
    if ctx.state == JourneyState.FORMS_IN_PROGRESS:
        return ctx.step_index, len(pb.form_guidance.fields)
    return ctx.step_index, 0


class JourneyView:
    def __init__(self, ctx: JourneyContext, screen: JourneyScreen, enrichment: ScreenEnrichment):
        self.ctx = ctx
        self.screen = screen
        self.enrichment = enrichment
        self.step_index, self.total_steps = step_totals(ctx)


def current_view() -> JourneyView:
    engine = get_engine()
    ctx = load_context()
    screen = engine.render(ctx)
    enrichment = build_enrichment(engine.knowledge, ctx, screen)
    return JourneyView(ctx, screen, enrichment)


def apply_action(action: dict[str, Any]) -> JourneyView | str:
    engine = get_engine()
    ctx = load_context()
    kind = action.get("type")

    try:
        if kind == "lookup":
            screen = engine.lookup_employer(ctx, action["employer"])
        elif kind == "provider_direct":
            screen = engine.set_provider_direct(ctx, action["provider"])
        elif kind == "disambiguate":
            screen = engine.disambiguate(ctx, action["answer"])
        elif kind == "access":
            screen = engine.submit_access(ctx, action["can_login"])
        elif kind == "access_recovered":
            screen = engine.submit_access_recovered(ctx)
        elif kind == "tax_type":
            screen = engine.submit_tax_type(ctx, action["tax_type"])
        elif kind == "channel":
            screen = engine.choose_channel(ctx, JourneyChannel(action["channel"]))
        elif kind == "step":
            screen = engine.advance_step(ctx, action["outcome"])
        elif kind == "confirm_in_flight":
            screen = engine.confirm_in_flight(ctx)
        elif kind == "mark_complete":
            screen = engine.mark_complete(ctx)
        elif kind == "escalate":
            screen = engine.escalate(ctx, action.get("reason", "user_requested"))
        elif kind == "handoff":
            screen = engine.take_handoff(ctx, action.get("reason", "provider_not_covered"))
        elif kind == "resume":
            screen = engine.resume_from_stuck(ctx)
        elif kind == "restart":
            ctx = engine.start()
            screen = engine.render(ctx)
        else:
            return f"Unknown action: {kind}"
    except InvalidTransitionError as exc:
        return str(exc)
    except Exception as exc:
        return f"Something went wrong. A BeeKeeper can help. ({exc})"

    save_context(ctx)
    enrichment = build_enrichment(engine.knowledge, ctx, screen)
    return JourneyView(ctx, screen, enrichment)


def list_providers() -> list[str]:
    return get_engine().knowledge.list_providers()

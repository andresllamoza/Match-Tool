"""Session gateway: engine → SQLite → URL query param → Streamlit rerun."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import streamlit as st

from api.journey_dispatch import dispatch_action
from api.journey_response import wrap_journey
from api.persistence import is_resumable, load_context, save_context
from engine.enrichment import build_enrichment
from engine.models import JourneyContext, JourneyScreen, JourneyState, ScreenEnrichment
from sandbox.boot import get_engine

QP_JOURNEY = "jid"
QP_FRESH = "fresh"


@dataclass
class JourneyView:
    ctx: JourneyContext
    screen: JourneyScreen
    enrichment: ScreenEnrichment
    step_index: int
    total_steps: int
    data: Any

    @property
    def provider_intel(self) -> dict:
        return wrap_journey(self.ctx, self.screen, include_intel=True).provider_intel


def _step_totals(ctx: JourneyContext) -> tuple[int, int]:
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


def _wrap_view(ctx: JourneyContext, screen: JourneyScreen) -> JourneyView:
    engine = get_engine()
    step_index, total_steps = _step_totals(ctx)
    enrichment = build_enrichment(engine.knowledge, ctx, screen)
    return JourneyView(
        ctx=ctx,
        screen=screen,
        enrichment=enrichment,
        step_index=step_index,
        total_steps=total_steps,
        data=wrap_journey(ctx, screen),
    )


def sync_url(ctx: JourneyContext) -> None:
    st.query_params[QP_JOURNEY] = ctx.journey_id
    if QP_FRESH in st.query_params:
        del st.query_params[QP_FRESH]


def clear_url() -> None:
    if QP_JOURNEY in st.query_params:
        del st.query_params[QP_JOURNEY]


def _persist(ctx: JourneyContext) -> None:
    save_context(ctx)
    st.session_state.journey_ctx = ctx.model_dump(mode="json")
    sync_url(ctx)


def load_ctx(*, fresh: bool = False) -> tuple[JourneyContext, bool]:
    """Return (context, welcome_back)."""
    if fresh or st.query_params.get(QP_FRESH) == "1":
        engine = get_engine()
        ctx = engine.start()
        _persist(ctx)
        st.session_state.name_captured = False
        st.session_state.show_provider_picker = False
        return ctx, False

    jid = st.query_params.get(QP_JOURNEY)
    if jid:
        ctx = load_context(jid)
        if ctx is not None:
            st.session_state.journey_ctx = ctx.model_dump(mode="json")
            welcome = is_resumable(ctx) and st.session_state.get("_welcome_shown") is not True
            if welcome:
                st.session_state._welcome_shown = True
            return ctx, welcome

    if "journey_ctx" in st.session_state:
        ctx = JourneyContext.model_validate(st.session_state.journey_ctx)
        _persist(ctx)
        return ctx, False

    engine = get_engine()
    ctx = engine.start()
    _persist(ctx)
    st.session_state.name_captured = False
    return ctx, False


def current_view() -> JourneyView:
    ctx = load_ctx()[0]
    screen = get_engine().render(ctx)
    return _wrap_view(ctx, screen)


def act(action: dict[str, Any]) -> JourneyView | str:
    """Single gateway for all transitions."""
    engine = get_engine()
    kind = action.get("type")

    if kind == "restart":
        ctx = engine.start()
        screen = engine.render(ctx)
        _persist(ctx)
        st.session_state.name_captured = False
        st.session_state.show_provider_picker = False
        st.session_state.pop("ui_error", None)
        st.session_state._welcome_shown = False
        return _wrap_view(ctx, screen)

    if kind == "set_name":
        ctx = JourneyContext.model_validate(st.session_state.journey_ctx)
        ctx.customer_first_name = (action.get("first") or "").strip()
        ctx.customer_last_name = (action.get("last") or "").strip()
        screen = engine.render(ctx)
        _persist(ctx)
        st.session_state.name_captured = True
        return _wrap_view(ctx, screen)

    ctx = JourneyContext.model_validate(st.session_state.journey_ctx)
    result = dispatch_action(ctx, action)
    if isinstance(result, dict):
        screen = result["screen"]
    else:
        screen = result
    _persist(ctx)
    st.session_state.pop("ui_error", None)
    return _wrap_view(ctx, screen)


def needs_name_capture(view: JourneyView) -> bool:
    if st.session_state.get("name_captured"):
        return False
    if view.ctx.state != JourneyState.ACCESS_RECOVERED:
        return False
    if view.enrichment.requires_tax_selection:
        return True
    return view.ctx.tax_fund_type is None and not view.ctx.customer_first_name

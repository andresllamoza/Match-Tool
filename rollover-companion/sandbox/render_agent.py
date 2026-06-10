"""Column 2 — BeeKeeper back-office mirror (read-only)."""

from __future__ import annotations

import streamlit as st

from engine.models import JourneyState
from sandbox.state import JourneyView
from sandbox.ui.channel import agent_custodian_note, call_script_card

IN_CHANNEL = {
    JourneyState.ONLINE_IN_PROGRESS,
    JourneyState.PHONE_IN_PROGRESS,
    JourneyState.FORMS_IN_PROGRESS,
}


def render_agent(view: JourneyView) -> None:
    intel = view.provider_intel
    screen = view.screen
    en = view.enrichment

    status = intel.get("provider_status", "PENDING")
    st.markdown(
        f'<div class="pb-agent-meta"><p class="pb-agent-meta-kicker">Provider status</p>'
        f"<p><strong>{status}</strong></p></div>",
        unsafe_allow_html=True,
    )

    if intel.get("escalation_triggers"):
        triggers = ", ".join(intel["escalation_triggers"][:4])
        st.markdown(
            f'<div class="pb-agent-meta"><p class="pb-agent-meta-kicker">Escalation triggers</p>'
            f"<p>{triggers}</p></div>",
            unsafe_allow_html=True,
        )

    if intel.get("call_phone"):
        st.markdown(
            f'<div class="pb-agent-meta"><p class="pb-agent-meta-kicker">Call</p>'
            f"<p><strong>{intel['call_phone']}</strong></p></div>",
            unsafe_allow_html=True,
        )

    if intel.get("call_intro"):
        st.markdown(
            call_script_card("phone", intel["call_intro"]),
            unsafe_allow_html=True,
        )

    if screen.next_beekeeper_script:
        st.markdown(
            f'<div class="pb-agent-meta"><p class="pb-agent-meta-kicker">Say next</p>'
            f"<p>{screen.next_beekeeper_script}</p></div>",
            unsafe_allow_html=True,
        )

    if en.check_destination:
        st.markdown(
            agent_custodian_note(
                en.check_destination,
                forward_step_required=en.forward_step_required,
            ),
            unsafe_allow_html=True,
        )

    st.caption(f"State: `{screen.state.value}` · Step {view.step_index + 1}/{view.total_steps or '—'}")

    if screen.state in IN_CHANNEL and en.channel_context:
        ctx = en.channel_context
        st.markdown(
            f"**Active channel step**  \n{ctx.say_this[:200]}{'…' if len(ctx.say_this) > 200 else ''}"
        )
        if ctx.check_payable:
            st.markdown(f"**Payable line**  \n`{ctx.check_payable}`")

    if intel.get("knowledge_rules"):
        with st.expander("Knowledge rules"):
            for rule in intel["knowledge_rules"][:5]:
                st.markdown(f"**{rule['title']}**  \n{rule['body'][:160]}…")

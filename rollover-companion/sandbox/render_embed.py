"""Column 3 — embed developer playground (read-only preview)."""

from __future__ import annotations

import streamlit as st

from engine.models import JourneyState
from sandbox.state import JourneyView
from sandbox.ui.channel import call_script_card, channel_step_header, routing_security_card

IN_CHANNEL = {
    JourneyState.ONLINE_IN_PROGRESS,
    JourneyState.PHONE_IN_PROGRESS,
    JourneyState.FORMS_IN_PROGRESS,
}


def _preview_body(view: JourneyView) -> None:
    screen = view.screen
    en = view.enrichment
    if screen.state in IN_CHANNEL and en.channel_context:
        ctx = en.channel_context
        ch_label = {"online": "online", "phone": "by phone", "forms": "forms"}.get(ctx.channel, "")
        st.markdown(
            channel_step_header(view.step_index, view.total_steps, screen.provider or "", ch_label),
            unsafe_allow_html=True,
        )
        st.markdown(call_script_card(ctx.channel, ctx.say_this), unsafe_allow_html=True)
        payable = ctx.check_payable
        mail = ctx.mailing_address or en.mailing_address
        if payable or mail:
            st.markdown(routing_security_card(payable, mail), unsafe_allow_html=True)
    else:
        st.markdown(f'<p class="pb-headline">{screen.headline}</p>', unsafe_allow_html=True)
        if screen.body:
            st.markdown(f'<p class="pb-body">{screen.body}</p>', unsafe_allow_html=True)


def render_embed(view: JourneyView, *, theme: str) -> None:
    theme_choice = st.radio(
        "Embed theme",
        options=["default", "minimal", "dark"],
        horizontal=True,
        key="embed_theme_radio",
        label_visibility="collapsed",
    )

    jid = view.ctx.journey_id
    snippet = (
        f'<iframe\n'
        f'  src="https://your-host/embed?jid={jid}&theme={theme_choice}"\n'
        f'  title="Rollover Companion"\n'
        f'  style="width:100%;min-height:480px;border:none;border-radius:16px"\n'
        f"/>"
    )
    st.code(snippet, language="html")

    st.markdown("**Live preview** (read-only)")
    with st.container(border=True):
        _preview_body(view)

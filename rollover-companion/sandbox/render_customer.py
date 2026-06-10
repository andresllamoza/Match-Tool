"""Column 1 — interactive customer workflow."""

from __future__ import annotations

import streamlit as st

from engine.models import JourneyState
from sandbox.boot import list_providers
from sandbox.state import JourneyView, act
from sandbox.ui.channel import (
    call_script_card,
    channel_step_header,
    phone_routing_intro,
    routing_security_card,
)
from sandbox.ui.widgets import form_submit, primary_button, secondary_button

PHASES = [("find", "Find"), ("access", "Access"), ("rollover", "Roll over"), ("track", "Track")]
IN_CHANNEL = {
    JourneyState.ONLINE_IN_PROGRESS,
    JourneyState.PHONE_IN_PROGRESS,
    JourneyState.FORMS_IN_PROGRESS,
}


def _go(action: dict) -> None:
    result = act(action)
    if isinstance(result, str):
        st.session_state.ui_error = result
    else:
        st.session_state.pop("ui_error", None)
    st.rerun()


def _progress(phase: str) -> None:
    ids = [p[0] for p in PHASES]
    idx = ids.index(phase) if phase in ids else 0
    parts = ['<div class="pb-phase-bar">']
    for i, (_, label) in enumerate(PHASES):
        done = i < idx
        active = i == idx
        dot = "done" if done else ("active" if active else "")
        cls = "active" if active else ""
        parts.append(
            f'<div class="pb-phase {cls}"><div class="pb-phase-dot {dot}"></div>{label}</div>'
        )
    parts.append("</div>")
    st.markdown("".join(parts), unsafe_allow_html=True)


def _show_routing(view: JourneyView) -> None:
    ctx_data = view.enrichment.channel_context
    if not ctx_data:
        return
    payable = ctx_data.check_payable or ""
    mail = ctx_data.mailing_address or view.enrichment.mailing_address
    lower = (ctx_data.say_this or "").lower()
    show = payable or any(w in lower for w in ("check", "payable", "mail", "pensionbee"))
    if not show and view.ctx.state != JourneyState.INITIATED:
        return
    if view.ctx.state == JourneyState.INITIATED and not payable:
        payable = view.enrichment.channel_context.check_payable if view.enrichment.channel_context else ""
    panel = ['<div class="pb-routing-panel">']
    if ctx_data.channel == "phone":
        panel.append(phone_routing_intro())
    security = routing_security_card(payable or None, mail or None)
    if security:
        panel.append(security)
    panel.append("</div>")
    if security:
        st.markdown("".join(panel), unsafe_allow_html=True)


def render_customer(view: JourneyView, *, welcome_back: bool = False, read_only: bool = False) -> None:
    screen = view.screen
    en = view.enrichment

    if welcome_back:
        provider = view.ctx.provider or view.ctx.uncovered_provider or "your provider"
        step = view.step_index + 1 if screen.state in IN_CHANNEL else ""
        step_txt = f" You're on step {step}." if step else ""
        st.markdown(
            f'<div class="pb-welcome-banner" role="status">'
            f'<p class="pb-welcome-kicker">Welcome back</p>'
            f'<p class="pb-welcome-body">We saved your progress moving your '
            f"<strong>{provider}</strong> 401(k).{step_txt}</p></div>",
            unsafe_allow_html=True,
        )

    if st.session_state.get("ui_error"):
        st.error(st.session_state.ui_error)

    if screen.state not in (JourneyState.COMPLETE, JourneyState.ESCALATED, JourneyState.PROVIDER_UNKNOWN):
        _progress(screen.phase.value)

    # Find
    if screen.state == JourneyState.PROVIDER_UNKNOWN:
        if st.session_state.get("show_provider_picker"):
            st.markdown('<p class="pb-headline">Pick your recordkeeper</p>', unsafe_allow_html=True)
            for p in list_providers():
                if secondary_button(p, key=f"c_prov_{p}"):
                    _go({"type": "provider_direct", "provider": p})
            if secondary_button("← Search by employer", key="c_hide_prov"):
                st.session_state.show_provider_picker = False
                st.rerun()
            return

        st.markdown(
            '<p class="pb-headline">Find your old 401(k)</p>'
            '<p class="pb-body">Tell us your former employer — we\'ll match you to the provider.</p>',
            unsafe_allow_html=True,
        )
        with st.form("c_employer"):
            employer = st.text_input("Former employer", placeholder="e.g. Target, Voya")
            if form_submit("Find my provider"):
                if employer.strip():
                    _go({"type": "lookup", "employer": employer.strip()})
                else:
                    st.session_state.ui_error = "Enter your former employer."
                    st.rerun()
        if secondary_button("I already know my provider →", key="c_show_prov"):
            st.session_state.show_provider_picker = True
            st.rerun()
        return

    if screen.state in (JourneyState.COMPLETE, JourneyState.ESCALATED):
        st.markdown(f'<p class="pb-headline">{screen.headline}</p>', unsafe_allow_html=True)
        st.markdown(f'<p class="pb-body">{screen.body}</p>', unsafe_allow_html=True)
        if primary_button("Start a new rollover", key="c_restart_done"):
            _go({"type": "restart"})
        return

    # Channel step header
    if screen.state in IN_CHANNEL and en.channel_context:
        ctx = en.channel_context
        ch_label = {"online": "online", "phone": "by phone", "forms": "paper forms"}.get(ctx.channel, "")
        st.markdown(
            channel_step_header(view.step_index, view.total_steps, screen.provider or "", ch_label),
            unsafe_allow_html=True,
        )
        if ctx.channel == "phone" and ctx.phone:
            st.markdown(
                f'<a class="pb-phone-cta" href="tel:{ctx.phone}">'
                f'<span><span class="pb-phone-kicker">Tap to call</span>'
                f'<span class="pb-phone-num">{ctx.phone}</span></span><span>📞</span></a>',
                unsafe_allow_html=True,
            )
        st.markdown(call_script_card(ctx.channel, ctx.say_this, field_label=ctx.form_field_label), unsafe_allow_html=True)
        _show_routing(view)
    else:
        st.markdown(f'<p class="pb-headline">{screen.headline}</p>', unsafe_allow_html=True)
        if screen.body:
            st.markdown(f'<p class="pb-body">{screen.body}</p>', unsafe_allow_html=True)
        if screen.state == JourneyState.INITIATED:
            _show_routing(view)

    if read_only:
        return

    # Decisions — one screen each
    if en.requires_tax_selection:
        st.markdown("**How is your old 401(k) taxed?**")
        for opt in en.tax_options:
            if secondary_button(opt["label"], key=f"c_tax_{opt['id']}", hint=opt.get("hint")):
                _go({"type": "tax_type", "tax_type": opt["id"]})
        return

    if screen.state in (JourneyState.PROVIDER_IDENTIFIED, JourneyState.PROVIDER_NOT_COVERED):
        if secondary_button("Yes, I can log in", key="c_acc_y", hint="We'll guide your rollover."):
            _go({"type": "access", "can_login": True})
        if secondary_button("No — locked out", key="c_acc_n", hint="Recovery steps or BeeKeeper."):
            _go({"type": "access", "can_login": False})
        return

    if screen.state == JourneyState.ACCESS_RECOVERED and any(
        "phone" in a.lower() or "form" in a.lower() for a in screen.secondary_actions
    ):
        st.markdown(f'<p class="pb-body">{screen.sla_note or ""}</p>', unsafe_allow_html=True)
        if secondary_button("Online portal", key="c_ch_o", hint="Fastest when you can log in."):
            _go({"type": "channel", "channel": "online"})
        if secondary_button("By phone", key="c_ch_p", hint="Number + script provided."):
            _go({"type": "channel", "channel": "phone"})
        if secondary_button("Paper forms", key="c_ch_f", hint="Mail a distribution form."):
            _go({"type": "channel", "channel": "forms"})
        return

    if screen.state in IN_CHANNEL:
        if primary_button(screen.primary_action or "Done", key="c_step_done"):
            _go({"type": "step", "outcome": "done"})
        if secondary_button("I'm stuck", key="c_step_stuck"):
            _go({"type": "step", "outcome": "stuck"})
        return

    if screen.state == JourneyState.STUCK:
        if primary_button("Talk to a BeeKeeper", key="c_stuck_esc"):
            _go({"type": "escalate", "reason": "stuck"})
        if secondary_button("Try again", key="c_stuck_resume"):
            _go({"type": "resume"})
        return

    if screen.state == JourneyState.ACCESS_BLOCKED:
        if primary_button("I've regained access", key="c_blocked_ok"):
            _go({"type": "access_recovered"})
        if secondary_button("Get BeeKeeper help", key="c_blocked_esc"):
            _go({"type": "escalate", "reason": "access"})
        return

    if screen.state in (JourneyState.INITIATED, JourneyState.IN_FLIGHT):
        kind = "confirm_in_flight" if screen.state == JourneyState.INITIATED else "mark_complete"
        if primary_button(screen.primary_action, key="c_track_pri"):
            _go({"type": kind})
        if secondary_button("It's taking longer than expected", key="c_track_esc"):
            _go({"type": "escalate", "reason": "delay"})

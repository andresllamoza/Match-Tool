"""Streamlit UI for the full rollover companion — one decision per screen."""

from __future__ import annotations

import streamlit as st

from ui.components import brand_header_bar  # noqa: E402

from .engine_bridge import JourneyView, apply_action, current_view, get_engine, list_providers, save_context
from ui.channel_step import (  # noqa: E402
    call_script_card,
    channel_step_header,
    fbo_security_card,
    financial_copy_field,
    phone_routing_intro,
)
from .widgets import form_submit_primary, icon_button, primary_button, secondary_button, text_link_button

# Engine imports after companion path is on sys.path (via engine_bridge).
from engine.assistant import ScopedAssistant  # noqa: E402
from engine.models import JourneyState  # noqa: E402

PHASES = [
    ("find", "Find"),
    ("access", "Access"),
    ("rollover", "Roll over"),
    ("track", "Track"),
]

IN_CHANNEL = {
    JourneyState.ONLINE_IN_PROGRESS,
    JourneyState.PHONE_IN_PROGRESS,
    JourneyState.FORMS_IN_PROGRESS,
}


def _render_progress(phase: str, *, variant: str = "default") -> None:
    ids = [p[0] for p in PHASES]
    try:
        idx = ids.index(phase)
    except ValueError:
        idx = 0

    if variant == "minimal":
        parts = ['<nav class="pb-step-nav" aria-label="Rollover progress">']
        for i, (_, label) in enumerate(PHASES):
            active = i == idx
            cls = "active" if active else ""
            parts.append(f'<div class="pb-step-item">')
            parts.append(f'<span class="pb-step-label {cls}">{label}</span>')
            if active:
                parts.append('<span class="pb-step-pill" aria-hidden="true"></span>')
            parts.append("</div>")
        parts.append("</nav>")
        st.markdown("".join(parts), unsafe_allow_html=True)
        return

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


def _render_find_perk(body: str) -> None:
    if "1%" not in body:
        return
    st.markdown(
        '<div class="pb-perk-below">'
        '<p class="pb-perk-kicker">PensionBee perk</p>'
        '<p class="pb-perk-body">Roll your old 401(k) to PensionBee and get a 1% match on '
        "eligible transfers.</p></div>",
        unsafe_allow_html=True,
    )


def _render_provider_picker() -> None:
    st.markdown("**Select your 401(k) provider**")
    for p in list_providers():
        if _selection_button(p, f"prov_{p}"):
            st.session_state.show_provider_picker = False
            _go({"type": "provider_direct", "provider": p})
    if secondary_button("← Search by employer instead", key="hide_provider_picker"):
        st.session_state.show_provider_picker = False
        st.rerun()


def _find_surface(view: JourneyView) -> str:
    """Match Next.js resolveDecisionMode — disambiguation before employer form."""
    screen = view.screen
    if st.session_state.get("show_provider_picker"):
        return "provider_picker"
    if screen.disambiguation_question and screen.disambiguation_options:
        return "disambiguation"
    return "employer_form"


def _find_card():
    try:
        return st.container(border=True)
    except TypeError:
        return st.container()


def _render_find_disambiguation(view: JourneyView) -> None:
    screen = view.screen
    with _find_card():
        _render_progress(screen.phase.value, variant="minimal")
        st.markdown(
            '<h1 class="pb-find-h1">Narrow it down</h1>'
            "<p class=\"pb-find-sub\">We need one more detail to locate the right 401(k) plan.</p>",
            unsafe_allow_html=True,
        )
        st.markdown(f"**{screen.disambiguation_question}**")
        for opt in screen.disambiguation_options:
            if _selection_button(opt, f"find_dis_{opt}"):
                _go({"type": "disambiguate", "answer": opt})
        if text_link_button("← Search a different employer", key="find_disambig_reset"):
            save_context(get_engine().start())
            st.session_state.show_provider_picker = False
            st.session_state.show_find_assistant = False
            st.session_state.pop("ui_error", None)
            st.session_state.employer_draft = ""
            st.rerun()
    _render_find_perk(screen.body)


def _render_find_step(view: JourneyView) -> None:
    screen = view.screen
    with _find_card():
        _render_progress(screen.phase.value, variant="minimal")
        st.markdown(
            '<h1 class="pb-find-h1">Find your old 401(k)</h1>'
            "<p class=\"pb-find-sub\">Tell us your former employer. We'll match you to the 401(k) "
            "provider and guide you through login, rollover, or a phone call.</p>",
            unsafe_allow_html=True,
        )
        try:
            form_ctx = st.form("employer_lookup_form", clear_on_submit=False, border=False)
        except TypeError:
            form_ctx = st.form("employer_lookup_form", clear_on_submit=False)
        with form_ctx:
            employer = st.text_input(
                "Former employer",
                key="employer_draft",
                placeholder="e.g. Google, Target, FedEx",
                label_visibility="visible",
            )
            submitted = form_submit_primary(screen.primary_action)
        if submitted:
            name = (employer or st.session_state.get("employer_draft", "")).strip()
            if name:
                st.session_state.pending_lookup = name
                st.rerun()
            else:
                st.session_state.ui_error = "Enter your former employer to continue."
                st.rerun()
        if text_link_button("I already know my 401(k) provider →", key="show_provider_picker_btn"):
            st.session_state.show_provider_picker = True
            st.rerun()
        if text_link_button("Ask a question about this step →", key="find_ask_assistant"):
            st.session_state.show_find_assistant = True
            st.rerun()
    _render_find_perk(screen.body)
    if st.session_state.get("show_find_assistant"):
        _render_assistant(view)


def _selection_button(label: str, key: str, description: str | None = None) -> bool:
    text = label
    if description:
        text = f"{label}\n\n{description}"
    return secondary_button(text, key=key)


def _show_mailing_details(say_this: str, step_index: int, total_steps: int) -> bool:
    lower = say_this.lower()
    if any(w in lower for w in ("check", "payable", "mail", "pensionbee", "destination", "ira")):
        return True
    if total_steps <= 0:
        return False
    return step_index >= total_steps - 3


def _render_channel_context(view: JourneyView) -> None:
    ctx_data = view.enrichment.channel_context
    if not ctx_data:
        return
    ch = ctx_data.channel
    en = view.enrichment

    if ch == "phone" and ctx_data.phone:
        st.markdown(
            f'<a class="pb-phone-cta" href="tel:{ctx_data.phone}">'
            f'<span><span class="pb-phone-kicker">Tap to call</span>'
            f'<span class="pb-phone-num">{ctx_data.phone}</span></span>'
            f'<span aria-hidden="true">📞</span></a>',
            unsafe_allow_html=True,
        )

    st.markdown(
        call_script_card(
            ch,
            ctx_data.say_this,
            field_label=ctx_data.form_field_label,
        ),
        unsafe_allow_html=True,
    )

    if ctx_data.portal_menu_hints:
        st.markdown(
            '<div class="pb-channel-hint-card"><p class="pb-channel-hint-kicker">'
            "Look for these menu labels</p><p class=\"pb-channel-hint\">"
            + " · ".join(ctx_data.portal_menu_hints)
            + "</p></div>",
            unsafe_allow_html=True,
        )
    if ctx_data.destination_hints:
        st.markdown(
            '<div class="pb-channel-hint-card"><p class="pb-channel-hint-kicker">'
            "Destination dropdown options</p><p class=\"pb-channel-hint\">"
            + " · ".join(ctx_data.destination_hints)
            + "</p></div>",
            unsafe_allow_html=True,
        )

    if _show_mailing_details(ctx_data.say_this, view.step_index, view.total_steps):
        payable = ctx_data.check_payable or ""
        mail = ctx_data.mailing_address or en.mailing_address
        parts: list[str] = ['<div class="pb-routing-panel">']
        if ch == "phone":
            parts.append(phone_routing_intro())
        fbo_html = fbo_security_card(payable)
        if fbo_html:
            parts.append(fbo_html)
        elif payable:
            parts.append(financial_copy_field("Payee name", payable, "pb-payable"))
        if mail:
            parts.append(financial_copy_field("Mailing address", mail, "pb-mail"))
        parts.append("</div>")
        if len(parts) > 2:
            st.markdown("".join(parts), unsafe_allow_html=True)

    if en.forward_step_required:
        st.markdown(
            '<p class="pb-forward-note">This provider may mail the check to your home address '
            "first — PensionBee will send a prepaid envelope to forward it.</p>",
            unsafe_allow_html=True,
        )

    if ctx_data.rep_questions:
        with st.expander("If the rep asks…"):
            for q in ctx_data.rep_questions:
                st.markdown(f"**{q.question}**  \n{q.answer}")


def _render_decisions(view: JourneyView) -> None:
    screen = view.screen
    en = view.enrichment
    state = screen.state

    if state in (JourneyState.COMPLETE, JourneyState.ESCALATED):
        return

    if en.requires_tax_selection:
        st.markdown("**How is your old 401(k) taxed?**")
        options = en.tax_options or [
            {"id": "pre_tax", "label": "Pre-tax (Traditional IRA)", "hint": "Most common"},
            {"id": "roth", "label": "Roth (Roth IRA)", "hint": "After-tax bucket"},
            {"id": "both", "label": "Both", "hint": "Split across IRA types"},
        ]
        for opt in options:
            if _selection_button(opt["label"], f"tax_{opt['id']}", opt.get("hint")):
                _go({"type": "tax_type", "tax_type": opt["id"]})
        return

    if st.session_state.get("show_provider_picker"):
        _render_provider_picker()
        return

    if screen.disambiguation_question and screen.disambiguation_options:
        st.markdown(f"**{screen.disambiguation_question}**")
        for opt in screen.disambiguation_options:
            if _selection_button(opt, f"dis_{opt}"):
                _go({"type": "disambiguate", "answer": opt})
        return

    if state == JourneyState.PROVIDER_UNKNOWN:
        return

    if state in (JourneyState.PROVIDER_IDENTIFIED, JourneyState.PROVIDER_NOT_COVERED):
        st.markdown("**Can you log in to your old 401(k) account right now?**")
        if _selection_button(
            "Yes, I can log in",
            "access_yes",
            "We'll walk you through the rollover online or by phone.",
        ):
            _go({"type": "access", "can_login": True})
        if _selection_button(
            "No, I'm locked out or never had access",
            "access_no",
            "We'll help you recover access or connect you with a BeeKeeper.",
        ):
            _go({"type": "access", "can_login": False})
        if state == JourneyState.PROVIDER_NOT_COVERED and secondary_button(
            "Talk to a BeeKeeper about this provider", key="handoff_provider"
        ):
            _go({"type": "handoff", "reason": "provider_not_covered"})
        return

    if state == JourneyState.ACCESS_RECOVERED and any(
        "phone" in a.lower() or "form" in a.lower() for a in screen.secondary_actions
    ):
        st.markdown("**How would you like to start your rollover?**")
        if _selection_button("Online", "ch_online", "Fastest when you can log in."):
            _go({"type": "channel", "channel": "online"})
        if _selection_button("By phone", "ch_phone", "We'll give you the number and script."):
            _go({"type": "channel", "channel": "phone"})
        if _selection_button("Paper forms", "ch_forms", "Download, fill, and mail."):
            _go({"type": "channel", "channel": "forms"})
        return

    if state in IN_CHANNEL:
        if view.total_steps > 0:
            st.progress((view.step_index + 1) / view.total_steps)
        if primary_button(screen.primary_action, key="channel_done"):
            _go({"type": "step", "outcome": "done"})
        if secondary_button("I'm stuck on this step", key="channel_stuck"):
            _go({"type": "step", "outcome": "stuck"})
        return

    if state == JourneyState.STUCK:
        if primary_button(screen.primary_action, key="stuck_escalate"):
            _go({"type": "escalate", "reason": "stuck_on_step"})
        if secondary_button("Try this step again", key="stuck_resume"):
            _go({"type": "resume"})
        return

    if state in (JourneyState.INITIATED, JourneyState.IN_FLIGHT):
        if primary_button(screen.primary_action, key="track_primary"):
            kind = "confirm_in_flight" if state == JourneyState.INITIATED else "mark_complete"
            _go({"type": kind})
        for i, action in enumerate(screen.secondary_actions):
            if "nothing arrived" in action.lower() or "help" in action.lower():
                if secondary_button(action, key=f"track_sec_{i}"):
                    _go({"type": "escalate", "reason": "tracking_delay"})
        return

    if state == JourneyState.ACCESS_BLOCKED:
        if primary_button(screen.primary_action, key="access_blocked_primary"):
            _go({"type": "access_recovered"})
        for i, action in enumerate(screen.secondary_actions):
            if "locked" in action.lower() or "beekeeper" in action.lower():
                if secondary_button(action, key=f"access_blocked_sec_{i}"):
                    _go({"type": "escalate", "reason": "access_lockout"})
        return

    if primary_button(screen.primary_action, key="fallback_primary"):
        if state == JourneyState.ACCESS_RECOVERED:
            _go({"type": "channel", "channel": "online"})


def _go(action: dict) -> None:
    result = apply_action(action)
    if isinstance(result, str):
        st.session_state.ui_error = result
    else:
        if (
            action.get("type") == "lookup"
            and hasattr(result, "ctx")
            and result.ctx.state == JourneyState.PROVIDER_UNKNOWN
            and hasattr(result, "screen")
            and not (
                result.screen.disambiguation_question and result.screen.disambiguation_options
            )
        ):
            st.session_state.ui_error = (
                "We couldn't find a 401(k) plan for that employer. "
                "Try the full company name (e.g. Google LLC), or pick your provider below."
            )
        else:
            st.session_state.pop("ui_error", None)
        if action.get("type") == "restart":
            st.session_state.show_provider_picker = False
            st.session_state.show_find_assistant = False
            st.session_state.employer_draft = ""
    st.rerun()


def _render_assistant(view: JourneyView) -> None:
    with st.expander("Ask a question about this step"):
        q = st.text_input("Your question", placeholder="e.g. Where does the check get mailed?")
        if primary_button("Ask", key="ask_btn") and q.strip():
            assistant = ScopedAssistant(get_engine().knowledge)
            provider = view.ctx.provider or view.ctx.uncovered_provider
            ans = assistant.answer(q.strip(), view.ctx.state, provider)
            if ans.get("in_scope"):
                st.success(ans["answer"])
            else:
                st.warning(ans["answer"])
        if secondary_button(
            "Skip this step — talk to a human BeeKeeper",
            key="ask_escalate",
        ):
            _go({"type": "escalate", "reason": "assistant_handoff"})


def run_journey_app() -> None:
    if "show_provider_picker" not in st.session_state:
        st.session_state.show_provider_picker = False
    if "show_find_assistant" not in st.session_state:
        st.session_state.show_find_assistant = False
    if "employer_draft" not in st.session_state:
        st.session_state.employer_draft = ""

    # Process employer search before any widgets render (Streamlit forbids mutating
    # session keys that are bound to widgets after those widgets are drawn).
    if st.session_state.get("pending_lookup"):
        employer = str(st.session_state.pending_lookup).strip()
        del st.session_state.pending_lookup
        if employer:
            _go({"type": "lookup", "employer": employer})
        else:
            st.session_state.ui_error = "Enter your former employer to continue."
            st.rerun()

    header_left, header_right = st.columns([6, 1])
    with header_left:
        brand_header_bar()
    with header_right:
        if icon_button("↺", key="restart_journey", help="Restart journey"):
            _go({"type": "restart"})

    if st.session_state.get("ui_error"):
        st.error(st.session_state.ui_error)

    view = current_view()
    screen = view.screen

    is_find_step = screen.state == JourneyState.PROVIDER_UNKNOWN

    if screen.state not in (JourneyState.COMPLETE, JourneyState.ESCALATED) and not is_find_step:
        _render_progress(screen.phase.value)

    if screen.provider and screen.state not in (
        JourneyState.PROVIDER_IDENTIFIED,
        JourneyState.PROVIDER_NOT_COVERED,
        JourneyState.PROVIDER_UNKNOWN,
    ):
        st.caption(f"{screen.provider}" + (f" · {screen.channel.value}" if screen.channel else ""))

    if not screen.has_reconstructed_content and screen.provider and screen.state in (
        JourneyState.PROVIDER_IDENTIFIED,
        JourneyState.ONLINE_IN_PROGRESS,
        JourneyState.PHONE_IN_PROGRESS,
    ):
        st.markdown('<span class="pb-badge-ok">✓ Verified Transfer Path</span>', unsafe_allow_html=True)
    elif screen.has_reconstructed_content:
        st.markdown(
            '<div class="pb-badge-warn"><strong>Double-check this layout</strong><br/>'
            "If your provider's phone menu sounds different, tell your BeeKeeper.</div>",
            unsafe_allow_html=True,
        )

    if screen.state in IN_CHANNEL and view.enrichment.channel_context:
        ctx = view.enrichment.channel_context
        provider = screen.provider or "your provider"
        channel_label = {"online": "online", "phone": "by phone", "forms": "paper forms"}.get(
            ctx.channel, ""
        )
        st.markdown(
            channel_step_header(
                view.step_index,
                view.total_steps,
                provider,
                channel_label,
            ),
            unsafe_allow_html=True,
        )
        if screen.edge_cases and view.step_index == 0:
            st.markdown(
                f'<div class="pb-edge-tip">{screen.edge_cases[0]}</div>',
                unsafe_allow_html=True,
            )
    elif not is_find_step:
        st.markdown(f'<h1 class="pb-headline">{screen.headline}</h1>', unsafe_allow_html=True)
        if screen.body:
            st.markdown(f'<p class="pb-body">{screen.body}</p>', unsafe_allow_html=True)

    if screen.edge_cases and screen.state not in IN_CHANNEL:
        for ec in screen.edge_cases:
            st.warning(ec)

    if screen.provenance_warning:
        st.warning(screen.provenance_warning)

    if screen.state in IN_CHANNEL:
        _render_channel_context(view)

    if screen.state == JourneyState.ACCESS_BLOCKED and screen.guidance:
        for i, g in enumerate(screen.guidance, 1):
            st.markdown(f"{i}. {g.text}")

    track = view.enrichment.track
    if track and screen.state in (JourneyState.INITIATED, JourneyState.IN_FLIGHT):
        st.info(
            f"**Timeline:** {track.typical_timeline}  \n"
            f"**Check:** {track.check_destination}  \n"
            f"**Day {track.follow_up_days}:** {track.nothing_arrived_message}"
        )

    if screen.state == JourneyState.COMPLETE:
        st.success("🎉 You're all set! Your rollover is complete.")
    elif screen.state == JourneyState.ESCALATED:
        st.info("A BeeKeeper will take it from here.")
    elif is_find_step:
        surface = _find_surface(view)
        if surface == "provider_picker":
            _render_provider_picker()
        elif surface == "disambiguation":
            _render_find_disambiguation(view)
        else:
            _render_find_step(view)
    else:
        _render_decisions(view)
        _render_assistant(view)

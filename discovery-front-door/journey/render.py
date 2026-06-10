"""Streamlit UI for the full rollover companion — one decision per screen."""

from __future__ import annotations

import html

import streamlit as st

from .engine_bridge import (
    JourneyView,
    apply_action,
    current_view,
    get_engine,
    get_session_store,
    list_providers,
    save_context,
)
from ui.shell import (  # noqa: E402
    render_footer,
    render_top_bar,
    resolve_footer,
    show_back_button,
)
from ui.channel_step import (  # noqa: E402
    call_card,
    call_script_card,
    channel_step_header,
    financial_copy_field,
    phone_routing_intro,
    routing_security_card,
)
from .widgets import (
    form_submit_primary,
    icon_button,
    option_card,
    primary_button,
    secondary_button,
    text_link_button,
)

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

SURFACES = ["Customer", "BeeKeeper", "Funnel"]


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


def _decision_hero(title: str, lead: str | None = None) -> None:
    st.markdown(f'<h1 class="pb-decision-hero">{title}</h1>', unsafe_allow_html=True)
    if lead:
        st.markdown(f'<p class="pb-decision-lead">{lead}</p>', unsafe_allow_html=True)


def _screen_owns_headline(view: JourneyView) -> bool:
    """Decision screens render their own hero — skip engine headline/body."""
    screen = view.screen
    ctx = view.ctx
    if screen.state in (JourneyState.PROVIDER_IDENTIFIED, JourneyState.PROVIDER_NOT_COVERED):
        return True
    if view.enrichment.requires_tax_selection:
        return True
    if (
        screen.state == JourneyState.ACCESS_RECOVERED
        and ctx.tax_fund_type
        and not view.enrichment.requires_tax_selection
    ):
        return True
    if screen.disambiguation_question and screen.disambiguation_options:
        return True
    return False


def _render_provider_picker() -> None:
    st.markdown('<div class="pb-shell-body">', unsafe_allow_html=True)
    _decision_hero("Select your 401(k) provider", "Pick the company that holds your old plan.")
    for p in list_providers():
        if secondary_button(p, key=f"prov_{p}"):
            st.session_state.show_provider_picker = False
            _go({"type": "provider_direct", "provider": p})
    if text_link_button("← Search by employer instead", key="hide_provider_picker"):
        st.session_state.show_provider_picker = False
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)


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
    st.markdown('<div class="pb-shell-body">', unsafe_allow_html=True)
    st.markdown(
        '<h1 class="pb-find-h1">Narrow it down</h1>'
        "<p class=\"pb-find-sub\">We need one more detail to locate the right 401(k) plan.</p>",
        unsafe_allow_html=True,
    )
    _decision_hero(screen.disambiguation_question or "Narrow it down")
    for opt in screen.disambiguation_options:
        if option_card(opt, key=f"find_dis_{opt}"):
            _go({"type": "disambiguate", "answer": opt})
    if text_link_button("← Search a different employer", key="find_disambig_reset"):
        _go({"type": "restart"})
    st.markdown("</div>", unsafe_allow_html=True)
    _render_find_perk(screen.body)


def _render_find_step(view: JourneyView) -> None:
    screen = view.screen
    st.markdown('<div class="pb-shell-body">', unsafe_allow_html=True)
    st.markdown(
        '<h1 class="pb-find-h1">Find your old 401(k)</h1>'
        "<p class=\"pb-find-sub\">Tell us your former employer. We'll match you to the 401(k) "
        "provider and guide you through login, rollover, or a phone call.</p>",
        unsafe_allow_html=True,
    )
    st.markdown('<div class="pb-find-form">', unsafe_allow_html=True)
    try:
        form_ctx = st.form("employer_lookup_form", clear_on_submit=False, border=False)
    except TypeError:
        form_ctx = st.form("employer_lookup_form", clear_on_submit=False)
    with form_ctx:
        st.text_input(
            "Former employer",
            key="employer_draft",
            placeholder="e.g. Google, Target, FedEx",
            label_visibility="visible",
        )
        submitted = form_submit_primary(screen.primary_action or "Find my 401(k)")
    st.markdown("</div>", unsafe_allow_html=True)
    if submitted:
        name = st.session_state.get("employer_draft", "").strip()
        if name:
            st.session_state.pending_lookup = name
            st.rerun()
        else:
            _set_ui_message("Enter your former employer to continue.")
            st.rerun()
    if text_link_button("I already know my 401(k) provider →", key="show_provider_picker_btn"):
        st.session_state.show_provider_picker = True
        st.rerun()
    if text_link_button("Ask a question about this step →", key="find_ask_assistant"):
        st.session_state.show_find_assistant = True
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
    _render_find_perk(screen.body)
    if st.session_state.get("show_find_assistant"):
        _render_assistant(view)


def _show_mailing_details(channel: str, payable: str, say_this: str, step_index: int, total_steps: int) -> bool:
    if payable and channel in ("phone", "forms"):
        return True
    lower = say_this.lower()
    if any(w in lower for w in ("check", "payable", "mail", "pensionbee", "destination", "ira")):
        return True
    if total_steps <= 0:
        return False
    return step_index >= total_steps - 3


def _render_fbo_copy(payable: str) -> None:
    if payable:
        st.code(payable, language=None)


def _render_initiated_fbo(view: JourneyView) -> None:
    cc = view.enrichment.channel_context
    if not cc or not cc.check_payable:
        return
    mail = cc.mailing_address or view.enrichment.mailing_address
    security_html = routing_security_card(cc.check_payable, mail)
    if security_html:
        st.markdown(f'<div class="pb-routing-panel">{security_html}</div>', unsafe_allow_html=True)
        _render_fbo_copy(cc.check_payable)


def _render_channel_context(view: JourneyView) -> None:
    ctx_data = view.enrichment.channel_context
    if not ctx_data:
        return
    ch = ctx_data.channel
    en = view.enrichment

    if ch == "phone" and ctx_data.phone:
        st.markdown(call_card(ctx_data.phone), unsafe_allow_html=True)

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

    payable = ctx_data.check_payable or ""
    mail = ctx_data.mailing_address or en.mailing_address
    if _show_mailing_details(ch, payable, ctx_data.say_this, view.step_index, view.total_steps):
        panel: list[str] = ['<div class="pb-routing-panel">']
        if ch == "phone":
            panel.append(phone_routing_intro())
        security_html = routing_security_card(payable or None, mail or None)
        if security_html:
            panel.append(security_html)
        panel.append("</div>")
        if security_html:
            st.markdown("".join(panel), unsafe_allow_html=True)
            if payable:
                _render_fbo_copy(payable)

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
        _decision_hero(
            "What kind of money is it?",
            "Pre-tax goes to a Traditional IRA, Roth to a Roth IRA.",
        )
        options = en.tax_options or [
            {"id": "pre_tax", "label": "Pre-tax (Traditional IRA)", "hint": "Most common"},
            {"id": "roth", "label": "Roth (Roth IRA)", "hint": "After-tax bucket"},
            {"id": "both", "label": "Both", "hint": "Split across IRA types"},
        ]
        for opt in options:
            if option_card(
                opt["label"],
                key=f"tax_{opt['id']}",
                caption=opt.get("hint"),
                primary=opt["id"] == "pre_tax",
            ):
                _go({"type": "tax_type", "tax_type": opt["id"]})
        return

    if st.session_state.get("show_provider_picker"):
        _render_provider_picker()
        return

    if screen.disambiguation_question and screen.disambiguation_options:
        _decision_hero(screen.disambiguation_question)
        for opt in screen.disambiguation_options:
            if option_card(opt, key=f"dis_{opt}"):
                _go({"type": "disambiguate", "answer": opt})
        return

    if state == JourneyState.PROVIDER_UNKNOWN:
        return

    if state in (JourneyState.PROVIDER_IDENTIFIED, JourneyState.PROVIDER_NOT_COVERED):
        _decision_hero(
            "Can you log in to your old 401(k)?",
            "We'll tailor the next steps to how you get in.",
        )
        if option_card(
            "Yes, I can log in",
            key="access_yes",
            caption="We'll walk you through it online or by phone.",
            primary=True,
        ):
            _go({"type": "access", "can_login": True})
        if option_card(
            "No — I'm locked out or never set it up",
            key="access_no",
            caption="We'll recover access or bring in a BeeKeeper.",
        ):
            _go({"type": "access", "can_login": False})
        return

    if state == JourneyState.ACCESS_RECOVERED and any(
        "phone" in a.lower() or "form" in a.lower() for a in screen.secondary_actions
    ):
        _decision_hero(
            "How would you like to start your rollover?",
            screen.sla_note if screen.sla_note else None,
        )
        pb = get_engine().knowledge.playbook_for(view.ctx) if view.ctx.provider else None
        is_two_hop = pb and pb.mechanism.value == "two_hop_acat"
        online_hint = (
            "Usually 2–5 business days (vs 7–10 by check)"
            if is_two_hop
            else "Fastest when you can log in."
        )
        if option_card("Do it online", key="ch_online", caption=online_hint, primary=True):
            _go({"type": "channel", "channel": "online"})
        if option_card(
            "By phone",
            key="ch_phone",
            caption="We'll give you the number and a read-along script.",
        ):
            _go({"type": "channel", "channel": "phone"})
        if option_card(
            "Paper forms",
            key="ch_forms",
            caption="Download, fill, and mail.",
        ):
            _go({"type": "channel", "channel": "forms"})
        return

    if state in IN_CHANNEL and view.total_steps > 0:
        st.progress((view.step_index + 1) / view.total_steps)


_FATAL_PREFIX = "__FATAL__:"


def _set_ui_message(message: str, *, fatal: bool = False) -> None:
    st.session_state.ui_error = message
    st.session_state.ui_error_fatal = fatal


def _clear_ui_message() -> None:
    st.session_state.pop("ui_error", None)
    st.session_state.pop("ui_error_fatal", None)


def _shell_beekeeper(view: JourneyView) -> None:
    get_engine().log_handoff_taken(view.ctx, f"voluntary:{view.screen.state.value}")
    save_context(view.ctx)
    st.toast("Your BeeKeeper has the full context of this journey.")


def _shell_action(action: dict) -> None:
    _go(action)


def _go(action: dict) -> None:
    st.session_state.journey_restored = False
    if action.get("type") == "go_back":
        st.session_state.show_provider_picker = False
    result = apply_action(action)
    if isinstance(result, str):
        if result.startswith(_FATAL_PREFIX):
            _set_ui_message(result[len(_FATAL_PREFIX) :], fatal=True)
        else:
            _set_ui_message(result, fatal=False)
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
            _set_ui_message(
                "We couldn't find a 401(k) plan for that employer. "
                "Try the full company name (e.g. Google LLC), or pick your provider below.",
                fatal=False,
            )
        else:
            _clear_ui_message()
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


def _render_funnel_surface() -> None:
    from engine.funnel import load_funnel_summary

    st.markdown('<h1 class="pb-headline">Journey funnel</h1>', unsafe_allow_html=True)
    st.caption("Stall points and handoff demand from the event stream.")
    summary = load_funnel_summary()
    if summary.total_journeys == 0 and not summary.by_state:
        st.markdown(
            '<div class="pb-channel-hint-card">No journeys yet — run one from the '
            "<b>Customer</b> surface, then come back here.</div>",
            unsafe_allow_html=True,
        )
        return
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Journeys", summary.total_journeys)
    m2.metric("Handoffs offered", summary.handoff_offered_count)
    m3.metric("Handoffs taken", summary.handoff_taken_count)
    m4.metric("Not covered", summary.provider_not_covered_count)
    if summary.by_state:
        st.markdown("##### Events by state")
        st.bar_chart({k: v for k, v in summary.by_state.items() if v > 0})
    if summary.stall_points:
        st.markdown("##### Stall points by provider")
        rows = [
            {"Provider": sp.provider or "—", "State": sp.state, "Count": sp.count}
            for sp in summary.stall_points
        ]
        st.dataframe(rows, use_container_width=True, hide_index=True)


def _render_beekeeper_surface(view: JourneyView) -> None:
    screen = view.screen
    notes = "".join(f"<li>{n}</li>" for n in screen.agent_notes) or "<li>—</li>"
    esc = "".join(f"<li>{e.action}</li>" for e in screen.active_escalations)
    edge = "".join(f"<li>{e}</li>" for e in screen.edge_cases)
    say = screen.next_beekeeper_script or "—"
    st.markdown(
        f"""<div class="pb-agent-panel">
        <h4>Say next</h4><div class="pb-agent-say">{say}</div>
        <h4>Agent notes</h4><ul>{notes}</ul>
        {f'<h4>Active escalations</h4><ul>{esc}</ul>' if esc else ''}
        {f'<h4>Edge cases</h4><ul>{edge}</ul>' if edge else ''}
        <h4>State debug</h4>
        <div class="pb-agent-debug">{view.ctx.state.value} · {view.ctx.provider or "?"} · step {view.ctx.step_index}
        · stuck×{view.ctx.stuck_count} · {view.ctx.journey_id}</div></div>""",
        unsafe_allow_html=True,
    )
    st.code(say, language=None)


def run_journey_app() -> None:
    if "show_provider_picker" not in st.session_state:
        st.session_state.show_provider_picker = False
    if "show_find_assistant" not in st.session_state:
        st.session_state.show_find_assistant = False
    if "employer_draft" not in st.session_state:
        st.session_state.employer_draft = ""
    if "journey_restored" not in st.session_state:
        st.session_state.journey_restored = False
    if "demo_surface" not in st.session_state:
        st.session_state.demo_surface = "Customer"

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

    surface = st.session_state.get("demo_surface", "Customer")

    if surface == "Funnel":
        _render_funnel_surface()
        st.stop()

    view = current_view()
    screen = view.screen
    is_find_step = screen.state == JourneyState.PROVIDER_UNKNOWN
    find_surface = _find_surface(view) if is_find_step else None

    render_top_bar(
        show_back=show_back_button(view),
        on_back=lambda: _go({"type": "go_back"}),
        on_save_exit=lambda: (
            save_context(view.ctx),
            st.toast("Saved — open the same link anytime to continue."),
        ),
    )

    if st.session_state.get("ui_error"):
        msg = html.escape(st.session_state.ui_error)
        if st.session_state.get("ui_error_fatal"):
            st.markdown(f'<div class="pb-snag">{msg}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="pb-notice">{msg}</div>', unsafe_allow_html=True)

    if screen.state not in (JourneyState.COMPLETE, JourneyState.ESCALATED):
        _render_progress(screen.phase.value)

    if st.session_state.get("journey_restored"):
        provider = view.ctx.provider or view.ctx.uncovered_provider or "your provider"
        stage = screen.headline or view.ctx.state.value.replace("_", " ")
        st.markdown(
            f'<div class="pb-welcome" role="status">'
            f'<p class="pb-welcome-kicker">🐝 Welcome back — we saved your spot</p>'
            f'<p class="pb-welcome-body">Continuing your <strong>{provider}</strong> rollover — {stage}.</p>'
            f"</div>",
            unsafe_allow_html=True,
        )
        st.session_state.journey_restored = False

    if screen.provider and screen.state not in (
        JourneyState.PROVIDER_IDENTIFIED,
        JourneyState.PROVIDER_NOT_COVERED,
        JourneyState.PROVIDER_UNKNOWN,
    ):
        st.caption(f"{screen.provider}" + (f" · {screen.channel.value}" if screen.channel else ""))

    if (
        not screen.has_reconstructed_content
        and screen.provider
        and screen.state
        in (
            JourneyState.ONLINE_IN_PROGRESS,
            JourneyState.PHONE_IN_PROGRESS,
        )
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
    elif not is_find_step and not _screen_owns_headline(view):
        st.markdown(f'<h1 class="pb-headline">{screen.headline}</h1>', unsafe_allow_html=True)
        if screen.body:
            st.markdown(f'<p class="pb-body">{screen.body}</p>', unsafe_allow_html=True)

    if screen.provenance_warning:
        st.markdown(
            f'<div class="pb-badge-warn">{html.escape(screen.provenance_warning)}</div>',
            unsafe_allow_html=True,
        )

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

    if screen.state == JourneyState.INITIATED:
        _render_initiated_fbo(view)

    if screen.state == JourneyState.COMPLETE:
        st.markdown('<div class="pb-shell-body">', unsafe_allow_html=True)
        st.success("🎉 You're all set! Your rollover is complete.")
        st.markdown("</div>", unsafe_allow_html=True)
    elif screen.state == JourneyState.ESCALATED:
        st.markdown('<div class="pb-shell-body">', unsafe_allow_html=True)
        st.markdown(
            '<p class="pb-body">A BeeKeeper will take it from here. '
            "Use Back to return to your last step, or save and come back later.</p>",
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)
    elif is_find_step:
        if find_surface == "provider_picker":
            _render_provider_picker()
        elif find_surface == "disambiguation":
            _render_find_disambiguation(view)
        else:
            _render_find_step(view)
    else:
        st.markdown('<div class="pb-shell-body">', unsafe_allow_html=True)
        _render_decisions(view)
        if screen.state not in (JourneyState.COMPLETE, JourneyState.ESCALATED):
            _render_assistant(view)
        st.markdown("</div>", unsafe_allow_html=True)

    if find_surface == "employer_form":
        st.markdown(
            '<div class="pb-shell-footer pb-shell-footer--find">'
            '<p class="pb-shell-bk-copy">🐝 Talk to your BeeKeeper</p></div>',
            unsafe_allow_html=True,
        )
        if text_link_button("Get a person to help", key="find_shell_bk"):
            _shell_beekeeper(view)
    else:
        footer = resolve_footer(view, find_surface=find_surface)
        render_footer(
            footer,
            on_action=_shell_action,
            on_beekeeper=lambda: _shell_beekeeper(view),
        )

    if surface == "BeeKeeper":
        _render_beekeeper_surface(view)

    with st.expander("Demo: ops surface & tools", expanded=False):
        try:
            demo_surface = st.segmented_control(
                "Surface", SURFACES, default=surface, label_visibility="collapsed"
            )
        except (AttributeError, TypeError):
            demo_surface = st.radio("Surface", SURFACES, horizontal=True, index=SURFACES.index(surface))
        if demo_surface and demo_surface != surface:
            st.session_state.demo_surface = demo_surface
            st.rerun()
        if icon_button("↺ Restart journey", key="restart_journey", help="Restart journey"):
            _go({"type": "restart"})

    with st.expander("Demo: customer name", expanded=False):
        from engine.customer_copy import DEFAULT_FIRST_NAME, DEFAULT_LAST_NAME

        c1, c2 = st.columns(2)
        demo_first = c1.text_input(
            "First",
            value=view.ctx.customer_first_name or DEFAULT_FIRST_NAME,
            key="demo_cust_first",
        )
        demo_last = c2.text_input(
            "Last",
            value=view.ctx.customer_last_name or DEFAULT_LAST_NAME,
            key="demo_cust_last",
        )
        if st.button("Apply name", key="demo_apply_name") and demo_first.strip() and demo_last.strip():
            _go(
                {
                    "type": "set_name",
                    "first_name": demo_first.strip(),
                    "last_name": demo_last.strip(),
                }
            )

    with st.expander("Resume a saved journey"):
        store = get_session_store()
        rows = store.recent()
        if not rows:
            st.caption("No saved journeys yet.")
        for r in rows:
            c1, c2 = st.columns([4, 1])
            c1.markdown(
                f"`{r['journey_id']}` — **{r['state']}**"
                + (f" · {r['provider']}" if r["provider"] else "")
                + f" · {r['updated_at'][:16]}"
            )
            if c2.button("Resume", key=f"res_{r['journey_id']}"):
                restored = store.load(r["journey_id"])
                if restored:
                    save_context(restored)
                    st.session_state.journey_restored = True
                    st.rerun()

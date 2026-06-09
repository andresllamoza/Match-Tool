"""Streamlit UI for the full rollover companion — one decision per screen."""

from __future__ import annotations

import streamlit as st

from .engine_bridge import JourneyView, apply_action, current_view, get_engine, list_providers

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


def inject_journey_css() -> None:
    st.markdown(
        """
<style>
  .pb-phase-bar { display:flex; gap:4px; margin-bottom:1.25rem; }
  .pb-phase { flex:1; text-align:center; font-size:0.72rem; font-weight:700; color:#6B6560; }
  .pb-phase.active { color:#111111; }
  .pb-phase-dot {
    height:4px; border-radius:999px; background:#EAE5DC; margin-bottom:6px;
  }
  .pb-phase-dot.done, .pb-phase-dot.active { background:#FFC72C; }
  .pb-card-j {
    background:#fff; border:1px solid #EAE5DC; border-radius:16px;
    padding:1.25rem 1.2rem; box-shadow:0 2px 12px rgba(17,17,17,0.06);
    margin-bottom:1rem;
  }
  .pb-h1 { font-size:1.65rem; font-weight:800; color:#111; line-height:1.2; margin:0 0 0.5rem; }
  .pb-body { color:#1E242B; line-height:1.55; margin-bottom:1rem; }
  .pb-badge-ok {
    display:inline-block; background:#E8F5EE; color:#1B7F4B;
    font-size:0.75rem; font-weight:700; padding:0.25rem 0.65rem; border-radius:999px;
    margin-bottom:0.75rem;
  }
  .pb-badge-warn {
    border:2px solid #F59E0B; background:#FFFBEB; border-radius:12px;
    padding:0.75rem 1rem; font-size:0.88rem; margin-bottom:1rem;
  }
  .pb-say {
    border:2px solid rgba(255,199,44,0.45); border-radius:12px; padding:1rem;
    background:#fff; margin:0.75rem 0;
  }
</style>
        """,
        unsafe_allow_html=True,
    )


def _render_progress(phase: str) -> None:
    ids = [p[0] for p in PHASES]
    try:
        idx = ids.index(phase)
    except ValueError:
        idx = 0
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


def _selection_button(label: str, key: str, description: str | None = None) -> bool:
    text = label
    if description:
        text = f"{label}\n\n{description}"
    return st.button(text, key=key, use_container_width=True)


def _render_channel_context(view: JourneyView) -> None:
    ctx_data = view.enrichment.channel_context
    if not ctx_data:
        return
    ch = ctx_data.channel
    if ch == "phone" and ctx_data.phone:
        st.markdown(f"**Call:** [{ctx_data.phone}](tel:{ctx_data.phone})")
    st.markdown(
        f'<div class="pb-say"><strong>Say / do this</strong><p style="margin:0.5rem 0 0;font-size:1.05rem;font-weight:600;">'
        f"{ctx_data.say_this}</p></div>",
        unsafe_allow_html=True,
    )
    if ctx_data.check_payable:
        st.code(f"Check payable to: {ctx_data.check_payable}", language=None)
    if ctx_data.mailing_address:
        st.code(f"Mail to: {ctx_data.mailing_address}", language=None)
    elif view.enrichment.mailing_address:
        st.code(f"Mail to: {view.enrichment.mailing_address}", language=None)
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
        st.markdown("**Select your 401(k) provider**")
        for p in list_providers():
            if _selection_button(p, f"prov_{p}"):
                st.session_state.show_provider_picker = False
                _go({"type": "provider_direct", "provider": p})
        if st.button("← Search by employer instead"):
            st.session_state.show_provider_picker = False
            st.rerun()
        return

    if screen.disambiguation_question and screen.disambiguation_options:
        st.markdown(f"**{screen.disambiguation_question}**")
        for opt in screen.disambiguation_options:
            if _selection_button(opt, f"dis_{opt}"):
                _go({"type": "disambiguate", "answer": opt})
        return

    if state == JourneyState.PROVIDER_UNKNOWN:
        employer = st.text_input(
            "Former employer or plan provider",
            value=st.session_state.get("employer_draft", ""),
            placeholder="e.g. Target, FedEx, Walmart",
            help="We need your former employer's name to match the distribution address your old custodian requires.",
        )
        st.session_state.employer_draft = employer
        if st.button(screen.primary_action, type="primary", use_container_width=True):
            if employer.strip():
                _go({"type": "lookup", "employer": employer.strip()})
            else:
                st.warning("Enter your former employer to continue.")
        if st.button("I already know my 401(k) provider"):
            st.session_state.show_provider_picker = True
            st.rerun()
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
            "No, I'm locked out",
            "access_no",
            "We'll help you recover access or connect you with a BeeKeeper.",
        ):
            _go({"type": "access", "can_login": False})
        if state == JourneyState.PROVIDER_NOT_COVERED and st.button("Talk to a BeeKeeper about this provider"):
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
            st.caption(f"Step {view.step_index + 1} of {view.total_steps}")
        if st.button(screen.primary_action, type="primary", use_container_width=True):
            _go({"type": "step", "outcome": "done"})
        if st.button("I'm stuck on this step"):
            _go({"type": "step", "outcome": "stuck"})
        return

    if state == JourneyState.STUCK:
        if st.button(screen.primary_action, type="primary", use_container_width=True):
            _go({"type": "escalate", "reason": "stuck_on_step"})
        if st.button("Try this step again"):
            _go({"type": "resume"})
        return

    if state in (JourneyState.INITIATED, JourneyState.IN_FLIGHT):
        if st.button(screen.primary_action, type="primary", use_container_width=True):
            kind = "confirm_in_flight" if state == JourneyState.INITIATED else "mark_complete"
            _go({"type": kind})
        for action in screen.secondary_actions:
            if "nothing arrived" in action.lower() or "help" in action.lower():
                if st.button(action):
                    _go({"type": "escalate", "reason": "tracking_delay"})
        return

    if state == JourneyState.ACCESS_BLOCKED:
        if st.button(screen.primary_action, type="primary", use_container_width=True):
            _go({"type": "access_recovered"})
        for action in screen.secondary_actions:
            if "locked" in action.lower() or "beekeeper" in action.lower():
                if st.button(action):
                    _go({"type": "escalate", "reason": "access_lockout"})
        return

    if st.button(screen.primary_action, type="primary", use_container_width=True):
        if state == JourneyState.ACCESS_RECOVERED:
            _go({"type": "channel", "channel": "online"})


def _go(action: dict) -> None:
    result = apply_action(action)
    if isinstance(result, str):
        st.error(result)
    st.rerun()


def _render_assistant(view: JourneyView) -> None:
    with st.expander("Ask a question about this step"):
        q = st.text_input("Your question", placeholder="e.g. Where does the check get mailed?")
        if st.button("Ask", key="ask_btn") and q.strip():
            assistant = ScopedAssistant(get_engine().knowledge)
            provider = view.ctx.provider or view.ctx.uncovered_provider
            ans = assistant.answer(q.strip(), view.ctx.state, provider)
            if ans.get("in_scope"):
                st.success(ans["answer"])
            else:
                st.warning(ans["answer"])
        if st.button("Skip this step — talk to a human BeeKeeper", key="ask_escalate"):
            _go({"type": "escalate", "reason": "assistant_handoff"})


def run_journey_app() -> None:
    inject_journey_css()

    if "show_provider_picker" not in st.session_state:
        st.session_state.show_provider_picker = False
    if "employer_draft" not in st.session_state:
        st.session_state.employer_draft = ""

    if st.session_state.get("pending_lookup"):
        employer = str(st.session_state.pending_lookup).strip()
        del st.session_state.pending_lookup
        if employer:
            result = apply_action({"type": "lookup", "employer": employer})
            if isinstance(result, str):
                st.error(result)
            st.rerun()

    col1, col2 = st.columns([4, 1])
    with col1:
        st.markdown("### 🐝 PensionBee Rollover Companion")
        st.caption("Full guided product — same engine as /customer in Next.js")
    with col2:
        if st.button("Restart"):
            _go({"type": "restart"})

    view = current_view()
    screen = view.screen

    if screen.state not in (JourneyState.COMPLETE, JourneyState.ESCALATED):
        _render_progress(screen.phase.value)

    st.markdown('<div class="pb-card-j">', unsafe_allow_html=True)

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

    st.markdown(f'<h1 class="pb-h1">{screen.headline}</h1>', unsafe_allow_html=True)
    if screen.body and screen.state not in IN_CHANNEL:
        st.markdown(f'<p class="pb-body">{screen.body}</p>', unsafe_allow_html=True)

    if screen.edge_cases:
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
    else:
        _render_decisions(view)
        _render_assistant(view)

    st.markdown("</div>", unsafe_allow_html=True)

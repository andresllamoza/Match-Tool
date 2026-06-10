"""Unified app shell — top bar, momentum rail, sticky footer."""

from __future__ import annotations

from dataclasses import dataclass, field

import streamlit as st

from engine.models import JourneyState

from journey.widgets import primary_button, secondary_button, text_link_button


@dataclass
class FooterAction:
    label: str
    action: dict
    key: str
    kind: str = "primary"  # primary | secondary


@dataclass
class FooterSpec:
    primary: FooterAction | None = None
    secondaries: list[FooterAction] = field(default_factory=list)
    show_beekeeper: bool = True
    beekeeper_key: str = "shell_bk"


def show_back_button(view) -> bool:
    ctx = view.ctx
    screen = view.screen
    if screen.state == JourneyState.COMPLETE:
        return False
    if not ctx.history_stack:
        return False
    if screen.state == JourneyState.PROVIDER_UNKNOWN:
        if not ctx.employer_query and not ctx.disambiguation_question:
            if not st.session_state.get("employer_draft", "").strip():
                if not st.session_state.get("show_provider_picker"):
                    return False
    return True


def render_top_bar(*, show_back: bool, on_back, on_save_exit) -> None:
    st.markdown('<div class="pb-shell-top">', unsafe_allow_html=True)
    c_back, c_brand, c_save = st.columns([1.1, 2, 1.1])
    with c_back:
        if show_back:
            if text_link_button("← Back", key="shell_back"):
                on_back()
        else:
            st.markdown("&nbsp;", unsafe_allow_html=True)
    with c_brand:
        st.markdown(
            '<p class="pb-shell-brand" aria-label="PensionBee">🐝 PensionBee</p>',
            unsafe_allow_html=True,
        )
    with c_save:
        if text_link_button("Save & exit", key="shell_save"):
            on_save_exit()
    st.markdown("</div>", unsafe_allow_html=True)


def render_footer(spec: FooterSpec | None, *, on_action, on_beekeeper) -> None:
    if spec is None:
        spec = FooterSpec()
    st.markdown('<div class="pb-shell-footer" role="contentinfo">', unsafe_allow_html=True)
    for sec in spec.secondaries:
        if secondary_button(sec.label, key=sec.key):
            on_action(sec.action)
    if spec.primary:
        if primary_button(spec.primary.label, key=spec.primary.key):
            on_action(spec.primary.action)
    if spec.show_beekeeper:
        st.markdown(
            '<p class="pb-shell-bk-copy">🐝 Talk to your BeeKeeper</p>',
            unsafe_allow_html=True,
        )
        if text_link_button("Get a person to help", key=spec.beekeeper_key):
            on_beekeeper()
    st.markdown("</div>", unsafe_allow_html=True)


def resolve_footer(view, *, find_surface: str | None = None) -> FooterSpec | None:
    """Return sticky-footer actions; None means choice cards in body only."""
    from journey.engine_bridge import JourneyView  # noqa: F401 — type context

    screen = view.screen
    en = view.enrichment
    state = screen.state

    if state == JourneyState.COMPLETE:
        return FooterSpec(
            primary=FooterAction("Start another rollover", {"type": "restart"}, "shell_primary"),
            show_beekeeper=False,
        )

    if state == JourneyState.ESCALATED:
        return FooterSpec(show_beekeeper=True)

    if state == JourneyState.PROVIDER_UNKNOWN:
        return FooterSpec()

    if en.requires_tax_selection:
        return FooterSpec()

    if st.session_state.get("show_provider_picker"):
        return FooterSpec()

    if screen.disambiguation_question and screen.disambiguation_options:
        return FooterSpec()

    if state in (JourneyState.PROVIDER_IDENTIFIED, JourneyState.PROVIDER_NOT_COVERED):
        secondaries: list[FooterAction] = []
        if state == JourneyState.PROVIDER_NOT_COVERED:
            secondaries.append(
                FooterAction(
                    "Talk to a BeeKeeper about this provider",
                    {"type": "handoff", "reason": "provider_not_covered"},
                    "shell_handoff",
                    kind="secondary",
                )
            )
        return FooterSpec(secondaries=secondaries)

    if state == JourneyState.ACCESS_RECOVERED and any(
        "phone" in a.lower() or "form" in a.lower() for a in screen.secondary_actions
    ):
        return FooterSpec()

    if state in {
        JourneyState.ONLINE_IN_PROGRESS,
        JourneyState.PHONE_IN_PROGRESS,
        JourneyState.FORMS_IN_PROGRESS,
    }:
        label = screen.primary_action or "Done — next step"
        return FooterSpec(
            primary=FooterAction(label, {"type": "step", "outcome": "done"}, "shell_primary"),
            secondaries=[
                FooterAction(
                    "I'm stuck on this step",
                    {"type": "step", "outcome": "stuck"},
                    "shell_stuck",
                    kind="secondary",
                )
            ],
        )

    if state == JourneyState.STUCK:
        return FooterSpec(
            primary=FooterAction(
                screen.primary_action or "Talk to your BeeKeeper",
                {"type": "escalate", "reason": "stuck_on_step"},
                "shell_primary",
            ),
            secondaries=[
                FooterAction(
                    "Try this step again",
                    {"type": "resume"},
                    "shell_resume",
                    kind="secondary",
                )
            ],
        )

    if state == JourneyState.INITIATED:
        secondaries = [
            FooterAction(
                action,
                {"type": "escalate", "reason": "tracking_delay"},
                f"shell_track_sec_{i}",
                kind="secondary",
            )
            for i, action in enumerate(screen.secondary_actions)
            if "nothing arrived" in action.lower() or "help" in action.lower()
        ]
        return FooterSpec(
            primary=FooterAction(
                screen.primary_action or "Track my transfer",
                {"type": "confirm_in_flight"},
                "shell_primary",
            ),
            secondaries=secondaries,
        )

    if state == JourneyState.IN_FLIGHT:
        secondaries = [
            FooterAction(
                action,
                {"type": "escalate", "reason": "tracking_delay"},
                f"shell_track_sec_{i}",
                kind="secondary",
            )
            for i, action in enumerate(screen.secondary_actions)
            if "nothing arrived" in action.lower() or "help" in action.lower()
        ]
        return FooterSpec(
            primary=FooterAction(
                screen.primary_action or "Mark complete",
                {"type": "mark_complete"},
                "shell_primary",
            ),
            secondaries=secondaries,
        )

    if state == JourneyState.ACCESS_BLOCKED:
        secondaries = [
            FooterAction(
                action,
                {"type": "escalate", "reason": "access_lockout"},
                f"shell_access_sec_{i}",
                kind="secondary",
            )
            for i, action in enumerate(screen.secondary_actions)
            if "locked" in action.lower() or "beekeeper" in action.lower()
        ]
        return FooterSpec(
            primary=FooterAction(
                screen.primary_action or "Continue",
                {"type": "access_recovered"},
                "shell_primary",
            ),
            secondaries=secondaries,
        )

    if state == JourneyState.ACCESS_RECOVERED:
        return FooterSpec(
            primary=FooterAction(
                screen.primary_action or "Continue",
                {"type": "channel", "channel": "online"},
                "shell_primary",
            ),
        )

    return FooterSpec()

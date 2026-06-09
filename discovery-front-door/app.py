"""
PensionBee Discovery Front Door — customer-facing "Find your old 401(k)" flow.

Presentation layer over discovery.DiscoveryFlow. Matcher logic unchanged.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from discovery.flow import DiscoveryFlow  # noqa: E402
from discovery.knowledge_bridge import KnowledgeBridge  # noqa: E402
from discovery.models import BalanceRange  # noqa: E402
from discovery.synthetic import build_adapters  # noqa: E402
from ui.brand import inject_brand_css  # noqa: E402
from ui.components import (  # noqa: E402
    error_card,
    format_balance_label,
    headline,
    logo_mark,
    next_step_card,
    provider_result_card,
    value_reveal_card,
    warm_message,
)
from ui.states import UiState, classify_ui_state, run_discovery_safe  # noqa: E402

US_STATES = [
    "",
    "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA",
    "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
    "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
    "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
    "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY",
    "DC",
]

BALANCE_OPTIONS = [(br, format_balance_label(br.value)) for br in BalanceRange]


@st.cache_resource
def _build_flow() -> DiscoveryFlow:
    adv, matcher = build_adapters(ROOT.parent)
    knowledge = KnowledgeBridge.from_dir(ROOT)
    return DiscoveryFlow(adv, matcher, knowledge)


def _init_session() -> None:
    defaults = {
        "ui_state": UiState.INPUT.value,
        "outcome": None,
        "last_employer": "",
        "last_balance": BalanceRange.R_50_100K.value,
        "last_state": "",
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


def _reset_to_input() -> None:
    st.session_state.ui_state = UiState.INPUT.value
    st.session_state.outcome = None


def _render_input(flow: DiscoveryFlow) -> None:
    logo_mark()
    headline(
        "Let's find your old 401(k)",
        "Tell us where you worked — we'll show who likely holds your plan.",
    )

    employer = st.text_input(
        "Former employer",
        value=st.session_state.last_employer,
        placeholder="e.g. Amazon, Walmart, Target",
        label_visibility="visible",
    )
    balance_values = [b[0].value for b in BALANCE_OPTIONS]
    try:
        balance_index = balance_values.index(st.session_state.last_balance)
    except ValueError:
        balance_index = balance_values.index(BalanceRange.R_50_100K.value)
    balance_key = st.selectbox(
        "About how much is in your 401(k)?",
        options=balance_values,
        format_func=lambda v: format_balance_label(v),
        index=balance_index,
    )
    state = st.selectbox(
        "State you worked in (optional)",
        options=US_STATES,
        index=US_STATES.index(st.session_state.last_state) if st.session_state.last_state in US_STATES else 0,
        format_func=lambda s: "Select a state" if s == "" else s,
    )

    if st.button("Find my 401(k)", type="primary", use_container_width=True):
        if not employer.strip():
            warm_message(
                "We need your former employer",
                "Type the company name as you'd remember it — even a partial name helps.",
            )
            return

        st.session_state.last_employer = employer.strip()
        st.session_state.last_balance = balance_key
        st.session_state.last_state = state

        with st.spinner("Looking up your plan…"):
            outcome, err = run_discovery_safe(
                flow,
                employer.strip(),
                BalanceRange(balance_key),
                state=state or None,
            )

        if err or outcome is None:
            st.session_state.ui_state = UiState.ERROR.value
            st.session_state.outcome = None
        else:
            st.session_state.outcome = outcome
            st.session_state.ui_state = classify_ui_state(outcome).value
        st.rerun()


def _render_result() -> None:
    outcome = st.session_state.outcome
    if outcome is None:
        _reset_to_input()
        st.rerun()
        return

    disc = outcome.discovery
    provider = disc.resolved_provider or "your recordkeeper"

    logo_mark()
    headline("Good news — we found a likely match")

    provider_result_card(provider, disc.employer_query, disc.confidence_tier)

    if outcome.value_reveal:
        value_reveal_card(outcome.value_reveal)

    if outcome.next_step:
        next_step_card(outcome.next_step.action)

    st.markdown('<div style="height:0.85rem"></div>', unsafe_allow_html=True)
    if st.button("Start your rollover", type="primary", use_container_width=True):
        warm_message(
            "You're on the right track",
            "A BeeKeeper can walk you through rolling over to PensionBee — real humans, no jargon.",
        )

    st.markdown('<div class="pb-text-action">', unsafe_allow_html=True)
    if st.button("Search another employer", key="result_restart"):
        _reset_to_input()
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)


def _render_low_confidence() -> None:
    outcome = st.session_state.outcome
    if outcome is None:
        _reset_to_input()
        st.rerun()
        return

    disc = outcome.discovery
    logo_mark()
    headline(
        "Almost there — one more detail",
        "We couldn't pin this down yet, but we can still help.",
    )

    question = disc.disambiguation_question or (
        "Which US state did you work in when you participated in this 401(k)?"
    )
    warm_message("Quick question", question)

    state = st.selectbox(
        "State you worked in",
        options=US_STATES[1:],
        index=None,
        placeholder="Select a state",
    )

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Try again", type="primary", use_container_width=True):
            if state:
                flow = _build_flow()
                with st.spinner("Trying again…"):
                    new_outcome, err = run_discovery_safe(
                        flow,
                        disc.employer_query,
                        BalanceRange(st.session_state.last_balance),
                        state=state,
                    )
                if err or new_outcome is None:
                    st.session_state.ui_state = UiState.ERROR.value
                else:
                    st.session_state.outcome = new_outcome
                    st.session_state.ui_state = classify_ui_state(new_outcome).value
                st.rerun()
    with col2:
        st.markdown('<div class="pb-secondary">', unsafe_allow_html=True)
        if st.button("Talk to a BeeKeeper", use_container_width=True):
            warm_message(
                "We've got you",
                "A BeeKeeper can help locate your old 401(k) and walk you through next steps. "
                "Real people — Monday to Friday, 9:30am–5pm ET.",
            )
        st.markdown("</div>", unsafe_allow_html=True)

    if not disc.resolved_provider:
        warm_message(
            "No dead ends here",
            "Even if we can't match your employer automatically, a BeeKeeper can help you "
            "figure out who holds your plan.",
        )

    st.markdown('<div class="pb-secondary">', unsafe_allow_html=True)
    if st.button("Start over", use_container_width=True):
        _reset_to_input()
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)


def _render_error() -> None:
    logo_mark()
    headline("Let's get you to a human")
    error_card()
    st.markdown('<div class="pb-secondary">', unsafe_allow_html=True)
    if st.button("Try again", use_container_width=True):
        _reset_to_input()
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)


def main() -> None:
    st.set_page_config(
        page_title="Find your old 401(k) | PensionBee",
        page_icon="🐝",
        layout="centered",
        initial_sidebar_state="collapsed",
    )
    inject_brand_css()
    _init_session()

    try:
        flow = _build_flow()
    except Exception:
        st.session_state.ui_state = UiState.ERROR.value
        _render_error()
        return

    state = UiState(st.session_state.ui_state)
    if state == UiState.INPUT:
        _render_input(flow)
    elif state == UiState.RESULT:
        _render_result()
    elif state == UiState.LOW_CONFIDENCE:
        _render_low_confidence()
    else:
        _render_error()


if __name__ == "__main__":
    main()

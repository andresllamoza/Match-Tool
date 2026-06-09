"""
Optional pre-signup beat: employer lookup + illustrative 1% match ($ range).
The full rollover product is the Home page (app.py).
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from discovery.adapters.matcher5500 import Local5500Adapter  # noqa: E402
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

st.set_page_config(page_title="Find & value | PensionBee", page_icon="🔍", layout="centered")
inject_brand_css()

US_STATES = [
    "",
    "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA",
    "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
    "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
    "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
    "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY",
    "DC",
]


@st.cache_resource
def _build_flow() -> DiscoveryFlow:
    use_synthetic = os.environ.get("USE_SYNTHETIC") == "1"
    matcher_ready, _ = Local5500Adapter.matcher_deps_available()
    if use_synthetic or not matcher_ready:
        adv, matcher = build_adapters()
    else:
        from discovery.adapters.advizorpro import AdvizorProAdapter

        adv = AdvizorProAdapter()
        matcher = Local5500Adapter.from_matcher(ROOT.parent)
    return DiscoveryFlow(adv, matcher, KnowledgeBridge.from_dir(ROOT))


def _init() -> None:
    for key, val in {
        "find_ui_state": UiState.INPUT.value,
        "find_outcome": None,
        "find_last_employer": "",
        "find_last_balance": BalanceRange.R_50_100K.value,
        "find_last_state": "",
    }.items():
        if key not in st.session_state:
            st.session_state[key] = val


_init()
flow = _build_flow()
state = UiState(st.session_state.find_ui_state)

if state == UiState.INPUT:
    logo_mark()
    headline(
        "Find your old 401(k)",
        "Optional pre-signup lookup + illustrative match. The full rollover is on the Home page.",
    )
    employer = st.text_input("Former employer", value=st.session_state.find_last_employer)
    balance_key = st.selectbox(
        "Balance range",
        options=[b.value for b in BalanceRange],
        format_func=format_balance_label,
    )
    if st.button("Find my 401(k)", type="primary", use_container_width=True) and employer.strip():
        st.session_state.find_last_employer = employer.strip()
        with st.spinner("Looking up…"):
            outcome, err = run_discovery_safe(flow, employer.strip(), BalanceRange(balance_key))
        if err or outcome is None:
            st.session_state.find_ui_state = UiState.ERROR.value
        else:
            st.session_state.find_outcome = outcome
            st.session_state.find_ui_state = classify_ui_state(outcome).value
        st.rerun()

elif state == UiState.RESULT:
    outcome = st.session_state.find_outcome
    disc = outcome.discovery
    logo_mark()
    headline("Likely match")
    provider_result_card(
        disc.resolved_provider or "your recordkeeper",
        disc.employer_query,
        disc.confidence_tier,
    )
    if outcome.value_reveal:
        value_reveal_card(outcome.value_reveal)
    if outcome.next_step:
        next_step_card(outcome.next_step.action)
    if st.button("Continue to full Rollover Companion →", type="primary", use_container_width=True):
        st.session_state.pending_lookup = disc.employer_query
        st.switch_page("app.py")
    if st.button("Search another employer"):
        st.session_state.find_ui_state = UiState.INPUT.value
        st.session_state.find_outcome = None
        st.rerun()

else:
    logo_mark()
    headline("Something went wrong")
    error_card()
    if st.button("Try again"):
        st.session_state.find_ui_state = UiState.INPUT.value
        st.rerun()

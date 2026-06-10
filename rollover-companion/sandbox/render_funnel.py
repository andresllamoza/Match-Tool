"""Funnel analytics surface."""

from __future__ import annotations

import streamlit as st

from engine.funnel import load_funnel_summary


def render_funnel() -> None:
    summary = load_funnel_summary()
    st.markdown("### Funnel analytics")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Journeys", summary.total_journeys)
    c2.metric("Completion rate", f"{summary.completion_rate:.0%}")
    c3.metric("Not covered", summary.provider_not_covered_count)
    c4.metric("Handoffs taken", summary.handoff_taken_count)

    if summary.by_state:
        st.markdown("**Events by state**")
        st.bar_chart({k: v for k, v in summary.by_state.items() if v > 0})
    else:
        st.info("No journey events logged yet — run a customer flow to populate the funnel.")

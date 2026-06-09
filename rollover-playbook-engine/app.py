"""Standalone Streamlit app — test the rollover playbook without the 5500 matcher."""

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine import FunnelStage, RolloverEngine  # noqa: E402
from playbook_ui import (  # noqa: E402
    STAGE_LABELS,
    flag_options_for_provider,
    owner_badge,
    source_badge,
    summary_lines,
)

st.set_page_config(
    page_title="Rollover Playbook",
    page_icon="📋",
    layout="wide",
)
st.title("Rollover Playbook Explorer")
st.caption(
    "Standalone decision engine — pick a recordkeeper and funnel stage, "
    "optionally simulate escalations. No employer lookup, no DOL data."
)

if "engine" not in st.session_state:
    st.session_state.engine = RolloverEngine()

eng: RolloverEngine = st.session_state.engine
kb = eng.knowledge
providers = kb.list_providers()

with st.sidebar:
    st.header("Inputs")
    provider = st.selectbox("Recordkeeper", providers, index=providers.index("Fidelity"))
    stage_key = st.selectbox(
        "Funnel stage",
        options=[s.value for s in FunnelStage],
        format_func=lambda v: STAGE_LABELS[FunnelStage(v)],
        index=0,
    )
    stage = FunnelStage(stage_key)

    st.subheader("Simulate edge cases")
    flag_opts = flag_options_for_provider(kb, provider)
    selected_flags = st.multiselect(
        "Active escalations / failure modes",
        options=[f for f, _ in flag_opts],
        format_func=lambda f: dict(flag_opts).get(f, f),
    )
    st.divider()
    st.markdown("**Deploy separately from the 5500 matcher**")
    st.code("streamlit run app.py", language="bash")
    st.caption("Main file for Streamlit Cloud: `rollover-playbook-engine/app.py`")

col_input, col_output = st.columns([1, 2], gap="large")

general = kb.general_guide

with col_input:
    st.subheader("General guide (all providers)")
    st.markdown(f"**Mail checks to:** {general.mailing_address}")
    st.markdown(f"**Timeline:** {general.typical_processing_time}")
    st.caption(general.account_numbers_policy)
    with st.expander("Universal rollover steps"):
        for i, step in enumerate(general.general_steps, 1):
            st.markdown(f"{i}. {step.text}")

    st.subheader("Provider facts")
    playbook = kb.get(provider)
    st.markdown(f"**Portal:** {playbook.portal or '—'}")
    st.markdown(f"**Mechanism:** `{playbook.mechanism.value}`")
    st.markdown(f"**Check destination:** {playbook.check_destination}")
    st.caption(general.employer_vs_provider_note)
    if playbook.edge_cases:
        with st.expander("Known edge cases"):
            for case in playbook.edge_cases:
                st.markdown(f"- {case}")

with col_output:
    flags = {f: True for f in selected_flags}
    resp = eng.recommend(provider, stage, flags)

    st.subheader("Next action")
    owner = resp.next_action.owner
    st.info(f"**{owner_badge(owner)}** · {source_badge(resp.next_action.source_status)}")
    st.write(resp.next_action.action)

    if resp.active_escalations or resp.active_failure_modes:
        st.warning("Pre-empted by active flag(s)")
        for item in resp.active_escalations + resp.active_failure_modes:
            st.markdown(f"- `{item.flag}` ({item.scope})")

    if resp.provenance_warning:
        st.warning(resp.provenance_warning)

    for line in summary_lines(resp):
        st.markdown(line)

    st.markdown(f"**Tax routing:** {resp.tax_routing_note}")

    with st.expander("General steps (all providers)", expanded=False):
        for i, step in enumerate(resp.general_steps, 1):
            st.markdown(f"{i}. {step.text}")

    with st.expander(f"{provider}-specific portal steps", expanded=stage.value == "provider_identified"):
        for i, step in enumerate(resp.steps, 1):
            st.markdown(
                f"{i}. **{owner_badge(step.owner)}** "
                f"({source_badge(step.source_status)}) — {step.text}"
            )

    with st.expander("Per-stage next actions (reference)", expanded=False):
        for stg in FunnelStage:
            action = playbook.next_actions[stg]
            marker = " ← current" if stg == stage else ""
            st.markdown(
                f"**{STAGE_LABELS[stg]}**{marker}: {action.action} "
                f"({owner_badge(action.owner)})"
            )

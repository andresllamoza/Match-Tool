"""Streamlit demo: in-product Add a transfer wizard."""

from __future__ import annotations

import os
import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from discovery.add_transfer import ACCOUNT_TYPE_401K, run_add_transfer
from discovery.adapters.advizorpro import AdvizorProAdapter
from discovery.adapters.matcher5500 import Local5500Adapter
from discovery.knowledge_bridge import KnowledgeBridge
from discovery.models import ConfidenceTier

st.set_page_config(page_title="Add a transfer", page_icon="🐝", layout="centered")
st.title("Add a transfer")
st.caption("Internal demo — 401(k) employer lookup → recordkeeper → next step")

use_synthetic = os.environ.get("USE_SYNTHETIC") == "1"
if use_synthetic:
    lookup = Local5500Adapter.from_synthetic()
    st.info("Synthetic mode (`USE_SYNTHETIC=1`) — fake employers, no DOL download.")
else:
    repo_root = ROOT.parent
    try:
        lookup = Local5500Adapter.from_matcher(repo_root)
        st.caption("Lookup source: DOL Form 5500 matcher")
    except ModuleNotFoundError as exc:
        st.error(
            f"Missing dependency for the 5500 matcher: `{exc.name}`. "
            "Redeploy after updating `discovery-front-door/requirements.txt`, "
            "or set **`USE_SYNTHETIC=1`** in Streamlit Advanced settings for an instant demo."
        )
        lookup = Local5500Adapter.from_synthetic()
        st.warning("Falling back to synthetic employers until dependencies are installed.")

knowledge = KnowledgeBridge.from_dir(ROOT)

account_type = st.selectbox("Account type", [ACCOUNT_TYPE_401K], index=0)
employer = st.text_input("Former employer name", placeholder="e.g. Amazon.com Services LLC")

if st.button("Look up recordkeeper", type="primary") and employer.strip():
    with st.spinner("Looking up recordkeeper…"):
        result = run_add_transfer(employer.strip(), account_type, lookup, knowledge)

    if result.disambiguation_question:
        st.warning(result.disambiguation_question)

    if result.provider:
        st.success(f"Likely recordkeeper: **{result.provider}** ({result.confidence_tier.value} confidence)")
    else:
        st.error("Could not identify a recordkeeper. Try a more specific employer name.")

    if result.next_step:
        st.subheader("Next step")
        st.write(result.next_step.action)
        st.caption(f"Owner: {result.next_step.owner} · Source: {result.next_step.source_status}")
        if result.next_step.provenance_warning:
            st.warning(result.next_step.provenance_warning)

"""
PensionBee Rollover Companion — FULL PRODUCT (Streamlit Cloud entrypoint).

This is the real guided rollover: find → access → roll over → track.
Uses the same JourneyEngine + knowledge layer as rollover-companion/web (/customer).

Optional sidebar page: Find & value reveal (pre-signup employer lookup + $ match teaser).
"""

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from journey import run_journey_app  # noqa: E402
from ui.brand import inject_brand_css  # noqa: E402

st.set_page_config(
    page_title="Rollover Companion | PensionBee",
    page_icon="🐝",
    layout="centered",
    initial_sidebar_state="collapsed",
)

inject_brand_css()

try:
    run_journey_app()
except Exception as exc:
    st.error("Something went wrong starting the rollover companion. A BeeKeeper can help.")
    st.exception(exc)

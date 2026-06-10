"""
PensionBee Rollover Companion — Streamlit Cloud entrypoint (no local install needed).

This IS the full customer product in your browser: find → access → roll over → track.
Runs the same JourneyEngine as rollover-companion/engine (Next.js is optional dev UI only).

Pages (sidebar):
  • Home (app.py) — full guided rollover journey
  • Find & value reveal — optional pre-signup employer lookup + 1% match teaser

Streamlit Cloud: set USE_SYNTHETIC=1 in secrets, then reboot after deploys.
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

"""
PensionBee Rollover Companion — Streamlit Cloud entrypoint (no local install needed).

This IS the full customer product in your browser: find → access → roll over → track.
Runs the same JourneyEngine as rollover-companion/engine (Next.js is optional dev UI only).

Pages (sidebar):
  • Home (app.py) — full guided rollover journey
  • Find & value reveal — optional pre-signup employer lookup + 1% match teaser

No secrets or env vars required — deploy and run as-is on Streamlit Cloud.
"""

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from journey import run_journey_app  # noqa: E402
from journey.engine_bridge import warm_lookup_cache  # noqa: E402
from ui.brand import inject_brand_css  # noqa: E402

st.set_page_config(
    page_title="Rollover Companion | PensionBee",
    page_icon="🐝",
    layout="centered",
    initial_sidebar_state="collapsed",
)

inject_brand_css()
warm_lookup_cache()

try:
    _expected = st.secrets.get("app_password", "")
except Exception:
    _expected = ""
if _expected:
    if not st.session_state.get("_authed"):
        st.markdown("### 🐝 PensionBee · Rollover Companion")
        pw = st.text_input("Password", type="password")
        if st.button("Sign in", type="primary"):
            if pw == _expected:
                st.session_state["_authed"] = True
                st.rerun()
            st.error("That's not it — try again.")
        st.stop()

try:
    run_journey_app()
except Exception:
    st.markdown(
        '<div class="pb-snag"><strong>We hit a snag loading this</strong> — '
        "a BeeKeeper can finish it with you.</div>",
        unsafe_allow_html=True,
    )

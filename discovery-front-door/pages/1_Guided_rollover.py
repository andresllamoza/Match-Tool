"""
Guided rollover companion — embedded in Streamlit via iframe.

Requires the Next.js app + API running (see README).
Set ROLLOVER_COMPANION_URL in env or Streamlit secrets to your deployed host.
"""

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from companion_link import companion_site_base, customer_url, embed_url, is_local_companion  # noqa: E402
from ui.brand import inject_brand_css  # noqa: E402
from ui.components import headline, logo_mark  # noqa: E402

st.set_page_config(
    page_title="Guided rollover | PensionBee",
    page_icon="🐝",
    layout="wide",
    initial_sidebar_state="collapsed",
)
inject_brand_css()

_init_employer = st.session_state.get("last_employer", "")
_init_provider = None
_outcome = st.session_state.get("outcome")
if _outcome is not None:
    _init_employer = _outcome.discovery.employer_query or _init_employer
    _init_provider = _outcome.discovery.resolved_provider

logo_mark()
headline(
    "Guided rollover",
    "Step-by-step help to log in, roll over, and track your transfer to PensionBee.",
)

employer = st.text_input(
    "Former employer (optional — pre-fills lookup)",
    value=_init_employer,
    placeholder="e.g. Target, FedEx, Walmart",
)

frame_url = embed_url(employer=employer, provider=_init_provider if employer == _init_employer else None)
tab_url = customer_url(employer=employer, provider=_init_provider if employer == _init_employer else None)

col_a, col_b = st.columns(2)
with col_a:
    st.link_button("Open in new tab →", tab_url, use_container_width=True)
with col_b:
    st.code(tab_url, language=None)

if is_local_companion():
    st.info(
        "Local demo: run `python3 -m uvicorn api.server:app --port 8000` and "
        "`cd rollover-companion/web && npm run dev` before the embed loads."
    )
else:
    st.caption(f"Companion host: {companion_site_base()}")

components.iframe(frame_url, height=780, scrolling=True)

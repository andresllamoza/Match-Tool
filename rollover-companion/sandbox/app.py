"""
PensionBee Rollover Companion — 3-surface Streamlit sandbox.

Run: cd rollover-companion && streamlit run sandbox/app.py

Persistence: journey ID in URL (?jid=…) + SQLite (data/pb_sessions.db).
"""

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sandbox.render_agent import render_agent  # noqa: E402
from sandbox.render_customer import render_customer  # noqa: E402
from sandbox.render_embed import render_embed  # noqa: E402
from sandbox.render_funnel import render_funnel  # noqa: E402
from sandbox.state import act, current_view, load_ctx  # noqa: E402
from sandbox.ui.brand import inject_sandbox_css  # noqa: E402


def _pick(label: str, options: list[str], default: str) -> str:
    try:
        return st.segmented_control(
            label, options, default=default, label_visibility="collapsed"
        )
    except (AttributeError, TypeError):
        return st.radio(
            label,
            options,
            index=options.index(default),
            horizontal=True,
            label_visibility="collapsed",
        )


st.set_page_config(
    page_title="Rollover Sandbox | PensionBee",
    page_icon="🐝",
    layout="wide",
    initial_sidebar_state="collapsed",
)

inject_sandbox_css()

if "show_provider_picker" not in st.session_state:
    st.session_state.show_provider_picker = False

left, right = st.columns([5, 1])
with left:
    st.markdown("### PensionBee · Production workspace")
    st.caption("Customer · Agent · Embed — one shared JourneyEngine")
with right:
    if st.button("↺ Fresh", help="Start a new session"):
        act({"type": "restart"})
        st.query_params["fresh"] = "1"
        st.rerun()

layout_mode = _pick("Layout", ["3-column", "Single surface"], "3-column")
surface_pick = _pick("Surface", ["Customer", "Agent", "Embed", "Funnel"], "Customer")

fresh = st.query_params.get("fresh") == "1"
_, welcome_back = load_ctx(fresh=fresh)
if fresh and "fresh" in st.query_params:
    del st.query_params["fresh"]

view = current_view()

if layout_mode == "3-column":
    col1, col2, col3 = st.columns(3, gap="medium")
    with col1:
        st.markdown('<p class="sandbox-surface-label">Customer flow</p>', unsafe_allow_html=True)
        render_customer(view, welcome_back=welcome_back)
    with col2:
        st.markdown('<p class="sandbox-surface-label">Agent view</p>', unsafe_allow_html=True)
        render_agent(view)
    with col3:
        st.markdown('<p class="sandbox-surface-label">Embed showcase</p>', unsafe_allow_html=True)
        render_embed(view, theme=st.session_state.get("embed_theme_radio", "default"))
else:
    if surface_pick == "Customer":
        render_customer(view, welcome_back=welcome_back)
    elif surface_pick == "Agent":
        render_agent(view)
    elif surface_pick == "Embed":
        render_embed(view, theme="default")
    else:
        render_funnel()

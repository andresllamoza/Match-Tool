"""Dev only: embed the Next.js /embed route when running locally with npm run dev."""

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from companion_link import companion_site_base, embed_url, is_local_companion  # noqa: E402

st.set_page_config(page_title="Next.js embed (dev)", layout="wide")
st.title("Next.js embed (development)")
st.caption("Production Streamlit Cloud uses the native Home page — same engine, no iframe.")

employer = st.text_input("Employer prefill", placeholder="Target")
url = embed_url(employer=employer)
st.code(url)
if is_local_companion():
    st.warning("Requires `npm run dev` in web/ and API on :8000")
components.iframe(url, height=720, scrolling=True)

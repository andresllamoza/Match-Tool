"""Streamlit UI for linking / embedding the rollover companion."""

from __future__ import annotations

import streamlit as st
import streamlit.components.v1 as components

from companion_link import companion_site_base, customer_url, embed_url, is_local_companion


def render_companion_handoff(
    *,
    employer: str,
    provider: str | None,
    embed_inline: bool = False,
) -> None:
    tab_url = customer_url(employer=employer, provider=provider)
    frame_url = embed_url(employer=employer, provider=provider)

    st.link_button(
        "Open guided rollover (new tab) →",
        tab_url,
        type="primary",
        use_container_width=True,
    )

    try:
        if st.button("Continue in Rollover Companion (Home)", use_container_width=True):
            st.session_state.pending_lookup = employer
            st.switch_page("app.py")
    except Exception:
        st.markdown(f"[Continue in Rollover Companion]({tab_url})")

    with st.expander("Copy link or embed URL"):
        st.code(tab_url, language=None)
        st.caption(f"Embed iframe src: {frame_url}")
        st.caption(f"Companion host: {companion_site_base()}")

    if is_local_companion():
        st.caption(
            "Local: start API on :8000 and `npm run dev` in web/ before opening."
        )

    if embed_inline:
        st.markdown("##### Rollover companion")
        components.iframe(frame_url, height=720, scrolling=True)

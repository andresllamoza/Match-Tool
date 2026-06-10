"""Streamlit widget helpers — version-safe buttons + forms."""

from __future__ import annotations

import html

import streamlit as st


def primary_button(label: str, *, key: str | None = None, use_container_width: bool = True) -> bool:
    kwargs: dict = {"use_container_width": use_container_width}
    if key:
        kwargs["key"] = key
    try:
        return st.button(label, type="primary", **kwargs)
    except TypeError:
        return st.button(label, **kwargs)


def secondary_button(label: str, *, key: str, use_container_width: bool = True) -> bool:
    kwargs: dict = {"key": key, "use_container_width": use_container_width}
    try:
        return st.button(label, type="secondary", **kwargs)
    except TypeError:
        return st.button(label, **kwargs)


def form_submit_primary(label: str) -> bool:
    try:
        return st.form_submit_button(label, type="primary", use_container_width=True)
    except TypeError:
        return st.form_submit_button(label, use_container_width=True)


def text_link_button(label: str, *, key: str) -> bool:
    """Chevron text-link escape hatch (find screen secondary actions)."""
    try:
        return st.button(label, type="tertiary", key=key, use_container_width=True)
    except TypeError:
        return st.button(label, key=key, use_container_width=True)


def option_caption(text: str) -> None:
    """Muted helper line tucked under an option button (4px gap via CSS)."""
    st.markdown(f'<p class="opt-caption">{html.escape(text)}</p>', unsafe_allow_html=True)


def option_card(
    title: str,
    *,
    key: str,
    caption: str | None = None,
    primary: bool = False,
) -> bool:
    """Single-line choice button + optional caption — never stack title+description in the label."""
    clicked = primary_button(title, key=key) if primary else secondary_button(title, key=key)
    if caption:
        option_caption(caption)
    return clicked


def icon_button(label: str, *, key: str, help: str | None = None) -> bool:
    """Compact header icon button (e.g. journey restart)."""
    kwargs: dict = {"key": key}
    if help:
        kwargs["help"] = help
    try:
        return st.button(label, type="tertiary", **kwargs)
    except TypeError:
        return st.button(label, **kwargs)

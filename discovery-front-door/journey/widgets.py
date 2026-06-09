"""Streamlit widget helpers — version-safe buttons + forms."""

from __future__ import annotations

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

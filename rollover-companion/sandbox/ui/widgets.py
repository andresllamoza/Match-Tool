from __future__ import annotations

import streamlit as st


def primary_button(label: str, *, key: str) -> bool:
    try:
        return st.button(label, type="primary", key=key, use_container_width=True)
    except TypeError:
        return st.button(label, key=key, use_container_width=True)


def secondary_button(label: str, *, key: str, hint: str | None = None) -> bool:
    text = f"{label}\n\n{hint}" if hint else label
    try:
        return st.button(text, type="secondary", key=key, use_container_width=True)
    except TypeError:
        return st.button(text, key=key, use_container_width=True)


def form_submit(label: str) -> bool:
    try:
        return st.form_submit_button(label, type="primary", use_container_width=True)
    except TypeError:
        return st.form_submit_button(label, use_container_width=True)

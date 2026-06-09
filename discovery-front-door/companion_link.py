"""Build URLs into the Next.js rollover companion (customer + embed routes)."""

from __future__ import annotations

import os
import urllib.parse


def _read_configured_base() -> str:
    try:
        import streamlit as st

        if hasattr(st, "secrets") and "ROLLOVER_COMPANION_URL" in st.secrets:
            return str(st.secrets["ROLLOVER_COMPANION_URL"]).strip().rstrip("/")
    except Exception:
        pass
    return os.environ.get("ROLLOVER_COMPANION_URL", "http://localhost:3000").strip().rstrip("/")


def companion_site_base() -> str:
    """Origin + optional port, without /customer or /embed path."""
    base = _read_configured_base()
    for suffix in ("/customer", "/embed"):
        if base.endswith(suffix):
            return base[: -len(suffix)]
    return base


def customer_url(*, employer: str = "", provider: str | None = None) -> str:
    params: dict[str, str] = {}
    if employer.strip():
        params["employer"] = employer.strip()
    if provider:
        params["provider"] = provider
    qs = urllib.parse.urlencode(params)
    url = f"{companion_site_base()}/customer"
    return f"{url}?{qs}" if qs else url


def embed_url(*, employer: str = "", provider: str | None = None) -> str:
    params: dict[str, str] = {}
    if employer.strip():
        params["employer"] = employer.strip()
    if provider:
        params["provider"] = provider
    qs = urllib.parse.urlencode(params)
    url = f"{companion_site_base()}/embed"
    return f"{url}?{qs}" if qs else url


def is_local_companion() -> bool:
    base = companion_site_base().lower()
    return "localhost" in base or "127.0.0.1" in base

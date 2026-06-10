"""Phone-step customer surface: no jargon, no false-error patterns."""

from __future__ import annotations

import re

import streamlit as st

from journey.engine_bridge import apply_action, get_engine, current_view, save_context
from journey.render import _render_channel_context
from ui.channel_step import call_card, call_script_card


class _SS(dict):
    def __getattr__(self, k):
        return self.get(k)

    def __setattr__(self, k, v):
        self[k] = v

    def pop(self, k, default=None):
        return dict.pop(self, k, default)


_JARGON = re.compile(
    r"participant|pattern|expectation|mechanism|participant-forward|Direct-to-PensionBee",
    re.I,
)
_ERROR_COPY = re.compile(r"went wrong|on our side|Something went wrong", re.I)


def _phone_view(provider: str):
    get_engine()
    save_context(get_engine().start())
    assert not isinstance(apply_action({"type": "provider_direct", "provider": provider}), str)
    for action in (
        {"type": "access", "can_login": True},
        {"type": "tax_type", "tax_type": "traditional"},
        {"type": "channel", "channel": "phone"},
    ):
        result = apply_action(action)
        assert not isinstance(result, str), result
    return current_view()


def test_phone_step_renders_without_exception(monkeypatch):
    monkeypatch.setattr(st, "session_state", _SS())
    st.session_state = _SS()
    st.query_params = {}
    st.cache_resource = lambda f: f
    monkeypatch.setattr(st, "markdown", lambda *a, **k: None)

    view = _phone_view("Empower")
    _render_channel_context(view)


def test_phone_step_html_has_no_jargon_or_error_copy():
    view = _phone_view("Vanguard")
    html_parts = [
        call_card(view.enrichment.channel_context.phone or ""),
        call_script_card("phone", view.enrichment.channel_context.say_this),
    ]
    blob = " ".join(html_parts)
    assert not _JARGON.search(blob)
    assert not _ERROR_COPY.search(blob)
    assert "call-card-num" in blob
    assert "SAY THIS" in blob
    assert "📞" not in blob


def test_customer_screen_edge_cases_not_in_channel_copy():
    view = _phone_view("Vanguard")
    assert view.screen.edge_cases, "fixture should have edge_cases in engine"
    for ec in view.screen.edge_cases:
        assert _JARGON.search(ec), "edge_cases in knowledge should still exist for BeeKeeper"

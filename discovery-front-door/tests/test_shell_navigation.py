"""App shell: go_back bridge + footer resolution."""

from __future__ import annotations

import streamlit as st

from engine.models import JourneyChannel, JourneyState
from journey.engine_bridge import apply_action, get_engine, save_context
from ui.shell import resolve_footer, show_back_button


class _SS(dict):
    def __getattr__(self, k):
        return self.get(k)

    def __setattr__(self, k, v):
        self[k] = v

    def pop(self, k, default=None):
        return dict.pop(self, k, default)


def _walk_to_channel(provider: str = "Fidelity"):
    get_engine()
    save_context(get_engine().start())
    apply_action({"type": "provider_direct", "provider": provider})
    apply_action({"type": "access", "can_login": True})
    apply_action({"type": "tax_type", "tax_type": "pre_tax"})
    return apply_action({"type": "channel", "channel": "online"})


def test_go_back_via_bridge():
    result = _walk_to_channel()
    assert not isinstance(result, str)
    assert result.ctx.state == JourneyState.ONLINE_IN_PROGRESS
    back = apply_action({"type": "go_back"})
    assert not isinstance(back, str)
    assert back.ctx.state == JourneyState.ACCESS_RECOVERED
    assert back.ctx.channel is None


def test_footer_primary_on_channel_step():
    result = _walk_to_channel()
    assert not isinstance(result, str)
    spec = resolve_footer(result)
    assert spec is not None
    assert spec.primary is not None
    assert spec.primary.action == {"type": "step", "outcome": "done"}


def test_back_hidden_on_fresh_find(monkeypatch):
    monkeypatch.setattr(st, "session_state", _SS())
    st.session_state = _SS(show_provider_picker=False, employer_draft="")
    get_engine()
    save_context(get_engine().start())
    from journey.engine_bridge import current_view

    view = current_view()
    assert view.ctx.state == JourneyState.PROVIDER_UNKNOWN
    assert show_back_button(view) is False

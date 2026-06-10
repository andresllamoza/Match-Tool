"""Full shell acceptance walk — every state, Back + footer primary."""

from __future__ import annotations

import json

import pytest
import streamlit as st

from engine.models import JourneyChannel, JourneyContext, JourneyState
from journey.engine_bridge import apply_action, get_engine, save_context, current_view
from ui.shell import resolve_footer, show_back_button


class _SS(dict):
    def __getattr__(self, k):
        return self.get(k)

    def __setattr__(self, k, v):
        self[k] = v

    def pop(self, k, default=None):
        return dict.pop(self, k, default)


def _assert_ok(result):
    assert not isinstance(result, str), result
    return result


def _fresh():
    get_engine()
    save_context(get_engine().start())


def _to_access(provider: str = "Fidelity", *, can_login: bool = True):
    _fresh()
    _assert_ok(apply_action({"type": "provider_direct", "provider": provider}))
    _assert_ok(apply_action({"type": "access", "can_login": can_login}))
    return current_view()


def _to_tax(provider: str = "Fidelity"):
    view = _to_access(provider)
    _assert_ok(apply_action({"type": "tax_type", "tax_type": "pre_tax"}))
    return current_view()


def _to_channel(channel: str, provider: str = "Fidelity"):
    _to_tax(provider)
    return _assert_ok(apply_action({"type": "channel", "channel": channel}))


def _advance_to_initiated(channel: str = "online", provider: str = "Fidelity"):
    view = _to_channel(channel, provider)
    engine = get_engine()
    while view.ctx.state in {
        JourneyState.ONLINE_IN_PROGRESS,
        JourneyState.PHONE_IN_PROGRESS,
        JourneyState.FORMS_IN_PROGRESS,
    }:
        view = _assert_ok(apply_action({"type": "step", "outcome": "done"}))
    assert view.ctx.state == JourneyState.INITIATED
    return view


@pytest.mark.parametrize("can_login", [True, False])
def test_access_yes_and_no_paths(can_login):
    view = _to_access("Empower", can_login=can_login)
    expected = JourneyState.ACCESS_RECOVERED if can_login else JourneyState.ACCESS_BLOCKED
    assert view.ctx.state == expected
    spec = resolve_footer(view)
    if can_login:
        assert spec.primary is None  # tax choice cards in body
    else:
        assert spec.primary is not None


@pytest.mark.parametrize("channel", ["online", "phone", "forms"])
def test_channel_paths_have_sticky_primary(channel):
    view = _to_channel(channel, "Vanguard")
    state_map = {
        "online": JourneyState.ONLINE_IN_PROGRESS,
        "phone": JourneyState.PHONE_IN_PROGRESS,
        "forms": JourneyState.FORMS_IN_PROGRESS,
    }
    assert view.ctx.state == state_map[channel]
    spec = resolve_footer(view)
    assert spec.primary is not None
    assert spec.primary.action == {"type": "step", "outcome": "done"}


def test_stuck_path_and_back():
    view = _to_channel("phone", "Voya")
    before_stuck = get_engine()._snapshot(view.ctx)
    _assert_ok(apply_action({"type": "step", "outcome": "stuck"}))
    view = current_view()
    assert view.ctx.state == JourneyState.STUCK
    spec = resolve_footer(view)
    assert spec.primary is not None
    _assert_ok(apply_action({"type": "go_back"}))
    view = current_view()
    assert view.ctx.state == before_stuck.state
    assert view.ctx.step_index == before_stuck.step_index
    assert view.ctx.state == JourneyState.PHONE_IN_PROGRESS


def test_initiated_in_flight_complete():
    view = _advance_to_initiated("online")
    spec = resolve_footer(view)
    assert spec.primary.action == {"type": "confirm_in_flight"}
    _assert_ok(apply_action({"type": "confirm_in_flight"}))
    view = current_view()
    assert view.ctx.state == JourneyState.IN_FLIGHT
    spec = resolve_footer(view)
    assert spec.primary.action == {"type": "mark_complete"}
    _assert_ok(apply_action({"type": "mark_complete"}))
    view = current_view()
    assert view.ctx.state == JourneyState.COMPLETE
    spec = resolve_footer(view)
    assert spec.primary.action == {"type": "restart"}
    assert show_back_button(view) is False


def test_provider_not_covered_and_escalated():
    _fresh()
    _assert_ok(apply_action({"type": "lookup", "employer": "Uncovered Demo Corp"}))
    view = current_view()
    assert view.ctx.state == JourneyState.PROVIDER_NOT_COVERED
    spec = resolve_footer(view)
    assert any(s.action.get("type") == "handoff" for s in spec.secondaries)
    _assert_ok(apply_action({"type": "handoff", "reason": "provider_not_covered"}))
    view = current_view()
    assert view.ctx.state == JourneyState.ESCALATED
    assert show_back_button(view) is True
    _assert_ok(apply_action({"type": "go_back"}))
    assert current_view().ctx.state == JourneyState.PROVIDER_NOT_COVERED


def test_disambiguation_back(monkeypatch):
    monkeypatch.setattr(st, "session_state", _SS())
    st.session_state = _SS(show_provider_picker=False, employer_draft="")
    _fresh()
    _assert_ok(apply_action({"type": "lookup", "employer": "Costco"}))
    view = current_view()
    if view.screen.disambiguation_options:
        _assert_ok(
            apply_action({"type": "disambiguate", "answer": view.screen.disambiguation_options[0]})
        )
        _assert_ok(apply_action({"type": "go_back"}))
        assert current_view().ctx.disambiguation_question


def test_post_rehydration_back():
    _to_channel("online", "Fidelity")
    view = current_view()
    raw = json.loads(view.ctx.model_dump_json())
    reloaded = JourneyContext.model_validate(raw)
    assert reloaded.history_stack
    engine = get_engine()
    save_context(reloaded)
    _assert_ok(apply_action({"type": "go_back"}))
    restored = current_view()
    assert restored.ctx.state == JourneyState.ACCESS_RECOVERED
    assert restored.ctx.channel is None


def test_provider_unknown_fresh_no_back(monkeypatch):
    monkeypatch.setattr(st, "session_state", _SS())
    st.session_state = _SS(show_provider_picker=False, employer_draft="")
    _fresh()
    view = current_view()
    assert view.ctx.state == JourneyState.PROVIDER_UNKNOWN
    assert show_back_button(view) is False
    spec = resolve_footer(view, find_surface="employer_form")
    assert spec.primary is None

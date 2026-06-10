"""Find step: low-confidence lookups must surface disambiguation (e.g. google)."""

from __future__ import annotations

import os

import pytest

from journey.engine_bridge import apply_action, get_engine, save_context
from journey.render import _find_surface
from engine.models import JourneyState


@pytest.fixture(autouse=True)
def _force_synthetic(monkeypatch):
    monkeypatch.setenv("USE_SYNTHETIC", "1")
    get_engine.clear()


def _fresh():
    ctx = get_engine().start()
    save_context(ctx)
    return ctx


def test_google_lookup_sets_disambiguation():
    _fresh()
    result = apply_action({"type": "lookup", "employer": "google"})
    assert not isinstance(result, str)
    assert result.ctx.state == JourneyState.PROVIDER_UNKNOWN
    assert result.screen.disambiguation_question
    assert len(result.screen.disambiguation_options) >= 2


def test_find_surface_prefers_disambiguation_over_form():
    _fresh()
    view = apply_action({"type": "lookup", "employer": "google"})
    assert not isinstance(view, str)

    class SS(dict):
        def __getattr__(self, k):
            return self.get(k)

        def __setattr__(self, k, v):
            self[k] = v

    import journey.render as jr

    jr.st.session_state = SS(show_provider_picker=False)
    assert _find_surface(view) == "disambiguation"

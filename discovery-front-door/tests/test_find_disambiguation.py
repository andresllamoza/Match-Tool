"""Find step: employer name resolves to recordkeeper (e.g. google → Vanguard)."""

from __future__ import annotations

import pytest

from journey.engine_bridge import apply_action, get_engine, save_context
from engine.models import JourneyState


@pytest.fixture(autouse=True)
def _clear_engine_cache():
    get_engine.clear()
    yield
    get_engine.clear()


def _fresh():
    ctx = get_engine().start()
    save_context(ctx)
    return ctx


def test_google_resolves_to_vanguard():
    _fresh()
    result = apply_action({"type": "lookup", "employer": "google"})
    assert not isinstance(result, str)
    assert result.ctx.state == JourneyState.PROVIDER_IDENTIFIED
    assert result.ctx.provider == "Vanguard"
    assert "Vanguard" in result.screen.headline


def test_google_alias_case_insensitive():
    _fresh()
    for name in ("Google", "GOOGLE", "alphabet"):
        save_context(get_engine().start())
        result = apply_action({"type": "lookup", "employer": name})
        assert not isinstance(result, str)
        assert result.ctx.provider == "Vanguard", name

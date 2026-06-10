"""Every find-step action: employer lookup, picker, restart, and full happy path."""

from __future__ import annotations

import pytest

from journey.engine_bridge import apply_action, get_engine, save_context
from engine.models import JourneyChannel, JourneyState


@pytest.fixture(autouse=True)
def _clear_engine():
    get_engine.clear()
    yield
    get_engine.clear()


def _fresh():
    save_context(get_engine().start())


@pytest.mark.parametrize(
    "employer,expected_provider",
    [
        ("google", "Vanguard"),
        ("Google", "Vanguard"),
        ("Target", "Alight Solutions"),
        ("target", "Alight Solutions"),
        ("FedEx", "Vanguard"),
        ("Walmart", "Merrill Lynch"),
    ],
)
def test_employer_lookup_advances_to_access(employer: str, expected_provider: str):
    _fresh()
    result = apply_action({"type": "lookup", "employer": employer})
    assert not isinstance(result, str), result
    assert result.ctx.state == JourneyState.PROVIDER_IDENTIFIED
    assert result.ctx.provider == expected_provider
    assert result.screen.headline
    assert "log in" in result.screen.headline.lower()


def test_empty_employer_stays_on_find():
    _fresh()
    result = apply_action({"type": "lookup", "employer": "   "})
    assert not isinstance(result, str)
    assert result.ctx.state == JourneyState.PROVIDER_UNKNOWN


def test_unknown_employer_stays_on_find():
    _fresh()
    result = apply_action({"type": "lookup", "employer": "Zzzzz Nonexistent Employer 99999"})
    assert not isinstance(result, str)
    assert result.ctx.state == JourneyState.PROVIDER_UNKNOWN
    assert result.ctx.provider is None


def test_provider_picker_direct():
    _fresh()
    result = apply_action({"type": "provider_direct", "provider": "Vanguard"})
    assert not isinstance(result, str)
    assert result.ctx.state == JourneyState.PROVIDER_IDENTIFIED
    assert result.ctx.provider == "Vanguard"


def test_restart_from_mid_journey():
    _fresh()
    apply_action({"type": "lookup", "employer": "google"})
    result = apply_action({"type": "restart"})
    assert not isinstance(result, str)
    assert result.ctx.state == JourneyState.PROVIDER_UNKNOWN


def test_google_full_button_path_to_online_channel():
    """Simulates: search → yes login → pre-tax → online → first step."""
    _fresh()
    r = apply_action({"type": "lookup", "employer": "google"})
    assert r.ctx.provider == "Vanguard"

    r = apply_action({"type": "access", "can_login": True})
    assert r.ctx.state == JourneyState.ACCESS_RECOVERED

    r = apply_action({"type": "tax_type", "tax_type": "pre_tax"})
    assert r.ctx.state == JourneyState.ACCESS_RECOVERED

    r = apply_action({"type": "channel", "channel": "online"})
    assert r.ctx.state == JourneyState.ONLINE_IN_PROGRESS
    assert r.ctx.channel == JourneyChannel.ONLINE
    assert r.screen.primary_action


def test_access_no_path():
    _fresh()
    apply_action({"type": "lookup", "employer": "google"})
    r = apply_action({"type": "access", "can_login": False})
    assert r.ctx.state == JourneyState.ACCESS_BLOCKED


def test_disambiguate_action_selects_provider():
    _fresh()
    r = apply_action({"type": "disambiguate", "answer": "Fidelity"})
    assert not isinstance(r, str)
    assert r.ctx.state == JourneyState.PROVIDER_IDENTIFIED
    assert r.ctx.provider == "Fidelity"

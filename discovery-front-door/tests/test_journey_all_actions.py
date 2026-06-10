"""Engine bridge: every Streamlit button maps to a valid transition."""

from __future__ import annotations

from journey.engine_bridge import apply_action, get_engine, save_context
from engine.models import JourneyChannel, JourneyState


def _fresh():
    ctx = get_engine().start()
    save_context(ctx)
    return ctx


def test_lookup_and_provider_direct():
    _fresh()
    r = apply_action({"type": "lookup", "employer": "Target"})
    assert not isinstance(r, str)
    assert r.ctx.state == JourneyState.PROVIDER_IDENTIFIED

    _fresh()
    r = apply_action({"type": "provider_direct", "provider": "Fidelity"})
    assert r.ctx.state == JourneyState.PROVIDER_IDENTIFIED


def test_access_tax_channel_step_track():
    _fresh()
    apply_action({"type": "provider_direct", "provider": "Fidelity"})
    r = apply_action({"type": "access", "can_login": True})
    assert r.ctx.state == JourneyState.ACCESS_RECOVERED

    apply_action({"type": "tax_type", "tax_type": "pre_tax"})
    r = apply_action({"type": "channel", "channel": "online"})
    assert r.ctx.state == JourneyState.ONLINE_IN_PROGRESS

    while r.ctx.state == JourneyState.ONLINE_IN_PROGRESS:
        r = apply_action({"type": "step", "outcome": "done"})

    r = apply_action({"type": "confirm_in_flight"})
    assert r.ctx.state == JourneyState.IN_FLIGHT

    r = apply_action({"type": "mark_complete"})
    assert r.ctx.state == JourneyState.COMPLETE


def test_stuck_resume_escalate_restart():
    _fresh()
    apply_action({"type": "provider_direct", "provider": "Voya"})
    apply_action({"type": "access", "can_login": True})
    apply_action({"type": "tax_type", "tax_type": "pre_tax"})
    apply_action({"type": "channel", "channel": "online"})
    apply_action({"type": "step", "outcome": "stuck"})
    r = apply_action({"type": "resume"})
    assert r.ctx.state == JourneyState.ONLINE_IN_PROGRESS

    r = apply_action({"type": "step", "outcome": "stuck"})
    assert not isinstance(r, str)
    assert r.ctx.state == JourneyState.ESCALATED

    r = apply_action({"type": "restart"})
    assert r.ctx.state == JourneyState.PROVIDER_UNKNOWN


def test_handoff_and_access_blocked():
    _fresh()
    apply_action({"type": "lookup", "employer": "Uncovered Demo Corp"})
    r = apply_action({"type": "handoff", "reason": "provider_not_covered"})
    assert r.ctx.state == JourneyState.ESCALATED

    _fresh()
    apply_action({"type": "provider_direct", "provider": "Fidelity"})
    r = apply_action({"type": "access", "can_login": False})
    assert r.ctx.state == JourneyState.ACCESS_BLOCKED
    r = apply_action({"type": "access_recovered"})
    assert r.ctx.state == JourneyState.ACCESS_RECOVERED

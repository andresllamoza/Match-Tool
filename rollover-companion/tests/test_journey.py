import json

import pytest

from engine.journey import InvalidTransitionError, JourneyEngine, valid_transitions
from engine.models import JourneyChannel, JourneyState


def test_all_transitions_have_valid_endpoints():
    states = set(JourneyState)
    for src, _action, dst in valid_transitions():
        assert src in states
        assert dst in states


def test_invalid_transition_raises(engine):
    ctx = engine.start()
    with pytest.raises(InvalidTransitionError):
        engine.submit_access(ctx, can_login=True)


def test_full_online_journey(engine):
    ctx = engine.start()
    engine.set_provider_direct(ctx, "Fidelity")
    engine.submit_access(ctx, can_login=True)
    engine.submit_tax_type(ctx, "pre_tax")
    engine.choose_channel(ctx, JourneyChannel.ONLINE)
    while ctx.state == JourneyState.ONLINE_IN_PROGRESS:
        engine.advance_step(ctx, "done")
    assert ctx.state == JourneyState.INITIATED
    engine.confirm_in_flight(ctx)
    assert ctx.state == JourneyState.IN_FLIGHT
    engine.mark_complete(ctx)
    assert ctx.state == JourneyState.COMPLETE


def test_access_blocked_path(engine):
    ctx = engine.start()
    engine.set_provider_direct(ctx, "Empower")
    engine.submit_access(ctx, can_login=False)
    assert ctx.state == JourneyState.ACCESS_BLOCKED
    screen = engine.render(ctx)
    assert "Empower" in screen.headline
    engine.submit_access_recovered(ctx)
    assert ctx.state == JourneyState.ACCESS_RECOVERED


def test_tax_routing_escalation(engine):
    ctx = engine.start()
    engine.set_provider_direct(ctx, "Vanguard")
    screen = engine.set_flag(ctx, "pre_tax_to_roth", True)
    assert ctx.state == JourneyState.ESCALATED
    assert "BeeKeeper" in screen.body or screen.next_beekeeper_script


def test_pre_tax_to_roth_tax_selection_escalates(engine):
    ctx = engine.start()
    engine.set_provider_direct(ctx, "Vanguard")
    engine.submit_access(ctx, can_login=True)
    screen = engine.submit_tax_type(ctx, "pre_tax_to_roth")
    assert ctx.state == JourneyState.ESCALATED


def test_stuck_then_escalate(engine):
    ctx = engine.start()
    engine.set_provider_direct(ctx, "Voya")
    engine.submit_access(ctx, can_login=True)
    engine.submit_tax_type(ctx, "pre_tax")
    engine.choose_channel(ctx, JourneyChannel.PHONE)
    engine.advance_step(ctx, "stuck")
    assert ctx.state == JourneyState.STUCK
    engine.escalate(ctx, "user_requested")
    assert ctx.state == JourneyState.ESCALATED


def test_reconstructed_steps_flagged(engine):
    ctx = engine.start()
    engine.set_provider_direct(ctx, "Vanguard")
    engine.submit_access(ctx, can_login=False)
    screen = engine.render(ctx)
    assert screen.has_reconstructed_content or any(g.reconstructed for g in screen.guidance)


def test_journey_events_logged(engine, tmp_logs):
    ctx = engine.start()
    engine.set_provider_direct(ctx, "Fidelity")
    lines = tmp_logs.journey_path.read_text().strip().splitlines()
    assert len(lines) >= 1
    record = json.loads(lines[-1])
    assert record["event_type"] == "journey"
    assert record["provider"] == "Fidelity"


def test_lookup_logs_comparison(engine, tmp_logs):
    ctx = engine.start()
    engine.lookup_employer(ctx, "Amazon.com Services LLC")
    lines = tmp_logs.comparison_path.read_text().strip().splitlines()
    assert len(lines) == 1
    record = json.loads(lines[0])
    assert record["event_type"] == "comparison"
    assert record["agreement"] is True
    assert record["matcher_result"] == "Fidelity"

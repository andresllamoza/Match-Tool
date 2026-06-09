"""v2 engine requirements — walk scenarios, handoffs, data registry, guardrails."""

from __future__ import annotations

import re

from engine.data_needed import keys_still_needed, report, resolve
from engine.funnel import load_funnel_summary
from engine.journey import JourneyEngine
from engine.models import JourneyChannel, JourneyState
from engine.walk import walk_employer


VERBATIM_CITI = [
    "PensionBee FBO [User's Full Name]",
    "PO Box 72, New York, NY 10272",
    "7–10 business days",
]


def test_walk_amazon_fidelity_online(engine, knowledge):
    result = walk_employer(engine, "Amazon.com Services LLC", verbose=False)
    assert result["provider"] == "Fidelity"
    assert result["channel"] == "online"
    assert result["state"] == "complete"
    fidelity = knowledge.get("Fidelity")
    access_steps = fidelity.access_recovery.reset_steps + fidelity.access_recovery.first_time_setup_steps
    assert any(s.source_status.value == "reconstructed" for s in access_steps)


def test_walk_walmart_provider_not_covered(engine):
    result = walk_employer(engine, "Walmart", verbose=False)
    assert result["state"] == "provider_not_covered"
    assert result["uncovered_provider"] == "Merrill Lynch"
    assert "BeeKeeper" in result["rendered_text"]


def test_walk_citi_forms_verbatim_strings(engine):
    result = walk_employer(engine, "Citi", channel=JourneyChannel.FORMS, verbose=False)
    assert result["provider"] == "Citi"
    assert result["channel"] == "forms"
    for phrase in VERBATIM_CITI:
        assert phrase in result["rendered_text"]


def test_data_needed_only_brand_hexes():
    still = keys_still_needed()
    assert set(still) == {"BRAND_HEX_BLUE", "BRAND_HEX_CREAM", "BRAND_HEX_INK"}
    assert "BRAND_HEX_CREAM" in report()


def test_data_needed_never_emits_placeholders():
    for key in keys_still_needed():
        value, _pending = resolve(key)
        assert "{{" not in value
        assert "}}" not in value


def test_stuck_twice_auto_escalates(engine):
    ctx = engine.start()
    engine.set_provider_direct(ctx, "Voya")
    engine.submit_access(ctx, can_login=True)
    engine.submit_tax_type(ctx, "pre_tax")
    engine.choose_channel(ctx, JourneyChannel.ONLINE)
    engine.advance_step(ctx, "stuck")
    assert ctx.state == JourneyState.STUCK
    assert ctx.stuck_count == 1
    engine.resume_from_stuck(ctx)
    engine.advance_step(ctx, "stuck")
    assert ctx.state == JourneyState.ESCALATED
    assert ctx.stuck_count == 2


def test_provider_not_covered_handoff_events(engine, tmp_logs):
    ctx = engine.start()
    engine.lookup_employer(ctx, "Walmart Inc")
    assert ctx.state == JourneyState.PROVIDER_NOT_COVERED
    engine.take_handoff(ctx)
    assert ctx.state == JourneyState.ESCALATED
    lines = tmp_logs.journey_path.read_text().strip().splitlines()
    actions = [__import__("json").loads(line)["action"] for line in lines]
    assert actions.count("handoff_offered") >= 1
    assert "handoff_taken" in actions


def test_promo_on_find_screen(engine):
    ctx = engine.start()
    screen = engine.render(ctx)
    assert "1%" in screen.body


def test_promo_on_complete_screen(engine):
    ctx = engine.start()
    engine.set_provider_direct(ctx, "Fidelity")
    engine.submit_access(ctx, can_login=True)
    engine.submit_tax_type(ctx, "pre_tax")
    engine.choose_channel(ctx, JourneyChannel.ONLINE)
    while ctx.state == JourneyState.ONLINE_IN_PROGRESS:
        engine.advance_step(ctx, "done")
    engine.confirm_in_flight(ctx)
    screen = engine.mark_complete(ctx)
    assert "1%" in screen.body


def test_no_unresolved_keys_in_rendered_surfaces(engine):
    ctx = engine.start()
    screens = [engine.render(ctx)]
    engine.lookup_employer(ctx, "Citi")
    screens.append(engine.render(ctx))
    engine.submit_access(ctx, can_login=True)
    engine.submit_tax_type(ctx, "pre_tax")
    engine.choose_channel(ctx, JourneyChannel.FORMS)
    while ctx.state == JourneyState.FORMS_IN_PROGRESS:
        screens.append(engine.render(ctx))
        engine.advance_step(ctx, "done")
    screens.append(engine.render(ctx))
    combined = " ".join(s.headline + " " + s.body for s in screens)
    assert not re.search(r"\{\{[A-Z0-9_]+\}\}", combined)


def test_citi_sla_slower_than_general(engine, knowledge):
    citi = knowledge.get("Citi")
    general = knowledge.general_guide.typical_processing_time
    assert "7–10" in citi.sla_note
    assert "2" in general or "4" in general


def test_funnel_counts_handoff_and_not_covered(engine, tmp_logs):
    walk_employer(engine, "Walmart", verbose=False)
    summary = load_funnel_summary(tmp_logs.journey_path)
    assert summary.provider_not_covered_count >= 1
    assert summary.handoff_offered_count >= 1


def test_walmart_lookup_uncovered(lookup_service):
    outcome = lookup_service.lookup("Walmart Inc")
    assert outcome.uncovered_provider == "Merrill Lynch"
    assert outcome.resolved_provider is None

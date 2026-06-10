from engine.enrichment import build_enrichment
from engine.journey import JourneyEngine
from engine.models import JourneyChannel, JourneyState


def test_phone_channel_enrichment_has_rep_questions():
    engine = JourneyEngine()
    ctx = engine.start()
    engine.set_provider_direct(ctx, "Empower")
    engine.submit_access(ctx, can_login=True)
    engine.submit_tax_type(ctx, "pre_tax")
    engine.choose_channel(ctx, JourneyChannel.PHONE)
    screen = engine.render(ctx)
    enrichment = build_enrichment(engine.knowledge, ctx, screen)
    assert enrichment.channel_context is not None
    assert enrichment.channel_context.phone
    assert len(enrichment.channel_context.rep_questions) >= 1
    assert enrichment.channel_context.check_payable


def test_general_online_enrichment_has_payable_and_menu_hints():
    engine = JourneyEngine()
    ctx = engine.start()
    engine.lookup_employer(ctx, "Uncovered Demo Corp")
    engine.submit_access(ctx, can_login=True)
    engine.submit_tax_type(ctx, "pre_tax")
    engine.choose_channel(ctx, JourneyChannel.ONLINE)
    screen = engine.render(ctx)
    enrichment = build_enrichment(engine.knowledge, ctx, screen)
    assert enrichment.general_path is True
    assert enrichment.channel_context is not None
    assert enrichment.channel_context.check_payable
    assert enrichment.channel_context.check_payable == "PensionBee FBO Jordan Rivera"
    assert enrichment.customer_display_name == "Jordan Rivera"
    # Step 1 is login — step 2 should surface withdrawal menu hints
    engine.advance_step(ctx, "done")
    screen = engine.render(ctx)
    enrichment = build_enrichment(engine.knowledge, ctx, screen)
    assert enrichment.channel_context.portal_menu_hints


def test_track_enrichment_follow_up_days():
    engine = JourneyEngine()
    ctx = engine.start()
    engine.set_provider_direct(ctx, "Fidelity")
    engine.submit_access(ctx, can_login=True)
    engine.submit_tax_type(ctx, "pre_tax")
    engine.choose_channel(ctx, JourneyChannel.ONLINE)
    while ctx.state == JourneyState.ONLINE_IN_PROGRESS:
        engine.advance_step(ctx, "done")
    engine.confirm_in_flight(ctx)
    screen = engine.render(ctx)
    enrichment = build_enrichment(engine.knowledge, ctx, screen)
    assert enrichment.track is not None
    assert enrichment.track.follow_up_days == 28

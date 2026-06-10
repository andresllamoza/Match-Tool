"""Post-signup flow: customer name is account-seeded, never prompted in the journey."""

from engine.customer_copy import DEFAULT_FIRST_NAME, DEFAULT_LAST_NAME, SYNTHETIC_CUSTOMER_NAME
from engine.enrichment import build_enrichment
from engine.models import JourneyChannel
from journey.engine_bridge import get_engine


def test_engine_start_seeds_customer_name():
    ctx = get_engine().start()
    assert ctx.customer_first_name == DEFAULT_FIRST_NAME
    assert ctx.customer_last_name == DEFAULT_LAST_NAME


def test_access_recovered_goes_to_tax_not_name():
    engine = get_engine()
    ctx = engine.start()
    engine.set_provider_direct(ctx, "Fidelity")
    engine.submit_access(ctx, can_login=True)
    assert ctx.state.value == "access_recovered"
    assert ctx.customer_first_name == DEFAULT_FIRST_NAME
    screen = engine.render(ctx)
    assert screen.state.value == "access_recovered"


def test_fbo_uses_seeded_name_without_user_input():
    engine = get_engine()
    ctx = engine.start()
    engine.set_provider_direct(ctx, "Empower")
    engine.submit_access(ctx, can_login=True)
    engine.submit_tax_type(ctx, "pre_tax")
    engine.choose_channel(ctx, JourneyChannel.PHONE)
    en = build_enrichment(engine.knowledge, ctx, engine.render(ctx))
    assert en.channel_context.check_payable == f"PensionBee FBO {SYNTHETIC_CUSTOMER_NAME}"

from engine.customer_copy import DEFAULT_FIRST_NAME, DEFAULT_LAST_NAME
from engine.journey import JourneyEngine


def test_start_seeds_demo_customer_name():
    ctx = JourneyEngine().start()
    assert ctx.customer_first_name == DEFAULT_FIRST_NAME
    assert ctx.customer_last_name == DEFAULT_LAST_NAME


def test_start_accepts_production_override():
    ctx = JourneyEngine().start(customer_first_name="Alex", customer_last_name="Chen")
    assert ctx.customer_first_name == "Alex"
    assert ctx.customer_last_name == "Chen"

from discovery.customer_copy import customer_next_copy


def test_prefers_customer_message():
    assert "PensionBee IRA" in customer_next_copy(
        customer_message="Start a direct rollover to your PensionBee IRA.",
        action="Guide the user to start a direct rollover.",
    )


def test_never_surfaces_ops_script():
    out = customer_next_copy(
        customer_message=None,
        action="Guide the user to start a direct rollover to an external IRA in the Vanguard portal.",
    )
    assert "Guide the user" not in out
    assert "Vanguard portal" in out


def test_fallback_when_empty():
    assert "PensionBee" in customer_next_copy(customer_message=None, action=None)

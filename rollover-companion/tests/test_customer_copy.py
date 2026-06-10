from engine.customer_copy import (
    SYNTHETIC_CUSTOMER_NAME,
    customer_full_name,
    format_check_payable,
    is_fbo_payable_line,
)


def test_format_check_payable_replaces_token():
    assert (
        format_check_payable("PensionBee FBO [your name]")
        == f"PensionBee FBO {SYNTHETIC_CUSTOMER_NAME}"
    )


def test_format_check_payable_uses_authenticated_names():
    assert format_check_payable("PensionBee FBO [your name]", "Alex", "Chen") == (
        "PensionBee FBO Alex Chen"
    )
    assert customer_full_name("Alex", "Chen") == "Alex Chen"


def test_is_fbo_payable_line():
    assert is_fbo_payable_line("PensionBee FBO Jordan Rivera")
    assert not is_fbo_payable_line("Payable to you")

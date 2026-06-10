from __future__ import annotations

SYNTHETIC_CUSTOMER_NAME = "Jordan Rivera"
PAYABLE_NAME_TOKEN = "[your name]"


def format_check_payable(
    template: str,
    customer_name: str = SYNTHETIC_CUSTOMER_NAME,
) -> str:
    """Replace the knowledge-layer placeholder with the customer's full name."""
    if not template:
        return template
    return template.replace(PAYABLE_NAME_TOKEN, customer_name)


def is_fbo_payable_line(text: str) -> bool:
    return "fbo" in text.lower() and "pensionbee" in text.lower()

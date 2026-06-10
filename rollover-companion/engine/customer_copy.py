from __future__ import annotations

DEFAULT_FIRST_NAME = "Jordan"
DEFAULT_LAST_NAME = "Rivera"
SYNTHETIC_CUSTOMER_NAME = f"{DEFAULT_FIRST_NAME} {DEFAULT_LAST_NAME}"
PAYABLE_NAME_TOKEN = "[your name]"


def customer_full_name(
    first_name: str | None = None,
    last_name: str | None = None,
) -> str:
    first = (first_name or DEFAULT_FIRST_NAME).strip()
    last = (last_name or DEFAULT_LAST_NAME).strip()
    return f"{first} {last}".strip()


def format_check_payable(
    template: str,
    first_name: str | None = None,
    last_name: str | None = None,
) -> str:
    """Replace the knowledge-layer placeholder with the customer's full name."""
    if not template:
        return template
    return template.replace(PAYABLE_NAME_TOKEN, customer_full_name(first_name, last_name))


def is_fbo_payable_line(text: str) -> bool:
    return "fbo" in text.lower() and "pensionbee" in text.lower()

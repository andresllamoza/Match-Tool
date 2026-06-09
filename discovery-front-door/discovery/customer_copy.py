from __future__ import annotations

_OPS_PREFIX = "guide the user to "


def customer_next_copy(*, customer_message: str | None, action: str | None) -> str:
    """Never surface BeeKeeper ops script to customers."""
    msg = (customer_message or "").strip()
    if msg and not msg.lower().startswith("guide the user"):
        return msg

    raw = (action or "").strip()
    if raw.lower().startswith(_OPS_PREFIX):
        rest = raw[len(_OPS_PREFIX) :].strip()
        if rest:
            return rest[0].upper() + rest[1:]

    if raw and not raw.lower().startswith("guide the user"):
        return raw

    return "Log in to your old 401(k) provider and start your rollover to PensionBee."

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DataNeededEntry:
    key: str
    status: str  # "needed" | "provided"
    fallback: str
    usage: str
    note: str = ""


DATA_NEEDED: dict[str, DataNeededEntry] = {
    "BRAND_HEX_CREAM": DataNeededEntry(
        key="BRAND_HEX_CREAM",
        status="needed",
        fallback="#FBF6EC",
        usage="Page background",
        note="[pending verification] — scrape pensionbee.com/us when available",
    ),
    "BRAND_HEX_BLUE": DataNeededEntry(
        key="BRAND_HEX_BLUE",
        status="needed",
        fallback="#0A2540",
        usage="Primary actions and headlines (PensionBee US primary)",
        note="[pending verification] — spec primary brand blue",
    ),
    "BRAND_HEX_INK": DataNeededEntry(
        key="BRAND_HEX_INK",
        status="needed",
        fallback="#1A1A1A",
        usage="Body text",
        note="[pending verification]",
    ),
}


def resolve(key: str) -> tuple[str, bool]:
    """Return (value, is_pending). Never returns unresolved {{KEY}} placeholders."""
    entry = DATA_NEEDED.get(key)
    if not entry:
        return "", False
    pending = entry.status == "needed"
    return entry.fallback, pending


def keys_still_needed() -> list[str]:
    return [k for k, e in DATA_NEEDED.items() if e.status == "needed"]


def report() -> str:
    lines = ["DATA_NEEDED registry", "─" * 40]
    for entry in DATA_NEEDED.values():
        flag = "NEEDED" if entry.status == "needed" else "OK"
        lines.append(f"{entry.key}: {flag}")
        lines.append(f"  fallback: {entry.fallback}")
        lines.append(f"  usage: {entry.usage}")
        if entry.note:
            lines.append(f"  note: {entry.note}")
    still = keys_still_needed()
    lines.append("─" * 40)
    lines.append(f"Still needed: {len(still)} — {', '.join(still) or 'none'}")
    return "\n".join(lines)

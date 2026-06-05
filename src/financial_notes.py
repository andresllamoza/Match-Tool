"""
Recordkeeper facts sourced from Notes to Financial Statements (Schedule H attachment).

DOL FOIA CSVs do not include the narrative Notes text (e.g. "Fidelity is the record
keeper"). This registry holds verified extractions for large plans where Schedule C
service codes 15/64 are missing or misleading.

Add entries after reading the plan's audited Notes (usually PDF page 20+ of the 5500).
"""

from __future__ import annotations

from typing import Any, Optional

# Plans with 5k+ participants typically file Schedule H with attached financials.
LARGE_PLAN_PARTICIPANT_THRESHOLD = 5_000

# Tiers produced when Schedule C Item 2 lacks recordkeeper service codes 15/64.
WEAK_DOL_RECORDKEEPER_TIERS = frozenset({"TIER1_ITEM1", "TIER1_SCH_H", "TIER2"})

FINANCIAL_STATEMENT_NOTES_REGISTRY: dict[str, dict[str, Any]] = {
    "NIKE": {
        "matched_employer_name": "NIKE, INC.",
        "recordkeeper": "Fidelity Workplace Services, LLC",
        "plan_name": "401(K) SAVINGS AND PROFIT SHARING PLAN FOR EMPLOYEES OF NIKE, INC.",
        "plan_year": 2024,
        "plan_participants": 48889,
        "ein": "930584541",
        "plan_type_code": "2E2F2H2J2K2R3F3H",
        "notes_plan_year": "May 31, 2024",
        "quote_recordkeeper": "Fidelity Workplace Services, LLC",
        "quote_trustee": "Northern Trust Company",
    },
}


def default_notes_reason(entry: dict[str, Any]) -> str:
    plan_year = entry.get("notes_plan_year", "the filed plan year")
    rk = entry.get("quote_recordkeeper", entry.get("recordkeeper", "the recordkeeper"))
    parts = [
        "Per the Notes to Financial Statements attached to Schedule H "
        f"(plan year ended {plan_year}): ",
        f'"{rk}" is identified as the record keeper of the Plan.',
    ]
    trustee = entry.get("quote_trustee")
    if trustee:
        parts.append(f'"{trustee}" is the trustee, not the recordkeeper.')
    parts.append(
        "This overrides weaker DOL Schedule C service-code signals for large audited plans."
    )
    return " ".join(parts)


def registry_entry(canonical_employer_key: str) -> Optional[dict[str, Any]]:
    """Return a registry entry for a normalized employer key, if verified."""
    key = (canonical_employer_key or "").strip().upper()
    if not key:
        return None
    return FINANCIAL_STATEMENT_NOTES_REGISTRY.get(key)


def is_large_plan_participants(participant_count: object) -> bool:
    try:
        count = int(float(participant_count or 0))
    except (TypeError, ValueError):
        return False
    return count >= LARGE_PLAN_PARTICIPANT_THRESHOLD


def dol_tier_is_weak(tier: object) -> bool:
    return str(tier or "") in WEAK_DOL_RECORDKEEPER_TIERS


def verification_hint() -> str:
    return (
        "Large plan with no Schedule C recordkeeper codes 15/64 in DOL data — verify "
        "the Notes to Financial Statements (Schedule H attachment) for the named "
        "record keeper."
    )

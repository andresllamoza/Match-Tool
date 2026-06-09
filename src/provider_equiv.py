"""Normalize recordkeeper names and test whether two labels refer to the same provider."""

from __future__ import annotations

import re

# Groups of equivalent recordkeeper labels (uppercase tokens).
PROVIDER_EQUIVALENCE_GROUPS: tuple[frozenset[str], ...] = (
    frozenset({"SCHWAB", "CHARLES SCHWAB", "CHARLES SCHWAB TRUST"}),
    frozenset({"EMPOWER", "EMPOWER RETIREMENT", "GREAT WEST", "GREAT-WEST", "PRUDENTIAL", "PRIAC"}),
    frozenset({"FIDELITY", "FIDELITY INVESTMENTS", "FIDELITY WORKPLACE"}),
    frozenset({"MERRILL", "MERRILL LYNCH", "BANK OF AMERICA MERRILL"}),
    frozenset({"PRINCIPAL", "PRINCIPAL LIFE"}),
    frozenset({"HANCOCK", "JOHN HANCOCK"}),
    frozenset({"ALIGHT", "TEMPO", "TEMPO HOLDING"}),
    frozenset({"VOYA", "ING", "RELIASTAR"}),
    frozenset({"TRANSAMERICA", "WESTERN NATIONAL"}),
    frozenset({"NEWPORT", "NEWPORT GROUP"}),
    frozenset({"LINCOLN", "LINCOLN FINANCIAL"}),
    frozenset({"VANGUARD"}),
)

# Matcher output → rollover playbook canonical provider (four supported guides).
PLAYBOOK_PROVIDER_HINTS: tuple[tuple[frozenset[str], str], ...] = (
    (frozenset({"FIDELITY", "FIDELITY INVESTMENTS", "FIDELITY WORKPLACE"}), "Fidelity"),
    (
        frozenset({"EMPOWER", "EMPOWER RETIREMENT", "GREAT WEST", "GREAT-WEST", "PRUDENTIAL", "PRIAC"}),
        "Empower",
    ),
    (frozenset({"VOYA", "ING", "RELIASTAR"}), "Voya"),
    (frozenset({"VANGUARD"}), "Vanguard"),
)

IGNORED_PROVIDER_VALUES = frozenset(
    {
        "",
        "NA",
        "N A",
        "N/A",
        "NOT SURE",
        "UNKNOWN",
        "NONE",
        "NO MATCH FOUND",
    }
)


def _tokenize_provider(name: str) -> str:
    text = str(name or "").upper().strip()
    text = re.sub(r"[^\w\s&-]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def provider_tokens(name: str) -> frozenset[str]:
    """Return canonical token(s) for a recordkeeper label."""
    text = _tokenize_provider(name)
    if text in IGNORED_PROVIDER_VALUES:
        return frozenset()

    for group in PROVIDER_EQUIVALENCE_GROUPS:
        for label in sorted(group, key=len, reverse=True):
            if label in text or text in label:
                return group

    roots = []
    for token in text.split():
        if len(token) >= 3:
            roots.append(token)
    return frozenset(roots) if roots else frozenset({text})


def providers_equivalent(left: str, right: str) -> bool:
    """True when two recordkeeper labels refer to the same provider family."""
    left_tokens = provider_tokens(left)
    right_tokens = provider_tokens(right)
    if not left_tokens or not right_tokens:
        return False
    if left_tokens & right_tokens:
        return True
    return False


def playbook_provider_hint(recordkeeper: str) -> str | None:
    """
    Map a DOL matcher recordkeeper label to a rollover-playbook provider name.

    Returns None when the label does not map to Fidelity, Empower, Vanguard, or Voya.
    """
    text = _tokenize_provider(recordkeeper)
    if not text or text in IGNORED_PROVIDER_VALUES:
        return None

    tokens = provider_tokens(recordkeeper)
    for group, canonical in PLAYBOOK_PROVIDER_HINTS:
        if tokens & group:
            return canonical
        for label in sorted(group, key=len, reverse=True):
            if label in text:
                return canonical
    return None


def normalize_for_playbook(recordkeeper: str) -> str:
    """Prefer playbook-canonical provider names; otherwise return the matcher label."""
    hint = playbook_provider_hint(recordkeeper)
    return hint or str(recordkeeper or "").strip()


def compare_providers(their_provider: str, our_recordkeeper: str) -> tuple[bool | None, str]:
    """
  Compare CSV Provider vs our tool result.

    Returns (agree, note):
      agree=True/False, or None when their provider is blank/unknown.
    """
    their = _tokenize_provider(their_provider)
    ours = _tokenize_provider(our_recordkeeper)

    if their in IGNORED_PROVIDER_VALUES:
        return None, "their_blank"
    if ours in IGNORED_PROVIDER_VALUES or our_recordkeeper == "No match found":
        return False, "our_no_match"
    if providers_equivalent(their, ours):
        return True, "equivalent"
    if their in ours or ours in their:
        return True, "substring"
    return False, "mismatch"

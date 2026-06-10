"""Batch lookup + path walk across 100 employer queries (synthetic matcher)."""

from __future__ import annotations

import csv
from pathlib import Path

import pytest

from adapters.synthetic_data import SYNTHETIC_EMPLOYERS
from engine.models import JourneyState
from engine.walk import walk_employer

REPO_ROOT = Path(__file__).resolve().parents[2]
RECORDKEEPER_CSV = REPO_ROOT / "data" / "recordkeeper_master.csv"

VALID_POST_LOOKUP = {
    JourneyState.PROVIDER_IDENTIFIED.value,
    JourneyState.PROVIDER_NOT_COVERED.value,
    JourneyState.PROVIDER_UNKNOWN.value,
}


def _employer_queries(limit: int = 100) -> list[str]:
    seen: set[str] = set()
    queries: list[str] = []

    def add(name: str) -> None:
        key = name.strip().lower()
        if not key or key in seen:
            return
        seen.add(key)
        queries.append(name.strip())

    for row in SYNTHETIC_EMPLOYERS:
        add(row["employer"])
        for alias in row.get("aliases", []):
            add(alias)

    if RECORDKEEPER_CSV.exists():
        with RECORDKEEPER_CSV.open(newline="", encoding="utf-8") as fh:
            reader = csv.DictReader(fh)
            for record in reader:
                add(record.get("EMPLOYER", "") or record.get("employer", ""))
                if len(queries) >= limit:
                    break

    if len(queries) < limit:
        for i in range(limit - len(queries)):
            add(f"Synthetic Batch Employer {i + 1} LLC")

    return queries[:limit]


EMPLOYER_BATCH = _employer_queries(100)


@pytest.mark.parametrize("employer", EMPLOYER_BATCH)
def test_lookup_employer_batch_no_crash(engine, employer: str):
    ctx = engine.start()
    screen = engine.lookup_employer(ctx, employer)
    assert screen.headline
    assert ctx.state.value in VALID_POST_LOOKUP


@pytest.mark.parametrize(
    "employer",
    [
        "Amazon.com Services LLC",
        "Walmart",
        "Target",
        "Citi",
        "FedEx Corporation",
        "Uncovered Demo Corp",
        "Northwind Traders",
    ],
)
def test_walk_employer_path_batch(engine, employer: str):
    result = walk_employer(engine, employer, verbose=False)
    assert result["employer"] == employer
    assert result["state"] in {
        JourneyState.COMPLETE.value,
        JourneyState.PROVIDER_UNKNOWN.value,
        JourneyState.PROVIDER_NOT_COVERED.value,
        JourneyState.PROVIDER_IDENTIFIED.value,
        JourneyState.INITIATED.value,
    }
    assert isinstance(result["trail"], list)
    assert result["trail"]

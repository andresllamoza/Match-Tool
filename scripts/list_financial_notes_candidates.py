#!/usr/bin/env python3
"""
List large employers where DOL data lacks Schedule C recordkeeper codes (15/64)
but no financial-statement Notes entry exists yet.

Use this to prioritize reading Notes to Financial Statements on large-company 5500s.

  python scripts/list_financial_notes_candidates.py
  python scripts/list_financial_notes_candidates.py --min-participants 10000 --limit 50
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src import financial_notes  # noqa: E402
from src.matcher import canonicalize_employer, load_dol_data  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--min-participants",
        type=int,
        default=financial_notes.LARGE_PLAN_PARTICIPANT_THRESHOLD,
        help="Minimum plan participants (BOY) on the newest filing row",
    )
    parser.add_argument("--limit", type=int, default=100, help="Max rows to print")
    args = parser.parse_args()

    df = load_dol_data()
    weak = df[df["TIER"].isin(financial_notes.WEAK_DOL_RECORDKEEPER_TIERS)].copy()
    weak["_n"] = pd.to_numeric(weak["_n"], errors="coerce").fillna(0)
    weak = weak.sort_values(["EMPLOYER_NORM", "YEAR", "_n"], ascending=[True, False, False])
    newest = weak.drop_duplicates(subset=["EMPLOYER_NORM"], keep="first")
    newest = newest[newest["_n"] >= args.min_participants]

    registered = set(financial_notes.FINANCIAL_STATEMENT_NOTES_REGISTRY)
    candidates = newest[
        ~newest["EMPLOYER_NORM"].isin(registered)
        & ~newest["EMPLOYER_NORM"].apply(
            lambda norm: financial_notes.registry_entry(norm) is not None
        )
    ]

    columns = [
        "EMPLOYER",
        "PLAN_NAME",
        "RK_CANON",
        "TIER",
        "YEAR",
        "_n",
    ]
    print(
        f"Large plans ({args.min_participants:,}+ participants) with weak DOL recordkeeper "
        f"signal and no Notes registry entry: {len(candidates):,}\n"
    )
    print(candidates[columns].head(args.limit).to_string(index=False))


if __name__ == "__main__":
    main()

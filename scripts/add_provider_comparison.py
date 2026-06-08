#!/usr/bin/env python3
"""Add Providers_Agree columns to an existing batch comparison CSV."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.provider_equiv import compare_providers


def add_comparison_columns(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    agrees: list[bool | None] = []
    notes: list[str] = []
    for _, row in out.iterrows():
        agree, note = compare_providers(
            str(row.get("Provider", "")),
            str(row.get("Our_Recordkeeper", "")),
        )
        agrees.append(agree)
        notes.append(note)
    out["Providers_Agree"] = agrees
    out["Compare_Note"] = notes
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input_csv", type=Path)
    parser.add_argument("-o", "--output", type=Path, required=True)
    parser.add_argument("--discrepancies", type=Path, default=None)
    args = parser.parse_args()

    df = pd.read_csv(args.input_csv, dtype=str).fillna("")
    out = add_comparison_columns(df)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(args.output, index=False)

    comparable = out[out["Compare_Note"] != "their_blank"]
    discrepancies = comparable[comparable["Providers_Agree"] == False]
    agreements = comparable[comparable["Providers_Agree"] == True]

    if args.discrepancies:
        discrepancies.to_csv(args.discrepancies, index=False)

    print(f"Rows: {len(out):,}")
    print(f"Agreements: {len(agreements):,} ({100 * len(agreements) / len(comparable):.1f}%)")
    print(f"Discrepancies: {len(discrepancies):,} ({100 * len(discrepancies) / len(comparable):.1f}%)")
    print(f"Output: {args.output}")
    if args.discrepancies:
        print(f"Discrepancies file: {args.discrepancies}")


if __name__ == "__main__":
    main()

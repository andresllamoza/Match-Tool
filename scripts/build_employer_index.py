#!/usr/bin/env python3
"""Rebuild data/employer_rk_index.csv from recordkeeper_master.csv (local dev only)."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "data" / "recordkeeper_master.csv"
OUT = ROOT / "data" / "employer_rk_index.csv"


def main() -> None:
    if not MASTER.is_file():
        raise SystemExit(f"Missing {MASTER} — build or download recordkeeper_master.csv first")
    df = pd.read_csv(
        MASTER,
        usecols=["EMPLOYER", "EMPLOYER_NORM", "RK_CANON", "_n"],
        dtype=str,
        low_memory=False,
    )
    df["_n"] = pd.to_numeric(df["_n"], errors="coerce").fillna(0)
    idx = df.sort_values("_n", ascending=False).drop_duplicates("EMPLOYER_NORM", keep="first")
    out = idx[["EMPLOYER_NORM", "EMPLOYER", "RK_CANON"]].rename(
        columns={
            "RK_CANON": "recordkeeper",
            "EMPLOYER": "employer_name",
            "EMPLOYER_NORM": "employer_norm",
        }
    )
    OUT.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(OUT, index=False)
    print(f"Wrote {len(out):,} rows → {OUT} ({OUT.stat().st_size / 1e6:.1f} MB)")


if __name__ == "__main__":
    main()

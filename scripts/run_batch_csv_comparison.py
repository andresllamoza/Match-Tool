#!/usr/bin/env python3
"""Run batch lookup on a CSV and append our tool's results as new columns."""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.batch_columns import detect_employer_column
from src.matcher import MatchResult, batch_match_top_results, load_dol_data

CHUNK_SIZE = 100


def confidence_label(result: MatchResult) -> str:
    if result.confidence >= 0.85:
        return "High"
    if result.confidence >= 0.60:
        return "Medium"
    return "Low"


def format_tool_result(result: MatchResult | None, input_name: str) -> str:
    if result is None:
        return f"No match found for input: {input_name}"
    parts = [
        f"Recordkeeper: {result.recordkeeper or 'Unknown'}",
        f"Matched employer: {result.matched_employer_name}",
        f"Confidence: {confidence_label(result)} ({result.confidence:.0%})",
        f"Match method: {result.match_method}",
    ]
    if result.plan_name:
        parts.append(f"Plan: {result.plan_name}")
    if result.plan_participants:
        parts.append(f"Participants: {int(result.plan_participants):,}")
    if result.plan_year:
        parts.append(f"Plan year: {result.plan_year}")
    if result.match_reason:
        parts.append(f"Reason: {result.match_reason}")
    return " | ".join(parts)


def run_batch_comparison(input_path: Path, output_path: Path) -> pd.DataFrame:
    uploaded = pd.read_csv(input_path, dtype=str).fillna("")
    employer_column = detect_employer_column(list(uploaded.columns))
    names = uploaded[employer_column].astype(str).tolist()

    print(f"Input: {input_path}")
    print(f"Rows: {len(names):,} | Employer column: {employer_column}")

    load_dol_data()
    results: list[MatchResult | None] = []
    started = time.perf_counter()
    for start in range(0, len(names), CHUNK_SIZE):
        chunk = names[start : start + CHUNK_SIZE]
        results.extend(batch_match_top_results(chunk))
        done = min(start + len(chunk), len(names))
        if done % 500 == 0 or done == len(names):
            elapsed = time.perf_counter() - started
            print(f"  Matched {done:,} / {len(names):,} ({elapsed:.1f}s)")

    output = uploaded.copy()
    output["Our_Recordkeeper"] = [
        (r.recordkeeper if r and r.recordkeeper else "No match found") for r in results
    ]
    output["Our_Matched_Employer"] = [
        (r.matched_employer_name if r else "") for r in results
    ]
    output["Our_Confidence"] = [
        (confidence_label(r) if r else "none") for r in results
    ]
    output["Our_Match_Method"] = [(r.match_method if r else "") for r in results]
    output["Our_Tool_Result"] = [
        format_tool_result(r, name) for r, name in zip(results, names, strict=True)
    ]

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output.to_csv(output_path, index=False)
    matched = sum(1 for r in results if r and r.recordkeeper)
    print(f"Output: {output_path}")
    print(f"Matched: {matched:,} / {len(names):,} ({100 * matched / len(names):.1f}%)")
    return output


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input_csv", type=Path)
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path("artifacts/batch_comparison_results.csv"),
    )
    args = parser.parse_args()
    run_batch_comparison(args.input_csv, args.output)


if __name__ == "__main__":
    main()

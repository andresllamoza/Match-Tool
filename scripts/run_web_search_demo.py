#!/usr/bin/env python3
"""
Print a 5-employer walkthrough for coworkers (terminal or paste into slides).

  python3 scripts/run_web_search_demo.py
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.matcher import load_dol_data, match  # noqa: E402

DEMO_CASES = [
    {
        "fortune_name": "Alphabet",
        "search_query": "Alphabet 401k plan recordkeeper",
        "web_recordkeeper": "Vanguard",
        "plan_name": "GOOGLE LLC 401(K) SAVINGS PLAN",
        "why_miss": "DOL employer is GOOGLE LLC; Fortune list says Alphabet.",
        "source": "https://www.hicapitalize.com/find-my-401k/google/",
    },
    {
        "fortune_name": "JP Morgan Chase",
        "search_query": "JP Morgan Chase 401k recordkeeper",
        "web_recordkeeper": "Empower",
        "plan_name": "JPMORGAN CHASE 401(K) SAVINGS PLAN",
        "why_miss": "DOL may match bank subsidiary rows, not the employee 401(k) plan.",
        "source": "https://www.jpmcbenefitsguide.com/content/dam/jpmorganchase/jpmc-benefits-guide/documents/jpmc-401k-plan-spd.pdf",
    },
    {
        "fortune_name": "Fannie Mae",
        "search_query": "Fannie Mae 401k plan recordkeeper",
        "web_recordkeeper": "Fidelity Investments",
        "plan_name": "FEDERAL NATIONAL MORTGAGE ASSN RETIREMENT SAVINGS PLAN FOR EMPLOYEES",
        "why_miss": "Legal name on 5500 is Federal National Mortgage Association.",
        "source": "https://meetbeagle.com/my-401k-login/FEDERAL-NATIONAL-MORTGAGE-ASSOCIATION-401k-login-56733",
    },
    {
        "fortune_name": "State Farm Insurance Cos.",
        "search_query": "State Farm 401k recordkeeper",
        "web_recordkeeper": "Alight Solutions",
        "plan_name": "State Farm 401(k) Savings Plan",
        "why_miss": "Fortune label vs State Farm Mutual Automobile Insurance Company on filings.",
        "source": "https://cache.hacontent.com/ybr/R516/01283_ybr_ybrfndt/downloads/spdRetirement2010.pdf",
    },
    {
        "fortune_name": "Express Scripts Holding",
        "search_query": "Express Scripts 401k recordkeeper",
        "web_recordkeeper": "Prudential / Empower (post-merger Cigna plan)",
        "plan_name": "EXPRESS SCRIPTS, INC. 401(K) PLAN → Cigna 401(k)",
        "why_miss": "M&A; plan merged; DOL row may be under Cigna Corp.",
        "source": "https://www.sec.gov/Archives/edgar/data/1739940/000095015921000180/cigna11k.htm",
    },
]


def dol_status(name: str) -> str:
    results = match(name, top_n=1)
    if not results:
        return "No match found"
    top = results[0]
    return f"{top.recordkeeper} @ {top.matched_employer_name} (conf {top.confidence:.0%})"


def main() -> None:
    print("=" * 72)
    print("WEB SEARCH FALLBACK DEMO — 5 Fortune employers")
    print("=" * 72)
    print()
    load_dol_data()
    for index, case in enumerate(DEMO_CASES, start=1):
        print(f"--- Example {index}: {case['fortune_name']} ---")
        print(f"  Fortune CSV name:     {case['fortune_name']}")
        print(f"  DOL tool today:       {dol_status(case['fortune_name'])}")
        print(f"  Google-style query:   \"{case['search_query']}\"")
        print(f"  Web suggests:         {case['web_recordkeeper']}")
        print(f"  Plan name:            {case['plan_name']}")
        print(f"  Why DOL missed:       {case['why_miss']}")
        print(f"  Sample source:        {case['source']}")
        print()
    print("Open docs/demo/web-search-fallback-demo.html in a browser for a slide-friendly table.")
    print("Full miss list: scripts/enrich_misses_web_search.py --from-batch-results <csv>")


if __name__ == "__main__":
    main()

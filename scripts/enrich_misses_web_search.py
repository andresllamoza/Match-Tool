#!/usr/bin/env python3
"""
Pilot: enrich batch "No match found" employers with web search hints.

Searches the public web (DuckDuckGo by default) with queries like:
  "{employer} 401k plan recordkeeper"

Outputs a CSV with snippets and a heuristic recordkeeper guess. Review before
trusting — use SEC Form 11-K / plan SPD links in the Source URL column.

Examples:
  python scripts/enrich_misses_web_search.py --from-batch-results uploads/batch.csv --limit 15
  python scripts/enrich_misses_web_search.py --fortune uploads/Fortune1000.csv --limit 20
  python scripts/enrich_misses_web_search.py --names "Alphabet" "Fannie Mae"

Google Custom Search (recommended for "{name} 401k plan" style queries):
  export GOOGLE_CSE_API_KEY=...
  export GOOGLE_CSE_ID=...
  python scripts/enrich_misses_web_search.py --engine google_cse \\
    --google-cse-key "$GOOGLE_CSE_API_KEY" --google-cse-id "$GOOGLE_CSE_ID" \\
    --from-batch-results uploads/batch_recordkeeper_lookup_results.csv --limit 50

Free tier: 100 queries/day. For ~173 Fortune misses, run over 2 days or enable billing.

Alternative: --engine sec_edgar (SEC full-text 11-K index, no API key).
DuckDuckGo (--engine duckduckgo) is unreliable for this use case.

Requires for duckduckgo: pip install duckduckgo-search
"""

from __future__ import annotations

import argparse
import re
import sys
import time
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.batch_columns import detect_employer_column  # noqa: E402
from src.matcher import batch_match_top_results, load_dol_data  # noqa: E402

SEC_SEARCH_URL = "https://efts.sec.gov/LATEST/search-index"
SEC_USER_AGENT = "RecordKeeper-Match-Tool/1.0 (research; contact: support@example.com)"

RECORDKEEPER_PATTERNS = [
    re.compile(
        r"record\s*keeper(?:\s+for\s+the\s+plan)?\s+is\s+([A-Za-z0-9.,&'\-\s]+?)(?:\.|,|\s+and\s+|\s+Bank)",
        re.I,
    ),
    re.compile(
        r"(?:administered|offered|provided)\s+(?:by|through)\s+([A-Za-z0-9.,&'\-\s]{3,60}?)(?:\.|,|\s+Their|\s+The)",
        re.I,
    ),
    re.compile(
        r"401\s*\(\s*k\s*\)\s+plan\s+through\s+([A-Za-z0-9.,&'\-\s]{3,40}?)(?:\.|,)",
        re.I,
    ),
    re.compile(
        r"401\s*\(\s*k\s*\)\s+provider[\"']?\s*(?:is|:)?\s*([A-Za-z0-9.,&'\-\s]{3,40})",
        re.I,
    ),
]

KNOWN_PROVIDERS = (
    "Fidelity",
    "Fidelity Investments",
    "Fidelity Workplace Services",
    "Vanguard",
    "Empower",
    "Empower Plan Services",
    "Merrill Lynch",
    "Alight",
    "Alight Solutions",
    "Voya",
    "Voya Financial",
    "Principal",
    "T. Rowe Price",
    "Schwab",
    "Charles Schwab",
    "ADP",
    "Paychex",
    "TIAA",
    "Transamerica",
    "Nationwide",
    "John Hancock",
    "MassMutual",
    "Lincoln Financial",
    "Prudential",
    "MetLife",
    "Bank of America",
    "J.P. Morgan",
    "JP Morgan",
    "Vestwell",
)


def build_search_query(employer_name: str) -> str:
    return f"{employer_name.strip()} 401k plan recordkeeper"


def extract_recordkeeper_hint(text: str) -> str:
    if not text:
        return ""
    for pattern in RECORDKEEPER_PATTERNS:
        match = pattern.search(text)
        if match:
            candidate = match.group(1).strip(" .,\"'")
            if len(candidate) >= 3:
                return candidate[:120]
    lowered = text.lower()
    for provider in sorted(KNOWN_PROVIDERS, key=len, reverse=True):
        if provider.lower() in lowered:
            return provider
    return ""


def search_duckduckgo(query: str, max_results: int = 5) -> list[dict[str, str]]:
    try:
        from duckduckgo_search import DDGS
    except ImportError as exc:
        raise SystemExit(
            "Install duckduckgo-search: pip install duckduckgo-search"
        ) from exc

    results: list[dict[str, str]] = []
    with DDGS() as ddgs:
        for item in ddgs.text(query, max_results=max_results):
            results.append(
                {
                    "title": str(item.get("title") or ""),
                    "url": str(item.get("href") or item.get("link") or ""),
                    "snippet": str(item.get("body") or item.get("snippet") or ""),
                }
            )
    return results


def search_sec_edgar_11k(employer_name: str, max_results: int = 3) -> list[dict[str, str]]:
    """Search SEC full-text index for Form 11-K filings mentioning the employer."""
    import json
    import urllib.parse
    import urllib.request

    params = urllib.parse.urlencode(
        {
            "q": f'"record keeper" {employer_name}',
            "forms": "11-K",
            "dateRange": "custom",
            "startdt": "2018-01-01",
            "enddt": "2026-12-31",
        }
    )
    request = urllib.request.Request(
        f"{SEC_SEARCH_URL}?{params}",
        headers={"User-Agent": SEC_USER_AGENT, "Accept": "application/json"},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        payload = json.load(response)

    hits: list[dict[str, str]] = []
    for item in (payload.get("hits") or {}).get("hits", [])[:max_results]:
        source = item.get("_source") or {}
        adsh = str(source.get("adsh") or "")
        cik = ""
        ciks = source.get("ciks") or []
        if ciks:
            cik = str(ciks[0]).lstrip("0") or str(ciks[0])
        filing_url = ""
        if cik and adsh:
            filing_url = f"https://www.sec.gov/Archives/edgar/data/{cik}/{adsh.replace('-', '')}/"
        hits.append(
            {
                "title": str(source.get("display_names") or [""])[0]
                if isinstance(source.get("display_names"), list)
                else str(source.get("display_names") or ""),
                "url": filing_url,
                "snippet": str(source.get("file_description") or "Form 11-K"),
            }
        )
    return hits


def fetch_sec_filing_excerpt(url: str, max_chars: int = 8000) -> str:
    if not url:
        return ""
    import urllib.request

    request = urllib.request.Request(url, headers={"User-Agent": SEC_USER_AGENT})
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            html = response.read(max_chars).decode("utf-8", errors="ignore")
    except Exception:
        return ""
    return re.sub(r"<[^>]+>", " ", html)


def search_google_cse(query: str, api_key: str, cse_id: str, max_results: int = 5) -> list[dict[str, str]]:
    import json
    import urllib.parse
    import urllib.request

    params = urllib.parse.urlencode(
        {
            "key": api_key,
            "cx": cse_id,
            "q": query,
            "num": min(max_results, 10),
        }
    )
    url = f"https://www.googleapis.com/customsearch/v1?{params}"
    with urllib.request.urlopen(url, timeout=30) as response:
        payload = json.load(response)
    items = payload.get("items") or []
    return [
        {
            "title": str(item.get("title") or ""),
            "url": str(item.get("link") or ""),
            "snippet": str(item.get("snippet") or ""),
        }
        for item in items[:max_results]
    ]


def load_misses_from_batch(path: Path) -> list[str]:
    df = pd.read_csv(path, dtype=str).fillna("")
    misses = df[df["Recordkeeper"].astype(str).str.strip() == "No match found"]
    return misses["Input name"].astype(str).tolist()


def load_misses_from_fortune(path: Path) -> list[str]:
    load_dol_data()
    df = pd.read_csv(path, dtype=str).fillna("")
    column = detect_employer_column(list(df.columns))
    names = df[column].astype(str).tolist()
    results = batch_match_top_results(names)
    return [
        name
        for name, result in zip(names, results, strict=True)
        if result is None or not str(result.recordkeeper or "").strip()
    ]


def enrich_employer(
    employer_name: str,
    *,
    engine: str,
    search_fn,
    pause_seconds: float,
) -> dict[str, object]:
    query = build_search_query(employer_name)
    time.sleep(pause_seconds)
    hits = search_fn(employer_name if engine == "sec_edgar" else query)
    combined = " ".join(
        f"{hit.get('title', '')} {hit.get('snippet', '')}" for hit in hits
    )
    guess = extract_recordkeeper_hint(combined)
    top = hits[0] if hits else {}
    return {
        "Input name": employer_name,
        "Search query": query,
        "Web recordkeeper guess": guess,
        "Has guess": bool(guess),
        "Top title": top.get("title", ""),
        "Top URL": top.get("url", ""),
        "Top snippet": (top.get("snippet", "") or "")[:500],
        "Hit count": len(hits),
        "Search engine": engine,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--from-batch-results", type=Path, help="Batch results CSV with misses")
    parser.add_argument("--fortune", type=Path, help="Fortune-style CSV; compute misses via matcher")
    parser.add_argument("--names", nargs="*", help="Explicit employer names")
    parser.add_argument("--limit", type=int, default=20, help="Max employers to search")
    parser.add_argument("--output", type=Path, default=Path("data/web_search_miss_enrichment.csv"))
    parser.add_argument("--pause", type=float, default=1.0, help="Seconds between searches")
    parser.add_argument(
        "--engine",
        choices=("sec_edgar", "duckduckgo", "google_cse"),
        default="sec_edgar",
        help="Search backend (default: sec_edgar — best for recordkeeper text)",
    )
    import os

    parser.add_argument(
        "--google-cse-key",
        default=os.environ.get("GOOGLE_CSE_API_KEY", ""),
        help="Google Custom Search API key (or GOOGLE_CSE_API_KEY env)",
    )
    parser.add_argument(
        "--google-cse-id",
        default=os.environ.get("GOOGLE_CSE_ID", ""),
        help="Google Programmable Search Engine ID (or GOOGLE_CSE_ID env)",
    )
    args = parser.parse_args()

    misses: list[str] = []
    if args.from_batch_results:
        misses.extend(load_misses_from_batch(args.from_batch_results))
    if args.fortune:
        misses.extend(load_misses_from_fortune(args.fortune))
    if args.names:
        misses.extend(args.names)

    # Preserve order, drop duplicates
    seen: set[str] = set()
    unique_misses: list[str] = []
    for name in misses:
        key = name.strip().lower()
        if key and key not in seen:
            seen.add(key)
            unique_misses.append(name.strip())

    if not unique_misses:
        raise SystemExit("No employer names to search. Pass --from-batch-results, --fortune, or --names.")

    to_search = unique_misses[: args.limit]
    print(f"Searching {len(to_search)} of {len(unique_misses)} misses...")

    engine = args.engine
    if engine == "google_cse":
        if not (args.google_cse_key and args.google_cse_id):
            raise SystemExit("google_cse requires --google-cse-key and --google-cse-id")

        def search_fn(query: str) -> list[dict[str, str]]:
            return search_google_cse(query, args.google_cse_key, args.google_cse_id)
    elif engine == "duckduckgo":

        def search_fn(query: str) -> list[dict[str, str]]:
            return search_duckduckgo(query)
    else:

        def search_fn(employer: str) -> list[dict[str, str]]:
            return search_sec_edgar_11k(employer)

    rows: list[dict[str, object]] = []
    for employer in to_search:
        try:
            row = enrich_employer(
                employer,
                engine=engine,
                search_fn=search_fn,
                pause_seconds=args.pause,
            )
            rows.append(row)
            status = row["Web recordkeeper guess"] or "(no guess)"
            print(f"  {employer}: {status}")
        except Exception as exc:
            print(f"  {employer}: ERROR {exc}")
            rows.append(
                {
                    "Input name": employer,
                    "Search query": build_search_query(employer),
                    "Web recordkeeper guess": "",
                    "Has guess": False,
                    "Top title": "",
                    "Top URL": "",
                    "Top snippet": str(exc)[:500],
                    "Hit count": 0,
                    "Search engine": engine,
                }
            )
        time.sleep(0.2)  # SEC fair-access pacing between employers

    output = args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(output, index=False)
    guessed = sum(1 for row in rows if row.get("Has guess"))
    print(f"\nWrote {output} — {guessed}/{len(rows)} rows with a recordkeeper guess ({engine}).")


if __name__ == "__main__":
    main()

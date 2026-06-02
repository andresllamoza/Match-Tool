"""
DOL 5500 recordkeeper lookup — v4 matcher.

Extracted from the original Colab notebook (recordkeeper_mvp.ipynb). Logic is
unchanged; only the structure has been reorganized for production use:
  - Module-level constants for legal suffixes, stopwords, and canonical map
  - Lazy data loading with caching (load_data() runs once per process)
  - Single public function: find_recordkeeper(employer_query)
"""

from __future__ import annotations

import os
import re
import urllib.request
import zipfile
from pathlib import Path
from typing import Optional

import pandas as pd


# =====================================================================
# Constants
# =====================================================================

# Data directory (matches the Colab convention)
DATA_DIR = Path(__file__).parent.parent / "data"

# Which year of DOL data to use. 2023 is the most recent year with complete
# filings as of the v4 validation run (Fortune 1000, 666/1000 high-confidence).
YEAR = 2023

# Download URLs for the three files the matcher needs
FILE_URLS = {
    "main": f"https://askebsa.dol.gov/FOIA%20Files/{YEAR}/Latest/F_5500_{YEAR}_Latest.zip",
    "providers": f"https://askebsa.dol.gov/FOIA%20Files/{YEAR}/Latest/F_SCH_C_PART1_ITEM2_{YEAR}_Latest.zip",
    "codes": f"https://askebsa.dol.gov/FOIA%20Files/{YEAR}/Latest/F_SCH_C_PART1_ITEM2_CODES_{YEAR}_Latest.zip",
}

# Expected CSV filenames after extraction
CSV_FILES = {
    "main": f"f_5500_{YEAR}_latest.csv",
    "providers": f"F_SCH_C_PART1_ITEM2_{YEAR}_Latest.csv",
    "codes": f"F_SCH_C_PART1_ITEM2_CODES_{YEAR}_Latest.csv",
}

# Schedule C service codes for recordkeeping services.
# 15 = Recordkeeping, 64 = Recordkeeping & Information Mgmt fees only.
RECORDKEEPER_CODES = {"15", "64"}

# Name normalization — strips legal suffixes and stopwords for matching
LEGAL_SUFFIXES = {
    "INCORPORATED", "CORPORATION", "COMPANY", "LIMITED", "HOLDINGS",
    "GROUP", "ENTERPRISES", "CORP", "INC", "LLC", "LP", "LTD", "LLP",
    "PLC", "NA", "N.A.", "CO", "HOLDING", "COS", "PARTNERSHIP",
    "INTERNATIONAL", "INTL", "USA", "US",
}
STOPWORDS = {"THE", "AND", "OF", "&"}

# Canonical provider mapping. Order matters — more specific patterns first.
# Reduces the long tail of provider name variants (e.g., 7 Fidelity spellings)
# to a single canonical name.
CANONICAL_MAP = [
    (r"TEMPO HOLDING", "Alight Solutions"),
    (r"\bALIGHT\b", "Alight Solutions"),
    (r"FID\w* INV", "Fidelity Investments"),
    (r"FIDELITY INV", "Fidelity Investments"),
    (r"FIDELITY WORKPLACE", "Fidelity Investments"),
    (r"\bFIDELITY\b", "Fidelity Investments"),
    (r"EMPOWER", "Empower Retirement"),
    (r"GREAT.WEST", "Empower Retirement"),  # Great-West is now Empower
    (r"\bVANGUARD\b", "Vanguard"),
    (r"MERRILL LYNCH", "Merrill Lynch"),
    (r"\bMERRILL\b", "Merrill Lynch"),
    (r"PRINCIPAL LIFE", "Principal"),
    (r"PRINCIPAL BANK", "Principal"),
    (r"\bPRINCIPAL\b", "Principal"),
    (r"TRANSAMERICA", "Transamerica"),
    (r"T\.? ROWE PRICE", "T. Rowe Price"),
    (r"SCHWAB", "Charles Schwab"),
    (r"\bVOYA\b", "Voya"),
    (r"JOHN HANCOCK", "John Hancock"),
    (r"PRUDENTIAL", "Prudential"),
    (r"\bPRIAC\b", "Prudential"),
    (r"NATIONWIDE", "Nationwide"),
    (r"MUTUAL OF AMERICA", "Mutual of America"),
    (r"MASS.+MUTUAL", "MassMutual"),
    (r"LINCOLN.+(FINANCIAL|NATIONAL)", "Lincoln Financial"),
    (r"\bPAYCHEX\b", "Paychex"),
    (r"\bADP\b", "ADP"),
    (r"ASCENSUS", "Ascensus"),
    (r"NEWPORT GROUP", "Newport Group"),
    (r"MILLIMAN", "Milliman"),
    (r"WILLIS TOWERS WATSON", "Willis Towers Watson"),
    (r"\bAON\b", "Aon"),
    (r"MERCER", "Mercer"),
    (r"NORTHERN TRUST", "Northern Trust"),
    (r"CONDUENT", "Conduent"),
]


# =====================================================================
# Helpers
# =====================================================================

def normalize_name(name) -> str:
    """Strip legal suffixes and stopwords; uppercase; collapse whitespace."""
    if pd.isna(name):
        return ""
    s = re.sub(r"[^\w\s&]", " ", str(name).upper())
    s = re.sub(r"\s+", " ", s).strip()
    tokens = [t for t in s.split() if t not in LEGAL_SUFFIXES and t not in STOPWORDS]
    return " ".join(tokens)


def _collapsed(s: str) -> str:
    """Remove internal spaces, e.g. 'JP MORGAN' -> 'JPMORGAN'."""
    return re.sub(r"\s+", "", s)


def canonicalize_provider(name) -> Optional[str]:
    """Map a raw provider name string to its canonical form."""
    if pd.isna(name):
        return None
    upper = str(name).upper()
    for pat, canon in CANONICAL_MAP:
        if re.search(pat, upper):
            return canon
    return str(name).strip()


def _find_col(df: pd.DataFrame, keywords: list[str]) -> Optional[str]:
    """Find the first column whose name contains all given keywords (case-insensitive)."""
    for col in df.columns:
        col_upper = col.upper()
        if all(kw.upper() in col_upper for kw in keywords):
            return col
    return None


# =====================================================================
# Data download + load (cached at module level)
# =====================================================================

_DATA_CACHE = {
    "f5500_pension": None,
    "providers": None,
    "codes": None,
    "provider_name_col": None,
    "code_col": None,
}


def _download_data() -> None:
    """Download and extract DOL CSVs if not already present locally."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    for name, url in FILE_URLS.items():
        csv_name = CSV_FILES[name]
        csv_path = DATA_DIR / csv_name
        if csv_path.exists():
            continue

        zip_path = DATA_DIR / f"{name}.zip"
        if not zip_path.exists():
            urllib.request.urlretrieve(url, str(zip_path))

        with zipfile.ZipFile(zip_path) as z:
            z.extractall(str(DATA_DIR))

        # Clean up zip after extraction to save disk space
        try:
            zip_path.unlink()
        except OSError:
            pass


def load_data(progress_callback=None) -> None:
    """
    Load and prepare the data. Idempotent — safe to call multiple times.

    Args:
        progress_callback: optional function(message: str) for status updates.
                          Streamlit passes st.write or similar; CLI can ignore.
    """
    if _DATA_CACHE["f5500_pension"] is not None:
        return

    def _msg(s: str) -> None:
        if progress_callback:
            progress_callback(s)

    _msg("Downloading DOL data (first run only)...")
    _download_data()

    _msg("Loading main 5500 file...")
    f5500 = pd.read_csv(
        DATA_DIR / CSV_FILES["main"],
        usecols=[
            "ACK_ID", "SPONSOR_DFE_NAME", "SPONS_DFE_EIN",
            "TOT_PARTCP_BOY_CNT", "TYPE_PENSION_BNFT_CODE",
        ],
        dtype=str,
        encoding="latin-1",
        low_memory=False,
    )
    f5500["SPONSOR_NORM"] = f5500["SPONSOR_DFE_NAME"].apply(normalize_name)
    f5500["_n_participants"] = pd.to_numeric(
        f5500["TOT_PARTCP_BOY_CNT"], errors="coerce"
    ).fillna(0)

    # Pension-only subset — kills the welfare-plan bug from v3
    pension_mask = (
        f5500["TYPE_PENSION_BNFT_CODE"].notna() &
        (f5500["TYPE_PENSION_BNFT_CODE"].str.strip() != "")
    )
    _DATA_CACHE["f5500_pension"] = f5500[pension_mask].copy()

    _msg("Loading Schedule C providers...")
    providers = pd.read_csv(
        DATA_DIR / CSV_FILES["providers"],
        dtype=str,
        encoding="latin-1",
        low_memory=False,
    )
    _DATA_CACHE["providers"] = providers
    _DATA_CACHE["provider_name_col"] = (
        _find_col(providers, ["NAME", "PROVIDER"]) or
        _find_col(providers, ["NAME"])
    )

    _msg("Loading Schedule C service codes...")
    codes = pd.read_csv(
        DATA_DIR / CSV_FILES["codes"],
        dtype=str,
        encoding="latin-1",
        low_memory=False,
    )
    _DATA_CACHE["codes"] = codes
    _DATA_CACHE["code_col"] = (
        _find_col(codes, ["CODE", "SERVICE"]) or
        _find_col(codes, ["CODE"])
    )

    _msg("Ready.")


# =====================================================================
# Public lookup function (v4 logic)
# =====================================================================

def find_recordkeeper(employer_query: str, top_n_plans: int = 3) -> dict:
    """
    Look up the 401(k) recordkeeper for an employer.

    Args:
        employer_query: employer name as the user typed it
        top_n_plans: how many top plans to inspect (by participant count)

    Returns:
        dict with keys:
          query                  — original employer input
          matched_employer       — matched sponsor name from DOL filings, or None
          ein                    — employer EIN, or None
          participants_top_plan  — participant count of the top matched plan
          recordkeeper           — canonical recordkeeper name(s), joined by "; ", or None
          recordkeeper_raw       — raw recordkeeper name(s) from filings, or None
          confidence             — "High" | "None"
          signals                — short diagnostic string
          num_filings_found      — number of filings matched
    """
    load_data()
    f5500_pension = _DATA_CACHE["f5500_pension"]
    providers = _DATA_CACHE["providers"]
    codes = _DATA_CACHE["codes"]
    PROVIDER_NAME_COL = _DATA_CACHE["provider_name_col"]
    CODE_COL = _DATA_CACHE["code_col"]

    q_norm = normalize_name(employer_query)
    if not q_norm:
        return {
            "query": employer_query, "matched_employer": None, "ein": None,
            "participants_top_plan": 0,
            "recordkeeper": None, "recordkeeper_raw": None,
            "confidence": "None",
            "signals": "empty query after normalization",
            "num_filings_found": 0,
        }

    # PRIMARY MATCH: word-boundary regex on normalized sponsor names
    q_pattern = r"\b" + re.escape(q_norm) + r"\b"
    mask = f5500_pension["SPONSOR_NORM"].str.contains(q_pattern, na=False, regex=True)
    matches = f5500_pension[mask]

    # FALLBACK: space-collapse (rescues 'JP MORGAN' -> 'JPMORGAN' class)
    if matches.empty:
        q_coll = _collapsed(q_norm)
        if q_coll != q_norm and len(q_coll) >= 4:
            collapsed_mask = f5500_pension["SPONSOR_NORM"].apply(
                lambda s: q_coll in _collapsed(s) if pd.notna(s) else False
            )
            matches = f5500_pension[collapsed_mask]

    if matches.empty:
        return {
            "query": employer_query, "matched_employer": None, "ein": None,
            "participants_top_plan": 0,
            "recordkeeper": None, "recordkeeper_raw": None,
            "confidence": "None",
            "signals": "no pension plan filing found",
            "num_filings_found": 0,
        }

    # Prefer exact normalized matches, then by participant count
    exact = matches[matches["SPONSOR_NORM"] == q_norm]
    if not exact.empty:
        matches = exact
    matches = matches.sort_values("_n_participants", ascending=False)
    top_plans = matches.head(top_n_plans)
    ack_ids = set(top_plans["ACK_ID"])

    # Look up providers with recordkeeper service codes (15 or 64)
    code_hits = codes[
        codes["ACK_ID"].isin(ack_ids) &
        codes[CODE_COL].isin(RECORDKEEPER_CODES)
    ]

    raw_providers = []
    for _, code_row in code_hits.iterrows():
        provider_row = providers[
            (providers["ACK_ID"] == code_row["ACK_ID"]) &
            (providers["ROW_ORDER"] == code_row["ROW_ORDER"])
        ]
        if not provider_row.empty:
            name = provider_row.iloc[0][PROVIDER_NAME_COL]
            if pd.notna(name):
                raw_providers.append((str(name).strip(), code_row[CODE_COL]))

    # Canonicalize and dedupe (preserving order)
    canonical_seen, canonical_names = set(), []
    raw_seen, raw_names = set(), []
    codes_seen = set()
    for raw_name, code in raw_providers:
        canon = canonicalize_provider(raw_name)
        if canon and canon not in canonical_seen:
            canonical_seen.add(canon)
            canonical_names.append(canon)
        if raw_name.upper() not in raw_seen:
            raw_seen.add(raw_name.upper())
            raw_names.append(raw_name)
        codes_seen.add(code)

    top = top_plans.iloc[0]

    if canonical_names:
        return {
            "query": employer_query,
            "matched_employer": top["SPONSOR_DFE_NAME"],
            "ein": top.get("SPONS_DFE_EIN"),
            "participants_top_plan": int(top["_n_participants"]),
            "recordkeeper": "; ".join(canonical_names),
            "recordkeeper_raw": "; ".join(raw_names),
            "confidence": "High",
            "signals": f"Code(s) {','.join(sorted(codes_seen))}",
            "num_filings_found": len(matches),
        }

    return {
        "query": employer_query,
        "matched_employer": top["SPONSOR_DFE_NAME"],
        "ein": top.get("SPONS_DFE_EIN"),
        "participants_top_plan": int(top["_n_participants"]),
        "recordkeeper": None,
        "recordkeeper_raw": None,
        "confidence": "None",
        "signals": "pension employer found but no code 15/64",
        "num_filings_found": len(matches),
    }

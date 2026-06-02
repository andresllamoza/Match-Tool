"""
DOL 5500 matcher logic.

This module wraps the v4 matching logic from the Colab notebook into a single
callable function. Paste your existing Colab logic into the marked sections.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional
import pandas as pd


# ---------- Data structures ----------

@dataclass
class MatchResult:
    """One candidate match returned by the matcher."""
    employer_query: str
    matched_employer_name: str
    recordkeeper: str
    confidence: float  # 0.0 to 1.0
    plan_name: Optional[str] = None
    plan_year: Optional[int] = None
    plan_participants: Optional[int] = None
    ein: Optional[str] = None

    @property
    def confidence_label(self) -> str:
        if self.confidence >= 0.85:
            return "High"
        if self.confidence >= 0.60:
            return "Medium"
        return "Low"


# ---------- Data loading ----------

DATA_DIR = Path(__file__).parent.parent / "data"

# Module-level cache so we don't reload the DOL CSVs on every query.
# Streamlit will call match() many times in a session; loading the joined
# dataframe once at startup is essential for responsiveness.
_DATAFRAME_CACHE: Optional[pd.DataFrame] = None


def load_dol_data() -> pd.DataFrame:
    """
    Load and join the four DOL Form 5500 CSV datasets.

    Returns the joined dataframe filtered to Schedule C service codes 15 and 64
    (recordkeeping services), with canonical provider names applied.

    PASTE YOUR V4 LOAD/JOIN LOGIC HERE.
    Expected inputs (drop into data/):
      - f_5500_YYYY_latest.csv         (main 5500 filings)
      - f_sch_c_YYYY_latest.csv        (Schedule C service providers)
      - f_sch_c_part1_item2_YYYY.csv   (service code detail)
      - any other DOL datasets your v4 pipeline uses

    Expected output: a single dataframe with at minimum these columns:
      - SPONSOR_DFE_NAME           (the employer)
      - PROVIDER_OTHER_NAME        (raw recordkeeper name from filing)
      - canonical_recordkeeper     (your canonicalized provider name)
      - PLAN_NAME
      - PLAN_YEAR_BEGIN_DATE
      - TOT_PARTCP_BOY_CNT
      - SPONS_DFE_EIN
    """
    global _DATAFRAME_CACHE
    if _DATAFRAME_CACHE is not None:
        return _DATAFRAME_CACHE

    # ---- BEGIN PASTE ZONE: v4 data loading and joins ----
    # df = pd.read_csv(DATA_DIR / "f_5500_2024_latest.csv", ...)
    # sch_c = pd.read_csv(DATA_DIR / "f_sch_c_2024_latest.csv", ...)
    # joined = df.merge(sch_c, on=["ACK_ID", "ROW_ORDER"], ...)
    # filtered = joined[joined["SERVICE_CODE"].isin(["15", "64"])]
    # filtered["canonical_recordkeeper"] = filtered["PROVIDER_OTHER_NAME"].apply(canonicalize)
    # ---- END PASTE ZONE ----

    raise NotImplementedError(
        "Paste the v4 data loading logic from your Colab notebook into load_dol_data()."
    )

    # _DATAFRAME_CACHE = filtered
    # return _DATAFRAME_CACHE


# ---------- Canonicalization ----------

def canonicalize_employer(name: str) -> str:
    """
    Normalize an employer name for matching.

    PASTE YOUR V4 CANONICALIZATION LOGIC HERE.
    Typical operations: lowercase, strip punctuation, strip suffixes like
    'INC', 'CORP', 'LLC', 'HOLDINGS', collapse whitespace.
    """
    # ---- BEGIN PASTE ZONE: v4 canonicalization ----
    # cleaned = name.upper().strip()
    # cleaned = re.sub(r"[^\w\s]", "", cleaned)
    # cleaned = re.sub(r"\b(INC|CORP|CORPORATION|LLC|LP|HOLDINGS|COMPANY|CO)\b", "", cleaned)
    # cleaned = re.sub(r"\s+", " ", cleaned).strip()
    # return cleaned
    # ---- END PASTE ZONE ----
    return name.upper().strip()


# ---------- Match function (the public API) ----------

def match(employer_query: str, top_n: int = 4) -> list[MatchResult]:
    """
    Look up the recordkeeper for an employer name.

    Args:
        employer_query: the user-typed employer name
        top_n: how many candidate matches to return (1 best + n-1 near-misses)

    Returns:
        A list of MatchResult, ordered by confidence descending.
        Empty list if no candidates were found above the noise threshold.
    """
    if not employer_query or not employer_query.strip():
        return []

    df = load_dol_data()
    canonical_query = canonicalize_employer(employer_query)

    # ---- BEGIN PASTE ZONE: v4 matching scoring logic ----
    # Compute similarity between canonical_query and each row's
    # canonicalized SPONSOR_DFE_NAME. Use whatever scorer your v4 used
    # (rapidfuzz token_set_ratio, etc.). Sort by score descending,
    # take top_n.
    #
    # candidates = []
    # for _, row in df.iterrows():
    #     score = fuzz.token_set_ratio(canonical_query, canonicalize_employer(row["SPONSOR_DFE_NAME"]))
    #     candidates.append((score, row))
    # candidates.sort(key=lambda x: x[0], reverse=True)
    # top = candidates[:top_n]
    # ---- END PASTE ZONE ----

    raise NotImplementedError(
        "Paste the v4 matching/scoring logic from your Colab notebook into match()."
    )

    # results = []
    # for score, row in top:
    #     results.append(MatchResult(
    #         employer_query=employer_query,
    #         matched_employer_name=row["SPONSOR_DFE_NAME"],
    #         recordkeeper=row["canonical_recordkeeper"],
    #         confidence=score / 100.0,
    #         plan_name=row.get("PLAN_NAME"),
    #         plan_year=row.get("PLAN_YEAR_BEGIN_DATE"),
    #         plan_participants=row.get("TOT_PARTCP_BOY_CNT"),
    #         ein=row.get("SPONS_DFE_EIN"),
    #     ))
    # return results

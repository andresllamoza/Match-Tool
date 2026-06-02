from dataclasses import dataclass
import os
from pathlib import Path
import re
from typing import Optional
import urllib.request
import zipfile

import pandas as pd
from rapidfuzz import fuzz, process


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
    match_method: str = "unknown"
    match_reason: str = ""

    @property
    def confidence_label(self) -> str:
        if self.confidence >= 0.85:
            return "High"
        if self.confidence >= 0.60:
            return "Medium"
        return "Low"


DATA_DIR = Path(__file__).parent.parent / "data"
MASTER_CACHE_FILENAME = "recordkeeper_master.csv"
MASTER_CACHE_VERSION_FILENAME = "recordkeeper_master.version"
MASTER_CACHE_VERSION = "2"

# 2023 is the latest complete year from the original MVP. Set DOL_YEARS to a
# comma-separated list (for example, "2024,2023") if you want broader coverage.
DEFAULT_YEARS = (2023,)
TIER_RANK = {"TIER1": 1, "TIER2": 2}
TIER1_RELATION = r"RECORDKEEPER|RECORD KEEPER|RECORDKEEPING|RECORD KEEPING|PLAN RECORDKEEPER"
TIER2_RELATION = r"CONTRACT ADMINISTRATOR|CONTRACT ADMIN"
TIER1_CODES = {"15", "64"}
TIER2_CODES = {"13"}
FUZZY_THRESHOLD = 92

LEGAL_SUFFIXES = {
    "INCORPORATED",
    "CORPORATION",
    "COMPANY",
    "LIMITED",
    "HOLDINGS",
    "GROUP",
    "ENTERPRISES",
    "CORP",
    "INC",
    "LLC",
    "LP",
    "LTD",
    "LLP",
    "PLC",
    "NA",
    "N.A.",
    "CO",
    "HOLDING",
    "COS",
    "PARTNERSHIP",
    "INTERNATIONAL",
    "INTL",
    "USA",
    "US",
}
STOPWORDS = {"THE", "AND", "OF", "&"}

CANONICAL_MAP = [
    (r"TEMPO HOLDING", "Alight Solutions"),
    (r"\bALIGHT\b", "Alight Solutions"),
    (r"FID\w* INV", "Fidelity Investments"),
    (r"FIDELITY INV", "Fidelity Investments"),
    (r"FIDELITY WORKPLACE", "Fidelity Investments"),
    (r"\bFIDELITY\b", "Fidelity Investments"),
    (r"EMPOWER", "Empower Retirement"),
    (r"GREAT.WEST", "Empower Retirement"),
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

_DATAFRAME_CACHE: Optional[pd.DataFrame] = None


def _master_cache_path() -> Path:
    return DATA_DIR / MASTER_CACHE_FILENAME


def _master_cache_version_path() -> Path:
    return DATA_DIR / MASTER_CACHE_VERSION_FILENAME


def _master_cache_is_current() -> bool:
    version_path = _master_cache_version_path()
    try:
        return version_path.read_text(encoding="utf-8").strip() == MASTER_CACHE_VERSION
    except FileNotFoundError:
        return False


def _configured_years() -> tuple[int, ...]:
    raw_years = os.environ.get("DOL_YEARS", "")
    if not raw_years.strip():
        return DEFAULT_YEARS

    years: list[int] = []
    for raw_year in raw_years.split(","):
        raw_year = raw_year.strip()
        if raw_year:
            years.append(int(raw_year))
    return tuple(years) or DEFAULT_YEARS


def _dol_url(year: int, filename: str) -> str:
    return f"https://askebsa.dol.gov/FOIA%20Files/{year}/Latest/{filename}.zip"


def _find_existing_csv(stem: str) -> Optional[Path]:
    for candidate in DATA_DIR.glob("*.csv"):
        if candidate.stem.lower() == stem.lower():
            return candidate
    return None


def _ensure_dol_csv(year: int, stem: str) -> Path:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    existing = _find_existing_csv(stem)
    if existing:
        return existing

    zip_path = DATA_DIR / f"{stem}.zip"
    if not zip_path.exists():
        urllib.request.urlretrieve(_dol_url(year, stem), zip_path)

    with zipfile.ZipFile(zip_path) as archive:
        archive.extractall(DATA_DIR)

    extracted = _find_existing_csv(stem)
    if not extracted:
        raise FileNotFoundError(f"Downloaded {stem}.zip but did not find {stem}.csv")
    return extracted


def _read_csv_columns(path: Path, columns: list[str], required: list[str]) -> pd.DataFrame:
    header = pd.read_csv(path, nrows=0, encoding="latin-1")
    available = [column for column in columns if column in header.columns]
    missing_required = [column for column in required if column not in available]
    if missing_required:
        raise ValueError(f"{path.name} is missing required columns: {missing_required}")
    return pd.read_csv(
        path,
        dtype=str,
        encoding="latin-1",
        low_memory=False,
        usecols=available,
    )


def _normalize_name(name: object) -> str:
    if pd.isna(name):
        return ""
    cleaned = re.sub(r"[^\w\s&]", " ", str(name).upper())
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    tokens = [
        token
        for token in cleaned.split()
        if token not in LEGAL_SUFFIXES and token not in STOPWORDS
    ]
    return " ".join(tokens)


def _collapsed(value: str) -> str:
    return re.sub(r"\s+", "", value)


def _canonicalize_recordkeeper(name: object) -> Optional[str]:
    if pd.isna(name):
        return None
    upper = str(name).upper()
    for pattern, canonical_name in CANONICAL_MAP:
        if re.search(pattern, upper):
            return canonical_name
    return str(name).strip()


def _codes_to_tier(codes: object) -> Optional[str]:
    if not isinstance(codes, str):
        return None
    code_set = {code.strip() for code in codes.split("|") if code.strip()}
    if code_set & TIER1_CODES:
        return "TIER1"
    if code_set & TIER2_CODES:
        return "TIER2"
    return None


def _relation_to_tier(relation: object) -> Optional[str]:
    if pd.isna(relation):
        return None
    relation_text = str(relation).upper()
    if re.search(TIER1_RELATION, relation_text):
        return "TIER1"
    if re.search(TIER2_RELATION, relation_text):
        return "TIER2"
    return None


def _first_non_null(*values: object) -> Optional[str]:
    for value in values:
        if value is None or pd.isna(value):
            continue
        text = str(value).strip()
        if text:
            return text
    return None


def _build_year_master(year: int) -> pd.DataFrame:
    main_path = _ensure_dol_csv(year, f"F_5500_{year}_Latest")
    provider_path = _ensure_dol_csv(year, f"F_SCH_C_PART1_ITEM2_{year}_Latest")
    codes_path = _ensure_dol_csv(year, f"F_SCH_C_PART1_ITEM2_CODES_{year}_Latest")

    filings = _read_csv_columns(
        main_path,
        [
            "ACK_ID",
            "SPONSOR_DFE_NAME",
            "SPONS_DFE_EIN",
            "PLAN_NAME",
            "PLAN_YEAR_BEGIN_DATE",
            "TYPE_PENSION_BNFT_CODE",
            "TOT_PARTCP_BOY_CNT",
        ],
        ["ACK_ID", "SPONSOR_DFE_NAME"],
    )
    if "TYPE_PENSION_BNFT_CODE" in filings.columns:
        filings = filings[
            filings["TYPE_PENSION_BNFT_CODE"].notna()
            & (filings["TYPE_PENSION_BNFT_CODE"].str.strip() != "")
        ].copy()
    filings["EMPLOYER_NORM"] = filings["SPONSOR_DFE_NAME"].apply(_normalize_name)
    if "TOT_PARTCP_BOY_CNT" in filings.columns:
        filings["_n"] = pd.to_numeric(
            filings["TOT_PARTCP_BOY_CNT"],
            errors="coerce",
        ).fillna(0)
    else:
        filings["_n"] = 0

    providers = _read_csv_columns(
        provider_path,
        ["ACK_ID", "ROW_ORDER", "PROVIDER_OTHER_NAME", "PROVIDER_OTHER_RELATION"],
        ["ACK_ID", "ROW_ORDER", "PROVIDER_OTHER_NAME"],
    )
    if "PROVIDER_OTHER_RELATION" not in providers.columns:
        providers["PROVIDER_OTHER_RELATION"] = ""

    codes = _read_csv_columns(
        codes_path,
        ["ACK_ID", "ROW_ORDER", "SERVICE_CODE"],
        ["ACK_ID", "ROW_ORDER", "SERVICE_CODE"],
    )
    codes = codes.dropna(subset=["SERVICE_CODE"]).copy()
    codes["SERVICE_CODE"] = codes["SERVICE_CODE"].astype(str).str.strip()
    code_groups = (
        codes.groupby(["ACK_ID", "ROW_ORDER"])["SERVICE_CODE"]
        .agg(lambda values: "|".join(sorted(set(values))))
        .reset_index()
        .rename(columns={"SERVICE_CODE": "CODES"})
    )

    providers = providers.merge(code_groups, on=["ACK_ID", "ROW_ORDER"], how="left")
    providers["_code_tier"] = providers["CODES"].apply(_codes_to_tier)
    providers["_relation_tier"] = providers["PROVIDER_OTHER_RELATION"].apply(_relation_to_tier)
    providers["TIER"] = providers.apply(
        lambda row: _first_non_null(row["_code_tier"], row["_relation_tier"]),
        axis=1,
    )
    providers = providers[providers["TIER"].notna()].copy()
    providers["PROVIDER_OTHER_NAME"] = (
        providers["PROVIDER_OTHER_NAME"].fillna("").str.strip().str.upper()
    )
    providers = providers[providers["PROVIDER_OTHER_NAME"] != ""]

    merged = filings.merge(
        providers[["ACK_ID", "PROVIDER_OTHER_NAME", "TIER"]],
        on="ACK_ID",
        how="inner",
    )
    merged["YEAR"] = year
    merged["_tier_rank"] = merged["TIER"].map(TIER_RANK)
    merged["EMPLOYER_COLLAPSED"] = merged["EMPLOYER_NORM"].apply(_collapsed)
    merged["RK_CANON"] = merged["PROVIDER_OTHER_NAME"].apply(_canonicalize_recordkeeper)
    return merged.rename(
        columns={
            "SPONSOR_DFE_NAME": "EMPLOYER",
            "PROVIDER_OTHER_NAME": "RK_RAW",
        }
    )


def _build_master() -> pd.DataFrame:
    frames = []
    errors = []
    for year in _configured_years():
        try:
            frames.append(_build_year_master(year))
        except Exception as exc:
            errors.append(f"{year}: {exc}")

    if not frames:
        raise RuntimeError("Could not build DOL lookup data. " + " | ".join(errors))

    master = pd.concat(frames, ignore_index=True)
    master = master.sort_values(
        ["EMPLOYER_NORM", "_tier_rank", "YEAR", "_n"],
        ascending=[True, True, False, False],
    )
    master = master.drop_duplicates(subset=["EMPLOYER_NORM"], keep="first")
    master = master[master["EMPLOYER_NORM"] != ""].copy()

    output_columns = [
        "EMPLOYER",
        "EMPLOYER_NORM",
        "EMPLOYER_COLLAPSED",
        "RK_RAW",
        "RK_CANON",
        "TIER",
        "YEAR",
        "_n",
        "_tier_rank",
        "PLAN_NAME",
        "PLAN_YEAR_BEGIN_DATE",
        "TOT_PARTCP_BOY_CNT",
        "SPONS_DFE_EIN",
    ]
    for column in output_columns:
        if column not in master.columns:
            master[column] = None
    master = master[output_columns]
    master.to_csv(_master_cache_path(), index=False)
    _master_cache_version_path().write_text(MASTER_CACHE_VERSION, encoding="utf-8")
    return master


def load_dol_data() -> pd.DataFrame:
    global _DATAFRAME_CACHE
    if _DATAFRAME_CACHE is not None:
        return _DATAFRAME_CACHE

    cache_path = _master_cache_path()
    if cache_path.exists() and _master_cache_is_current():
        _DATAFRAME_CACHE = pd.read_csv(cache_path, dtype=str, low_memory=False)
        _DATAFRAME_CACHE["_n"] = pd.to_numeric(_DATAFRAME_CACHE["_n"], errors="coerce").fillna(0)
        _DATAFRAME_CACHE["_tier_rank"] = pd.to_numeric(
            _DATAFRAME_CACHE["_tier_rank"],
            errors="coerce",
        ).fillna(99)
        return _DATAFRAME_CACHE

    _DATAFRAME_CACHE = _build_master()
    return _DATAFRAME_CACHE


def canonicalize_employer(name: str) -> str:
    """Normalize an employer name using the Colab matcher rules."""
    return _normalize_name(name)


def _candidate_result(
    employer_query: str,
    row: pd.Series,
    confidence: float,
    match_method: str,
    match_reason: str,
) -> MatchResult:
    participants = pd.to_numeric(row.get("TOT_PARTCP_BOY_CNT") or row.get("_n"), errors="coerce")
    if pd.isna(participants):
        participant_count = None
    else:
        participant_count = int(participants)

    return MatchResult(
        employer_query=employer_query,
        matched_employer_name=str(row.get("EMPLOYER") or ""),
        recordkeeper=str(row.get("RK_CANON") or row.get("RK_RAW") or ""),
        confidence=max(0.0, min(1.0, confidence)),
        plan_name=row.get("PLAN_NAME"),
        plan_year=row.get("PLAN_YEAR_BEGIN_DATE") or row.get("YEAR"),
        plan_participants=participant_count,
        ein=row.get("SPONS_DFE_EIN"),
        match_method=match_method,
        match_reason=match_reason,
    )


def _rank_rows(rows: pd.DataFrame) -> pd.DataFrame:
    return rows.sort_values(["_tier_rank", "_n", "YEAR"], ascending=[True, False, False])


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
    if not canonical_query:
        return []

    candidates: dict[str, tuple[float, pd.Series, str, str]] = {}

    def add_rows(
        rows: pd.DataFrame,
        confidence: float,
        match_method: str,
        match_reason: str,
    ) -> None:
        for _, row in _rank_rows(rows).iterrows():
            key = str(row["EMPLOYER_NORM"])
            existing = candidates.get(key)
            if existing is None or confidence > existing[0]:
                candidates[key] = (confidence, row, match_method, match_reason)

    exact_rows = df[df["EMPLOYER_NORM"] == canonical_query]
    if not exact_rows.empty:
        add_rows(
            exact_rows,
            1.0,
            "exact_normalized",
            "The normalized input exactly matched the normalized DOL employer name.",
        )

    query_pattern = r"\b" + re.escape(canonical_query) + r"\b"
    boundary_rows = df[df["EMPLOYER_NORM"].str.contains(query_pattern, na=False, regex=True)]
    if not boundary_rows.empty:
        add_rows(
            boundary_rows,
            0.96,
            "word_boundary",
            "The normalized input appeared as a full-word phrase inside the DOL employer name.",
        )

    collapsed_query = _collapsed(canonical_query)
    if collapsed_query != canonical_query and len(collapsed_query) >= 4:
        collapsed_rows = df[
            df["EMPLOYER_COLLAPSED"].fillna("").str.contains(
                collapsed_query,
                na=False,
                regex=False,
            )
        ]
        if not collapsed_rows.empty:
            add_rows(
                collapsed_rows,
                0.93,
                "spacing_insensitive",
                "The normalized input matched after removing spaces from both names.",
            )

    all_names = df["EMPLOYER_NORM"].dropna().tolist()
    fuzzy_matches = process.extract(
        canonical_query,
        all_names,
        scorer=fuzz.WRatio,
        limit=max(top_n * 5, 20),
    )
    for matched_name, score, _ in fuzzy_matches:
        if score < FUZZY_THRESHOLD:
            continue
        add_rows(
            df[df["EMPLOYER_NORM"] == matched_name],
            score / 100.0,
            "fuzzy",
            f"RapidFuzz WRatio scored {score:.0f}, meeting the {FUZZY_THRESHOLD} threshold.",
        )

    ranked_candidates = sorted(
        candidates.values(),
        key=lambda item: (
            item[0],
            -int(item[1].get("_tier_rank") or 99),
            float(item[1].get("_n") or 0),
            int(float(item[1].get("YEAR") or 0)),
        ),
        reverse=True,
    )
    return [
        _candidate_result(employer_query, row, confidence, match_method, match_reason)
        for confidence, row, match_method, match_reason in ranked_candidates[:top_n]
    ]

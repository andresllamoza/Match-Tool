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
    plan_type_code: Optional[str] = None
    relation_tier: Optional[str] = None
    match_method: str = "unknown"
    match_reason: str = ""

    @property
    def confidence_label(self) -> str:
        if self.confidence >= 0.85:
            return "High"
        if self.confidence >= 0.60:
            return "Medium"
        return "Low"


@dataclass
class EmployerSuggestion:
    """A lightweight employer autocomplete suggestion from the DOL master list."""

    employer_name: str
    recordkeeper: str
    confidence: float
    match_method: str
    ein: Optional[str] = None
    plan_participants: Optional[int] = None


DATA_DIR = Path(__file__).parent.parent / "data"
MASTER_CACHE_FILENAME = "recordkeeper_master.csv"
MASTER_CACHE_VERSION_FILENAME = "recordkeeper_master.version"
MASTER_CACHE_VERSION = "6"

# Prefer the newest complete DOL filing year and keep 2023 as a fallback for
# plans that have not yet filed or were only present in the original MVP data.
DEFAULT_YEARS = (2024, 2023)
TIER_RANK = {"TIER1": 1, "TIER2": 2}
TIER1_RELATION = r"RECORDKEEPER|RECORD KEEPER|RECORDKEEPING|RECORD KEEPING|PLAN RECORDKEEPER"
TIER2_RELATION = r"CONTRACT ADMINISTRATOR|CONTRACT ADMIN"
TIER1_CODES = {"15", "64"}
TIER2_CODES = {"13"}
FUZZY_THRESHOLD = 92
SUGGESTION_FUZZY_THRESHOLD = 70
PLAN_CHARACTERISTIC_RE = re.compile(r"\d[A-Z0-9]")
DC_PLAN_NAME_RE = re.compile(
    r"\b("
    r"401\s*\(?K\)?|"
    r"403\s*\(?B\)?|"
    r"457\s*\(?B\)?|"
    r"PROFIT\s+SHARING|"
    r"DEFINED\s+CONTRIBUTION"
    r")\b",
    re.IGNORECASE,
)

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
SUGGESTION_GENERIC_TOKENS = {
    "ADMINISTRATION",
    "ASSOCIATES",
    "BENEFIT",
    "BENEFITS",
    "BUSINESS",
    "CENTER",
    "CENTERS",
    "ENTERPRISE",
    "ENTERPRISES",
    "GLOBAL",
    "MANAGEMENT",
    "NATIONAL",
    "SERVICE",
    "SERVICES",
    "SYSTEM",
    "SYSTEMS",
}
BRAND_ALIAS_TARGETS = {
    "CITI": ("CITIGROUP",),
}

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

DISNEY_2024_OVERRIDE = {
    "matched_employer_name": "TWDC ENTERPRISES 18 CORP.",
    "recordkeeper": "Fidelity Investments",
    "plan_name": "DISNEY RETIREMENT SAVINGS PLAN",
    "plan_year": 2024,
    "plan_participants": 44099,
    "ein": "95-4545390",
    "plan_type_code": "2A2E2F2G2T3F3H",
    "match_method": "curated_override",
    "match_reason": (
        "Disney's 2024 Form 5500 for the Disney Retirement Savings Plan lists "
        "TWDC Enterprises 18 Corp. as sponsor and Fidelity Investments "
        "Institutional on Schedule C with service code 64."
    ),
}

# Keep this list small: use it only where public filings or plan materials
# identify the 401(k) provider but name matching or DOL rows are misleading.
CURATED_EMPLOYER_OVERRIDES = {
    "DISNEY": DISNEY_2024_OVERRIDE,
    "WALT DISNEY": DISNEY_2024_OVERRIDE,
    "BANK AMERICA": {
        "matched_employer_name": "BANK OF AMERICA CORPORATION",
        "recordkeeper": "Merrill Lynch",
        "plan_name": "THE BANK OF AMERICA 401(K) PLAN",
        "plan_year": 2023,
        "plan_participants": 263860,
        "ein": "560906609",
        "plan_type_code": "2E2F2G2J2K2O2S2T3H3J",
        "match_method": "curated_override",
        "match_reason": (
            "Bank of America 401(k) participant materials direct employees to "
            "Merrill Lynch Benefits OnLine, so this curated override replaces a "
            "misleading DOL pension-plan provider row."
        ),
    }
}

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


def _plan_characteristic_codes(value: object) -> set[str]:
    if pd.isna(value):
        return set()
    return set(PLAN_CHARACTERISTIC_RE.findall(str(value).upper()))


def _has_defined_contribution_pension_code(value: object) -> bool:
    """Return true for Form 5500 pension feature codes that indicate DC plans."""
    return any(code.startswith("2") for code in _plan_characteristic_codes(value))


def _looks_like_defined_contribution_plan_name(value: object) -> bool:
    """Return true when a no-code filing name clearly describes a DC plan."""
    if pd.isna(value):
        return False
    return DC_PLAN_NAME_RE.search(str(value)) is not None


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
        filings["TYPE_PENSION_BNFT_CODE"] = (
            filings["TYPE_PENSION_BNFT_CODE"].fillna("").str.strip().str.upper()
        )
        code_indicates_dc = filings["TYPE_PENSION_BNFT_CODE"].apply(
            _has_defined_contribution_pension_code
        )
        if "PLAN_NAME" in filings.columns:
            name_indicates_dc = filings["PLAN_NAME"].apply(_looks_like_defined_contribution_plan_name)
        else:
            name_indicates_dc = False
        filings = filings[code_indicates_dc | name_indicates_dc].copy()
    filings["EMPLOYER_NORM"] = filings["SPONSOR_DFE_NAME"].apply(_normalize_name)
    if "PLAN_NAME" in filings.columns:
        filings["PLAN_NORM"] = filings["PLAN_NAME"].apply(_normalize_name)
    else:
        filings["PLAN_NORM"] = ""
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
    merged["PLAN_COLLAPSED"] = merged["PLAN_NORM"].apply(_collapsed)
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
    master = master[master["EMPLOYER_NORM"] != ""].copy()

    output_columns = [
        "EMPLOYER",
        "EMPLOYER_NORM",
        "EMPLOYER_COLLAPSED",
        "PLAN_NORM",
        "PLAN_COLLAPSED",
        "RK_RAW",
        "RK_CANON",
        "TIER",
        "YEAR",
        "_n",
        "_tier_rank",
        "PLAN_NAME",
        "TYPE_PENSION_BNFT_CODE",
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


def employer_search_index() -> pd.DataFrame:
    """Return the canonical employer rows needed by the typeahead UI."""
    df = load_dol_data()
    columns = [
        "EMPLOYER",
        "EMPLOYER_NORM",
        "EMPLOYER_COLLAPSED",
        "PLAN_NORM",
        "PLAN_COLLAPSED",
        "RK_RAW",
        "RK_CANON",
        "SPONS_DFE_EIN",
        "TOT_PARTCP_BOY_CNT",
        "_n",
        "_tier_rank",
        "YEAR",
    ]
    available_columns = [column for column in columns if column in df.columns]
    return df[available_columns].copy()


def canonicalize_employer(name: str) -> str:
    """Normalize an employer name using the Colab matcher rules."""
    return _normalize_name(name)


def _text_column(df: pd.DataFrame, column: str) -> pd.Series:
    if column in df.columns:
        return df[column].fillna("").astype(str)
    return pd.Series([""] * len(df), index=df.index, dtype=str)


def _is_meaningful_suggestion_token(token: str) -> bool:
    return token not in SUGGESTION_GENERIC_TOKENS and (
        len(token) >= 3 or any(char.isdigit() for char in token)
    )


def _brand_alias_targets(canonical_query: str) -> tuple[str, ...]:
    return BRAND_ALIAS_TARGETS.get(canonical_query, ())


def _brand_alias_rows(index: pd.DataFrame, alias_target: str) -> pd.DataFrame:
    employer_norms = _text_column(index, "EMPLOYER_NORM")
    return index[
        (employer_norms == alias_target)
        | employer_norms.str.startswith(f"{alias_target} ", na=False)
    ]


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
    plan_year = _first_non_null(row.get("PLAN_YEAR_BEGIN_DATE"), row.get("YEAR"))

    return MatchResult(
        employer_query=employer_query,
        matched_employer_name=str(row.get("EMPLOYER") or ""),
        recordkeeper=str(row.get("RK_CANON") or row.get("RK_RAW") or ""),
        confidence=max(0.0, min(1.0, confidence)),
        plan_name=row.get("PLAN_NAME"),
        plan_year=plan_year,
        plan_participants=participant_count,
        ein=row.get("SPONS_DFE_EIN"),
        plan_type_code=row.get("TYPE_PENSION_BNFT_CODE"),
        relation_tier=row.get("TIER"),
        match_method=match_method,
        match_reason=match_reason,
    )


def _curated_override_result(employer_query: str, canonical_query: str) -> Optional[MatchResult]:
    override = CURATED_EMPLOYER_OVERRIDES.get(canonical_query)
    if override is None:
        return None

    return MatchResult(
        employer_query=employer_query,
        matched_employer_name=override["matched_employer_name"],
        recordkeeper=override["recordkeeper"],
        confidence=1.0,
        plan_name=override["plan_name"],
        plan_year=override["plan_year"],
        plan_participants=override["plan_participants"],
        ein=override["ein"],
        plan_type_code=override["plan_type_code"],
        relation_tier="TIER1",
        match_method=override["match_method"],
        match_reason=override["match_reason"],
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

    for alias_target in _brand_alias_targets(canonical_query):
        alias_rows = _brand_alias_rows(df, alias_target)
        if not alias_rows.empty:
            add_rows(
                alias_rows,
                0.98,
                "brand_alias",
                (
                    f'"{employer_query}" is a known shorthand for {alias_target}; '
                    "the result comes from matching that filing name."
                ),
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

    plan_boundary_rows = df[_text_column(df, "PLAN_NORM").str.contains(query_pattern, regex=True)]
    if not plan_boundary_rows.empty:
        add_rows(
            plan_boundary_rows,
            0.94,
            "plan_word_boundary",
            "The normalized input appeared as a full-word phrase inside the DOL plan name.",
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

        plan_collapsed_rows = df[
            _text_column(df, "PLAN_COLLAPSED").str.contains(
                collapsed_query,
                na=False,
                regex=False,
            )
        ]
        if not plan_collapsed_rows.empty:
            add_rows(
                plan_collapsed_rows,
                0.91,
                "plan_spacing_insensitive",
                "The normalized input matched the DOL plan name after removing spaces.",
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
    results = [
        _candidate_result(employer_query, row, confidence, match_method, match_reason)
        for confidence, row, match_method, match_reason in ranked_candidates[:top_n]
    ]

    override_result = _curated_override_result(employer_query, canonical_query)
    if override_result is not None:
        override_employer_norm = canonicalize_employer(override_result.matched_employer_name)
        results = [
            result
            for result in results
            if canonicalize_employer(result.matched_employer_name) != override_employer_norm
        ]
        results.insert(0, override_result)

    return results[:top_n]


def suggest_employers(employer_query: str, limit: int = 5) -> list[EmployerSuggestion]:
    """
    Suggest related employer names that exist in the lookup data.

    This powers the lightweight UI suggestions below the search box. Suggestions
    ignore too-short or generic queries, then rank exact/prefix/substring/token
    matches before fuzzy fallback so the list stays related and typo-tolerant.
    """
    return suggest_employers_from_index(employer_query, load_dol_data(), limit=limit)


def suggest_employers_from_index(
    employer_query: str,
    index: pd.DataFrame,
    limit: int = 5,
) -> list[EmployerSuggestion]:
    """Suggest employer names from a preloaded canonical employer index."""
    if limit <= 0 or not employer_query or not employer_query.strip():
        return []

    canonical_query = canonicalize_employer(employer_query)
    if len(canonical_query) < 3:
        return []
    query_tokens = [
        token
        for token in canonical_query.split()
        if _is_meaningful_suggestion_token(token)
    ]
    if not query_tokens:
        return []

    candidates: dict[str, tuple[int, float, pd.Series, str]] = {}

    def add_rows(
        rows: pd.DataFrame,
        priority: int,
        confidence: float,
        match_method: str,
    ) -> None:
        for _, row in _rank_rows(rows).iterrows():
            key = str(row["EMPLOYER_NORM"])
            existing = candidates.get(key)
            if existing is None or (priority, confidence) > (existing[0], existing[1]):
                candidates[key] = (priority, confidence, row, match_method)

    employer_norms = _text_column(index, "EMPLOYER_NORM")
    employer_collapsed = _text_column(index, "EMPLOYER_COLLAPSED")
    plan_norms = _text_column(index, "PLAN_NORM")
    plan_collapsed = _text_column(index, "PLAN_COLLAPSED")

    exact_rows = index[employer_norms == canonical_query]
    if not exact_rows.empty:
        add_rows(exact_rows, 4, 1.0, "exact_normalized")

    for alias_target in _brand_alias_targets(canonical_query):
        alias_rows = _brand_alias_rows(index, alias_target)
        if not alias_rows.empty:
            add_rows(alias_rows, 5, 0.98, "brand_alias")

    prefix_rows = index[employer_norms.str.startswith(canonical_query)]
    if not prefix_rows.empty:
        add_rows(prefix_rows, 3, 0.95, "prefix")

    contains_rows = index[employer_norms.str.contains(canonical_query, na=False, regex=False)]
    if not contains_rows.empty:
        add_rows(contains_rows, 2, 0.90, "contains")

    plan_contains_rows = index[plan_norms.str.contains(canonical_query, na=False, regex=False)]
    if not plan_contains_rows.empty:
        add_rows(plan_contains_rows, 2, 0.87, "plan_contains")

    def is_related_by_token(employer_norm: object) -> bool:
        if not query_tokens or pd.isna(employer_norm):
            return False
        employer_tokens = str(employer_norm).split()
        return any(
            employer_token.startswith(query_token) or query_token.startswith(employer_token)
            for query_token in query_tokens
            for employer_token in employer_tokens
            if _is_meaningful_suggestion_token(employer_token)
        )

    token_rows = index[index["EMPLOYER_NORM"].apply(is_related_by_token)]
    if not token_rows.empty:
        add_rows(token_rows, 2, 0.85, "token_related")

    collapsed_query = _collapsed(canonical_query)
    if collapsed_query != canonical_query and len(collapsed_query) >= 4:
        collapsed_rows = index[
            employer_collapsed.str.contains(
                collapsed_query,
                na=False,
                regex=False,
            )
        ]
        if not collapsed_rows.empty:
            add_rows(collapsed_rows, 2, 0.88, "spacing_insensitive")

        plan_collapsed_rows = index[
            plan_collapsed.str.contains(
                collapsed_query,
                na=False,
                regex=False,
            )
        ]
        if not plan_collapsed_rows.empty:
            add_rows(plan_collapsed_rows, 2, 0.86, "plan_spacing_insensitive")

    if len(canonical_query) >= 3:
        all_names = index["EMPLOYER_NORM"].dropna().tolist()
        fuzzy_matches = process.extract(
            canonical_query,
            all_names,
            scorer=fuzz.token_sort_ratio,
            limit=max(limit * 6, 20),
        )
        for matched_name, score, _ in fuzzy_matches:
            if score < SUGGESTION_FUZZY_THRESHOLD:
                continue
            add_rows(
                index[index["EMPLOYER_NORM"] == matched_name],
                1,
                score / 100.0,
                "fuzzy",
            )

    ranked_candidates = sorted(
        candidates.values(),
        key=lambda item: (
            item[0],
            item[1],
            -int(item[2].get("_tier_rank") or 99),
            float(item[2].get("_n") or 0),
            int(float(item[2].get("YEAR") or 0)),
        ),
        reverse=True,
    )
    suggestions = []
    for _, confidence, row, match_method in ranked_candidates[:limit]:
        participants = pd.to_numeric(
            row.get("TOT_PARTCP_BOY_CNT") or row.get("_n"),
            errors="coerce",
        )
        suggestions.append(
            EmployerSuggestion(
                employer_name=str(row.get("EMPLOYER") or ""),
                recordkeeper=str(row.get("RK_CANON") or row.get("RK_RAW") or ""),
                confidence=max(0.0, min(1.0, confidence)),
                match_method=match_method,
                ein=row.get("SPONS_DFE_EIN"),
                plan_participants=None if pd.isna(participants) else int(participants),
            )
        )
    return suggestions

from dataclasses import dataclass
import os
from pathlib import Path
import re
from typing import Optional
import urllib.request
import zipfile

import numpy as np
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
MASTER_CACHE_VERSION = "8"

# Prefer the newest complete DOL filing year, then fall back through older
# releases for plans that have not filed recently or have changed sponsors.
DEFAULT_YEARS = (2024, 2023, 2022, 2021, 2020)
TIER_RANK = {"TIER1": 1, "TIER2": 2, "TIER1_ITEM1": 1, "TIER1_SCH_H": 1}
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
    "DISNEY": ("TWDC",),
    "WALT DISNEY": ("TWDC",),
    # Fortune / brand names → legal DOL employer keys
    "ALPHABET": ("GOOGLE",),
    "FANNIE MAE": ("FEDERAL NATIONAL MORTGAGE ASSOCIATION",),
    "STATE FARM INSURANCE": ("STATE FARM",),
    "EXPRESS SCRIPTS": ("CIGNA",),
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

JPMC_401K_OVERRIDE = {
    "matched_employer_name": "JPMORGAN CHASE BANK, NATIONAL ASSOCIATION",
    "recordkeeper": "Empower",
    "plan_name": "JPMORGAN CHASE 401(K) SAVINGS PLAN",
    "plan_year": 2024,
    "plan_participants": 299277,
    "ein": "134994650",
    "plan_type_code": "2E2F2G2J2K2S2T3F3H",
    "match_method": "curated_override",
    "match_reason": (
        "The JPMorgan Chase 401(k) Savings Plan SPD names Empower as the third-party "
        "recordkeeper. DOL Schedule C Item 1 can list investment managers such as "
        "Fidelity without being the plan recordkeeper."
    ),
}

MCDONALDS_401K_OVERRIDE = {
    "matched_employer_name": "MCDONALDS CORPORATION AND SUBSIDIARIES",
    "recordkeeper": "Empower",
    "plan_name": "MCDONALD'S CORPORATION 401(K) PLAN",
    "plan_year": 2024,
    "plan_participants": 32808,
    "ein": "362361282",
    "plan_type_code": "2E2F2G2I2J2K2P2S2T3H3F",
    "match_method": "curated_override",
    "match_reason": (
        "McDonald's Corporation 401(k) plan materials and SEC filings name Empower "
        "as recordkeeper (since January 2020). DOL Schedule C can still list legacy "
        "providers such as Voya without reflecting the current recordkeeper."
    ),
}

STATE_FARM_401K_OVERRIDE = {
    "matched_employer_name": "STATE FARM MUTUAL AUTOMOBILE INSURANCE COMPANY",
    "recordkeeper": "Alight Solutions",
    "plan_name": "STATE FARM 401(K) SAVINGS PLAN",
    "plan_year": 2024,
    "plan_participants": 102869,
    "ein": "370533100",
    "plan_type_code": "2E2F2G2J2K2S2T3F3H",
    "match_method": "curated_override",
    "match_reason": (
        "State Farm plan materials name Alight Solutions as recordkeeper via the "
        "State Farm Benefits Center (1-866-935-4015). DOL Schedule C may list "
        "Vanguard for investment platform services on the same plan."
    ),
}

# Keep this list small: use it only where public filings or plan materials
# identify the 401(k) provider but name matching or DOL rows are misleading.
CURATED_EMPLOYER_OVERRIDES = {
    "DISNEY": DISNEY_2024_OVERRIDE,
    "WALT DISNEY": DISNEY_2024_OVERRIDE,
    "MCDONALDS": MCDONALDS_401K_OVERRIDE,
    "MCDONALD S": MCDONALDS_401K_OVERRIDE,
    "JP MORGAN CHASE": JPMC_401K_OVERRIDE,
    "JPMORGAN CHASE": JPMC_401K_OVERRIDE,
    "JPMORGAN CHASE BANK NATIONAL ASSOCIATION": JPMC_401K_OVERRIDE,
    "STATE FARM": STATE_FARM_401K_OVERRIDE,
    "STATE FARM INSURANCE": STATE_FARM_401K_OVERRIDE,
    "STATE FARM MUTUAL AUTOMOBILE INSURANCE": STATE_FARM_401K_OVERRIDE,
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
_EMPLOYER_NORM_UNIVERSE: Optional[list[str]] = None
# Skip expensive fuzzy pass when a strong non-fuzzy candidate already exists.
SKIP_FUZZY_MIN_CONFIDENCE = 0.85


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
    text = str(name).upper()
    text = re.sub(r"'S\b", "S", text)  # McDonald's → MCDONALDS (not MCDONALD S)
    cleaned = re.sub(r"[^\w\s&]", " ", text)
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


ITEM1_RECORDKEEPER_NAME_RE = re.compile(
    r"FIDELITY|FID\s|FID\.|RECORD\s*KEEP|RETIREMENT\s+PLAN\s+SRV|PLAN\s+ADMIN|"
    r"EMPOWER|ALIGHT|GREAT\s*WEST|VOYA|PRINCIPAL|NATIONWIDE|"
    r"PAYCHEX|\bADP\b|ASCENSUS|MASSMUTUAL|MUTUAL\s+OF\s+AMERICA",
    re.IGNORECASE,
)
ITEM1_ADVISOR_TRUSTEE_NAME_RE = re.compile(
    r"INV\s+ADV|INVESTMENT\s+ADV|INSTITUTIONAL\s+TRUST|TRUST\s+COMPANY|"
    r"\bMERCER\b|BLACKROCK|NORTHERN\s+TRUST|NEWPORT|WILLIS\s+TOWERS|"
    r"\bAON\b|CONSULT",
    re.IGNORECASE,
)


def _score_item1_provider_name(provider_name: str) -> int:
    """Rank Schedule C Part 1 Item 1 eligible providers toward recordkeeper vs advisor/trustee."""
    upper = provider_name.upper()
    score = 0
    if ITEM1_RECORDKEEPER_NAME_RE.search(upper):
        score += 100
    if re.search(r"WORKPLACE", upper):
        score += 60
    if re.search(r"OPS|OPERATIONS|RECORD|RETIREMENT", upper):
        score += 40
    if ITEM1_ADVISOR_TRUSTEE_NAME_RE.search(upper):
        score -= 50
    if re.search(r"TRUSTEE|CUSTOD", upper) and not re.search(r"FIDELITY|FID\s", upper):
        score -= 30
    return score


def _pick_item1_recordkeeper_provider(provider_names: list[str]) -> Optional[tuple[str, str]]:
    """Return (raw_name, canonical_name) for the best Item 1 eligible provider, if any."""
    ranked: list[tuple[int, str, str]] = []
    for raw_name in provider_names:
        cleaned = str(raw_name or "").strip().upper()
        if not cleaned:
            continue
        canonical = _canonicalize_recordkeeper(cleaned)
        if not canonical:
            continue
        ranked.append((_score_item1_provider_name(cleaned), cleaned, canonical))
    if not ranked:
        return None
    ranked.sort(key=lambda item: item[0], reverse=True)
    _, raw_name, canonical_name = ranked[0]
    return raw_name, canonical_name


def _filing_master_row(
    filing: pd.Series,
    provider_name: str,
    canonical_name: str,
    year: int,
    tier: str,
) -> dict[str, object]:
    employer_norm = filing["EMPLOYER_NORM"]
    plan_norm = filing.get("PLAN_NORM", "")
    return {
        "ACK_ID": filing["ACK_ID"],
        "EMPLOYER": filing["SPONSOR_DFE_NAME"],
        "EMPLOYER_NORM": employer_norm,
        "EMPLOYER_COLLAPSED": _collapsed(employer_norm),
        "PLAN_NORM": plan_norm,
        "PLAN_COLLAPSED": _collapsed(plan_norm) if plan_norm else "",
        "RK_RAW": provider_name,
        "RK_CANON": canonical_name,
        "TIER": tier,
        "YEAR": year,
        "_n": filing.get("_n", 0),
        "_tier_rank": TIER_RANK[tier],
        "PLAN_NAME": filing.get("PLAN_NAME"),
        "TYPE_PENSION_BNFT_CODE": filing.get("TYPE_PENSION_BNFT_CODE"),
        "PLAN_YEAR_BEGIN_DATE": filing.get("PLAN_YEAR_BEGIN_DATE"),
        "TOT_PARTCP_BOY_CNT": filing.get("TOT_PARTCP_BOY_CNT"),
        "SPONS_DFE_EIN": filing.get("SPONS_DFE_EIN"),
    }


def _build_item1_fallback(filings: pd.DataFrame, merged: pd.DataFrame, year: int) -> pd.DataFrame:
    """
    Add recordkeeper rows from Schedule C Part 1 Item 1 (eligible providers) when Item 2
    service codes did not produce a recordkeeper-tier provider for the filing.
    """
    covered_acks = set(merged["ACK_ID"]) if not merged.empty else set()
    missing = filings[~filings["ACK_ID"].isin(covered_acks)].copy()
    if missing.empty:
        return pd.DataFrame()

    item1_path = _ensure_dol_csv(year, f"F_SCH_C_PART1_ITEM1_{year}_Latest")
    item1 = _read_csv_columns(
        item1_path,
        ["ACK_ID", "ROW_ORDER", "PROVIDER_ELIGIBLE_NAME"],
        ["ACK_ID", "PROVIDER_ELIGIBLE_NAME"],
    )
    item1["PROVIDER_ELIGIBLE_NAME"] = (
        item1["PROVIDER_ELIGIBLE_NAME"].fillna("").str.strip().str.upper()
    )
    item1 = item1[item1["PROVIDER_ELIGIBLE_NAME"] != ""]
    item1 = item1[item1["ACK_ID"].isin(missing["ACK_ID"])]

    rows: list[dict[str, object]] = []
    for ack_id, group in item1.groupby("ACK_ID"):
        picked = _pick_item1_recordkeeper_provider(group["PROVIDER_ELIGIBLE_NAME"].tolist())
        if picked is None:
            continue
        raw_name, canonical_name = picked
        filing = missing[missing["ACK_ID"] == ack_id].iloc[0]
        rows.append(
            _filing_master_row(filing, raw_name, canonical_name, year, "TIER1_ITEM1")
        )
    return pd.DataFrame(rows)


def _build_schedule_h_fallback(
    filings: pd.DataFrame,
    merged: pd.DataFrame,
    item1_rows: pd.DataFrame,
    year: int,
) -> pd.DataFrame:
    """
    Use Schedule H fiduciary trust / custodian name fields when still no provider row exists.
    Many large plans list the recordkeeper trust there even when Schedule C codes are sparse.
    """
    covered_acks = set()
    for frame in (merged, item1_rows):
        if not frame.empty and "ACK_ID" in frame.columns:
            covered_acks.update(frame["ACK_ID"].dropna().astype(str))

    missing = filings[~filings["ACK_ID"].isin(covered_acks)].copy()
    if missing.empty:
        return pd.DataFrame()

    sch_h_path = _find_existing_csv(f"F_SCH_H_{year}_Latest")
    if sch_h_path is None:
        try:
            sch_h_path = _ensure_dol_csv(year, f"F_SCH_H_{year}_Latest")
        except Exception:
            return pd.DataFrame()

    sch_h = _read_csv_columns(
        sch_h_path,
        ["ACK_ID", "FDCRY_TRUST_NAME", "FDCRY_TRUSTEE_CUST_NAME"],
        ["ACK_ID"],
    )
    sch_h = sch_h[sch_h["ACK_ID"].isin(missing["ACK_ID"])]

    rows: list[dict[str, object]] = []
    for _, sch_row in sch_h.iterrows():
        provider_name = _first_non_null(
            sch_row.get("FDCRY_TRUST_NAME"),
            sch_row.get("FDCRY_TRUSTEE_CUST_NAME"),
        )
        if not provider_name:
            continue
        canonical_name = _canonicalize_recordkeeper(provider_name)
        if not canonical_name:
            continue
        filing = missing[missing["ACK_ID"] == sch_row["ACK_ID"]].iloc[0]
        rows.append(
            _filing_master_row(
                filing,
                str(provider_name).strip().upper(),
                canonical_name,
                year,
                "TIER1_SCH_H",
            )
        )
    return pd.DataFrame(rows)


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
    merged = merged.rename(
        columns={
            "SPONSOR_DFE_NAME": "EMPLOYER",
            "PROVIDER_OTHER_NAME": "RK_RAW",
        }
    )

    item1_rows = _build_item1_fallback(filings, merged, year)
    sch_h_rows = _build_schedule_h_fallback(filings, merged, item1_rows, year)
    fallback_frames = [frame for frame in (item1_rows, sch_h_rows) if not frame.empty]
    if fallback_frames:
        merged = pd.concat([merged, *fallback_frames], ignore_index=True)
    return merged


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


def _reset_match_caches() -> None:
    global _EMPLOYER_NORM_UNIVERSE
    _EMPLOYER_NORM_UNIVERSE = None


def _employer_norm_universe(df: pd.DataFrame) -> list[str]:
    global _EMPLOYER_NORM_UNIVERSE
    if _EMPLOYER_NORM_UNIVERSE is None:
        _EMPLOYER_NORM_UNIVERSE = df["EMPLOYER_NORM"].dropna().unique().tolist()
    return _EMPLOYER_NORM_UNIVERSE


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
        _reset_match_caches()
        return _DATAFRAME_CACHE

    _DATAFRAME_CACHE = _build_master()
    _reset_match_caches()
    return _DATAFRAME_CACHE


def employer_search_index() -> pd.DataFrame:
    """Return one best row per employer for the typeahead UI (not every plan row)."""
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
    slim = df[available_columns]
    return _rank_rows(slim).drop_duplicates(subset=["EMPLOYER_NORM"], keep="first")


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


def _recordkeeper_source_reason(tier: object, provider_name: object) -> Optional[str]:
    """Explain which part of the 5500 filing package supplied the provider (for Match detail)."""
    tier_text = str(tier or "")
    provider_text = str(provider_name or "").strip()
    if tier_text == "TIER1_ITEM1":
        return (
            "Listed on Schedule C Part 1 (eligible service providers on the filing). "
            "For some large plans the recordkeeper is also named in the Notes to Financial "
            "Statements attached to Schedule H (not available in DOL CSV extracts). "
            "This is separate from the Schedule C Part 1 Item 2 compensation table with "
            "service codes 15/64. "
            f"Provider on filing: {provider_text}."
        )
    if tier_text == "TIER1_SCH_H":
        return (
            "Listed on Schedule H (financial information) as the fiduciary trust or "
            "custodian for plan assets — the section at the end of the financial schedule "
            "in the full 5500 PDF. "
            f"Name on filing: {provider_text}."
        )
    return None


def _candidate_result(
    employer_query: str,
    row: pd.Series,
    confidence: float,
    match_method: str,
    match_reason: str,
) -> MatchResult:
    source_reason = _recordkeeper_source_reason(row.get("TIER"), row.get("RK_RAW"))
    if source_reason:
        match_reason = source_reason

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


def _override_dict_to_result(
    employer_query: str,
    override: dict[str, object],
    *,
    default_match_method: str = "curated_override",
) -> MatchResult:
    return MatchResult(
        employer_query=employer_query,
        matched_employer_name=str(override["matched_employer_name"]),
        recordkeeper=str(override["recordkeeper"]),
        confidence=1.0,
        plan_name=override.get("plan_name"),
        plan_year=override.get("plan_year"),
        plan_participants=override.get("plan_participants"),
        ein=override.get("ein"),
        plan_type_code=override.get("plan_type_code"),
        relation_tier="TIER1",
        match_method=str(override.get("match_method", default_match_method)),
        match_reason=str(override.get("match_reason") or ""),
    )


def _curated_override_result(employer_query: str, canonical_query: str) -> Optional[MatchResult]:
    override = CURATED_EMPLOYER_OVERRIDES.get(canonical_query)
    if override is None:
        return None
    return _override_dict_to_result(employer_query, override)


def _financial_notes_override_result(
    employer_query: str,
    canonical_employer_key: str,
) -> Optional[MatchResult]:
    from src import financial_notes

    entry = financial_notes.registry_entry(canonical_employer_key)
    if entry is None:
        return None
    payload = dict(entry)
    payload.setdefault("match_method", "financial_statement_notes")
    payload.setdefault("match_reason", financial_notes.default_notes_reason(entry))
    return _override_dict_to_result(employer_query, payload, default_match_method="financial_statement_notes")


def _should_try_financial_notes(
    results: list[MatchResult],
    canonical_query: str,
) -> bool:
    from src import financial_notes

    if financial_notes.registry_entry(canonical_query) is not None:
        return True
    if not results:
        return True
    top = results[0]
    if not financial_notes.is_large_plan_participants(top.plan_participants):
        return False
    if financial_notes.dol_tier_is_weak(top.relation_tier):
        return True
    if top.match_method == "fuzzy" and top.confidence < 0.90:
        return True
    return False


def _resolve_financial_notes_override(
    employer_query: str,
    canonical_query: str,
    results: list[MatchResult],
) -> Optional[MatchResult]:
    keys: list[str] = []
    if canonical_query:
        keys.append(canonical_query)
    if results:
        keys.append(canonicalize_employer(results[0].matched_employer_name))
    for key in keys:
        notes_result = _financial_notes_override_result(employer_query, key)
        if notes_result is not None:
            return notes_result
    return None


def _apply_financial_notes_fallback(
    employer_query: str,
    canonical_query: str,
    results: list[MatchResult],
) -> list[MatchResult]:
    from src import financial_notes

    if not _should_try_financial_notes(results, canonical_query):
        return results

    notes_result = _resolve_financial_notes_override(employer_query, canonical_query, results)
    if notes_result is not None:
        employer_norm = canonicalize_employer(notes_result.matched_employer_name)
        filtered = [
            result
            for result in results
            if canonicalize_employer(result.matched_employer_name) != employer_norm
        ]
        return [notes_result, *filtered]

    if results:
        top = results[0]
        if (
            financial_notes.is_large_plan_participants(top.plan_participants)
            and financial_notes.dol_tier_is_weak(top.relation_tier)
            and financial_notes.registry_entry(canonical_query) is None
            and financial_notes.registry_entry(
                canonicalize_employer(top.matched_employer_name)
            )
            is None
        ):
            hint = financial_notes.verification_hint()
            if hint not in (top.match_reason or ""):
                top.match_reason = f"{top.match_reason} {hint}".strip()

    return results


def _rank_rows(rows: pd.DataFrame) -> pd.DataFrame:
    return rows.sort_values(["_tier_rank", "YEAR", "_n"], ascending=[True, False, False])


def _finalize_match_results(
    employer_query: str,
    canonical_query: str,
    ranked_candidates: list[tuple[float, pd.Series, str, str]],
    top_n: int,
) -> list[MatchResult]:
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
    else:
        results = _apply_financial_notes_fallback(employer_query, canonical_query, results)

    return results[:top_n]


def _fuzzy_match_limit(top_n: int) -> int:
    return max(top_n * 5, 20)


def _add_fuzzy_candidate_rows(
    df: pd.DataFrame,
    candidates: dict[str, tuple[float, pd.Series, str, str]],
    matched_name: str,
    score: float,
) -> None:
    if score < FUZZY_THRESHOLD:
        return
    rows = df[df["EMPLOYER_NORM"] == matched_name]
    if rows.empty:
        return
    confidence = score / 100.0
    match_reason = (
        f"RapidFuzz WRatio scored {score:.0f}, meeting the {FUZZY_THRESHOLD} threshold."
    )
    for _, row in _rank_rows(rows).iterrows():
        key = str(row["EMPLOYER_NORM"])
        existing = candidates.get(key)
        if existing is None or confidence > existing[0]:
            candidates[key] = (confidence, row, "fuzzy", match_reason)


def _add_fuzzy_candidates(
    df: pd.DataFrame,
    canonical_query: str,
    candidates: dict[str, tuple[float, pd.Series, str, str]],
    top_n: int,
) -> None:
    """Append fuzzy employer-name matches when non-fuzzy signals are weak."""
    best_confidence = max((item[0] for item in candidates.values()), default=0.0)
    if best_confidence >= SKIP_FUZZY_MIN_CONFIDENCE:
        return

    fuzzy_matches = process.extract(
        canonical_query,
        _employer_norm_universe(df),
        scorer=fuzz.WRatio,
        limit=_fuzzy_match_limit(top_n),
    )
    for matched_name, score, _ in fuzzy_matches:
        _add_fuzzy_candidate_rows(df, candidates, matched_name, score)


def _apply_batch_fuzzy_candidates(
    df: pd.DataFrame,
    fuzzy_queue: list[tuple[int, str, str, dict[str, tuple[float, pd.Series, str, str]]]],
    top_n: int,
) -> None:
    """Run one vectorized fuzzy pass for all batch rows that need it."""
    if not fuzzy_queue:
        return

    universe = _employer_norm_universe(df)
    if not universe:
        return

    queries = [canonical_query for _, _, canonical_query, _ in fuzzy_queue]
    limit = _fuzzy_match_limit(top_n)
    score_matrix = process.cdist(
        queries,
        universe,
        scorer=fuzz.WRatio,
        score_cutoff=FUZZY_THRESHOLD,
        workers=-1,
        dtype=np.float32,
    )

    for row_idx, (_, _employer_query, _canonical_query, candidates) in enumerate(fuzzy_queue):
        row_scores = score_matrix[row_idx]
        if not np.any(row_scores):
            continue
        top_indices = np.argpartition(row_scores, -limit)[-limit:]
        top_indices = top_indices[np.argsort(row_scores[top_indices])[::-1]]
        for choice_index in top_indices:
            score = float(row_scores[choice_index])
            if score < FUZZY_THRESHOLD:
                continue
            _add_fuzzy_candidate_rows(df, candidates, universe[choice_index], score)


def _collect_match_candidates(
    df: pd.DataFrame,
    employer_query: str,
    canonical_query: str,
    top_n: int,
    *,
    skip_fuzzy: bool = False,
) -> dict[str, tuple[float, pd.Series, str, str]]:
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

    if not skip_fuzzy:
        _add_fuzzy_candidates(df, canonical_query, candidates, top_n)

    return candidates


def _rank_match_candidates(
    candidates: dict[str, tuple[float, pd.Series, str, str]],
) -> list[tuple[float, pd.Series, str, str]]:
    return sorted(
        candidates.values(),
        key=lambda item: (
            item[0],
            -int(item[1].get("_tier_rank") or 99),
            int(float(item[1].get("YEAR") or 0)),
            float(item[1].get("_n") or 0),
        ),
        reverse=True,
    )


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

    candidates = _collect_match_candidates(df, employer_query, canonical_query, top_n)
    ranked = _rank_match_candidates(candidates)
    return _finalize_match_results(employer_query, canonical_query, ranked, top_n)


def batch_match_top_results(employer_names: list[str]) -> list[Optional[MatchResult]]:
    """
    Match many employer names efficiently for CSV batch upload.

    Loads DOL data once and skips fuzzy search when a strong exact/alias/boundary
  match already exists (typical for Fortune-style company lists).
    """
    cleaned_names = [str(name or "").strip() for name in employer_names]
    if not cleaned_names:
        return []

    df = load_dol_data()
    results: list[Optional[MatchResult]] = [None] * len(cleaned_names)
    fuzzy_queue: list[tuple[int, str, str, dict[str, tuple[float, pd.Series, str, str]]]] = []

    for index, employer_query in enumerate(cleaned_names):
        if not employer_query:
            continue
        canonical_query = canonicalize_employer(employer_query)
        if not canonical_query:
            continue

        override_result = _curated_override_result(employer_query, canonical_query)
        if override_result is not None:
            results[index] = override_result
            continue

        notes_result = _resolve_financial_notes_override(employer_query, canonical_query, [])
        if notes_result is not None:
            results[index] = notes_result
            continue

        candidates = _collect_match_candidates(
            df,
            employer_query,
            canonical_query,
            top_n=1,
            skip_fuzzy=True,
        )
        ranked = _rank_match_candidates(candidates)
        if ranked and ranked[0][0] >= SKIP_FUZZY_MIN_CONFIDENCE:
            finalized = _finalize_match_results(employer_query, canonical_query, ranked, top_n=1)
            results[index] = finalized[0] if finalized else None
        else:
            fuzzy_queue.append((index, employer_query, canonical_query, candidates))

    _apply_batch_fuzzy_candidates(df, fuzzy_queue, top_n=1)
    for index, employer_query, canonical_query, candidates in fuzzy_queue:
        ranked = _rank_match_candidates(candidates)
        if ranked:
            finalized = _finalize_match_results(employer_query, canonical_query, ranked, top_n=1)
            results[index] = finalized[0] if finalized else None

    return results


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
        employer_tokens = [
            token
            for token in str(employer_norm).split()
            if _is_meaningful_suggestion_token(token)
        ]
        if not employer_tokens:
            return False

        def token_matches(query_token: str) -> bool:
            return any(
                employer_token.startswith(query_token) or query_token.startswith(employer_token)
                for employer_token in employer_tokens
            )

        if len(query_tokens) > 1:
            return all(token_matches(query_token) for query_token in query_tokens)
        return token_matches(query_tokens[0])

    best_priority = max((item[0] for item in candidates.values()), default=0)
    if best_priority < 3 and len(candidates) < limit:
        token_rows = index[index["EMPLOYER_NORM"].apply(is_related_by_token)]
        if not token_rows.empty:
            add_rows(token_rows, 2, 0.85, "token_related")
        best_priority = max((item[0] for item in candidates.values()), default=0)

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

    best_confidence = max((item[1] for item in candidates.values()), default=0.0)
    if (
        len(canonical_query) >= 3
        and best_priority < 3
        and best_confidence < 0.92
        and len(candidates) < limit
    ):
        all_names = index["EMPLOYER_NORM"].dropna().unique().tolist()
        fuzzy_matches = process.extract(
            canonical_query,
            all_names,
            scorer=fuzz.token_sort_ratio,
            limit=max(limit * 6, 20),
        )
        for matched_name, score, _ in fuzzy_matches:
            if score < SUGGESTION_FUZZY_THRESHOLD:
                continue
            if len(query_tokens) > 1:
                matched_tokens = [
                    token
                    for token in str(matched_name).split()
                    if _is_meaningful_suggestion_token(token)
                ]
                if not all(
                    any(
                        matched_token.startswith(query_token)
                        or query_token.startswith(matched_token)
                        for matched_token in matched_tokens
                    )
                    for query_token in query_tokens
                ):
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
            int(float(item[2].get("YEAR") or 0)),
            float(item[2].get("_n") or 0),
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

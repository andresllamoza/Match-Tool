"""Fast employer → recordkeeper lookup from a compact bundled CSV (Streamlit Cloud)."""

from __future__ import annotations

import re
from functools import lru_cache
from pathlib import Path

from engine.models import LookupResult

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
    "CO",
    "HOLDING",
    "INTERNATIONAL",
    "INTL",
    "USA",
    "US",
}
STOPWORDS = {"THE", "AND", "OF", "&"}


def _normalize_name(name: str) -> str:
    text = name.upper().strip()
    text = re.sub(r"'S\b", "S", text)
    cleaned = re.sub(r"[^\w\s&]", " ", text)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    tokens = [
        token
        for token in cleaned.split()
        if token not in LEGAL_SUFFIXES and token not in STOPWORDS
    ]
    return " ".join(tokens)


@lru_cache(maxsize=4)
def _load_index(path: str) -> tuple[dict[str, tuple[str, str, str]], list[str], list[str], list[str]]:
    import pandas as pd

    df = pd.read_csv(path, dtype=str)
    by_norm: dict[str, tuple[str, str, str]] = {}
    norms: list[str] = []
    names: list[str] = []
    rks: list[str] = []
    for row in df.itertuples(index=False):
        norm = str(row.employer_norm)
        name = str(row.employer_name)
        rk = str(row.recordkeeper)
        by_norm[norm] = (norm, name, rk)
        norms.append(norm)
        names.append(name)
        rks.append(rk)
    return by_norm, norms, names, rks


class EmployerIndexAdapter:
    """~90k employers from DOL master, loads in under a second on Streamlit Cloud."""

    name = "matcher5500"

    def __init__(self, path: Path):
        self._path = path

    @classmethod
    def from_csv(cls, path: Path) -> EmployerIndexAdapter | None:
        if not path.is_file():
            return None
        return cls(path)

    def lookup(self, employer_name: str, years=None, state=None) -> LookupResult:
        from rapidfuzz import fuzz, process

        by_norm, norms, names, rks = _load_index(str(self._path))
        key = _normalize_name(employer_name)
        if not key:
            return LookupResult(source=self.name, provider=None, confidence=0.0)

        if key in by_norm:
            _, matched, rk = by_norm[key]
            return LookupResult(
                source=self.name,
                provider=rk,
                confidence=1.0,
                matched_employer_name=matched,
                raw_confidence_label="High",
            )

        hit = process.extractOne(key, norms, scorer=fuzz.WRatio, score_cutoff=96)
        if hit:
            matched_norm, score, idx = hit
            if len(matched_norm) >= max(4, len(key) * 0.45):
                return LookupResult(
                    source=self.name,
                    provider=rks[idx],
                    confidence=score / 100.0,
                    matched_employer_name=names[idx],
                    raw_confidence_label="High" if score >= 85 else "Medium",
                )

        hit = process.extractOne(employer_name, names, scorer=fuzz.WRatio, score_cutoff=92)
        if hit:
            _, score, idx = hit
            return LookupResult(
                source=self.name,
                provider=rks[idx],
                confidence=score / 100.0,
                matched_employer_name=names[idx],
                raw_confidence_label="High" if score >= 85 else "Medium",
            )

        return LookupResult(source=self.name, provider=None, confidence=0.0)

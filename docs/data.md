# Data pipeline

All runtime data lives under **`data/`** (gitignored). Only `data/.gitkeep` is committed.

## Source

Public DOL EBSA FOIA files:

`https://askebsa.dol.gov/FOIA%20Files/{year}/Latest/{filename}.zip`

Default years: **2024, 2023, 2022, 2021, 2020** (`DEFAULT_YEARS` in `src/matcher.py`).

## Files per year

| Zip / CSV stem | Role |
|----------------|------|
| `F_5500_{year}_Latest` | Sponsor, plan name, EIN, participants, pension feature codes |
| `F_SCH_C_PART1_ITEM2_{year}_Latest` | Service providers and relations per filing |
| `F_SCH_C_PART1_ITEM2_CODES_{year}_Latest` | Schedule C service codes per provider row |
| `F_SCH_C_PART1_ITEM1_{year}_Latest` | **Fallback:** eligible provider list (e.g. Fidelity ops co when Item 2 lacks codes 15/64) |
| `F_SCH_H_{year}_Latest` | **Fallback:** fiduciary trust / custodian name on financial schedule (when populated) |

## Join logic (summary)

1. Filter filings to **defined contribution** plans (pension codes starting with `2`, or plan name patterns like `401(k)`).
2. Join providers on `ACK_ID`; attach service codes on `ACK_ID` + `ROW_ORDER`.
3. Classify provider tier:
   - **TIER1:** service codes `15` or `64`, or relation matches recordkeeper patterns.
   - **TIER2:** code `13` or contract administrator relation.
4. **Fallback** when a DC filing has no Item 2 recordkeeper row:
   - **Schedule C Part 1 Item 1** eligible providers (canonical name + recordkeeper-oriented name scoring; fixes cases like Nike → Fidelity).
   - **Schedule H** `FDCRY_TRUST_NAME` / `FDCRY_TRUSTEE_CUST_NAME` when present (the fiduciary/custodian block at the end of Schedule H in the full 5500 PDF).

### PDF vs CSV (important)

The **full 5500** you read on eFast is a bundle: main form, Schedule R, **Schedule H (financial statements)**, Schedule C, etc.

**Notes to Financial Statements** (the CPA attachment behind Schedule H Part III — often page 20+ of the PDF) are **not** in DOL FOIA CSVs. Nike’s 2024 notes (plan year ended May 31, 2024) state explicitly:

> *Fidelity Workplace Services, LLC … is the record keeper of the Plan.*  
> *The Northern Trust Company … is the trustee.*

The matcher uses a **curated override** for Nike keyed to that language. For other employers without an override, we fall back to **Schedule C Part 1 Item 1** (`FID INV INSTL OPS CO` for Nike) when Item 2 lacks recordkeeper service codes 15/64.
5. Canonicalize provider strings → Fidelity, Empower, Merrill, etc. (`CANONICAL_MAP`).
6. Concatenate years; sort by employer, tier, year (desc), participants (desc).

## Cache

| File | Purpose |
|------|---------|
| `data/recordkeeper_master.csv` | Denormalized master used by `match()` |
| `data/recordkeeper_master.version` | Must match `MASTER_CACHE_VERSION` (currently **8**) |

If version mismatches, master is rebuilt on next `load_dol_data()`.

## Environment

| Variable | Example | Effect |
|----------|---------|--------|
| `DOL_YEARS` | `2024,2023` | Limit which years to download/build |

## Outputs written by the app (local)

| File | Written by |
|------|------------|
| `data/lookup_attempts_master.csv` | `src/lookup_log.py` |
| `data/provider_feedback.csv` | `app.py` feedback form |

## Master CSV columns (main ones)

`EMPLOYER`, `EMPLOYER_NORM`, `RK_CANON`, `TIER`, `YEAR`, `PLAN_NAME`, `SPONS_DFE_EIN`, `TOT_PARTCP_BOY_CNT`, …

Inspect after a local build:

```bash
python -c "import pandas as pd; df=pd.read_csv('data/recordkeeper_master.csv', nrows=3); print(df.columns.tolist()); print(df.head())"
```

---

[← Back to home](index.md)

# 5500 Recordkeeper Lookup

Internal PensionBee tool to find the **401(k) recordkeeper** for a US employer using public **DOL Form 5500** filings (Schedule C, recordkeeper-related service codes and relations).

| | |
|---|---|
| **Live app** | Streamlit Community Cloud (password-gated) |
| **Repo** | [andresllamoza/RecordKeeper-Match-Tool](https://github.com/andresllamoza/RecordKeeper-Match-Tool) |
| **Docs site** | [GitHub Pages](https://andresllamoza.github.io/RecordKeeper-Match-Tool/) (architecture, data, demo script) |

---

## Quick start (local demo)

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Optional: skip multi-year download on first run (single year only)
# export DOL_YEARS=2024

cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# Edit app_password in secrets.toml

streamlit run app.py
```

**First run:** the matcher downloads DOL CSVs from [askebsa.dol.gov](https://askebsa.dol.gov) and builds `data/recordkeeper_master.csv` (~2–5 minutes depending on network). Later runs load the cache in a few seconds.

Open `http://localhost:8501`, sign in, type an employer name (at least 3 letters), pick a filing name from suggestions, and view the recordkeeper result.

---

## What it does

- **Single lookup:** typeahead over ~**86k** employer/plan names from DOL filings **2020–2024**, then fuzzy and rule-based matching to a canonical recordkeeper.
- **Batch lookup:** upload a CSV of employer names; download results with confidence tier.
- **Verification:** expandable match detail (plan name, EIN, participants, match reason).
- **Feedback:** flag wrong provider; attempts logged to `data/lookup_attempts_master.csv` (local) for review.

## What it does *not* do

- Roth vs traditional splits, employment status, balance confirmation, rollover advice, or tax guidance.
- It is a **lookup** tool, not a decision system.

---

## Repository map (where to read the code)

| Path | Purpose |
|------|---------|
| [`app.py`](app.py) | Streamlit UI: auth, employer search, results, batch upload, feedback, lookup log |
| [`src/matcher.py`](src/matcher.py) | DOL download/join, master cache, `match()`, `suggest_employers()`, canonical providers, curated overrides |
| [`src/lookup_log.py`](src/lookup_log.py) | Append/read lookup attempt CSV |
| [`tests/test_lookup_log.py`](tests/test_lookup_log.py) | Matcher and logging tests (25 cases) |
| [`recordkeeper_mvp.py`](recordkeeper_mvp.py) | Original Colab export (reference only; production logic is in `src/matcher.py`) |
| [`data/`](data/) | Runtime data (gitignored except `.gitkeep`): DOL CSVs, `recordkeeper_master.csv`, logs |

Theme and Streamlit config: [`.streamlit/config.toml`](.streamlit/config.toml).

---

## Data pipeline

The matcher does **not** ship DOL files in git. On first use it:

1. Downloads per-year zips from DOL FOIA “Latest” URLs (default years **2024 → 2020**).
2. Joins `F_5500`, Schedule C Part 1 Item 2 providers, and service codes; keeps defined-contribution plans and recordkeeper-tier providers.
3. **Fallback** when Item 2 has no recordkeeper codes: Schedule C Part 1 Item 1 eligible providers (e.g. Nike → Fidelity) and Schedule H fiduciary trust fields when filed.
3. Canonicalizes provider names (Fidelity, Empower, Merrill, etc.).
4. Writes **`data/recordkeeper_master.csv`** and version file `data/recordkeeper_master.version` (cache v7).

Override **`DOL_YEARS`** (comma-separated) to limit years, e.g. `export DOL_YEARS=2024` for a faster first build.

See [docs/data.md](docs/data.md) on the GitHub Pages site for file names, columns, and cache behavior.

---

## Demo script (tomorrow)

Use these employers to show search, overrides, and confidence:

| Type in search | Select / expect | Recordkeeper (typical) |
|----------------|-----------------|-------------------------|
| `Amazon` | AMAZON.COM SERVICES, LLC | Fidelity Investments |
| `Disney` or `Walt Disney` | TWDC ENTERPRISES 18 CORP. | Fidelity Investments (curated 2024 override) |
| `Microsoft` | MICROSOFT CORPORATION | Fidelity Investments |
| `Target` | TARGET CORPORATION | Alight Solutions |
| `Walmart` | WALMART INC. | Merrill Lynch |
| `Bank of America` | BANK OF AMERICA CORPORATION | Merrill Lynch (curated; avoids pension-row noise) |
| `Citi` | CITIGROUP INC | Empower Retirement (brand alias) |
| `Nike` | NIKE, INC. | Fidelity Investments (Schedule C Item 1 fallback) |

**Talking points:** DOL legal names vs brand names; “Match detail” explains *why*; batch CSV for Ops; data lag 12–24 months on plan changes.

**Before the demo:** run the app once locally or on Streamlit Cloud so the master cache is warm (cold start otherwise downloads ~1GB+ of CSVs).

---

## Tests

```bash
source venv/bin/activate
python -m unittest tests.test_lookup_log -v
```

All tests use in-memory fixtures; no DOL download required.

---

## Deploy

Streamlit Community Cloud: point the app at `app.py`, set `app_password` in Secrets, Python **3.11** (`runtime.txt`). Full steps: [DEPLOYMENT.md](DEPLOYMENT.md).

---

## Current limitations

- Fortune 1000 reference set: **~666/1000** high-confidence matches on v4 logic (improvement is a separate project).
- Welfare or pension rows can still appear in edge cases; DC filters and curated overrides reduce but do not eliminate noise.
- DOL releases update quarterly; refresh by deleting `data/recordkeeper_master.*` and restarting.

---

## Built by

Andres Llamoza, PensionBee US Operations

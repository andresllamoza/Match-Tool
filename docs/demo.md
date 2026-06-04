# Demo script

Use this flow for a **5–8 minute** walkthrough. Warm the app once before the meeting (first load builds DOL cache).

## 1. Sign in

- Show password gate → internal tool, not public data exposure beyond DOL public filings.

## 2. Single lookup — brand vs legal name

1. Type **`Disney`** (≥3 letters).
2. Show suggestion list: filing names like **TWDC ENTERPRISES 18 CORP.** with Fidelity in meta.
3. Click **Select** on the best match.
4. Result: **Fidelity Investments**, HIGH confidence.
5. Open **Match detail** → read *curated override* reason (2024 5500, Schedule C code 64).

Repeat briefly with **`Amazon`** → **AMAZON.COM SERVICES, LLC** / Fidelity (word-boundary / legal name match).

## 3. Curated override — Bank of America

1. Search **`Bank of America`**.
2. Result: **Merrill Lynch** on **401(k) plan**, not Fidelity from pension row.
3. Match detail explains curated override vs misleading pension filing.

## 4. Item 1 fallback — Nike

1. Type **`Nike`** → select **NIKE, INC.** (401(k) plan).
2. Result: **Fidelity Investments** (from Schedule C Part 1 Item 1 eligible providers — `FID INV INSTL OPS CO` — when Item 2 service codes omit recordkeeper code 64).

## 5. Typeahead quality — Citi

1. Type **`Citi`**.
2. Show **CITIGROUP INC** ranked above **CITI TRENDS INC** (brand alias).

## 6. Batch lookup (optional)

1. Scroll to **Batch lookup**.
2. Upload CSV with column `employer_name` (or `name` / `company` — auto-detected).
3. **Run batch lookup** → summary match rate → **Download results as CSV**.

## 7. Feedback and audit (optional)

- **No, this is not my provider** → correction form.
- **Master list of entered attempts** → Ops audit trail (local/cloud ephemeral).

---

## Suggested CSV for batch smoke test

```csv
employer_name
Microsoft Corporation
Walmart Inc
Target Corporation
```

## If something fails live

| Issue | What to say |
|-------|-------------|
| Long spinner | First load downloading DOL data; retry or use pre-warmed instance |
| No match | Employer may be below 5500 threshold or different spelling in filings |
| Medium confidence | Older filing year or contract-administrator tier — verify in Match detail |

---

[← Back to home](index.md)

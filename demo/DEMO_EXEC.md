# Executive demo — Head of Product & CTO

**Duration:** 3–4 minutes live (or share pre-recorded [`demo/recordkeeper_exec_demo.mp4`](recordkeeper_exec_demo.mp4), ~2:20)  
**Password:** `demo`  
**Batch file:** `demo/fortune_demo_batch_25.csv`

---

## 30-second pitch

> PensionBee Ops needs the **401(k) recordkeeper** for a US employer before we can route a rollover or consolidation. That information lives in public **DOL Form 5500** filings — legal entity names, not brand names — across millions of rows.
>
> This tool **searches ~86k employer/plan names**, matches fuzzy and curated rules, and returns the recordkeeper in **under a second** for a single lookup. Ops can also **batch 25–2,500 names** from a CSV. Every result shows **why** we matched (DOL row, override, or financial-statement notes).

---

## Three proof lookups (if you only have 90 seconds)

| Type & press Enter | Recordkeeper | Why it matters |
|--------------------|--------------|----------------|
| **Nike** | Fidelity Workplace Services, LLC | Notes fallback when Schedule C is thin |
| **JP Morgan Chase** | Empower | Brand ≠ bank legal name; curated override |
| **State Farm Insurance Cos.** | Alight Solutions | DOL row noise; plan-materials override |

---

## Live walkthrough (3:40)

### 0:00–0:15 — Login & UI

- Open app → password `demo`
- Point out **PensionBee gold UI**, single search box, **Enter or Search** (no dead typing lag)

### 0:15–1:30 — Six single lookups (~12s each)

Type name → **Enter** (or gold **Search**) → pause on **result card** (recordkeeper first) → glance at **Other filing names** below.

| # | Type | Highlight |
|---|------|-----------|
| 1 | Walmart | Merrill Lynch — fast baseline |
| 2 | Nike | **Fidelity Workplace Services** — notes registry |
| 3 | Alphabet | **Vanguard** — brand alias (Google) |
| 4 | JP Morgan Chase | **Empower** — override |
| 5 | State Farm Insurance Cos. | **Alight Solutions** — override |
| 6 | Microsoft | Fidelity — high-confidence DOL |

### 1:30–3:20 — Batch (25 rows)

- Scroll to **Batch lookup**
- Upload `demo/fortune_demo_batch_25.csv`
- **Run batch lookup** (~1s warm)
- Slow scroll through table; call out **confidence tier** column
- Show **Download CSV** for Ops handoff

### 3:20–3:40 — Close

- “**Match detail** expander explains provenance — DOL Schedule C, override, or notes.”
- “Data is public DOL; refresh quarterly. Not tax or rollover advice — **lookup only**.”

---

## Anticipated questions

| Question | Answer |
|----------|--------|
| Coverage on Fortune 1000? | ~666/1000 high-confidence on current logic; batch benchmark ~88s for full 1k with warm cache |
| Wrong provider? | Feedback button + `lookup_attempts_master.csv`; curated overrides in `matcher.py` |
| Disney / Amazon? | In batch CSV; Disney uses TWDC brand alias |
| Cold start? | First run downloads DOL zips (~2–5 min); **warm cache before the meeting** |
| Production? | Streamlit Cloud + password; see `DEPLOYMENT.md` |

---

## Pre-meeting checklist

```bash
# Warm cache (run once before demo)
python3 -c "from src.matcher import load_dol_data; load_dol_data()"

# Optional: confirm tests
python3 -m pytest tests/ -q

# Start app
streamlit run app.py
```

- [ ] `app_password` set in `.streamlit/secrets.toml` (local) or Streamlit Secrets (cloud)
- [ ] Browser tab at login screen before attendees join
- [ ] `demo/fortune_demo_batch_25.csv` on desktop or in repo
- [ ] Do **not** open Master attempts log or feedback forms during demo

---

## What we are *not* showing

- Roth vs traditional, balances, employment status
- Web-search enrichment pilot (separate script / HTML doc)
- Full Fortune 1000 batch (too long live; mention benchmark number only)

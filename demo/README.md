# Demo assets

| File | Purpose |
|------|---------|
| [`recordkeeper_demo_90s.mp4`](recordkeeper_demo_90s.mp4) | **Primary demo video** — 5 employers, ≤90s, clean UI |
| [`DEMO_SCRIPT_90s.md`](DEMO_SCRIPT_90s.md) | Timed script for the 90s video |
| [`DEMO_EXEC.md`](DEMO_EXEC.md) | Head of Product / CTO — pitch, proof lookups, checklist |
| [`DEMO_SCRIPT_COMPACT.md`](DEMO_SCRIPT_COMPACT.md) | Longer walkthrough with batch (~4 min) |
| [`fortune_demo_batch_25.csv`](fortune_demo_batch_25.csv) | 25-row batch CSV (`name` column) |

**Clean UI for demos:** open `/?demo=1` to hide batch, filing suggestions, and Streamlit chrome.

**Password:** `demo`

**Warm cache before meeting:**

```bash
python3 -c "from src.matcher import load_dol_data; load_dol_data()"
streamlit run app.py
```

**Re-record 90s video:**

```bash
bash scripts/capture_demo_90s.sh
```

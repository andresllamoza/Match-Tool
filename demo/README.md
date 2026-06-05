# Demo assets

| File | Purpose |
|------|---------|
| [`DEMO_EXEC.md`](DEMO_EXEC.md) | **Head of Product / CTO** — pitch, proof lookups, checklist |
| [`DEMO_SCRIPT_COMPACT.md`](DEMO_SCRIPT_COMPACT.md) | Timed walkthrough for live or recording |
| [`DEMO_SCRIPT.md`](DEMO_SCRIPT.md) | Full 10-lookup + batch script |
| [`fortune_demo_batch_25.csv`](fortune_demo_batch_25.csv) | 25-row batch CSV (`name` column) |
| [`recordkeeper_exec_demo.mp4`](recordkeeper_exec_demo.mp4) | Pre-recorded walkthrough (~2:20, polished gold UI) |

**Password:** `demo`

**Warm cache before meeting:**

```bash
python3 -c "from src.matcher import load_dol_data; load_dol_data()"
streamlit run app.py
```

**Re-record video locally:**

```bash
bash scripts/capture_exec_demo.sh
```

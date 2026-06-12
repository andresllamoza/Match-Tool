# AGENTS.md

## Cursor Cloud specific instructions

### Product overview

Single-service Python app: **DOL 5500 Recordkeeper Lookup** (Streamlit). Users search US employers against public DOL Form 5500 filings to find the likely 401(k) recordkeeper.

### Services

| Service | Port | Start command |
|---------|------|---------------|
| Streamlit app | 8501 | `source venv/bin/activate && streamlit run app.py --server.headless true --server.port 8501` |

No Docker, database, or separate API server.

### One-time local setup (not in update script)

1. **Python venv** — Ubuntu needs `python3.12-venv` before `python3 -m venv venv` works (`sudo apt-get install -y python3.12-venv`).
2. **Streamlit secrets** — Copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml` and set `app_password`. Without this, the login gate blocks the app.

### Testing

```bash
source venv/bin/activate
python -m unittest discover -s tests -v
```

No linter configured in this repo.

### DOL data download (first lookup)

The matcher auto-downloads public DOL FOIA CSVs into `data/` on first use. Default years: 2020–2024 (~300MB+, several minutes). For faster local dev, limit to one year:

```bash
export DOL_YEARS=2024
```

Pre-built cache: `data/recordkeeper_master.csv` (gitignored). Subsequent runs reuse it.

### Optional env vars

- `DOL_YEARS` — comma-separated filing years (default `2024,2023,2022,2021,2020`)
- `LOOKUP_LOG_PATH` — override lookup audit log path (default `data/lookup_attempts_master.csv`)

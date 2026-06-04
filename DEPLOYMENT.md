# Deployment — Streamlit Community Cloud

## Prerequisites

- GitHub repo: [RecordKeeper-Match-Tool](https://github.com/andresllamoza/RecordKeeper-Match-Tool)
- Streamlit Community Cloud account linked to GitHub
- A shared **app password** for internal demo access

## One-time setup

1. Go to [share.streamlit.io](https://share.streamlit.io) → **New app**.
2. **Repository:** `andresllamoza/RecordKeeper-Match-Tool`
3. **Branch:** `main` (or your demo branch)
4. **Main file path:** `app.py`
5. **Python version:** 3.11 (matches `runtime.txt`)

### Secrets

In the app **Settings → Secrets**, add:

```toml
app_password = "your-strong-shared-password"
```

Do not commit real passwords. Local dev: copy [`.streamlit/secrets.toml.example`](.streamlit/secrets.toml.example) to `.streamlit/secrets.toml`.

## First deploy / cold start

On the **first** request after deploy (or after cache invalidation), Streamlit will:

1. Download DOL Form 5500 zips for years 2024–2020 (several hundred MB total).
2. Build `data/recordkeeper_master.csv` inside the container filesystem.

This can take **several minutes** and may hit Streamlit’s execution timeout on the very first load. Mitigations:

- **Warm the app** the day before: open the deployed URL, sign in, run one lookup (e.g. `Microsoft`).
- **Reduce years** for a faster cold start: in Cloud **Advanced settings → Secrets** or environment, you cannot set env vars easily on free tier — for demos, consider a branch with `DOL_YEARS=2024` only (set in matcher via env if you add it to Streamlit secrets as custom config; today use local `export DOL_YEARS=2024` or pre-build cache — see below).

Optional local pre-build before demo (upload is not supported on Community Cloud; warming via HTTP is the practical approach):

```bash
export DOL_YEARS=2024   # optional: single year
python -c "from src.matcher import load_dol_data; load_dol_data(); print('cache ready')"
```

## What gets persisted on Cloud

- **Not persisted** across redeploys: downloaded DOL CSVs and `recordkeeper_master.csv` (ephemeral filesystem).
- **Persisted** only if you add external storage (not in v1): lookup logs and feedback CSVs under `data/` are also ephemeral on Community Cloud.

For demos, rely on the in-session cache after first successful load within the same running instance.

## Health check before a demo

1. Open the app URL → password screen loads.
2. Sign in → employer search appears.
3. Type `Disney` → suggestions include TWDC / Disney plan names.
4. Select employer → **Fidelity Investments**, curated override reason in Match detail.
5. Expand **Batch lookup** → upload a 3-row CSV smoke test.

## Updating the app

Push to `main` (or the branch connected in Streamlit). Cloud rebuilds automatically. If matcher cache version changes (`MASTER_CACHE_VERSION` in `src/matcher.py`), the next session rebuilds the master file.

## GitHub Pages (documentation only)

Docs live in [`docs/`](docs/). Enable in repo **Settings → Pages → Build from branch → `main` → `/docs`**.

Site URL: `https://andresllamoza.github.io/RecordKeeper-Match-Tool/`

This does **not** host the Streamlit app — only README-style documentation for reviewers.

## Troubleshooting

| Symptom | Likely cause | Fix |
|---------|----------------|-----|
| “Set app_password in secrets” | Missing secret | Add `app_password` in Streamlit Secrets |
| Spinner > 5 min then error | DOL download timeout | Warm app; reduce `DOL_YEARS`; retry |
| No suggestions | Query &lt; 3 chars | Type at least 3 letters |
| Wrong provider for BofA / Disney | Old cache | Bump cache version or delete master cache files in `data/` locally |

# Deploy Rollover Companion API

FastAPI backend for the Next.js customer app (`web/`). Ships with the knowledge layer and ~89k employer index baked in — real lookups, no DOL download at runtime.

## Quick path (Railway + Vercel)

1. **Railway** — New project → Deploy from GitHub → set **Root Directory** to `rollover-companion`
2. Wait for deploy; copy the public URL (e.g. `https://rollover-companion-production.up.railway.app`)
3. **Vercel** (`web/` root) — Settings → Environment Variables → `API_URL` = Railway URL (no trailing slash)
4. **Redeploy** Vercel once after setting `API_URL` (the Next.js API proxy reads it at request time)

## Local run

```bash
cd rollover-companion
pip install -r requirements.txt
uvicorn api.server:app --host 0.0.0.0 --port 8000
```

Smoke checks:

```bash
curl http://127.0.0.1:8000/api/health
curl http://127.0.0.1:8000/api/providers
```

## Docker

```bash
cd rollover-companion
docker build -t rollover-companion .
docker run -p 8000:8000 -e CORS_ORIGINS=http://localhost:3000 rollover-companion
```

## Health check

`GET /api/health` → `{"status":"ok"}`

Railway and Render use this path automatically (`railway.toml`, `render.yaml`).

## Baked data (no external fetch)

| Asset | Path |
|-------|------|
| Employer index (~89k rows) | `data/employer_rk_index.csv` |
| Provider playbooks | `rollover-knowledge-layer/*.md` |

When DOL master cache is absent (normal in Docker), `Local5500Adapter` uses the bundled CSV automatically.

## Environment variables

| Variable | Default | Notes |
|----------|---------|-------|
| `PORT` | `8000` | Set by Railway/Render |
| `CORS_ORIGINS` | `*` | Comma-separated allowed origins for Next.js (e.g. `https://your-app.vercel.app`) |
| `PB_SESSION_DB` | `data/pb_sessions.db` | Use a persistent volume path in production |
| `PB_COOKIE_SECURE` | `false` | Set `true` behind HTTPS |
| `JOURNEY_LOG_PATH` | `data/journey_events.jsonl` | Optional analytics log |

**Next.js only:** `API_URL` — set on Vercel, not on this API.

## CORS

Set `CORS_ORIGINS` to your Vercel production URL (and preview URLs if needed):

```
CORS_ORIGINS=https://your-app.vercel.app,https://your-app-*.vercel.app
```

## Persistence

Sessions are stored in SQLite (`PB_SESSION_DB`). Mount a volume at `/app/data` (Railway) or `/var/data` (Render) so journeys survive restarts.

## Tests

```bash
cd rollover-companion
pytest -q
```

209 tests should pass including API health, employer index, and journey flows.

### Frontend smoke (Playwright)

With the API and Next.js dev server running:

```bash
cd web
npm ci
npx playwright install chromium
API_URL=http://127.0.0.1:8000 npm run dev &
PLAYWRIGHT_BASE_URL=http://127.0.0.1:3000 npm run test:e2e
```

Against production: `PLAYWRIGHT_BASE_URL=https://your-app.vercel.app npm run test:e2e`

## Rate limiting

Public endpoints are throttled in-memory (default 60 requests / 60s per IP on journey start and employer lookup). Tune with `RATE_LIMIT_MAX` and `RATE_LIMIT_WINDOW_SEC`.

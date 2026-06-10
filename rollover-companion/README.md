# Rollover Companion

PensionBee's guided **401(k) → IRA rollover engine** — one headless journey rendered on three surfaces:

| Surface | URL | Purpose |
|---------|-----|---------|
| **Customer flow** | `/` | Guided web experience, mobile-first + polished desktop |
| **Agent view** | `/agent` | Same journey for BeeKeepers with intel panel |
| **Embed mode** | `/embed` | Mountable component / iframe for signup flow |
| **Funnel view** | `/funnel` | Internal stall-point analytics from JourneyEvents |

---

## React SPA (mock journey — Head of Product demo)

```bash
cd rollover-companion/spa
npm install && npm run dev
```

Customer flow at `/`, agent console at `/agent`. Journey logic in `useJourney()` + `journeyEngine.ts` — structured for FastAPI swap-in.

## Quick start (no Node.js — recommended)

Pure Python UI: **FastAPI + Jinja2 + HTMX + Tailwind CDN**. One process, cookie + SQLite session persistence.

```bash
cd rollover-companion
pip install -r requirements.txt
bash scripts/dev-htmx.sh
```

Open **http://localhost:8000/customer**, **/agent**, **/embed**, **/sandbox**.

Sessions survive refresh via the HTTP-only `pb_session` cookie and `data/pb_sessions.db`.

## Streamlit demo (production surface for tomorrow)

Customer / BeeKeeper / Funnel in one app — **this is the demo entrypoint**:

```bash
cd rollover-companion
bash scripts/run-sandbox.sh
# or: streamlit run sandbox/app.py
```

- **Surfaces:** segmented control — Customer journey, BeeKeeper intel, Funnel analytics
- **Persistence:** `?journey=` URL + SQLite write-through — survives hard refresh
- **FBO compliance:** every provider shows `PensionBee FBO [name]` from `enrichment.channel_context`
- **Deploy:** Streamlit Cloud main file `rollover-companion/sandbox/app.py`; optional `app_password` secret

## Quick start (Next.js — optional)

```bash
cd rollover-companion
pip install -r requirements.txt

# Terminal 1 — API
python3 -m uvicorn api.server:app --host 0.0.0.0 --port 8000 --reload

# Terminal 2 — Web (requires Node.js)
cd web && npm install && npm run dev
```

Open **http://localhost:3000** (customer), **/agent**, **/embed**, **/funnel**.

Or: `bash scripts/dev.sh` (starts both via tmux).

```bash
pytest -q                  # 32 engine + API tests
python3 cli.py demo        # headless CLI walkthrough
cd web && npm run build    # production frontend build
```

---

## Architecture

```
rollover-knowledge-layer/     Markdown → pydantic (runtime, never hardcoded)
engine/                       State machine, guardrails, assistant, funnel analytics
adapters/                     AdvizorPro stub + 5500 matcher
api/server.py                 FastAPI — JSON API + HTMX HTML surfaces
api/templates/                Jinja2 partials (Tailwind CDN, no build step)
web/                          Next.js 14 — optional; customer, agent, embed, funnel
```

**Event streams** (JSONL, no PII):
- `data/journey_events.jsonl` — every state transition
- `data/comparison_events.jsonl` — every employer lookup

Override with `JOURNEY_LOG_PATH` / `COMPARISON_LOG_PATH`.

---

## Design system

- Canvas `#FAF8F5`, bee yellow `#FFC72C`, charcoal CTAs `#111111`, white cards
- DM Sans, 16px rounded cards, one primary action per screen
- Mobile-first single column; desktop uses wider grid layouts with side panels
- Reconstructed steps show provenance warnings in both customer and agent surfaces
- Errors end with "a BeeKeeper can help" — never raw tracebacks

---

## Embed mode

**iframe:**
```html
<iframe
  src="https://your-host/embed"
  title="Rollover Companion"
  style="width:100%;min-height:640px;border:none;border-radius:16px"
/>
```

**React mount:**
```tsx
import { EmbedWidget } from "./web/src/embed";
<EmbedWidget theme="minimal" />
```

Set `API_URL` when building Next.js if the API is on a different host.

---

## Swapping AdvizorPro

Edit `adapters/advizorpro.py` — replace `lookup()` body with the real API call.
For 5500 matcher: `USE_SYNTHETIC=0` + repo-root `src/matcher.py` deps installed.

---

## What it does NOT do

- No PII, no live provider APIs, no fabricated balances
- No global chatbot — scoped assistant only, refuses out-of-scope questions
- No tax advice — conversions escalate to BeeKeeper

---

## Build status

| Slice | Status |
|-------|--------|
| 1. Engine + CLI + tests | ✅ |
| 2. Customer FIND + ACCESS + full journey UI | ✅ |
| 3. Agent view | ✅ |
| 4. Rollover channels (online / phone / forms) | ✅ |
| 5. Track + funnel + embed | ✅ |

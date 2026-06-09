# Rollover Companion

PensionBee's guided **401(k) → IRA rollover engine** — one headless journey rendered on three surfaces:

| Surface | URL | Purpose |
|---------|-----|---------|
| **Customer flow** | `/` | Guided web experience, mobile-first + polished desktop |
| **Agent view** | `/agent` | Same journey for BeeKeepers with intel panel |
| **Embed mode** | `/embed` | Mountable component / iframe for signup flow |
| **Funnel view** | `/funnel` | Internal stall-point analytics from JourneyEvents |

---

## Quick start (full stack)

```bash
cd rollover-companion
python3 -m pip install -r requirements.txt
pip install -r requirements.txt   # engine + API

# Terminal 1 — API
python3 -m uvicorn api.server:app --host 0.0.0.0 --port 8000 --reload

# Terminal 2 — Web
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
api/server.py                 Thin FastAPI over the engine
web/                          Next.js 14 — customer, agent, embed, funnel
```

**Event streams** (JSONL, no PII):
- `data/journey_events.jsonl` — every state transition
- `data/comparison_events.jsonl` — every employer lookup

Override with `JOURNEY_LOG_PATH` / `COMPARISON_LOG_PATH`.

---

## Design system

- Cream background `#FBF6EC`, brand blue `#1B4F9C`, bee yellow accents
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
For 5500 matcher (default when deps installed): run from repo root with `pip install -r requirements.txt`.
The API (`api/sessions.py`) builds `JourneyEngine` via `adapters/factory.py`, which wires
`Local5500Adapter.from_matcher()` → `src.matcher.match` → `normalize_for_playbook()` → playbook guides.

Set `USE_SYNTHETIC=1` to force fixture employers (no DOL download).

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

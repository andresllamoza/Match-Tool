# Morning Report — Rollover Companion

**GO** — App shell landed on `main`. Back + sticky primary verified on all paths. Suites green. Payee grep clean. Reboot Streamlit Cloud after pull.

Suite: **208 passed** (rollover-companion) + **81 passed** (discovery-front-door) | Payee grep: **clean** | Deployed boot: **reboot required after merge**

## Landed on main

- **App shell** — unified top bar (← Back · 🐝 PensionBee · Save & exit), momentum rail, scrollable body, sticky footer (secondary → primary → BeeKeeper)
- **Engine `go_back`** — `HistorySnapshot` stack; back-through-steps, post-rehydration back, empty-stack no-op verified
- **Phone-step polish** — included (false error fix, call card, palette, script card, no edge_case jargon on customer surface)

## State verification checklist (acceptance walk @ 390px)

| State / path | Back | Sticky primary | Verified |
|--------------|------|----------------|----------|
| `provider_unknown` (employer form) | hidden on fresh | Find my 401(k) (form submit) | ✓ |
| `provider_unknown` → disambiguation | ✓ | choice cards | ✓ |
| `provider_unknown` → provider picker | ✓ | choice cards | ✓ |
| `provider_identified` | ✓ | choice cards (access) | ✓ |
| `provider_not_covered` | ✓ | handoff secondary | ✓ |
| `access_blocked` (access no) | ✓ | Continue | ✓ |
| `access_recovered` → tax | ✓ | choice cards | ✓ |
| `access_recovered` → channel | ✓ | choice cards | ✓ |
| `online_in_progress` | ✓ | Done — next step | ✓ |
| `phone_in_progress` | ✓ | Done — next step | ✓ |
| `forms_in_progress` | ✓ | Done — next step | ✓ |
| `stuck` → back | ✓ | resumes in-channel step | ✓ |
| `initiated` | ✓ | Track my transfer | ✓ |
| `in_flight` | ✓ | Mark complete | ✓ |
| `complete` | hidden | Start another rollover | ✓ |
| `escalated` → back | ✓ | BeeKeeper only | ✓ |
| Post-rehydration `go_back` | ✓ | — | ✓ |

Automated: `discovery-front-door/tests/test_acceptance_walk.py`

## Screenshots

- Shell chrome (390px): `artifacts/screenshots/shell-access-390px.png`, `shell-channel-390px.png`, `shell-phone-step-390px.png`
- Phone steps (390px): `artifacts/screenshots/vanguard-by-phone-390px.png`, `empower-by-phone-390px.png`

## Demo notes

- Entry: `discovery-front-door/app.py` — **reboot Streamlit Cloud** after merge
- Ops surface: **Demo: ops surface & tools** expander
- **Save & exit** persists to SQLite; resume via journey URL

**HOLD** — no new features before demo. Fixes only if acceptance catches regressions.

## Web product path (in progress on `cursor/web-landing-app-route-9ebe`)

- **Not in repo:** TanStack Start (landing claim was not committed). **In repo:** Next.js 14 + FastAPI at `web/` (Vercel Root Directory: `web`).
- **Added:** `/` motion landing (framer-motion), `/app` journey with AppShell (Back · rail · sticky footer), `go_back` in API dispatch.
- **Streamlit** (`discovery-front-door/app.py`) remains ops/BeeKeeper + Streamlit Cloud demo until web deploy is wired.

Rubric score: **8/8 PASS**

# Morning Report — Rollover Companion

**GO / NO-GO:** GO — `discovery-front-door/app.py` is the deployed Streamlit entrypoint; demo-ready with persistence, FBO compliance, and three surfaces.

**Suite:** 201 passed (rollover-companion) + 59 passed (discovery-front-door) | **Payee grep:** clean | **Deployed boot:** ok (`discovery-front-door/app.py`)

## Done

- `290703a` — Compliance hotfix: Empower/Fidelity FBO payee + Check_Destination_Matrix rule
- `1906152` — Engine: matcher5500 index fallback, SQLite SessionStore, FBO invariant tests
- `f4a69ce` — Streamlit sandbox backup (`rollover-companion/sandbox/app.py`)
- `cursor/discovery-front-door-demo-9f5f` — **Production deploy surface:** persistence (`?journey=` + SQLite), welcome-back banner, name capture, FBO card + `st.code` copy + cashout warning, BeeKeeper + Funnel surfaces, channel SLA framing, optional `app_password` gate

## Skipped + why

- **premium-channel-step merge** — skipped per Phase 2 handoff; polish ported directly into `discovery-front-door/` instead
- **discovery-front-door parity with sandbox monolith** — not needed; sandbox remains fallback only

## Rubric score

8/8 on `discovery-front-door` after this branch (tokens, one-decision screens, FBO from enrichment, persistence, mobile CSS, BeeKeeper paths, voice)

## Demo notes

- **Entrypoint:** `discovery-front-door/app.py` on Streamlit Cloud (not `rollover-companion/sandbox/app.py`)
- **Run locally:** `cd discovery-front-door && streamlit run app.py`
- **Secrets:** optional `app_password` in Streamlit secrets
- **FBO moment:** Citi → phone → personalized `PensionBee FBO [name]`; hard refresh resumes via `?journey=`
- **Costco:** type full name or use **Jetstream Airlines** for disambiguation demo; **Uncovered Demo Corp** for concierge handoff

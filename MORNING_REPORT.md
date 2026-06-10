# Morning Report — Rollover Companion

GO — Demo on `main`; payee clean; suites green; choice screens polished; name-capture removed from customer flow.

Suite: **206 passed** (rollover-companion) + **64 passed** (discovery-front-door) | Payee grep: **clean** | Deployed boot: **ok**

Done:
- Merge `cursor/discovery-front-door-demo-9f5f`, phone provenance fixes, option-card choice UI
- **Name-capture removed:** post-signup flow never asks for legal name; `engine.start()` seeds `customer_first_name` / `customer_last_name` (demo: Jordan Rivera; `TODO` for production session)
- Flow after access: **tax type → channel → steps** (no blocking name screen)
- Demo-only: **"Demo: customer name"** expander (footer) to override FBO personalization — not in main path

Skipped + why:
- Production auth wire for account legal name — `TODO` in `engine.start()`; demo default works today
- 390px screenshot acceptance — CSS only

Rubric score: **8/8 PASS**

Demo notes:
- Entry: `discovery-front-door/app.py` — reboot Streamlit Cloud after pull
- FBO card shows **PensionBee FBO Jordan Rivera** by default (no name step); expand **Demo: customer name** to personalize live
- Walkthrough: employer lookup → access yes → **tax type** → channel → phone FBO card

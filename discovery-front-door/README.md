# Ungated Discovery & Value-Reveal Front Door

A pre-signup flow that shows a prospect **concrete value before asking for
commitment** — their likely 401(k) provider, a quantified dollar match, and one
next step — and, behind the same call, **validates whether the free DOL 5500
matcher can replace the paid AdvizorPro database**.

Today discovery is gated behind signup and leans on AdvizorPro. That's the
biggest top-of-funnel leak. This is the Robinhood-style move: a real number,
felt first; signup is the action that comes *after*.

```
employer name ─▶ likely provider ─▶ $ match (from a self-reported range) ─▶ next step
                                                                   (no signup yet)
```

---

## The three beats

1. **DISCOVER (ungated)** — `(employer_name, optional years, optional state)` →
   likely provider + confidence tier, driven by the **free 5500 matcher**. Low
   confidence returns **one disambiguating question, never a list**.
2. **VALUE REVEAL** — from the user's **self-reported balance range** (a coarse
   bucket they pick), compute the illustrative match (`match_rate`, default 1%).
   A real dollar figure, labeled promotional. **No exact balance is ever taken,
   stored, or shown.**
3. **NEXT STEP** — the single action to confirm the real balance at the provider
   (login / set-up-access / lockout fallback, sourced from the rollover
   knowledge layer), then hand to the rollover playbook. **No signup required.**

## The validation harness (the strategic point)

Every discovery runs **both** lookups behind one interface (`ProviderLookupPort`)
and logs a `ComparisonEvent`. Aggregated, that answers: *can the free 5500 tool
replace the paid database, and where does each win?*

```
MATCHER vs ADVIZORPRO  (n=30 synthetic employers)
  agreement rate      : 57%
  matcher coverage    : 80%      advizorpro coverage : 77%
  matcher ONLY (wins) : 5        <- free 5500 found what the paid DB missed
  advizorpro ONLY     : 4        <- remaining gap to close
```

---

## In-product "Add a transfer" flow (the real product surface)

This is the scoped, post-signup experience: a signed-up user adds a transfer →
picks **401(k)** → enters their employer → **AdvizorPro names the recordkeeper**
→ one next step hands off to the rollover playbook. AdvizorPro is invoked **only
inside this flow** — nowhere else.

```bash
streamlit run app.py        # the add-transfer wizard (internal demo)
```

- Pure logic lives in `discovery/add_transfer.py` (tested without a browser);
  `app.py` is a thin Streamlit UI over it.
- No dollar-match figure here — that needs finance/legal sign-off (see the
  value-reveal flow below, which is kept separate for that reason).
- Streamlit is the **internal demo / ops** surface; production lives in
  PensionBee's real web stack.

## Quick start

**Important:** `streamlit run app.py` is only the **discovery / value-reveal** beat (employer → provider → $ match). The full guided rollover UI lives in **`rollover-companion/web`** at `/customer`. After discovery, click **Continue in rollover companion** (or open `/customer` directly).

```bash
# Terminal 1 — rollover engine API
cd rollover-companion && python3 -m uvicorn api.server:app --port 8000

# Terminal 2 — full product UI (PensionBee design system + one-step flow)
cd rollover-companion/web && npm install && npm run dev
# → http://localhost:3000/customer

# Optional — discovery front door (hands off to companion)
export ROLLOVER_COMPANION_URL=http://localhost:3000/customer
USE_SYNTHETIC=1 streamlit run discovery-front-door/app.py
```

Or from repo root: `bash scripts/run-product-demo.sh`

```bash
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt

pytest -q                                                   # discovery tests
streamlit run app.py                                        # discovery only
```

## Lookup source (interim: the 5500 matcher)

The app's lookup source is pluggable via `ProviderLookupPort`:

- **DOL Form 5500 matcher (default)** — wraps `src.matcher.match` from the
  Match-Tool repo. Real employer→recordkeeper lookups. Requires running where
  `src/` is importable (i.e. from the Match-Tool repo) plus `pandas`/`rapidfuzz`.
  First lookup downloads/builds the DOL cache (slow) — warm it before demoing.
- **Synthetic (`USE_SYNTHETIC=1`)** — instant, no data, fake employers. Use to
  show the flow without the DOL download.
- **AdvizorPro (later)** — drop in `discovery/adapters/advizorpro.py`'s real
  API version; nothing else changes.

### Launch options

| Goal | How |
|------|-----|
| **Show the flow now (no data)** | `USE_SYNTHETIC=1 streamlit run app.py`, or deploy with that env var set |
| **Real 5500 lookups** | Deploy from the **Match-Tool repo** on Streamlit Cloud, main file `discovery-front-door/app.py`. Root `requirements.txt` includes `pydantic`/`pyyaml` (added). Warm the DOL cache first (see the matcher's `DEPLOYMENT.md`). |

### Separate internal tooling (not the product surface)

The pre-signup value-reveal flow and the matcher-vs-AdvizorPro validation
harness below are **internal experiments/QA**, not part of the add-transfer
product. Kept because the harness still answers "where does AdvizorPro miss?"

```bash
python cli.py --demo                                        # value-reveal flow + validation summary
python cli.py --compare                                     # matcher-vs-AdvizorPro coverage only
```

As a library:

```python
from discovery import DiscoveryFlow, KnowledgeBridge
from discovery.synthetic import build_adapters
from discovery.models import BalanceRange

adv, matcher = build_adapters()
flow = DiscoveryFlow(adv, matcher, KnowledgeBridge.from_dir())
outcome = flow.run("Acme Robotics Inc", BalanceRange.R_50_100K)
print(outcome.discovery.resolved_provider, outcome.value_reveal.match_low)
```

---

## The public ↔ private data boundary (encoded, not just documented)

| Public / OK to use | Private / never touched here |
|---|---|
| Employer name (user-typed) | The user's **actual account balance** |
| DOL Form 5500 filings (public) | SSN, account numbers, any PII |
| AdvizorPro response (your licensed data) | Live provider account data |
| A **self-reported balance range** (coarse bucket) | A precise balance figure |

The boundary is enforced in the types: `ValueReveal` has **no `balance` field at
all** — only the `BalanceRange` the user picked and figures derived from it
(`test_value_reveal.py` asserts this). The match figure carries a promotional
disclaimer and is never presented as guaranteed.

---

## Swapping the AdvizorPro stub for the real API

`discovery/adapters/advizorpro.py` is a stub that reads a synthetic fixture.
To go live, provide a class with the same shape — that's the entire change:

```python
class AdvizorProAdapter:
    name = "advizorpro"
    def lookup(self, employer_name, years=None, state=None) -> LookupResult:
        resp = advizorpro_client.search(employer_name, state=state)   # real API
        return LookupResult(
            source="advizorpro",
            provider=resp.recordkeeper or None,
            confidence=0.99 if resp.recordkeeper else 0.0,
            matched_employer_name=resp.employer_legal_name,
        )
```

Nothing else changes — `DiscoveryFlow` and the harness depend only on
`ProviderLookupPort`. Likewise, wire the **real 5500 matcher** with
`Local5500Adapter.from_matcher()` (wraps `src.matcher.match`), instead of
`from_synthetic(...)`.

---

## Repository map

| Path | Purpose |
|------|---------|
| `discovery/models.py` | pydantic schema; the data boundary lives here |
| `discovery/ports.py` | `ProviderLookupPort` — the one pluggable interface |
| `discovery/adapters/advizorpro.py` | **stub** paid-DB adapter (swap for the API) |
| `discovery/adapters/matcher5500.py` | 5500 adapter: `from_synthetic` / `from_matcher` |
| `discovery/discover.py` · `value.py` · `next_step.py` | Beats 1 · 2 · 3 |
| `discovery/comparison.py` | `ComparisonEvent` logging + `summarize()` |
| `discovery/flow.py` | orchestrates the beats + harness |
| `discovery/knowledge_bridge.py` | reads the rollover knowledge layer for next steps |
| `discovery/synthetic.py` | ~30 synthetic employers across every outcome |
| `cli.py` | `--discover` / `--compare` / `--demo` |
| `tests/` | 18 pytest cases |

---

## What it does NOT do

- No real PII, no live AdvizorPro call (stubbed), no live provider login — all
  synthetic/static inputs.
- Never fabricates a balance; the value reveal uses a self-reported range only.
- Never presents the match as guaranteed (promotional/illustrative, labeled).
- No chatbot, no UI — typed library + CLI + JSONL outputs, with a clean seam for
  a future web front end.

---

## Built by

Andres Llamoza, PensionBee US Operations.

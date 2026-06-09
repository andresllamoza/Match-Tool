# Rollover Companion

PensionBee's guided **401(k) → IRA rollover engine** — a headless journey state machine
that powers the customer flow, BeeKeeper agent view, and embeddable signup component.

**Slice 1 (this release):** knowledge parser, journey engine, state machine, lookup adapters,
scoped assistant, event logging, CLI, and tests. No UI yet.

---

## What it does

- Parses provider facts from `rollover-knowledge-layer/*.md` at runtime (never hardcoded).
- Runs a typed state machine: `provider_unknown` → `provider_identified` → access →
  rollover (online / phone / forms) → `initiated` → `in_flight` → `complete`, plus
  `stuck` and `escalated`.
- Logs every transition as a `JourneyEvent` (JSONL) and every lookup as a `ComparisonEvent`.
- Looks up recordkeepers via pluggable adapters: **AdvizorPro stub** + **local 5500 matcher**
  (synthetic by default; real matcher when DOL cache is available).
- Enforces tax-routing guardrails (`pre_tax_to_roth` → hard escalation, never advice text).
- Surfaces `reconstructed` steps with provenance warnings in rendered output.
- Exposes a **scoped assistant** that refuses out-of-scope questions.

## What it explicitly does NOT do

- No user PII, no live provider APIs, no credential handling, no fabricated balances.
- No global chatbot — conversation is a scoped escape hatch (assistant module only).
- No tax advice. Conversions and notary requirements route to a BeeKeeper.
- No UI in slice 1 — use the CLI or import the engine as a library.

## Data boundaries

| Data | Source | In engine? |
|------|--------|------------|
| Employer → recordkeeper | Public DOL 5500 / AdvizorPro stub | Lookup adapters only |
| Provider rollover steps | `rollover-knowledge-layer/` markdown | Parsed at runtime |
| Account numbers | Customer-specific | Never auto-surfaced — escalate |
| Balances | User-reported only | Never invented |

---

## Quick start

```bash
cd rollover-companion
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt

pytest -q                          # engine tests
python cli.py demo                 # headless Fidelity online journey
python cli.py lookup "Amazon.com Services LLC"
python cli.py transitions          # valid state machine edges
python cli.py ask "mailing address?" --provider Vanguard --state forms_in_progress
```

### Library usage

```python
from engine import JourneyEngine, JourneyChannel

engine = JourneyEngine()
ctx = engine.start()
engine.lookup_employer(ctx, "Target Corporation")
engine.submit_access(ctx, can_login=True)
engine.choose_channel(ctx, JourneyChannel.ONLINE)
```

---

## Architecture

```
rollover-knowledge-layer/   Markdown → pydantic (provider, mechanism, steps, access_recovery, call_script, form_guidance)
engine/
  knowledge.py              Parser + alias resolution
  journey.py                State machine + screen rendering
  lookup.py                 Dual-adapter lookup + ComparisonEvent
  guardrails.py             Tax routing + escalation pre-emption
  assistant.py              Scoped Q&A (knowledge-layer only)
  events.py                 JourneyEvent + ComparisonEvent JSONL
adapters/
  advizorpro.py             Stub — swap `lookup()` for real API
  matcher5500.py            Synthetic or `src.matcher.match`
cli.py                      Headless demo + inspection
```

Event logs default to `data/journey_events.jsonl` and `data/comparison_events.jsonl`.
Override with `JOURNEY_LOG_PATH` and `COMPARISON_LOG_PATH`.

---

## Swapping the AdvizorPro stub

Implement the `LookupAdapter` protocol in `adapters/advizorpro.py`:

```python
def lookup(self, employer_name: str, ...) -> LookupResult:
    # Call real AdvizorPro API
    return LookupResult(source="advizorpro", provider=..., confidence=...)
```

Pass your adapter into `LookupService(knowledge, matcher, your_adapter, logger)`.

For the 5500 matcher, set `USE_SYNTHETIC=0` and ensure repo-root `src/matcher.py`
dependencies are installed, or keep `USE_SYNTHETIC=1` for demo data.

---

## Build order (vertical slices)

1. **Knowledge parser + journey engine + CLI** ← you are here
2. Customer surface: FIND IT + GET ACCESS (branded Next.js)
3. Agent view of FIND + ACCESS
4. DO THE ROLLOVER: online → phone → forms
5. TRACK IT + funnel view + embed mode

---

## Built by

PensionBee US Operations — Rollover Companion engine.

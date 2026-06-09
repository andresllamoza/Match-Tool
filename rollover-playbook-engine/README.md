# Rollover Playbook Engine

A **decision engine** for 401(k) → PensionBee IRA rollovers. Given a user at a
known point in the funnel with a known recordkeeper, it returns the **single
best next action**, **who owns it**, the path to completion, the check
destination, the escalation triggers, the tax guardrail, the expected SLA, and
the known failure modes with their human-routing actions.

It is **not** a help-doc lookup. Its job is to drive the funnel from
*provider identified* → *rollover initiated* and to pre-empt the failures that
cause drop-off and "where's my money" tickets.

```
provider_identified ──▶ rollover_initiated ──▶ in_flight ──▶ completed
        └── highest-leverage gap; the engine biases toward closing it fast ──┘
```

---

## Why it exists (the value)

The Match-Tool tells you *who* the recordkeeper is. This tells Ops *exactly how
to move the money* — consistently, with the riskiest steps surfaced before the
user hits them. That's the step that converts an acquired user into funded AUM.

---

## Quick start

```bash
cd rollover-playbook-engine
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt

pytest -q                                   # engine + UI helper tests
python cli.py --demo                        # three contrasting mechanisms
python cli.py --provider Empower --flag notary_required
python cli.py --provider Voya --stage rollover_initiated --flag phone_verify_required
```

### Streamlit (standalone — no 5500 matcher)

This tool is **independent** of the DOL employer lookup. Use it to iterate on
provider playbooks, funnel stages, and escalation flags while someone else
tests the 5500 matcher.

```bash
cd rollover-playbook-engine
streamlit run app.py
```

**Streamlit Cloud:** main file `rollover-playbook-engine/app.py` on any branch.
No secrets or DOL cache required.

| Repo tool | Streamlit entry | Purpose |
|---|---|---|
| **This playbook** | `rollover-playbook-engine/app.py` | Recordkeeper known → next action |
| 5500 matcher | `app.py` (repo root) | Employer name → recordkeeper |
| Add-a-transfer demo | `discovery-front-door/app.py` | Full flow: lookup + playbook |

As a library:

```python
from engine import RolloverEngine, FunnelStage

eng = RolloverEngine()
resp = eng.recommend("Fidelity", FunnelStage.PROVIDER_IDENTIFIED)
print(resp.next_action.action, "->", resp.next_action.owner.value)   # one action, owned
```

---

## Operating principles (encoded as behavior, not prose)

1. **One source of truth.** Provider facts live in the markdown front matter of
   `rollover-knowledge-layer/*.md`. Ops edits content; code never carries facts.
2. **One next action, never a menu.** `recommend()` returns exactly one
   `NextAction`. The engine reduces decisions; it does not list them.
3. **Lowest-friction path that completes.** Fidelity two-hop ACAT over a check;
   direct-to-provider check over participant-forward.
4. **Fail loud, route early.** Active escalations/failure modes **pre-empt** the
   normal stage action — the human handoff surfaces before the user hits it.
5. **Provenance is mandatory.** Every step carries `source_status`
   (`verified | reconstructed`). Any reconstructed recommendation is flagged in
   output and never presented as fact.
6. **Tax routing is a guardrail, not advice.** Pre-tax→Traditional, Roth→Roth;
   explicit pre-tax→Roth is a *conversion* → a triggered escalation, never
   guidance text.

---

## Schema (per provider)

`provider`, `aliases`, `mechanism` (`two_hop_acat | check_to_participant |
check_to_provider`), `check_destination`, `forward_step_required`,
`preferred_path`, `sla_days` + `sla_note`, `tax_routing_note`, `next_actions`
(one per funnel stage), `steps[]` (`text`, `owner`, `source_status`),
`edge_cases[]`, `escalation_triggers[]`, `failure_modes[]`
(`symptom` → `routing_action`).

The matrix rule is enforced as a validator: only `check_to_participant`
requires a forward step. Inconsistent data fails to load.

---

## Repository map

| Path | Purpose |
|------|---------|
| `rollover-knowledge-layer/General_Rollover_Guide.md` | **Universal layer** — FIN training facts (address, tax routing, general steps, handoffs) |
| `rollover-knowledge-layer/*_Rollover_Guide.md` | **Provider layer** — Fidelity/Empower/Vanguard/Voya portal paths on top of the general guide |
| `rollover-knowledge-layer/Check_Destination_Matrix.md` | Mechanism matrix + global tax/escalation rules |
| `engine/models.py` | pydantic schema + invariants (mechanism↔forward-step, all stages covered) |
| `engine/knowledge.py` | Parse front matter → typed schema; alias resolution |
| `engine/engine.py` | Decision rule: one next action, escalations pre-empt, provenance surfaced |
| `engine/invocation_log.py` | `log_invocation()` → JSONL measurement hook |
| `cli.py` | CLI incl. `--demo` |
| `tests/` | 20 tests (knowledge, engine, provenance) |

---

## Measurement hook

`log_invocation(provider, funnel_stage, path_taken, outcome)` appends one JSON
line per call (no PII — provider, stage, decision path, outcome only). It's a
deliberate placeholder for funnel instrumentation: swap the sink for a
warehouse/event stream to report **completion-rate lift and time-to-initiation
by provider**. Set `ROLLOVER_LOG_PATH` to redirect it.

---

## Status & provenance

General rollover steps and customer-facing facts come from the FIN training guide
(`General_Rollover_Guide.md`, `verified`). Provider guides add portal-specific
steps on top. Typical processing time defaults to **2–4 weeks** from the general
guide when a provider SLA is not yet quantified.

## What it explicitly does NOT do

- It does **not** invent or "improve" provider steps. If the markdown doesn't
  say it, the engine doesn't claim it. Unknown provider → raises, never guesses.
- No user PII, no live provider API calls, no account data — public/static only.
- No tax advice. Conversions and notary requirements route to a BeeKeeper.
- Streamlit explorer (`app.py`) for Ops/product testing; production UI TBD.

---

## Built by

Andres Llamoza, PensionBee US Operations.

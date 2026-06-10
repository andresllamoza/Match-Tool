---
# GLOBAL routing rules — applied to every provider by the engine.
# Edit this block to change cross-provider behavior; the prose below is human
# reference only and is not parsed.

tax_routing:
  pre_tax: "Pre-tax → Traditional/Rollover IRA"
  roth: "Roth → Roth IRA"
  automatic_when: "Routing is automatic when both PensionBee IRAs are open."
  # Guardrail, NOT advice. Encoded as a triggered escalation below.
  conversion_rule: "Explicit pre-tax → Roth is a Roth conversion (a taxable event). Do not advise — escalate to a BeeKeeper."

# Escalations that apply to ALL providers. `flag` is the boolean an Ops caller
# passes in to activate the trigger. Owner is who the action routes to.
global_escalations:
  - id: pre_tax_to_roth
    flag: pre_tax_to_roth
    trigger: "User explicitly wants pre-tax funds moved into a Roth IRA"
    action: "Roth conversion (taxable event). Do not advise — escalate to a BeeKeeper."
    owner: beekeeper
    source_status: verified

# Failure modes that apply to ALL providers (recordkeeper-agnostic).
global_failure_modes:
  - id: automation_credential_fail
    flag: automation_credential_fail
    symptom: "Automated login / stored credential to the recordkeeper portal fails"
    routing_action: "Route to a BeeKeeper for a manual, guided portal walkthrough before the user stalls."
    owner: beekeeper
    source_status: verified
---

# Check Destination Matrix (Internal Reference)

Routing logic for the rollover playbook. Three mechanisms.

| Provider | Mechanism | Check destination | Forward step needed? | Notable edge case |
|---|---|---|---|---|
| Fidelity | Two-hop IRA → ACAT (preferred) | No check (ACAT) | No | Express rollover to Fidelity Rollover IRA, then ACAT |
| Fidelity (phone fallback) | Call → check | Participant first | Yes | Only if Avenue 3 unavailable |
| Empower | Check-based | Participant first | Yes — prepaid envelope | Notary required on some plans (escalate) |
| Vanguard | Check-based | Directly to IRA provider (PensionBee) | No | — |
| Voya | Check-based | Directly to IRA provider (PensionBee) | No | Phone verification gate on some plans |

## Rules

- **PAYEE vs DESTINATION — never confuse them.** Every rollover check, for every provider, is payable to **PensionBee FBO [user's name]**. "Check destination" above is only WHERE the check is MAILED. A check made payable to the participant personally is a **withdrawal/cashout** (taxable event), not a rollover — stop and escalate to a BeeKeeper before anything is cashed.
- **Fidelity:** prefer the two-hop ACAT (no check). Phone fallback puts the check with the participant.
- **Empower:** check goes to the **participant first**; they forward via prepaid envelope.
- **Vanguard / Voya:** check can usually be sent **directly to the IRA provider (PensionBee)** — no forward step.

## Tax routing (all providers)

Pre-tax → Traditional/Rollover IRA. Roth → Roth IRA. Automatic when both PensionBee IRAs are open. Explicit pre-tax-into-Roth = Roth conversion (taxable) → escalate to BeeKeeper.

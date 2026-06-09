---
provider: Voya
aliases:
  - Voya Financial
  - Voya Institutional
  - ING
mechanism: check_to_provider
check_destination: "Directly to the IRA provider (PensionBee)"
forward_step_required: false
preferred_path: "Online portal; phone fallback. Check mailed directly to PensionBee."
portal: Voya participant portal

sla_days: null
sla_source_status: verified
sla_note: "Typical 2–4 weeks (general guide), but historically SLOWER than Fidelity/Vanguard. Ops to provide median days to fund."

tax_routing_note: "Pre-tax → Traditional/Rollover IRA; Roth → Roth IRA. Pre-tax→Roth = conversion = escalate."

next_actions:
  provider_identified:
    action: "Guide the user to start a direct rollover to the PensionBee IRA in the Voya portal; warn that a phone-verification step may gate the request."
    owner: user
    source_status: verified
  rollover_initiated:
    action: "If the portal stalls pending verification, have the user call Voya to confirm identity/intent so the check is released."
    owner: user
    source_status: verified
  in_flight:
    action: "BeeKeeper tracks the direct check until received and applied; flag the slower historical SLA so the user isn't left waiting."
    owner: beekeeper
    source_status: verified
  completed:
    action: "Rollover complete — funds in the PensionBee IRA. No further action."
    owner: system
    source_status: verified

steps:
  - text: "Log in to the Voya participant portal."
    owner: user
    source_status: verified
  - text: "Locate the old 401(k) plan to roll over."
    owner: user
    source_status: verified
  - text: "Begin the rollover/distribution request and select a direct rollover."
    owner: user
    source_status: verified
  - text: "Set the destination as the PensionBee IRA; check payable per PensionBee instructions, mailed directly to PensionBee where allowed."
    owner: user
    source_status: verified
  - text: "Complete any required forms."
    owner: user
    source_status: verified
  - text: "If the portal stalls pending phone verification, call Voya to confirm identity/intent before the check is released."
    owner: user
    source_status: verified
  - text: "Capture the confirmation screen."
    owner: user
    source_status: verified
  - text: "On receipt of the direct check, BeeKeeper applies it to the PensionBee IRA."
    owner: beekeeper
    source_status: verified

edge_cases:
  - "Phone verification gate on some plans — flag so users aren't left waiting on a stalled portal request."
  - "Historically slower completion times than Fidelity/Vanguard — set timeline expectations."

escalation_triggers: []

failure_modes:
  - id: phone_verify_required
    flag: phone_verify_required
    symptom: "Portal request stalls pending a phone-verification step before the check will release"
    routing_action: "Tell the user to call Voya to confirm identity/intent now; surface this BEFORE they hit a silent stall."
    owner: user
    source_status: verified
---

# Voya Rollover Guide (Internal Reference)

**Provider:** Voya
**Check destination rule:** Check can usually be sent **directly to the IRA provider (PensionBee)**.
**PensionBee preferred path:** Online portal; phone fallback.

## Mechanism

Voya is a check-based external rollover. Like Vanguard, the check can usually be mailed **directly to PensionBee**, so the user does not have to forward it.

> Portal step wording reconstructed from flow memory — spot-check against the live Scribe before publishing.

## Phone verification (known edge case)

Some Voya rollovers require a phone verification step before the request will process. If the portal stalls pending verification, the user must call Voya to confirm identity/intent before the check is released.

## Phone path (when portal fails)

Call Voya, request a rollover. They ask how to make the check payable and whether funds are pre-tax or Roth. For Voya the check can usually be sent **directly to the IRA provider (PensionBee)**.

## Known edge cases

- Phone verification gate on some plans — flag so users aren't left waiting on a stalled portal request.
- Historically slower completion times than Fidelity/Vanguard — set timeline expectations.

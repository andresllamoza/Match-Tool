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
    customer_message: "Start a direct rollover to your PensionBee IRA in the Voya portal. Some plans require a quick phone call to verify your identity before the check is sent — we'll walk you through it if that comes up."
    owner: user
    source_status: verified
  rollover_initiated:
    action: "If the portal stalls pending verification, have the user call Voya to confirm identity/intent so the check is released."
    customer_message: "Your rollover is in motion. If the Voya portal seems stuck, call Voya to confirm your identity — that unlocks the check."
    owner: user
    source_status: verified
  in_flight:
    action: "BeeKeeper tracks the direct check until received and applied; flag the slower historical SLA so the user isn't left waiting."
    customer_message: "We're tracking your check. Voya can take a little longer than other providers — expect 2–4 weeks, sometimes more. We'll keep you updated."
    owner: beekeeper
    source_status: verified
  completed:
    action: "Rollover complete — funds in the PensionBee IRA. No further action."
    customer_message: "Your rollover is complete — your funds are in your PensionBee IRA."
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

access_recovery:
  portal_name: Voya participant portal
  info_needed:
    - "Social Security number"
    - "Date of birth"
    - "Former employer name"
  reset_steps:
    - text: "On the Voya login page, use 'Forgot username/password'."
      owner: user
      source_status: reconstructed
    - text: "Verify identity and reset credentials."
      owner: user
      source_status: reconstructed
  first_time_setup_steps:
    - text: "Register for online access with plan details from your statement."
      owner: user
      source_status: reconstructed
  lockout_fallback:
    phone: "800-584-6001"
    what_to_say: "I need help accessing my former employer 401(k) and may need phone verification for a rollover."
    owner: user
    source_status: verified

call_script:
  phone: "800-584-6001"
  intro: "Call Voya to request a direct rollover — some plans require phone verification before the check releases."
  steps:
    - text: "Confirm identity and rollover intent (phone verification gate on some plans)."
      owner: user
      source_status: verified
    - text: "Request direct rollover to PensionBee IRA — check mailed directly to PensionBee."
      owner: user
      source_status: verified
    - text: "Ask for expected check issuance timeline (Voya can be slower than peers)."
      owner: user
      source_status: verified
  rep_questions:
    - question: "Pre-tax or Roth?"
      answer: "Pre-tax → Traditional IRA. Roth → Roth IRA."
      source_status: verified
    - question: "Mailing address?"
      answer: "PO Box 72, New York, NY 10272"
      source_status: verified
  check_payable: "PensionBee FBO [your name]"
  mailing_address: "PO Box 72, New York, NY 10272"

form_guidance:
  fields:
    - label: "Distribution type"
      instruction: "Direct rollover to external IRA."
      source_status: verified
    - label: "Destination"
      instruction: "PensionBee — PO Box 72, New York, NY 10272"
      source_status: verified
    - label: "Phone verification"
      instruction: "If portal stalls, call Voya to confirm identity before the check releases."
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

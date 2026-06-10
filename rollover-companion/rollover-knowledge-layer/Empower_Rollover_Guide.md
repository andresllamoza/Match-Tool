---
provider: Empower
aliases:
  - Empower Retirement
  - Great-West
mechanism: check_to_participant
check_destination: "Participant first (forwards to PensionBee via prepaid envelope)"
forward_step_required: true
preferred_path: "Online portal where available; phone fallback. Both produce a check to the user."
portal: Empower participant portal

sla_days: null
sla_source_status: verified
sla_note: "Typical 2–4 weeks (general guide). Check-to-participant adds a forward leg; Ops to provide median days to fund."

tax_routing_note: "Pre-tax → Traditional/Rollover IRA; Roth → Roth IRA. Pre-tax→Roth = conversion = escalate."

next_actions:
  provider_identified:
    action: "Guide the user to start a direct rollover in the Empower portal to the PensionBee IRA, and warn now that the check mails to THEM."
    customer_message: "Start a direct rollover to your PensionBee IRA in the Empower portal. Important: Empower mails the check to your home address first — we'll send you a prepaid envelope to forward it to us."
    owner: user
    source_status: verified
  rollover_initiated:
    action: "Confirm Empower mails the check to the user's address on file; PensionBee sends a prepaid envelope for them to forward it."
    customer_message: "Watch for a check in the mail at your address on file. We'll send a prepaid envelope — forward the check to PensionBee as soon as it arrives."
    owner: beekeeper
    source_status: verified
  in_flight:
    action: "BeeKeeper tracks the forwarded check until it is received and applied to the PensionBee IRA."
    customer_message: "We're tracking your rollover. Once the check arrives at your address, forward it using the prepaid envelope we sent. This usually takes 2–4 weeks."
    owner: beekeeper
    source_status: verified
  completed:
    action: "Rollover complete — funds in the PensionBee IRA. No further action."
    customer_message: "Your rollover is complete — your funds are in your PensionBee IRA."
    owner: system
    source_status: verified

steps:
  - text: "Log in to the Empower participant portal."
    owner: user
    source_status: verified
  - text: "Locate the old 401(k) plan to roll over."
    owner: user
    source_status: verified
  - text: "Begin the rollover/distribution request and select a direct rollover."
    owner: user
    source_status: verified
  - text: "Set the destination as the PensionBee IRA (direct rollover; check payable per PensionBee instructions)."
    owner: user
    source_status: verified
  - text: "Complete any required forms."
    owner: user
    source_status: verified
  - text: "Capture the confirmation screen. Confirm the check mails to the user's address; PensionBee sends a prepaid envelope to forward it."
    owner: user
    source_status: verified
  - text: "On receipt of the forwarded check, BeeKeeper applies it to the PensionBee IRA."
    owner: beekeeper
    source_status: verified

edge_cases:
  - "Notary requirement on some plans (escalate; virtual notary support available)."
  - "Check mails to the user, not PensionBee — a common source of user confusion. Set expectation explicitly."

escalation_triggers:
  - id: notary_required
    flag: notary_required
    trigger: "Notary or additional paperwork required on the plan"
    action: "HARD ESCALATION — route to a BeeKeeper. PensionBee offers virtual notary support, which requires human coordination."
    owner: beekeeper
    source_status: verified

failure_modes:
  - id: check_to_user_confusion
    flag: check_to_user_confusion
    symptom: "User expects the check to go straight to PensionBee, but it arrives at their own address"
    routing_action: "Pre-empt at initiation: BeeKeeper sets expectation and ensures the prepaid envelope is sent so the user forwards it."
    owner: beekeeper
    source_status: verified

access_recovery:
  portal_name: Empower participant portal
  info_needed:
    - "Social Security number"
    - "Date of birth"
    - "Former employer name"
  reset_steps:
    - text: "Go to the Empower login page and select 'Forgot username or password?'"
      owner: user
      source_status: reconstructed
    - text: "Complete identity verification and set a new password."
      owner: user
      source_status: reconstructed
  first_time_setup_steps:
    - text: "Choose 'Register' or 'Create an account' on the Empower portal."
      owner: user
      source_status: reconstructed
    - text: "Enter plan/employer details from your statement."
      owner: user
      source_status: reconstructed
  lockout_fallback:
    phone: "800-338-4015"
    what_to_say: "I need help accessing my former employer 401(k) to request a rollover."
    owner: user
    source_status: verified

call_script:
  phone: "800-338-4015"
  intro: "Call Empower and say you want a direct rollover from your old 401(k) to an external IRA."
  steps:
    - text: "Verify identity and confirm the plan you are rolling over."
      owner: user
      source_status: verified
    - text: "Request a direct rollover — check will mail to your address on file."
      owner: user
      source_status: verified
    - text: "Set expectation: you will forward the check to PensionBee using the prepaid envelope."
      owner: user
      source_status: verified
  rep_questions:
    - question: "Pre-tax or Roth?"
      answer: "Pre-tax → Traditional IRA. Roth → Roth IRA."
      source_status: verified
    - question: "Who should the check be payable to?"
      answer: "Payable to you (participant); you forward to PensionBee at PO Box 72, New York, NY 10272."
      source_status: verified
  check_payable: "PensionBee FBO [your name]"
  mailing_address: "Your address on file (then forward to PensionBee)"

form_guidance:
  fields:
    - label: "Distribution type"
      instruction: "Direct rollover to external IRA."
      source_status: verified
    - label: "Receiving institution"
      instruction: "Enter PensionBee as the receiving provider."
      source_status: verified
    - label: "Check destination"
      instruction: "Check mails to YOU first — PensionBee sends a prepaid envelope to forward it."
      source_status: verified
    - label: "Notary"
      instruction: "If notary is required, STOP — escalate to a BeeKeeper (virtual notary available)."
      source_status: verified
---

# Empower Rollover Guide (Internal Reference)

**Provider:** Empower
**Check destination rule:** Check mailed to the **participant first**, who forwards it to PensionBee via prepaid envelope.
**PensionBee preferred path:** Online portal where available; phone fallback. Both produce a check to the user.

## Mechanism

Empower is a check-based external rollover. Unlike Vanguard/Voya, Empower mails the check to the **user's address on file**, not directly to PensionBee. The user forwards it using the prepaid envelope PensionBee provides.

> Portal step wording reconstructed from flow memory — spot-check against the live Scribe before publishing.

## Notary / additional paperwork (HARD ESCALATION)

Some Empower plans require additional forms or notarization. If a notary requirement appears, route to a BeeKeeper — PensionBee offers virtual notary support, which requires human coordination.

## Phone path (when portal fails)

Call Empower, request a rollover. They ask how to make the check payable and whether funds are pre-tax or Roth. **Check goes to the participant first**, who forwards it.

## Known edge cases

- Notary requirement on some plans (escalate; virtual notary support available).
- Check mails to user, not PensionBee — common source of user confusion. Set expectation explicitly.

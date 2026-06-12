---
provider: Vanguard
aliases:
  - The Vanguard Group
  - Vanguard Group
mechanism: check_to_provider
check_destination: "Directly to the IRA provider (PensionBee)"
forward_step_required: false
preferred_path: "Online portal; phone fallback. Check mailed directly to PensionBee."
portal: Vanguard participant portal

sla_days: null
sla_source_status: verified
sla_note: "Typical 2–4 weeks (general guide). Direct-to-provider check."

tax_routing_note: "Pre-tax → Traditional/Rollover IRA; Roth → Roth IRA. Pre-tax→Roth = conversion = escalate."

next_actions:
  provider_identified:
    action: "Guide the user to start a direct rollover to an external IRA in the Vanguard portal, with the check mailed directly to PensionBee."
    customer_message: "Start a direct rollover to your PensionBee IRA in the Vanguard portal. The check can usually be mailed directly to PensionBee — no need to forward it yourself."
    owner: user
    source_status: verified
  rollover_initiated:
    action: "Confirm the check is set payable per PensionBee instructions and mailed directly to PensionBee — no forward step needed."
    customer_message: "Your rollover request is submitted. Vanguard will mail a check directly to PensionBee — this usually takes 2–4 weeks."
    owner: user
    source_status: verified
  in_flight:
    action: "BeeKeeper tracks the direct check until it is received and applied to the PensionBee IRA."
    customer_message: "We're waiting for your check to arrive at PensionBee. Most Vanguard rollovers complete within 2–4 weeks."
    owner: beekeeper
    source_status: verified
  completed:
    action: "Rollover complete — funds in the PensionBee IRA. No further action."
    customer_message: "Your rollover is complete — your funds are in your PensionBee IRA."
    owner: system
    source_status: verified

steps:
  - text: "Navigate to the Vanguard login page and click 'Log In'."
    owner: user
    source_status: verified
  - text: "Enter username and password and log in (use 'Forgot your username or password?' or 'Set up online account access' if needed)."
    owner: user
    source_status: verified
  - text: "Click 'Access my money', then 'Options if I leave my employer'."
    owner: user
    source_status: verified
  - text: "Scroll to 'After you leave your employer, what can you do with your money?' and click 'See what they are'."
    owner: user
    source_status: verified
  - text: "Select the rollover option and choose a direct rollover to an external IRA."
    owner: user
    source_status: verified
  - text: "Enter the PensionBee IRA destination details; set the check payable per PensionBee instructions, mailed directly to PensionBee where allowed."
    owner: user
    source_status: verified
  - text: "Confirm and capture the confirmation screen."
    owner: user
    source_status: verified
  - text: "On receipt of the direct check, BeeKeeper applies it to the PensionBee IRA."
    owner: beekeeper
    source_status: verified

edge_cases:
  - "Direct-to-PensionBee mailing is the default expectation — faster than the participant-forward pattern."

escalation_triggers: []

failure_modes:
  - id: separation_not_confirmed
    flag: separation_not_confirmed
    symptom: "User has not separated from the employer tied to this 401(k), or it is an active plan at a current employer"
    routing_action: "Stop — confirm separation and that this is the correct old plan before initiating. Route to BeeKeeper if unclear."
    owner: beekeeper
    source_status: verified

access_recovery:
  portal_name: Vanguard participant portal
  info_needed:
    - "Social Security number"
    - "Date of birth"
    - "Vanguard account or employer plan details"
  reset_steps:
    - text: "On the Vanguard login page, click 'Forgot your username or password?'"
      owner: user
      source_status: reconstructed
    - text: "Complete verification and reset credentials."
      owner: user
      source_status: reconstructed
  first_time_setup_steps:
    - text: "Select 'Set up online account access' on the Vanguard login page."
      owner: user
      source_status: reconstructed
    - text: "Provide employer/plan info from your statement."
      owner: user
      source_status: reconstructed
  lockout_fallback:
    # phone verified 2026-06-10 — https://corporate.vanguard.com/content/corporatesite/us/en/corp/contact-us.html (retirement plan participants: 800-523-1188)
    phone: "800-523-1188"
    what_to_say: "I need help accessing my former employer 401(k) to request a rollover."
    owner: user
    source_status: verified

call_script:
  # phone verified 2026-06-10 — https://corporate.vanguard.com/content/corporatesite/us/en/corp/contact-us.html (retirement plan participants: 800-523-1188)
  phone: "800-523-1188"
  intro: "Call Vanguard and request a direct rollover from your old 401(k) to an external IRA."
  steps:
    - text: "Confirm identity and the plan being rolled over."
      owner: user
      source_status: verified
    - text: "Request direct rollover — check mailed directly to PensionBee where allowed."
      owner: user
      source_status: verified
    - text: "Capture confirmation number and expected timeline."
      owner: user
      source_status: verified
  rep_questions:
    - question: "Pre-tax or Roth?"
      answer: "Pre-tax → Traditional IRA. Roth → Roth IRA."
      source_status: verified
    - question: "Mailing address for the check?"
      answer: "PO Box 72, New York, NY 10272 — payable per PensionBee instructions."
      source_status: verified
  check_payable: "PensionBee FBO [your name]"
  mailing_address: "PO Box 72, New York, NY 10272"

form_guidance:
  fields:
    - label: "Navigation"
      instruction: "Access my money → Options if I leave my employer → direct rollover to external IRA."
      source_status: reconstructed
    - label: "Receiving provider"
      instruction: "Enter PensionBee destination details."
      source_status: verified
    - label: "Mailing address"
      instruction: "PO Box 72, New York, NY 10272"
      source_status: verified
---

# Vanguard Rollover Guide (Internal Reference)

**Provider:** Vanguard
**Check destination rule:** Check can usually be sent **directly to the IRA provider (PensionBee)**.
**PensionBee preferred path:** Online portal; phone fallback.

## Mechanism

Vanguard is a check-based external rollover. Unlike Empower, the check can usually be mailed **directly to PensionBee**, so the user does not have to forward it.

## Before you start

- User has separated from the employer tied to this 401(k).
- User has online access, a recent statement, or a screenshot showing the balance.
- User has confirmed this is the specific plan to roll over (not an active plan at a current employer).

> Portal step wording reconstructed from flow memory — spot-check against the live Scribe before publishing.

## Phone path (when portal fails)

Call Vanguard, request a rollover. They ask how to make the check payable and whether funds are pre-tax or Roth. For Vanguard the check can usually be sent **directly to the IRA provider (PensionBee)**.

## Notes

- Direct-to-PensionBee mailing is the default expectation — faster than the participant-forward pattern.

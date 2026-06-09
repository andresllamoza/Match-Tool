---
provider: Citi
aliases:
  - Citigroup
  - Citi Retirement Services
mechanism: check_to_provider
check_destination: "Directly to the IRA provider (PensionBee)"
forward_step_required: false
preferred_path: "Online portal or paper forms; check mailed directly to PensionBee."
portal: Citi participant portal

sla_days: null
sla_source_status: verified
sla_note: "7–10 business days for check issuance and receipt (Citi-specific; slower than Fidelity/Vanguard)."

tax_routing_note: "Pre-tax → Traditional/Rollover IRA; Roth → Roth IRA. Pre-tax→Roth = conversion = escalate."

next_actions:
  provider_identified:
    action: "Guide the user through Citi forms with verbatim PensionBee payable and mailing instructions."
    customer_message: "Complete your Citi rollover paperwork with PensionBee as the destination. Citi checks typically take 7–10 business days to arrive."
    owner: user
    source_status: verified
  rollover_initiated:
    action: "Confirm check payable and mailing address match PensionBee instructions exactly."
    customer_message: "Your Citi rollover is submitted. Expect 7–10 business days for the check to reach PensionBee."
    owner: user
    source_status: verified
  in_flight:
    action: "BeeKeeper tracks the direct check; set Citi SLA expectation (7–10 business days)."
    customer_message: "We're tracking your Citi check. These often take 7–10 business days — longer than some other providers."
    owner: beekeeper
    source_status: verified
  completed:
    action: "Rollover complete — funds in the PensionBee IRA. No further action."
    customer_message: "Your rollover is complete — your funds are in your PensionBee IRA."
    owner: system
    source_status: verified

steps:
  - text: "Log in to the Citi participant portal or request paper forms."
    owner: user
    source_status: verified
  - text: "Select direct rollover to an external IRA."
    owner: user
    source_status: verified
  - text: "Enter PensionBee as receiving provider."
    owner: user
    source_status: verified
  - text: "Submit and retain confirmation."
    owner: user
    source_status: verified

edge_cases:
  - "Citi timelines are slower (7–10 business days) — set expectations early."

escalation_triggers: []

failure_modes: []

access_recovery:
  portal_name: Citi participant portal
  info_needed:
    - "Social Security number"
    - "Date of birth"
    - "Former employer or plan name"
  reset_steps:
    - text: "Use 'Forgot password' on the Citi retirement portal."
      owner: user
      source_status: verified
  first_time_setup_steps:
    - text: "Register with plan details from your statement."
      owner: user
      source_status: verified
  lockout_fallback:
    phone: "800-755-8114"
    what_to_say: "I need help accessing my former employer 401(k) to request a rollover."
    owner: user
    source_status: verified

call_script:
  phone: "800-755-8114"
  intro: "Call Citi and request a direct rollover to an external IRA at PensionBee."
  steps:
    - text: "Confirm identity and request a direct rollover distribution."
      owner: user
      source_status: verified
    - text: "Provide PensionBee payable-to and mailing instructions when asked."
      owner: user
      source_status: verified
  rep_questions:
    - question: "Pre-tax or Roth?"
      answer: "Pre-tax → Traditional IRA. Roth → Roth IRA."
      source_status: verified
    - question: "Check payable to?"
      answer: "PensionBee FBO [User's Full Name]"
      source_status: verified
    - question: "Mailing address?"
      answer: "PO Box 72, New York, NY 10272"
      source_status: verified
  check_payable: "PensionBee FBO [User's Full Name]"
  mailing_address: "PO Box 72, New York, NY 10272"

form_guidance:
  fields:
    - label: "Check payable to"
      instruction: "PensionBee FBO [User's Full Name]"
      source_status: verified
    - label: "Mailing address"
      instruction: "PO Box 72, New York, NY 10272"
      source_status: verified
    - label: "Processing timeline"
      instruction: "Expect 7–10 business days for Citi to issue and mail the check."
      source_status: verified
---

# Citi Rollover Guide (Internal Reference)

Citi rollovers use verified PensionBee payable and mailing strings. SLA is **7–10 business days**, slower than Fidelity/Vanguard.

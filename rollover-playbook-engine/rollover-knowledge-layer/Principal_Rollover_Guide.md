---
provider: Principal
aliases:
  - Principal Financial
  - Principal Financial Group
mechanism: check_to_provider
check_destination: "Check mailed directly to PensionBee"
forward_step_required: false
preferred_path: "Online at accounts.principal.com — rollover IRA mailed to financial institution."
portal: accounts.principal.com

sla_days: 10
sla_source_status: verified
sla_note: "7–10 business days for Principal to process and mail the check to PensionBee."

tax_routing_note: "Pre-tax → Traditional/Rollover IRA; Roth → Roth IRA. Pre-tax→Roth = conversion = escalate."

next_actions:
  provider_identified:
    action: "Guide Principal portal rollover — mailed directly to PensionBee."
    customer_message: "Start your Principal rollover at accounts.principal.com. Select rollover to an outside IRA mailed directly to PensionBee."
    owner: user
    source_status: verified
  rollover_initiated:
    action: "Confirm mailed-to-institution delivery; set 7–10 business day expectation."
    customer_message: "Your Principal rollover is submitted. The check is mailed directly to PensionBee and usually takes 7–10 business days."
    owner: user
    source_status: verified
  in_flight:
    action: "BeeKeeper tracks Principal check to PensionBee."
    customer_message: "We're tracking your Principal check — these typically take 7–10 business days to reach PensionBee."
    owner: beekeeper
    source_status: verified
  completed:
    action: "Rollover complete — funds in PensionBee IRA."
    customer_message: "Your rollover is complete — your funds are in your PensionBee IRA."
    owner: system
    source_status: verified

steps:
  - text: "Go to accounts.principal.com and click Log in."
    owner: user
    source_status: verified
  - text: "Enter your username and click Next."
    owner: user
    source_status: verified
  - text: "Enter your password and click Verify."
    owner: user
    source_status: verified
  - text: "From your 401(k) overview, click Rollovers, then Rollover IRA."
    owner: user
    source_status: verified
  - text: "Under Move outside Principal, click Learn more about an outside IRA."
    owner: user
    source_status: verified
  - text: "Click Start request to begin your rollover to PensionBee."
    owner: user
    source_status: verified
  - text: "Select Traditional pre-tax IRA or Roth IRA to match your funds, then Distribution details."
    owner: user
    source_status: verified
  - text: "Select Transfer the entire available amount, then Delivery options."
    owner: user
    source_status: verified
  - text: "Select Mailed directly to a financial institution, then Final review."
    owner: user
    source_status: verified
  - text: "Review rollover details including fees, then Submit."
    owner: user
    source_status: verified
  - text: "Accept disclosures, confirm today's date, and Submit request."
    owner: user
    source_status: verified
  - text: "Enter the phone verification code and click Verify."
    owner: user
    source_status: verified
  - text: "Save your request number and send the confirmation screenshot to PensionBee (BeeHive or info@pensionbee.com — subject: Your Name + Principal + Rollover Confirmation)."
    owner: user
    source_status: verified

edge_cases:
  - "Principal typically takes 7–10 business days to process and mail the check."
  - "Distribution fee reduces the amount received — review estimated amount on final screen."

escalation_triggers: []

failure_modes: []

access_recovery:
  portal_name: Principal accounts portal
  info_needed:
    - "Principal username"
    - "Social Security number"
  reset_steps:
    - text: "Use Forgot username or password on accounts.principal.com."
      owner: user
      source_status: verified
  first_time_setup_steps:
    - text: "Register using plan details from your Principal statement."
      owner: user
      source_status: verified
  lockout_fallback:
    # phone verified 2026-06-10 — https://www.principal.com/service-and-support (401k participants: 800-547-7754)
    phone: "800-547-7754"
    what_to_say: "I need help accessing my Principal 401(k) to request a rollover."
    owner: user
    source_status: verified

call_script:
  # phone verified 2026-06-10 — https://www.principal.com/service-and-support (401k participants: 800-547-7754)
  phone: "800-547-7754"
  intro: "Call Principal and request a direct rollover to PensionBee mailed to the financial institution. Use general PensionBee payable and mailing when asked."
  steps:
    - text: "Confirm identity and request direct rollover to external IRA at PensionBee."
      owner: user
      source_status: verified
    - text: "Request check be mailed directly to PensionBee (financial institution)."
      owner: user
      source_status: verified
    - text: "When asked for check payable-to and mailing address, use PensionBee rollover instructions."
      owner: user
      source_status: verified
  rep_questions:
    - question: "Pre-tax or Roth?"
      answer: "Pre-tax → Traditional IRA. Roth → Roth IRA."
      source_status: verified
    - question: "Check payable to?"
      answer: "PensionBee FBO [your name]"
      source_status: verified
    - question: "Mailing address?"
      answer: "PO Box 72, New York, NY 10272"
      source_status: verified
  check_payable: "PensionBee FBO [your name]"
  mailing_address: "PO Box 72, New York, NY 10272"

form_guidance:
  fields:
    - label: "Receiving institution"
      instruction: "PensionBee"
      source_status: verified
    - label: "Check payable to"
      instruction: "PensionBee FBO [your name]"
      source_status: verified
    - label: "Mailing address"
      instruction: "PO Box 72, New York, NY 10272"
      source_status: verified
    - label: "Processing timeline"
      instruction: "Expect 7–10 business days for Principal to mail the check to PensionBee."
      source_status: verified
---

# Principal Rollover Guide (Internal Reference)

Source: [Scribe — Principal Rollover guide](https://scribehow.com/viewer/Principal__Rollover_guide___iYBQwhJRC2w9jTjosGAhA)

Phone fallback uses **general rollover guide** payable/mailing strings.

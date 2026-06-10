---
provider: Merrill Lynch
aliases:
  - Merrill
  - Bank of America Merrill Lynch
  - Benefits OnLine
mechanism: check_to_participant
check_destination: "Check mailed to participant address on file; forward to PensionBee via prepaid envelope"
forward_step_required: true
preferred_path: "Online at benefits.ml.com — rollover to external IRA at PensionBee."
portal: benefits.ml.com

sla_days: null
sla_source_status: verified
sla_note: "Typical 2–4 weeks including check mail to participant and forward to PensionBee."

tax_routing_note: "Pre-tax → Traditional/Rollover IRA; Roth → Roth IRA. Pre-tax→Roth = conversion = escalate."

next_actions:
  provider_identified:
    action: "Guide Merrill Benefits OnLine rollover; warn check mails to user address first."
    customer_message: "Start your Merrill rollover at benefits.ml.com. Important: the check is mailed to your address on file — we'll send a prepaid envelope to forward it to PensionBee."
    owner: user
    source_status: verified
  rollover_initiated:
    action: "Confirm address on file is current; Merrill mails check to participant; PensionBee sends prepaid envelope."
    customer_message: "Your Merrill rollover is submitted. Watch for the check at your home address, then forward it using the prepaid envelope we send."
    owner: beekeeper
    source_status: verified
  in_flight:
    action: "BeeKeeper tracks forwarded check until received at PensionBee."
    customer_message: "We're tracking your Merrill rollover. Forward the check as soon as it arrives — this usually takes 2–4 weeks total."
    owner: beekeeper
    source_status: verified
  completed:
    action: "Rollover complete — funds in PensionBee IRA."
    customer_message: "Your rollover is complete — your funds are in your PensionBee IRA."
    owner: system
    source_status: verified

steps:
  - text: "Go to benefits.ml.com/Accounts/Home and log in to your Merrill account."
    owner: user
    source_status: verified
  - text: "Click your plan name under Employer Sponsored Plans."
    owner: user
    source_status: verified
  - text: "Click View your withdrawal and rollover options."
    owner: user
    source_status: verified
  - text: "Under Rollover to an IRA, click Start a Rollover."
    owner: user
    source_status: verified
  - text: "Under Withdrawal Type, select SEPARATED FROM SERVICE WITHDRAWAL."
    owner: user
    source_status: verified
  - text: "Under Rollover Amount, check Maximum for a full rollover, then Continue."
    owner: user
    source_status: verified
  - text: "Select Rollover to another financial institution, then Add another Institution."
    owner: user
    source_status: verified
  - text: "Under Rollover Account Type, select IRA."
    owner: user
    source_status: verified
  - text: "In Rollover Institution Name, type PensionBee."
    owner: user
    source_status: verified
  - text: "Enter your PensionBee account number from BeeHive (upper-right icon) — BeeKeeper can help if needed."
    owner: user
    source_status: verified
  - text: "Verify the address on file matches your current address and click Save. If wrong, call Merrill to update before proceeding."
    owner: user
    source_status: verified
  - text: "Read Merrill's notice and click Next."
    owner: user
    source_status: verified
  - text: "Under Delivery Selections, select Standard Mail and Continue."
    owner: user
    source_status: verified
  - text: "Review the 402(f) Tax Notice, enter your Benefits OnLine password, Submit, and send the confirmation screenshot to PensionBee (BeeHive or info@pensionbee.com — subject: Your Name + Merrill + Rollover Confirmation)."
    owner: user
    source_status: verified

edge_cases:
  - "Address on file must match current address — all checks go there. Call Merrill to update if wrong."
  - "Check mails to the participant, not PensionBee — PensionBee sends a prepaid envelope to forward."

escalation_triggers: []

failure_modes:
  - id: address_mismatch
    flag: address_mismatch
    symptom: "Mailing address on Merrill file does not match customer's current address"
    routing_action: "Do not proceed — customer must call Merrill to update address before rollover."
    owner: beekeeper
    source_status: verified

access_recovery:
  portal_name: Merrill Benefits OnLine
  info_needed:
    - "Benefits OnLine username"
    - "Social Security number"
  reset_steps:
    - text: "Go to benefits.ml.com and use Forgot username or password."
      owner: user
      source_status: verified
  first_time_setup_steps:
    - text: "Register for Benefits OnLine using plan details from your statement."
      owner: user
      source_status: verified
  lockout_fallback:
    # phone verified 2026-06-10 — https://www.benefits.ml.com/ (Retirement & Benefits Contact Center: 800-228-4015)
    phone: "800-228-4015"
    what_to_say: "I need help accessing my Merrill 401(k) to request a rollover."
    owner: user
    source_status: verified

call_script:
  # phone verified 2026-06-10 — https://www.benefits.ml.com/ (Retirement & Benefits Contact Center: 800-228-4015)
  phone: "800-228-4015"
  intro: "Call Merrill and request a direct rollover to PensionBee. If portal steps fail, use general PensionBee payable and mailing instructions."
  steps:
    - text: "Confirm identity and request a direct rollover to an external IRA at PensionBee."
      owner: user
      source_status: verified
    - text: "Note the check will mail to your address on file — PensionBee will send a prepaid envelope to forward it."
      owner: user
      source_status: verified
    - text: "When asked for payable and mailing details, use PensionBee rollover instructions."
      owner: user
      source_status: verified
  rep_questions:
    - question: "Pre-tax or Roth?"
      answer: "Pre-tax → Traditional IRA. Roth → Roth IRA."
      source_status: verified
    - question: "Check payable to?"
      answer: "PensionBee FBO [your name] (or payable to you if they mail to participant — forward to PensionBee)"
      source_status: verified
    - question: "Mailing address?"
      answer: "Your address on file for participant delivery; forward to PO Box 72, New York, NY 10272"
      source_status: verified
  check_payable: "PensionBee FBO [your name]"
  mailing_address: "Your address on file (forward to PensionBee)"

form_guidance:
  fields:
    - label: "Rollover institution"
      instruction: "PensionBee"
      source_status: verified
    - label: "Account number"
      instruction: "PensionBee IRA account number from BeeHive — route to BeeKeeper if needed."
      source_status: verified
    - label: "Check payable to"
      instruction: "PensionBee FBO [your name]"
      source_status: verified
---

# Merrill Lynch Rollover Guide (Internal Reference)

Source: [Scribe — Merrill Rollover Guide](https://scribehow.com/viewer/Merrill_Rollover_Guide__Ly5TkN1gSbeQMa7uqJGkpA)

Phone fallback uses **general rollover guide** payable/mailing when reps ask.

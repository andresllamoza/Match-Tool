---
provider: Alight Solutions
aliases:
  - Alight
  - Alight Financial
mechanism: check_to_provider
check_destination: "Electronic direct rollover to PensionBee (via UMB); check fallback possible"
forward_step_required: false
preferred_path: "Online via employer HR site → RolloverCentral → select PensionBee → direct electronic rollover."
portal: "Employer benefits site (via alight.com/find-your-hr-website)"

sla_days: null
sla_source_status: verified
sla_note: "2–3 business days for electronic direct rollover; up to 2 weeks if sent by check."

tax_routing_note: "Pre-tax → Traditional/Rollover IRA; Roth → Roth IRA. Pre-tax→Roth = conversion = escalate."

next_actions:
  provider_identified:
    action: "Guide user through Alight → RolloverCentral → PensionBee VAN entry and direct rollover submission."
    customer_message: "Roll over via your employer's Alight benefits site and RolloverCentral. You'll link your PensionBee account with a 14-digit VAN from BeeHive, then submit a direct electronic rollover."
    owner: user
    source_status: verified
  rollover_initiated:
    action: "Confirm VAN matches PensionBee account; user submitted direct rollover; $25 fee acknowledged."
    customer_message: "Your Alight rollover is submitted. Electronic transfers usually arrive in 2–3 business days. Send your confirmation screenshot to PensionBee via BeeHive chat or info@pensionbee.com."
    owner: user
    source_status: verified
  in_flight:
    action: "BeeKeeper tracks electronic transfer or check; set 2–3 day vs 2-week expectation."
    customer_message: "We're tracking your Alight rollover. Funds usually arrive in 2–3 business days electronically — checks can take up to 2 weeks."
    owner: beekeeper
    source_status: verified
  completed:
    action: "Rollover complete — funds in PensionBee IRA."
    customer_message: "Your rollover is complete — your funds are in your PensionBee IRA."
    owner: system
    source_status: verified

steps:
  - text: "Go to alight.com/find-your-hr-website and click Find Your HR Website."
    owner: user
    source_status: verified
  - text: "Search for your employer name and open their benefits website."
    owner: user
    source_status: verified
  - text: "Log on with your username and password (your login page may look different)."
    owner: user
    source_status: verified
  - text: "Click Savings & Retirement."
    owner: user
    source_status: verified
  - text: "Click Withdrawals and Rollovers Out."
    owner: user
    source_status: verified
  - text: "Click here to add a Rollover account (financial institutions section)."
    owner: user
    source_status: verified
  - text: "When RolloverCentral opens in a new tab, click Get Started."
    owner: user
    source_status: verified
  - text: "Accept Terms & Conditions and click Continue."
    owner: user
    source_status: verified
  - text: "Fill Age, Account Balance, Email, set Have an existing IRA to Yes, then Get Started."
    owner: user
    source_status: verified
  - text: "Next to Add Your Rollover to an Existing IRA, click Go."
    owner: user
    source_status: verified
  - text: "Select PensionBee as your IRA provider."
    owner: user
    source_status: verified
  - text: "Click the link to pensionbee.com/us/beehive/transfer/rollover-central and log in to get your 14-digit VAN."
    owner: user
    source_status: verified
  - text: "Enter your PensionBee VAN in IRA Account Number and Confirm IRA Account Number."
    owner: user
    source_status: verified
  - text: "Select IRA Account Type, when you opened the account, and your rollover reason; click Continue."
    owner: user
    source_status: verified
  - text: "Click Continue, close RolloverCentral, and return to the Alight site."
    owner: user
    source_status: verified
  - text: "Go to Savings → Withdrawals and Rollovers Out and verify the PensionBee account number under Rollover to Institution."
    owner: user
    source_status: verified
  - text: "Confirm account details match PensionBee and proceed."
    owner: user
    source_status: verified
  - text: "Return to Savings → Withdrawals and Rollovers Out."
    owner: user
    source_status: verified
  - text: "Click Get Started next to Total Distribution or Partial Distribution."
    owner: user
    source_status: verified
  - text: "Select Roll Over an Amount to an IRA or Another Employer's Plan."
    owner: user
    source_status: verified
  - text: "Select IRA as account type and click Continue."
    owner: user
    source_status: verified
  - text: "Acknowledge the $25 processing fee and click Continue."
    owner: user
    source_status: verified
  - text: "Choose All of the Cash Available or Specific Amount, then Continue."
    owner: user
    source_status: verified
  - text: "Review Your Total Payment and click Continue."
    owner: user
    source_status: verified
  - text: "Tick the Acknowledgement box and click Continue."
    owner: user
    source_status: verified
  - text: "Under destination, select Direct Rollover (electronic transfer to UMB, 2–3 business days)."
    owner: user
    source_status: verified
  - text: "Click Continue, review Destination for Cash Rollover, and click Submit."
    owner: user
    source_status: verified
  - text: "Complete MFA — Text Me a Code or Call Me With a Code, select your phone, enter the code."
    owner: user
    source_status: verified
  - text: "Capture the confirmation screen and send it to PensionBee via BeeHive chat or info@pensionbee.com (subject: Your Name + Alight + Rollover Confirmation)."
    owner: user
    source_status: verified

edge_cases:
  - "$25 processing fee is deducted from the rollover amount."
  - "VAN (14-digit Virtual Account Number) must come from PensionBee BeeHive — route account number requests to a BeeKeeper."
  - "Electronic transfer is preferred (2–3 days); check fallback can take up to 2 weeks."

escalation_triggers:
  - id: van_account_number
    flag: account_number_request
    trigger: "Customer needs PensionBee VAN or IRA account number for RolloverCentral"
    action: "Route to BeeKeeper to provide VAN securely via BeeHive rollover-central link."
    owner: beekeeper
    source_status: verified

failure_modes: []

access_recovery:
  portal_name: "Employer benefits site via Alight"
  info_needed:
    - "Employer name"
    - "Alight / benefits portal username"
  reset_steps:
    - text: "Go to alight.com/find-your-hr-website and locate your employer's HR site."
      owner: user
      source_status: verified
    - text: "Use Forgot password on your employer's benefits login page."
      owner: user
      source_status: verified
  first_time_setup_steps:
    - text: "Register on your employer's Alight benefits portal using details from your statement or HR."
      owner: user
      source_status: verified
  lockout_fallback:
    phone: "Your employer benefits / Alight support number on your statement"
    what_to_say: "I need help accessing my retirement account to start a rollover."
    owner: user
    source_status: verified

call_script:
  phone: "The number on your 401(k) statement or employer benefits site"
  intro: "If you cannot complete the online RolloverCentral path, call and request a direct rollover to PensionBee. Use the general PensionBee payable and mailing instructions when asked."
  steps:
    - text: "Confirm identity and request a direct rollover distribution to an external IRA."
      owner: user
      source_status: verified
    - text: "Say PensionBee is the receiving provider."
      owner: user
      source_status: verified
    - text: "When asked for check payable-to and mailing address, use your PensionBee rollover instructions (see copy chips or general guide)."
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
    - label: "IRA provider"
      instruction: "PensionBee"
      source_status: verified
    - label: "IRA account number (VAN)"
      instruction: "14-digit Virtual Account Number from BeeHive rollover-central — BeeKeeper provides if needed."
      source_status: verified
    - label: "Check payable to (if paper)"
      instruction: "PensionBee FBO [your name]"
      source_status: verified
    - label: "Mailing address (if paper)"
      instruction: "PO Box 72, New York, NY 10272"
      source_status: verified
---

# Alight Rollover Guide via RolloverCentral (Internal Reference)

Source: [Scribe — Alight Rollover Guide via RolloverCentral](https://scribehow.com/viewer/Alight_Rollover_Guide_via_RolloverCentral__YM03ADJfRtuhprOG5XYdTQ)

Used for Citigroup, Target, Goldman Sachs, and other employers on Alight. Phone fallback uses the **general rollover guide** payable/mailing strings.

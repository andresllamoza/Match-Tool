---
# Typed facts the engine parses. Ops edits here; prose below is human context.
# source_status: `verified` = PensionBee's own routing rule / internal process;
# `reconstructed` = portal step wording reconstructed from flow memory,
# spot-check against the live Scribe before trusting as fact.

provider: Fidelity
aliases:
  - Fidelity Investments
  - Fidelity Workplace Services, LLC
  - NetBenefits
  - FIIOC
mechanism: two_hop_acat
check_destination: "No check (ACAT)"
forward_step_required: false
preferred_path: "401(k) → Fidelity Rollover IRA → ACAT to PensionBee (no check)"
portal: NetBenefits

sla_days: null
sla_source_status: verified
sla_note: "Typical 2–4 weeks (general guide). Two-hop ACAT; Ops to provide median days to fund."

tax_routing_note: "Pre-tax → Traditional/Rollover IRA; Roth → Roth IRA. Pre-tax→Roth = conversion = escalate."

# The single best next action per funnel stage. The engine returns exactly one.
next_actions:
  provider_identified:
    action: "Guide the user to start an Express rollover into a Fidelity Rollover IRA (Avenue 3 — no check)."
    customer_message: "Start an Express rollover in Fidelity NetBenefits — roll your 401(k) into a Fidelity Rollover IRA first. No paper check needed; we'll pull the funds over electronically."
    owner: user
    source_status: verified
  rollover_initiated:
    action: "Have the user share their Fidelity Rollover IRA account info via Beehive chat to trigger the ACAT."
    customer_message: "Share your Fidelity Rollover IRA account details with us in chat so we can start the electronic transfer into your PensionBee IRA."
    owner: user
    source_status: verified
  in_flight:
    action: "BeeKeeper monitors the ACAT leg until funds land in the PensionBee IRA."
    customer_message: "Your transfer is in progress. Electronic transfers usually complete within a few weeks — we'll notify you when your funds arrive."
    owner: beekeeper
    source_status: verified
  completed:
    action: "Rollover complete — funds in the PensionBee IRA. No further action."
    customer_message: "Your rollover is complete — your funds are in your PensionBee IRA."
    owner: system
    source_status: verified

steps:
  - text: "Log in to Fidelity NetBenefits."
    owner: user
    source_status: verified
  - text: "Locate the old 401(k) plan to roll over."
    owner: user
    source_status: verified
  - text: "Enter the rollover/withdrawal flow (under the withdrawals/loans area of the employer plan, not the retail account view)."
    owner: user
    source_status: verified
  - text: "Select 'Express rollover to Fidelity' to route funds into a Fidelity Rollover IRA."
    owner: user
    source_status: verified
  - text: "Open the Fidelity Rollover IRA if one does not exist (pre-tax → Rollover/Traditional; Roth → Roth)."
    owner: user
    source_status: verified
  - text: "Confirm the amount and complete the rollover into the Rollover IRA."
    owner: user
    source_status: verified
  - text: "Provide PensionBee the Fidelity Rollover IRA account info via Beehive chat to trigger the ACAT."
    owner: user
    source_status: verified
  - text: "PensionBee initiates the ACAT into the PensionBee IRA; BeeKeeper monitors until funds land."
    owner: beekeeper
    source_status: verified

edge_cases:
  - "Phone/check fallback puts the check with the participant; prefer Avenue 3 (ACAT) to avoid it entirely."

escalation_triggers: []

failure_modes:
  - id: avenue3_unavailable
    flag: avenue3_unavailable
    symptom: "Express rollover (Avenue 3) is unavailable or the portal blocks the IRA hop"
    routing_action: "Fall back to the phone path; check goes to the participant first, who forwards it. BeeKeeper sets expectation."
    owner: beekeeper
    source_status: verified

access_recovery:
  portal_name: NetBenefits
  info_needed:
    - "Social Security number"
    - "Date of birth"
    - "Former employer name"
  reset_steps:
    - text: "Go to NetBenefits and click 'Forgot username or password?'"
      owner: user
      source_status: reconstructed
    - text: "Verify identity with SSN and date of birth, then reset credentials."
      owner: user
      source_status: reconstructed
  first_time_setup_steps:
    - text: "Choose 'Set up online access' on the NetBenefits login page."
      owner: user
      source_status: reconstructed
    - text: "Enter employer/plan details from your most recent statement or W-2."
      owner: user
      source_status: reconstructed
  lockout_fallback:
    phone: "800-835-5099"
    what_to_say: "I need help accessing my former employer 401(k) in NetBenefits to start a rollover."
    owner: user
    source_status: verified

call_script:
  phone: "800-835-5099"
  intro: "Call Fidelity NetBenefits and say you want to roll over your old 401(k) to an IRA."
  steps:
    - text: "Confirm your identity (name, SSN, employer/plan)."
      owner: user
      source_status: verified
    - text: "Request a direct rollover distribution to an external IRA."
      owner: user
      source_status: verified
    - text: "If Avenue 3 is available, prefer Express rollover to a Fidelity Rollover IRA instead of a check."
      owner: user
      source_status: verified
  rep_questions:
    - question: "Pre-tax or Roth?"
      answer: "Pre-tax → Traditional/Rollover IRA. Roth → Roth IRA. Mixed → two separate rollovers."
      source_status: verified
    - question: "Who should the check be payable to?"
      answer: "For phone/check path: payable to you; you forward to PensionBee. Prefer online Express rollover to avoid a check."
      source_status: verified
  check_payable: "Participant name (phone/check fallback only)"
  mailing_address: "PO Box 72, New York, NY 10272"

form_guidance:
  fields:
    - label: "Distribution type"
      instruction: "Select direct rollover to another retirement account."
      source_status: verified
    - label: "Receiving institution"
      instruction: "Other / Add My Own — enter PensionBee."
      source_status: verified
    - label: "Mailing address"
      instruction: "PO Box 72, New York, NY 10272"
      source_status: verified
    - label: "Account type"
      instruction: "Pre-tax → Traditional IRA number. Roth → Roth IRA number."
      source_status: verified
---

# Fidelity Rollover Guide (Internal Reference)

**Provider:** Fidelity (NetBenefits)
**Check destination rule:** N/A — no check. Two-hop IRA-then-ACAT.
**PensionBee preferred path:** 401(k) → Fidelity Rollover IRA → ACAT to PensionBee

## Mechanism

Fidelity is a **two-hop** process, distinct from every other provider:

1. **Hop 1 — 401(k) → Fidelity Rollover IRA.** The 401(k) is rolled into a Fidelity Rollover IRA in the user's own name, still at Fidelity. Pre-tax → Rollover/Traditional IRA; Roth → Roth IRA.
2. **Hop 2 — ACAT to PensionBee.** Once the Rollover IRA is funded, the user provides their Fidelity account info and PensionBee initiates an ACAT to pull the assets into the PensionBee IRA. No check involved.

This is PensionBee's preferred path because it is easier on the customer than the standard call-to-check format.

## Three avenues (internal awareness)

- **Avenue 1 — Phone → physical check.** The common industry default.
- **Avenue 2 — Online portal → physical check.** Self-service version of Avenue 1.
- **Avenue 3 — 401(k) → Fidelity Rollover IRA → ACAT.** What PensionBee does. Preferred.

> Portal step wording reconstructed from flow memory — spot-check against the live Scribe before publishing.

## Phone path (when portal fails)

Standard call: tell Fidelity you want a rollover. They ask how to make the check payable and whether funds are pre-tax or Roth. **Check goes to the participant first** under the phone/check path — the participant then forwards it. PensionBee prefers Avenue 3 to avoid this entirely.

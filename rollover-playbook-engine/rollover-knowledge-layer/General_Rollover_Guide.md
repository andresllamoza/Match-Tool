---
# General 401(k) → PensionBee rollover guide (FIN AI training source).
# Applies to ALL recordkeepers. Provider guides add portal-specific steps on top.

destination_name: PensionBee
mailing_address: "PO Box 72, New York, NY 10272"
typical_processing_time: "2 to 4 weeks for check issuance and receipt"
account_numbers_policy: "Customer-specific. Never auto-surface — route to BeeKeeper."

employer_vs_provider_note: >
  The employer (e.g. Five Below) is not the recordkeeper. Confirm whether the
  customer means their former employer or the financial institution (Fidelity,
  Empower, Vanguard, etc.) that manages the 401(k).

general_steps:
  - text: "Log in to the old 401(k) provider's website (not the employer's HR site)."
    owner: user
    source_status: verified
  - text: "Open Withdrawals, Rollovers, or Distributions."
    owner: user
    source_status: verified
  - text: "Choose rollover to another retirement account (direct rollover)."
    owner: user
    source_status: verified
  - text: "For receiving provider, choose Other / Add My Own / Not Listed and enter PensionBee."
    owner: user
    source_status: verified
  - text: "Mailing address: PO Box 72, New York, NY 10272."
    owner: user
    source_status: verified
  - text: "Pre-tax funds → Traditional IRA account number. Roth funds → Roth IRA account number."
    owner: user
    source_status: verified
  - text: "Mixed pre-tax and Roth → two separate checks, one per account type."
    owner: user
    source_status: verified
  - text: "Submit the request and capture the confirmation screen."
    owner: user
    source_status: verified

portal_menu_aliases:
  - Withdrawals
  - Rollovers
  - Distributions
  - Transfer Out
  - Move Money
  - Take a Withdrawal

destination_dropdown_aliases:
  - Other
  - Add My Own
  - Other Provider
  - Custom Provider
  - Not Listed
  - Manual Entry

# Additional global escalations from FIN handoff rules (merged with Check_Destination_Matrix).
global_escalations:
  - id: account_number_request
    flag: account_number_request
    trigger: "Customer asks for Traditional or Roth IRA account number"
    action: "Do not auto-surface account numbers — route to a BeeKeeper to provide them securely."
    owner: beekeeper
    source_status: verified
  - id: portal_navigation_stuck
    flag: portal_navigation_stuck
    trigger: "Customer is stuck on a portal screen and needs real-time visual guidance"
    action: "Route to a BeeKeeper for a live portal walkthrough."
    owner: beekeeper
    source_status: verified
  - id: mixed_funds_split_help
    flag: mixed_funds_split_help
    trigger: "Customer has mixed pre-tax and Roth and wants help splitting amounts"
    action: "Route to a BeeKeeper — two checks required; confirm amounts per account type."
    owner: beekeeper
    source_status: verified
  - id: outbound_transfer_intent
    flag: outbound_transfer_intent
    trigger: "Customer wants to move funds OUT of PensionBee to another provider"
    action: "Outbound transfer — do not use inbound rollover steps. Route to a BeeKeeper."
    owner: beekeeper
    source_status: verified
  - id: ambiguous_rollover_intent
    flag: ambiguous_rollover_intent
    trigger: "Customer intent unclear (inbound rollover vs outbound vs find lost 401k)"
    action: "Disambiguate: (1) roll INTO PensionBee, (2) move OUT of PensionBee, or (3) find lost 401k — then route accordingly."
    owner: beekeeper
    source_status: verified

global_failure_modes:
  - id: pension_finding_intent
    flag: pension_finding_intent
    symptom: "Customer wants to find a lost 401(k), not initiate a rollover they already identified"
    routing_action: "Route to Find My 401(k) / pension-finding flow — not inbound rollover instructions."
    owner: beekeeper
    source_status: verified
  - id: provider_not_in_dropdown
    flag: provider_not_in_dropdown
    symptom: "PensionBee does not appear in the old provider's destination dropdown"
    routing_action: "Expected — guide customer to Other / Add My Own and enter PensionBee manually."
    owner: user
    source_status: verified
---

# General 401(k) Rollover to PensionBee (Internal Reference)

Source: FIN AI training doc — conversational customer guidance for any recordkeeper.
Provider-specific portal paths live in `*_Rollover_Guide.md`; this guide is the universal layer.

## Quick reference

| Field | Value |
|-------|-------|
| Destination | PensionBee |
| Mailing address | PO Box 72, New York, NY 10272 |
| Pre-tax → | Traditional IRA |
| Roth → | Roth IRA |
| Mixed funds | Two separate checks |
| Typical timeline | 2–4 weeks |

## When to hand off to a human

- Account number requests (never auto-surface)
- Stuck on a portal screen
- Mixed fund split help
- Outbound transfer intent
- Tax questions beyond basic Traditional vs Roth routing
- Frustration or confusion needing reassurance

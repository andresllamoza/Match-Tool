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
sla_source_status: reconstructed
sla_note: "Not yet quantified. Check-to-participant adds a forward leg; Ops to provide median days to fund."

tax_routing_note: "Pre-tax → Traditional/Rollover IRA; Roth → Roth IRA. Pre-tax→Roth = conversion = escalate."

next_actions:
  provider_identified:
    action: "Guide the user to start a direct rollover in the Empower portal to the PensionBee IRA, and warn now that the check mails to THEM."
    owner: user
    source_status: reconstructed
  rollover_initiated:
    action: "Confirm Empower mails the check to the user's address on file; PensionBee sends a prepaid envelope for them to forward it."
    owner: beekeeper
    source_status: verified
  in_flight:
    action: "BeeKeeper tracks the forwarded check until it is received and applied to the PensionBee IRA."
    owner: beekeeper
    source_status: verified
  completed:
    action: "Rollover complete — funds in the PensionBee IRA. No further action."
    owner: system
    source_status: verified

steps:
  - text: "Log in to the Empower participant portal."
    owner: user
    source_status: reconstructed
  - text: "Locate the old 401(k) plan to roll over."
    owner: user
    source_status: reconstructed
  - text: "Begin the rollover/distribution request and select a direct rollover."
    owner: user
    source_status: reconstructed
  - text: "Set the destination as the PensionBee IRA (direct rollover; check payable per PensionBee instructions)."
    owner: user
    source_status: reconstructed
  - text: "Complete any required forms."
    owner: user
    source_status: reconstructed
  - text: "Capture the confirmation screen. Confirm the check mails to the user's address; PensionBee sends a prepaid envelope to forward it."
    owner: user
    source_status: reconstructed
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

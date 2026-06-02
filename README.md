# DOL 5500 Recordkeeper Lookup

A simple internal tool to look up the 401(k) recordkeeper for an employer using Department of Labor Form 5500 filings.

## What it does

Type an employer name (e.g. `Microsoft`, `Walmart`, `JP Morgan Chase`). The tool returns the 401(k) recordkeeper based on the employer's latest Form 5500 Schedule C filing, with the EIN, plan participant count, and filing diagnostics for verification.

## What problem it solves

When a PensionBee user mentions an employer but doesn't know their recordkeeper, the current path is: open the DOL Form 5500 data, join three datasets on ACK_ID and ROW_ORDER, filter Schedule C records to service codes 15 (Recordkeeping) and 64 (Recordkeeping & Information Mgmt fees), canonicalize the long tail of provider name variants, and match the employer name accounting for legal-entity suffixes and spelling variants. This takes 5–10 minutes per lookup and requires data familiarity.

This tool collapses that to one text input.

## What it does NOT do

- Identify Roth vs Traditional account splits
- Confirm a user's current employment or termination status
- Confirm the user has an active or funded balance
- Provide rollover guidance (use the Rollover Knowledge Layer for that)
- Provide tax advice

It is a lookup tool, not a decision system.

## How the matching works

The tool wraps the **v4 matcher** validated against the Fortune 1000 reference set (~666/1000 high-confidence matches). The pipeline:

1. **Normalize** the employer query — uppercase, strip legal suffixes (INC, CORP, LLC, HOLDINGS, etc.), strip stopwords (THE, AND, OF), collapse whitespace.
2. **Pension-only filter** — restricts to filings where `TYPE_PENSION_BNFT_CODE` is set, excluding welfare/health plans (eliminates the Walmart-matches-grocery-plan class of error).
3. **Word-boundary regex match** against normalized sponsor names. A space-collapse fallback catches `JP MORGAN` ↔ `JPMORGAN`.
4. **Rank** matched plans by participant count (so the main 401(k) wins over a small executive plan).
5. **Look up Schedule C** providers for the top plans, filtering to service codes 15 and 64.
6. **Canonicalize** the recordkeeper names using a hand-curated regex map (so 7 Fidelity variants collapse to "Fidelity Investments").

## Current state

- Year: 2023 DOL filings (the latest year with complete coverage at validation time)
- Match rate: ~666/1000 high-confidence on the Fortune 1000 reference set
- Known limitations:
  - Plans below the 5500 filing threshold (~100 participants) won't appear
  - Recordkeepers reported only at the master trust level (not on the operating plan's Schedule C) won't be matched
  - Some employers file under a holding company name that doesn't textually match the operating company

## How it's hosted

Streamlit Community Cloud, password-gated, code in a private GitHub repo. DOL data is downloaded at first run directly from `askebsa.dol.gov` (public source) and cached locally.

## Productionizing path

If adoption is real, the natural next steps are:

1. **Bulk lookup** — paste a list of employer names, get a CSV back
2. **Multi-year fallback** — if 2023 has no filing, try 2022, 2021
3. **EIN-based exact lookup** — when EIN is known, removes all name-matching ambiguity
4. **Match-rate improvement** — investigate the ~334 non-matches systematically
5. **Migration to PensionBee infrastructure** with SSO

None of these are required for v1.

## Built by

Andres Llamoza, PensionBee US Operations

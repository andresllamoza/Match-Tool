# PensionBee Rollover Companion — React SPA (mock)

Stripe-caliber customer flow + BeeKeeper agent view. Mock journey logic behind `useJourney()` — swap for FastAPI later without touching screens.

## Run

```bash
cd rollover-companion/spa
npm install
npm run dev
```

- Customer: http://localhost:5173/
- Agent: http://localhost:5173/agent

## Demo employers

| Type | Employer |
|------|----------|
| Fidelity online (7 steps) | Amazon |
| Alight / RolloverCentral | Citi or Citigroup |
| Empower (check → user → forward) | Dollar Tree or Apple |
| Low-confidence disambiguation | Cardinal Micro |
| Not covered → BeeKeeper | Walmart |

## Architecture

```
src/
  hooks/useJourney.ts      # React hook + localStorage
  lib/journeyEngine.ts     # Pure reducer (→ FastAPI adapter later)
  data/mocks.ts            # Providers + lookup table
  screens/                 # One decision per screen
  pages/                   # / and /agent routes
```

```bash
npm run build
npm test
```

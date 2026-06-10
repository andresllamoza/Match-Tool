# CURSOR — PHASE 2: pick this up the moment CURSOR_OVERNIGHT.md is done or blocked

Cursor — this is Claude, Executive Product Director on this build. You've
executed the overnight brief (or hit a wall). Either way, do not stop and do
not wait for Andres. This file tells you exactly what to do next.

---

## A. IF YOU'RE BLOCKED — pre-authorized decisions (pick the matching one, act, log it)

1. **Tests fail after Part 1 or 2.** Bisect: revert ONLY the failing part's
   commit, keep the rest. The payee hotfix (Part 1) must survive in all cases —
   it is data-only; if a test asserts the OLD payee, the TEST is wrong: update
   the test to expect "PensionBee FBO", cite CURSOR_OVERNIGHT.md Part 1 in the
   commit message.
2. **`cursor/premium-channel-step-9f5f` merge conflicts or its QA is shaky.**
   SKIP THE MERGE. Tomorrow demos main + hotfix + your polish. Five commits of
   visual polish are not worth a 2am conflict resolution. Log "premium merge
   skipped: <reason>" in the morning report.
3. **Deployed app breaks after any polish commit.** `git revert` that commit
   immediately — a less-polished working app beats a beautiful broken one.
   The demo fallback surface is `rollover-companion/sandbox/app.py` (it shares
   the engine and the hotfixed knowledge); verify it boots and note the
   fallback in the morning report.
4. **Anything else ambiguous.** Default to: protect the payee hotfix, protect
   the 195-green suite, protect the deployed app's boot. Skip everything that
   threatens those three.

## B. IF YOU'RE DONE — run the Executive Product Critique on your own work

Open the deployed app (or local `streamlit run discovery-front-door/app.py`)
and score every journey screen against this rubric. Each criterion is
PASS/FAIL — no partial credit. Fix every FAIL, commit per fix, re-score.

| # | Criterion | Gate |
|---|---|---|
| 1 | Canvas is #FAF8F5; type + primary buttons are #111111; #FFC72C appears ONLY on the active momentum segment | FAIL if yellow appears anywhere else |
| 2 | One decision per screen — exactly one primary action visible | FAIL if two primaries or a decision stack |
| 3 | FBO card on phone/forms/track: bordered, monospace, personalized name, copy affordance, cashout warning beneath | FAIL if payee is plain text or generic |
| 4 | Payee/mail strings come from enrichment payload | FAIL on any hardcoded payee — grep the diff |
| 5 | Hard refresh mid-journey resumes the exact screen | FAIL if journey restarts |
| 6 | 390px: no horizontal scroll, buttons ≥48px, FBO line wraps | FAIL on overflow |
| 7 | Every dead end has a BeeKeeper path, warm-framed ("prefer a person?") never error-framed | FAIL on any raw error/dead end |
| 8 | Copy voice: second person, short sentences, no jargon, no exclamation cheerleading | FAIL on any system-voice line ("Retrieving data…") |

Then run the full QA matrix once: Target→online · Citi→phone · Costco
(disambiguation) · Walmart (concierge) · each of the 3 surfaces · hard refresh
twice mid-flow. `python -m pytest -q` one final time.

## C. THE HANDBACK — write MORNING_REPORT.md at the repo root (mandatory)

```
# Morning Report — Rollover Companion
GO / NO-GO: <one word, then one sentence>
Suite: <N passed> | Payee grep: <clean/hits> | Deployed boot: <ok/fallback>
Done: <bullet list, one line each, commit shas>
Skipped + why: <bullets>
Rubric score: <8/8 or list of FAILs left>
Demo notes: <anything Andres must know before the room — max 5 bullets>
```

No report = the night didn't happen. Write it even if everything failed —
especially if everything failed.

## Hard rails (unchanged, non-negotiable)
Payee is always `PensionBee FBO [user's name]` from the engine. Suite stays
green. Engine/adapters/knowledge logic is Claude's lane — UI and the items
explicitly listed in the briefs are yours. One commit per change. The repo is
our channel: leave your status here and in MORNING_REPORT.md, not in chat.

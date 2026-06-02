# Cursor / Claude Code Starter Prompts

Use these prompts when you sit down to work on the repo. Each is scoped to one specific task — that's how you stay in control of what the AI generates rather than letting it sprawl.

---

## Prompt 1: Move v4 logic from Colab into the matcher module

Use this in Cursor (Cmd+L for chat) or Claude Code after you've opened the repo and have your Colab notebook open in another tab.

> I have a Streamlit app for looking up 401(k) recordkeepers using DOL Form 5500 data. The matching logic lives in `src/matcher.py` and has two function bodies that need to be filled in:
>
> 1. `load_dol_data()` — loads and joins four DOL CSV datasets, filters to Schedule C service codes 15 and 64, and applies canonical provider name mapping. Should return a single dataframe with columns: SPONSOR_DFE_NAME, PROVIDER_OTHER_NAME, canonical_recordkeeper, PLAN_NAME, PLAN_YEAR_BEGIN_DATE, TOT_PARTCP_BOY_CNT, SPONS_DFE_EIN.
>
> 2. `match()` — takes an employer name string and a `top_n` integer, scores it against the dataframe rows, returns the top N as `MatchResult` objects (dataclass already defined).
>
> I have the working v4 logic in this Colab notebook: [paste the relevant Colab cells here]. Please port it into `src/matcher.py` filling in the PASTE ZONE sections. Preserve the matching behavior exactly — don't try to improve the algorithm, just restructure for the module.
>
> Use the existing function signatures and dataclass. Keep the module-level dataframe cache so the data only loads once per session.

---

## Prompt 2: Add bulk lookup (only AFTER the basic version is shipped and someone has asked for it)

> Extend the existing Streamlit app to support bulk lookup. Add a second tab or section to `app.py`:
>
> - User uploads a CSV with an "employer_name" column, OR pastes a list of employer names (one per line) into a textarea
> - For each name, run the existing `match()` function with top_n=1
> - Return a downloadable CSV with columns: input_name, matched_employer, recordkeeper, confidence, ein, plan_name
>
> Don't change anything about the single-lookup tab. Keep the password auth in place. Limit to 100 names per submission to avoid timeouts.

---

## Prompt 3: Improve match rate (separate later project, don't do this for v1)

> The v4 matcher hits 666/1000 high-confidence matches on the Fortune 1000 reference set. I want to investigate the 334 non-matches without changing the production app yet. Help me:
>
> 1. Create a `notebooks/match_failure_analysis.ipynb` notebook
> 2. Load the same DOL data the production matcher uses
> 3. For each unmatched Fortune 1000 employer, find the closest candidates and categorize the failure mode (legal-entity-name mismatch, holding-company structure, employer below 5500 threshold, etc.)
> 4. Output a frequency table of failure modes so I can decide which to tackle
>
> Don't modify `src/matcher.py`. This is investigation only.

---

## A note on using AI tools well for this project

The temptation will be to ask Claude Code to "build the whole thing." Resist it. The scaffold you have is structured to require you to engage with the substance — your v4 logic — explicitly. That engagement is the *learning*, and the learning is what compounds into your next three projects.

Specifically:

- After Prompt 1, read what Claude Code produced and ask "why did you structure this part this way?" for at least one decision. That five-minute conversation is the difference between "I used AI to build something" and "I have a workflow."
- Don't ask Claude Code to deploy for you. Deploy yourself the first time. The Streamlit Cloud UI is the kind of thing you should see end-to-end once so you understand what's happening.
- When you hit a bug in your v4 logic during the port, fix it manually before asking AI to help. Building the muscle of reading your own code under pressure is what makes the next tool faster.

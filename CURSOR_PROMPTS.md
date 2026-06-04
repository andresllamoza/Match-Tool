# Cursor / Claude Code starter prompts

Scoped prompts for extending this repo without letting the AI rewrite production behavior unintentionally.

---

## Prompt 1: Port Colab logic into the matcher (historical — already done)

> I have a Streamlit app for looking up 401(k) recordkeepers using DOL Form 5500 data. The matching logic lives in `src/matcher.py`. Port working Colab logic into the module, preserving matching behavior exactly — do not “improve” the algorithm during the port.

---

## Prompt 2: Bulk lookup (implemented in `app.py`)

> Extend the Streamlit app to support bulk lookup: CSV upload with an employer name column, run `match()` with top_n=1 per row, return downloadable CSV. Do not change the single-lookup flow. Limit batch size to avoid timeouts.

---

## Prompt 3: Match failure analysis (investigation only)

> Create `notebooks/match_failure_analysis.ipynb` using the same DOL pipeline as production. Categorize Fortune 1000 non-matches (legal name, holding company, below 5500 threshold, etc.). Do **not** modify `src/matcher.py`.

---

## Note on using AI tools well

- After any port, read the diff and ask why one structural choice was made.
- Deploy Streamlit yourself at least once end-to-end.
- When matcher bugs appear, try fixing manually before asking AI to rewrite core logic.

# Deployment Steps

From your laptop to a live, password-protected URL. ~60 minutes the first time.

## Phase 1: Local setup (10 min)

**1. Drop the repo into your projects folder:**

```bash
cd ~/ops-projects
# Unzip the bundle into this folder, then:
cd dol-5500-lookup
```

You should see:

```
dol-5500-lookup/
├── .gitignore
├── .streamlit/
│   ├── config.toml
│   └── secrets.toml.example
├── README.md
├── DEPLOYMENT.md            (this file)
├── app.py
├── data/.gitkeep
├── requirements.txt
└── src/
    ├── __init__.py
    └── matcher.py
```

**2. Set up a virtual env:**

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**3. Create your local secrets file:**

```bash
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
```

Open `.streamlit/secrets.toml` and replace the placeholder with a real password. This file is gitignored — it won't be committed.

## Phase 2: Test locally (5 min + first download)

```bash
streamlit run app.py
```

A browser tab opens at `http://localhost:8501`. Sign in with your password.

**First run downloads ~300MB of DOL data** from `askebsa.dol.gov` automatically. You'll see "Loading DOL data (first run only, ~30s)..." — actually closer to 1–3 minutes the first time depending on your connection. Subsequent runs use the cached files in `data/`.

Type an employer name (try `Microsoft`, `Walmart`, `JP Morgan Chase`). You should see a result card with the recordkeeper and an expandable "Match detail" section.

**If something breaks here, fix it before deploying.** It's much easier to debug locally than on Streamlit Cloud.

## Phase 3: Push to GitHub (5 min)

```bash
git init
git add .
git status   # verify: no data/ contents, no secrets.toml staged
git commit -m "Initial commit: DOL 5500 recordkeeper lookup tool"

# Create a private repo on github.com first, then:
git remote add origin git@github.com:YOUR_USERNAME/dol-5500-lookup.git
git branch -M main
git push -u origin main
```

**Before pushing, open the repo on GitHub.com after pushing and visually confirm:**
- No CSV files in `data/`
- No `.streamlit/secrets.toml`

If either is there, stop and fix the .gitignore before going further.

## Phase 4: Deploy to Streamlit Cloud (10–15 min)

**1.** Go to [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub.

**2.** Click "New app." Select your `dol-5500-lookup` repo, branch `main`, main file `app.py`. Pick a URL slug (e.g. `pensionbee-5500-lookup`).

**3.** Before clicking Deploy, click **Advanced settings → Secrets** and paste:

```toml
app_password = "your-real-password-here"
```

Use a real password, not the placeholder. This is what stops the public internet from accessing the tool.

**4.** Click Deploy. First build takes 3–5 minutes (installing Python + pandas). Then the app starts and downloads the DOL data — that first-load is slow (3–5 minutes for download + parse). Subsequent loads in the same Streamlit Cloud session are fast.

**5.** Once the app is up, test the deployed URL end-to-end.

## Phase 5: Notify and share (5 min)

Once the deployed URL works end-to-end, send your VP a one-line heads-up Slack:

> FYI — I productionized the 5500 matcher we discussed earlier as a small internal tool. It runs against public DOL Form 5500 data, hosted on Streamlit Cloud, password-gated. Anything I should think about before I share the URL internally? Happy to walk through it.

This is the senior-level move. You're not asking permission — you're giving notice and inviting concerns.

**Then send the URL to one stakeholder.** Probably the Head of Product who received your original decision memo:

> Quick follow-up to the 5500 recordkeeper memo from [DATE]. I built a simple lookup tool that uses the v4 matching logic on the 2023 DOL data. Type an employer name, see the recordkeeper. URL: [link], password: [share separately]. Curious whether this is useful in its current form, or what would make it more useful.

## Phase 6: Track adoption (ongoing)

For your July comp conversation, the question is "who used this?" Track it informally:

- Note each time someone uses the tool — who, for what
- After 4–6 weeks, count: unique users, lookups performed, estimated time saved per lookup
- One sentence by July: *Built and deployed an internal 5500 lookup tool used by [N] colleagues across [teams], collapsing manual recordkeeper research from ~10 minutes to seconds per lookup.*

## Troubleshooting

**"Loading DOL data..." takes forever on Streamlit Cloud.**
Expected on first deploy. The ~300MB download from DOL plus parsing pandas dataframes can take 3–5 minutes. After that, the data is cached in memory (`@st.cache_resource`) for the lifetime of the Streamlit process.

**"Loading DOL data..." times out on Streamlit Cloud.**
Free-tier Streamlit Cloud has memory and time limits. If you hit them, options are:
1. Commit a slimmer pre-processed parquet file instead of downloading raw CSVs
2. Upgrade to a paid tier
3. Move to a different host (Render, Railway, or PensionBee infrastructure)

**App is slow on first query after a sleep.**
Streamlit Cloud free tier sleeps the app after periods of inactivity. The first request after sleep takes ~30s, plus another 1–2 min for data reload. For a tool used several times a week, annoying but tolerable.

**"Error running matcher: NoneType has no attribute X"**
Usually means the DOL CSVs didn't extract correctly. Check `data/` locally — you should see three CSV files named like `f_5500_2023_latest.csv`. If not, delete `data/` and rerun.

**Match rate seems lower than 666/1000 for my test queries.**
The 666/1000 number is for Fortune 1000 employers, who are well-represented in 5500 data. Smaller employers may not file 5500s (the threshold is 100+ participants), so misses are expected for SMBs.

## What's NOT in this version (intentionally)

- Bulk CSV upload / batch lookup
- CSV export of results
- SSO / non-password auth
- Match-rate improvements beyond v4
- Multi-year fallback
- Roth/Traditional logic

Build only what's been requested after the tool is in use, not what you imagine will be useful.

"""
DOL 5500 Recordkeeper Lookup Streamlit app.

Run locally: streamlit run app.py
"""

import csv
from datetime import datetime, timezone
import html
import json

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

from src.lookup_log import append_lookup_attempt, read_lookup_attempts
from src.matcher import (
    DATA_DIR,
    MatchResult,
    employer_search_index,
    match,
)


SUGGESTION_LIMIT = 8
FEEDBACK_LOG_FILENAME = "provider_feedback.csv"
FEEDBACK_COLUMNS = [
    "timestamp_utc",
    "input_name",
    "matched_employer",
    "shown_recordkeeper",
    "suggested_recordkeeper",
    "notes",
]


st.set_page_config(
    page_title="5500 Recordkeeper Lookup",
    page_icon="Search",
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    :root {
        --pb-cream: #FFF8EA;
        --pb-card: #FFFCF4;
        --pb-navy: #071426;
        --pb-muted: #667085;
        --pb-gold: #FFB200;
        --pb-gold-dark: #9A6200;
        --pb-amber-soft: #FFF1D1;
        --pb-gray-soft: #F1F3F5;
        --pb-border: #E8DCC6;
        --pb-shadow: 0 24px 70px rgba(7, 20, 38, 0.10);
    }

    html, body, [class*="css"] {
        font-family: "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }

    .stApp {
        color: var(--pb-navy);
        background:
            radial-gradient(circle at top left, rgba(255, 178, 0, 0.16), transparent 28rem),
            linear-gradient(180deg, #FFF8EA 0%, #FFFDF7 58%, #FFF8EA 100%);
    }

    .block-container {
        padding-top: 3.25rem;
        padding-bottom: 3.5rem;
        max-width: 820px;
    }

    .tool-header {
        margin-bottom: 1.7rem;
    }

    .tool-kicker {
        display: inline-flex;
        align-items: center;
        gap: 0.45rem;
        margin-bottom: 0.8rem;
        padding: 0.32rem 0.68rem;
        border: 1px solid rgba(255, 178, 0, 0.38);
        border-radius: 999px;
        background: rgba(255, 178, 0, 0.12);
        color: var(--pb-gold-dark);
        font-size: 0.72rem;
        font-weight: 800;
        letter-spacing: 0.08em;
        text-transform: uppercase;
    }

    .tool-kicker-dot {
        width: 0.5rem;
        height: 0.5rem;
        border-radius: 999px;
        background: var(--pb-gold);
        box-shadow: 0 0 0 4px rgba(255, 178, 0, 0.18);
    }

    .tool-title {
        font-size: clamp(2.35rem, 5vw, 4rem);
        font-weight: 800;
        color: var(--pb-navy);
        letter-spacing: -0.055em;
        margin: 0;
        line-height: 0.98;
    }

    .tool-subtitle {
        max-width: 42rem;
        font-size: 1.02rem;
        line-height: 1.7;
        color: var(--pb-muted);
        margin-top: 1rem;
    }

    div[data-testid="stTextInput"] {
        margin-bottom: 1.15rem;
    }

    div[data-testid="stTextInput"] label {
        color: var(--pb-navy);
        font-size: 0.88rem;
        font-weight: 800;
        letter-spacing: -0.01em;
    }

    div[data-testid="stTextInput"] input {
        min-height: 4rem;
        border: 1.5px solid #E2D3B7;
        border-radius: 20px;
        background: rgba(255, 252, 244, 0.96);
        color: var(--pb-navy);
        font-size: 1.08rem;
        font-weight: 600;
        padding: 0.9rem 1.12rem;
        box-shadow: 0 16px 38px rgba(7, 20, 38, 0.07);
        transition: border-color 160ms ease, box-shadow 160ms ease, background 160ms ease;
    }

    div[data-testid="stTextInput"] input:focus {
        border-color: var(--pb-gold);
        background: #FFFFFF;
        box-shadow: 0 0 0 4px rgba(255, 178, 0, 0.16), 0 18px 44px rgba(7, 20, 38, 0.10);
    }

    .empty-state {
        margin: 1.45rem 0 1.65rem;
        padding: 1.45rem;
        border: 1px solid rgba(232, 220, 198, 0.95);
        border-radius: 28px;
        background: rgba(255, 252, 244, 0.78);
        box-shadow: var(--pb-shadow);
        text-align: center;
    }

    .empty-illustration {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 5.2rem;
        height: 5.2rem;
        margin-bottom: 0.85rem;
        border-radius: 28px;
        background: #FFF0C7;
        border: 1px solid rgba(255, 178, 0, 0.32);
    }

    .empty-title {
        margin: 0 0 0.3rem;
        color: var(--pb-navy);
        font-size: 1rem;
        font-weight: 800;
    }

    .empty-copy {
        max-width: 32rem;
        margin: 0 auto;
        color: var(--pb-muted);
        font-size: 0.92rem;
        line-height: 1.65;
    }

    .result-card {
        position: relative;
        overflow: hidden;
        background: rgba(255, 252, 244, 0.95);
        border: 1px solid var(--pb-border);
        border-radius: 28px;
        padding: 1.55rem 1.65rem;
        margin: 1.2rem 0 1rem;
        box-shadow: var(--pb-shadow);
    }

    .result-card::before {
        content: "";
        position: absolute;
        inset: 0 auto 0 0;
        width: 0.45rem;
        background: var(--pb-gold);
    }

    .result-card.medium-confidence::before {
        background: #D98C00;
    }

    .result-card.low-confidence::before,
    .result-card.no-match::before {
        background: #A7ADB5;
    }

    .result-eyebrow {
        margin: 0 0 0.55rem;
        color: var(--pb-gold-dark);
        font-size: 0.72rem;
        font-weight: 800;
        letter-spacing: 0.09em;
        text-transform: uppercase;
    }

    .result-recordkeeper {
        font-size: clamp(1.85rem, 4vw, 2.55rem);
        font-weight: 800;
        color: var(--pb-navy);
        letter-spacing: -0.04em;
        margin: 0 0 0.45rem 0;
        line-height: 1.05;
    }

    .result-source {
        display: flex;
        flex-wrap: wrap;
        gap: 0.34rem;
        align-items: center;
        margin: 0 0 0.9rem;
        color: #6B5B40;
        font-size: 0.88rem;
        font-weight: 600;
    }

    .result-employer {
        font-size: 0.98rem;
        color: var(--pb-muted);
        margin: 0 0 1rem 0;
    }

    .result-confidence {
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        font-size: 0.76rem;
        font-weight: 800;
        padding: 0.42rem 0.72rem;
        border-radius: 999px;
        letter-spacing: 0.075em;
        text-transform: uppercase;
    }

    .confidence-high {
        background: var(--pb-gold);
        color: #2A1A00;
        box-shadow: 0 8px 20px rgba(255, 178, 0, 0.25);
    }

    .confidence-medium {
        background: var(--pb-amber-soft);
        color: #8A5700;
        border: 1px solid rgba(217, 140, 0, 0.24);
    }

    .confidence-low {
        background: var(--pb-gray-soft);
        color: #56616D;
        border: 1px solid #D9DEE4;
    }

    .confidence-note {
        display: inline-block;
        margin-left: 0.55rem;
        color: #667085;
        font-size: 0.82rem;
        font-weight: 600;
    }

    .feedback-panel {
        margin: 0.8rem 0 1.2rem;
        padding: 1rem 1.1rem;
        border: 1px solid rgba(232, 220, 198, 0.95);
        border-radius: 22px;
        background: rgba(255, 252, 244, 0.86);
    }

    .feedback-title {
        margin: 0 0 0.25rem;
        color: var(--pb-navy);
        font-size: 1rem;
        font-weight: 800;
    }

    .feedback-copy {
        margin: 0 0 0.8rem;
        color: var(--pb-muted);
        font-size: 0.88rem;
        line-height: 1.55;
    }

    .stButton > button,
    .stDownloadButton > button,
    div[data-testid="stFormSubmitButton"] button {
        border: 1px solid rgba(255, 178, 0, 0.45);
        border-radius: 999px;
        background: #FFF3CD;
        color: #3A2600;
        font-weight: 800;
        min-height: 2.75rem;
        padding: 0.55rem 1rem;
        transition: transform 120ms ease, box-shadow 120ms ease, background 120ms ease;
    }

    .stButton > button:hover,
    .stDownloadButton > button:hover,
    div[data-testid="stFormSubmitButton"] button:hover {
        border-color: var(--pb-gold);
        background: #FFE6A3;
        color: #241700;
        box-shadow: 0 10px 24px rgba(255, 178, 0, 0.20);
        transform: translateY(-1px);
    }

    .near-miss {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0.78rem 0.85rem;
        border-bottom: 1px solid rgba(232, 220, 198, 0.86);
        font-size: 0.92rem;
    }

    .near-miss:last-child {
        border-bottom: none;
    }

    .near-miss-name {
        color: var(--pb-navy);
        font-weight: 800;
    }

    .near-miss-rk {
        color: var(--pb-muted);
        font-size: 0.85rem;
    }

    .suggestions-header {
        margin: 0;
        font-size: 1rem;
        font-weight: 750;
        color: var(--pb-navy);
    }

    .suggestions-caption {
        margin-top: 0.3rem;
        margin-bottom: 0.85rem;
        font-size: 0.8rem;
        color: var(--pb-muted);
    }

    .suggestions-panel {
        margin: 0.85rem 0 1.35rem 0;
        padding: 1.1rem 1.15rem 0.85rem 1.15rem;
        background: rgba(255, 252, 244, 0.92);
        border: 1px solid var(--pb-border);
        border-radius: 24px;
        box-shadow: 0 14px 34px rgba(7, 20, 38, 0.08);
    }

    .suggestions-kicker {
        color: var(--pb-gold-dark);
        font-size: 0.7rem;
        font-weight: 800;
        letter-spacing: 0.08em;
        margin-bottom: 0.2rem;
        text-transform: uppercase;
    }

    .suggestion-row {
        min-height: 4.25rem;
        margin-bottom: 0.55rem;
        padding: 0.85rem 0.95rem;
        background: #FFFCF4;
        border: 1px solid var(--pb-border);
        border-radius: 16px;
    }

    .suggestion-row:hover {
        background: #FFF7E6;
        border-color: rgba(255, 178, 0, 0.38);
    }

    .suggestion-name {
        color: var(--pb-navy);
        font-size: 0.92rem;
        font-weight: 700;
        line-height: 1.35;
    }

    .suggestion-meta {
        color: var(--pb-muted);
        font-size: 0.76rem;
        margin-top: 0.28rem;
    }

    .suggestion-note {
        color: #7B6A4B;
        font-size: 0.76rem;
        margin-top: 0.35rem;
    }

    div[data-testid="stExpander"] details {
        border: 1px solid rgba(232, 220, 198, 0.95);
        border-radius: 22px;
        background: rgba(255, 252, 244, 0.78);
        box-shadow: 0 10px 26px rgba(7, 20, 38, 0.06);
        overflow: hidden;
    }

    div[data-testid="stExpander"] summary {
        color: var(--pb-navy);
        font-weight: 800;
        padding: 0.25rem 0;
    }

    div[data-testid="stExpander"] details[open] > div {
        animation: pb-expand 180ms ease-out;
    }

    @keyframes pb-expand {
        from {
            opacity: 0;
            transform: translateY(-0.35rem);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    .footer-note {
        margin-top: 2.5rem;
        padding-top: 1.05rem;
        border-top: 1px solid rgba(232, 220, 198, 0.95);
        font-size: 0.78rem;
        color: #7D705C;
        text-align: center;
    }
</style>
""",
    unsafe_allow_html=True,
)


def check_password() -> bool:
    """Simple password gate backed by Streamlit secrets."""
    if st.session_state.get("authenticated"):
        return True

    try:
        expected_password = st.secrets.get("app_password", "")
    except Exception:
        expected_password = ""

    st.markdown(
        '<div class="tool-header"><h1 class="tool-title">5500 Recordkeeper Lookup</h1>'
        '<div class="tool-subtitle">Internal tool - sign in to continue</div></div>',
        unsafe_allow_html=True,
    )
    password = st.text_input("Password", type="password", key="password_input")
    if not expected_password:
        st.warning("Set `app_password` in Streamlit Cloud secrets to enable sign-in.")
        return False

    if password:
        if password == expected_password:
            st.session_state["authenticated"] = True
            st.rerun()
        else:
            st.error("Incorrect password.")
    return False


if not check_password():
    st.stop()


def filing_year(result: MatchResult) -> int | None:
    raw_year = result.plan_year
    if raw_year is None:
        return None
    if isinstance(raw_year, int):
        return raw_year

    year_text = str(raw_year)
    for start in range(0, max(len(year_text) - 3, 0)):
        candidate = year_text[start : start + 4]
        if candidate.isdigit():
            return int(candidate)
    return None


def confidence_tier(result: MatchResult) -> tuple[str, str, str]:
    year = filing_year(result)
    relation_tier = getattr(result, "relation_tier", None)

    if result.match_method == "fuzzy" and result.confidence < 0.90:
        return ("LOW", "confidence-low", "verify manually")
    if result.confidence < 0.75:
        return ("LOW", "confidence-low", "verify manually")
    if relation_tier == "TIER2":
        return ("MEDIUM", "confidence-medium", "contract administrator signal")
    if year is not None and year < 2023:
        return ("MEDIUM", "confidence-medium", "older filing")
    if result.confidence < 0.90:
        return ("MEDIUM", "confidence-medium", "review match detail")
    return ("HIGH", "confidence-high", "")


def result_card_class(result: MatchResult) -> str:
    tier_label, _, _ = confidence_tier(result)
    if tier_label == "HIGH":
        return "result-card"
    if tier_label == "MEDIUM":
        return "result-card medium-confidence"
    return "result-card low-confidence"


def result_source_line(result: MatchResult) -> str:
    details = ["Source: DOL Form 5500"]
    year = filing_year(result)
    if year:
        details.append(f"{year} filing")
    if result.plan_participants:
        details.append(f"Plan size: {result.plan_participants:,} participants")
    return " &middot; ".join(html.escape(detail) for detail in details)


def append_provider_feedback(
    input_name: str,
    result: MatchResult,
    suggested_recordkeeper: str,
    notes: str,
) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    feedback_path = DATA_DIR / FEEDBACK_LOG_FILENAME
    write_header = not feedback_path.exists() or feedback_path.stat().st_size == 0
    with feedback_path.open("a", newline="", encoding="utf-8") as feedback_file:
        writer = csv.DictWriter(feedback_file, fieldnames=FEEDBACK_COLUMNS)
        if write_header:
            writer.writeheader()
        writer.writerow(
            {
                "timestamp_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                "input_name": input_name,
                "matched_employer": result.matched_employer_name,
                "shown_recordkeeper": result.recordkeeper,
                "suggested_recordkeeper": suggested_recordkeeper.strip(),
                "notes": notes.strip(),
            }
        )


def show_provider_feedback_form() -> None:
    st.session_state["show_provider_feedback"] = True
    st.session_state.pop("provider_feedback_submitted", None)


def render_provider_feedback_form(lookup_employer: str, result: MatchResult) -> None:
    st.markdown(
        '<div class="feedback-panel">'
        '<div class="feedback-title">Tell us what the right provider should be</div>'
        '<div class="feedback-copy">'
        "This helps PensionBee spot plan transitions, stale filings, or legal-name mismatches."
        "</div>"
        "</div>",
        unsafe_allow_html=True,
    )
    with st.form("provider_feedback_form", clear_on_submit=True):
        suggested_recordkeeper = st.text_input(
            "Who do you think the provider is?",
            placeholder="e.g. Fidelity Investments",
            key="provider_feedback_recordkeeper",
        )
        notes = st.text_input(
            "Optional context",
            placeholder="e.g. employee portal, benefits guide, HR confirmation",
            key="provider_feedback_notes",
        )
        submitted = st.form_submit_button("Submit feedback")

    if submitted:
        if not suggested_recordkeeper.strip():
            st.warning("Add the provider you expected so we can review it.")
            return
        append_provider_feedback(lookup_employer, result, suggested_recordkeeper, notes)
        st.session_state["provider_feedback_submitted"] = True
        st.success("Thanks - feedback captured for review.")


@st.cache_data(show_spinner="Preparing employer command menu...")
def load_command_search_csv() -> str:
    index = employer_search_index().copy()
    if index.empty:
        return "employer_name,recordkeeper,plan_size\n"

    plan_size_source = index["_n"] if "_n" in index.columns else 0
    year_source = index["YEAR"] if "YEAR" in index.columns else 0
    index["_plan_size"] = pd.to_numeric(plan_size_source, errors="coerce").fillna(0)
    index["_year_sort"] = pd.to_numeric(year_source, errors="coerce").fillna(0)
    index["recordkeeper"] = index.get("RK_CANON", "").fillna("")
    index.loc[index["recordkeeper"] == "", "recordkeeper"] = index.get("RK_RAW", "").fillna("")
    index = index[index["EMPLOYER"].fillna("").astype(str).str.strip() != ""].copy()
    index = index.sort_values(["_plan_size", "_year_sort"], ascending=[False, False])
    index = index.drop_duplicates(subset=["EMPLOYER"], keep="first")
    search_rows = index.rename(
        columns={"EMPLOYER": "employer_name", "_plan_size": "plan_size"}
    )[["employer_name", "recordkeeper", "plan_size"]]
    return search_rows.to_csv(index=False)


def selected_employer_from_query_params() -> str:
    try:
        value = st.query_params.get("selected_employer", "")
    except AttributeError:
        value = st.experimental_get_query_params().get("selected_employer", [""])[0]
    if isinstance(value, list):
        value = value[0] if value else ""
    return str(value).strip()


def reset_lookup_feedback() -> None:
    st.session_state.pop("last_logged_lookup_signature", None)
    st.session_state.pop("show_provider_feedback", None)
    st.session_state.pop("provider_feedback_submitted", None)


def render_command_search(selected_employer: str) -> None:
    csv_payload = load_command_search_csv()
    component_html = f"""
<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <script src="https://cdn.jsdelivr.net/npm/fuse.js@6.6.2"></script>
  <script src="https://cdn.jsdelivr.net/npm/papaparse@5.4.1/papaparse.min.js"></script>
  <style>
    :root {{ --pb-card:#FFFCF4; --pb-navy:#071426; --pb-muted:#667085; --pb-gold:#FFB200; --pb-amber-soft:#FFF1D1; --pb-gray-soft:#F1F3F5; --pb-border:#E8DCC6; --pb-shadow:0 24px 70px rgba(7,20,38,.14); }}
    * {{ box-sizing:border-box; }}
    body {{ margin:0; background:transparent; color:var(--pb-navy); font-family:Inter,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; }}
    .command-shell {{ position:relative; padding:0 .15rem 1rem; }}
    .command-label {{ display:block; margin:0 0 .48rem .12rem; color:var(--pb-navy); font-size:.88rem; font-weight:800; letter-spacing:-.01em; }}
    .command-input-wrap {{ display:flex; align-items:center; gap:.75rem; min-height:4.1rem; padding:.75rem 1rem; border:1.5px solid #E2D3B7; border-radius:22px; background:rgba(255,252,244,.97); box-shadow:0 18px 44px rgba(7,20,38,.09); transition:border-color 160ms ease, box-shadow 160ms ease, background 160ms ease; }}
    .command-input-wrap:focus-within {{ border-color:var(--pb-gold); background:#fff; box-shadow:0 0 0 4px rgba(255,178,0,.16),0 22px 54px rgba(7,20,38,.13); }}
    .command-icon {{ flex:0 0 auto; color:#9A6200; }}
    .command-input {{ width:100%; border:0; outline:0; background:transparent; color:var(--pb-navy); font-size:1.08rem; font-weight:650; letter-spacing:-.01em; }}
    .command-input::placeholder {{ color:#9AA1AA; font-weight:560; }}
    .command-shortcut {{ flex:0 0 auto; padding:.24rem .44rem; border:1px solid rgba(232,220,198,.96); border-radius:9px; background:rgba(255,241,209,.72); color:#8A5700; font-size:.68rem; font-weight:800; letter-spacing:.04em; }}
    .command-panel {{ position:absolute; z-index:20; top:5.95rem; left:.15rem; right:.15rem; overflow:hidden; border:1px solid var(--pb-border); border-radius:24px; background:rgba(255,252,244,.98); box-shadow:var(--pb-shadow); animation:menu-in 140ms ease-out; }}
    .command-panel[hidden] {{ display:none; }}
    .command-panel-header {{ display:flex; justify-content:space-between; gap:1rem; padding:.78rem .95rem .58rem; border-bottom:1px solid rgba(232,220,198,.72); color:#7D705C; font-size:.72rem; font-weight:800; letter-spacing:.08em; text-transform:uppercase; }}
    .command-list {{ max-height:22rem; overflow-y:auto; padding:.4rem; }}
    .command-item {{ display:grid; grid-template-columns:1fr auto; gap:.85rem; width:100%; padding:.82rem .9rem; border:0; border-radius:16px; background:transparent; color:inherit; cursor:pointer; text-align:left; }}
    .command-item:hover,.command-item[data-active="true"] {{ background:#FFF3CD; box-shadow:inset 0 0 0 1px rgba(255,178,0,.35); }}
    .command-name {{ color:var(--pb-navy); font-size:.95rem; font-weight:760; line-height:1.35; }}
    .command-name strong {{ font-weight:900; color:#2A1A00; background:rgba(255,178,0,.28); border-radius:4px; padding:0 .05rem; }}
    .command-meta {{ display:block; margin-top:.22rem; color:var(--pb-muted); font-size:.78rem; font-weight:620; line-height:1.35; }}
    .command-badge {{ align-self:start; min-width:4.2rem; padding:.34rem .5rem; border-radius:999px; font-size:.66rem; font-weight:900; letter-spacing:.08em; text-align:center; }}
    .badge-high {{ background:var(--pb-gold); color:#2A1A00; box-shadow:0 8px 20px rgba(255,178,0,.23); }}
    .badge-medium {{ background:var(--pb-amber-soft); color:#8A5700; border:1px solid rgba(217,140,0,.24); }}
    .badge-low {{ background:var(--pb-gray-soft); color:#56616D; border:1px solid #D9DEE4; }}
    .command-empty {{ padding:1.25rem 1rem; color:var(--pb-muted); font-size:.92rem; font-weight:680; text-align:center; }}
    @keyframes menu-in {{ from {{ opacity:0; transform:translateY(-.35rem) scale(.99); }} to {{ opacity:1; transform:translateY(0) scale(1); }} }}
  </style>
</head>
<body>
  <div class="command-shell" id="command-root">
    <label class="command-label" for="employer-command-input">Employer name</label>
    <div class="command-input-wrap">
      <svg class="command-icon" width="22" height="22" viewBox="0 0 24 24" fill="none" aria-hidden="true"><circle cx="11" cy="11" r="7" stroke="currentColor" stroke-width="2"></circle><path d="M16.5 16.5L21 21" stroke="currentColor" stroke-width="2" stroke-linecap="round"></path></svg>
      <input id="employer-command-input" class="command-input" type="text" role="combobox" aria-autocomplete="list" aria-expanded="false" aria-controls="employer-command-results" autocomplete="off" placeholder="Search employers by filing name..." />
      <span class="command-shortcut">ESC</span>
    </div>
    <div class="command-panel" id="command-panel" hidden><div class="command-panel-header"><span>Employers</span><span>Enter to select</span></div><div class="command-list" id="employer-command-results" role="listbox"></div></div>
  </div>
  <script>
    const CSV_DATA = {json.dumps(csv_payload)};
    const INITIAL_EMPLOYER = {json.dumps(selected_employer)};
    const MAX_RESULTS = {SUGGESTION_LIMIT};
    const root = document.getElementById("command-root");
    const input = document.getElementById("employer-command-input");
    const panel = document.getElementById("command-panel");
    const list = document.getElementById("employer-command-results");
    let fuse = null;
    let activeIndex = 0;
    let currentResults = [];
    function escapeHtml(value) {{ return String(value ?? "").replaceAll("&","&amp;").replaceAll("<","&lt;").replaceAll(">","&gt;").replaceAll('"',"&quot;").replaceAll("'","&#039;"); }}
    function planSizeLabel(value) {{ const size = Number(value) || 0; return size ? new Intl.NumberFormat("en-US").format(size) + " participants" : ""; }}
    function confidenceFor(result, query) {{ const name = String(result.item.employer_name || "").toLowerCase(); const q = query.trim().toLowerCase(); if (name === q || name.startsWith(q)) return "HIGH"; if ((result.score ?? 1) <= .18) return "HIGH"; if ((result.score ?? 1) <= .32) return "MEDIUM"; return "LOW"; }}
    function badgeClass(label) {{ return label === "HIGH" ? "badge-high" : label === "MEDIUM" ? "badge-medium" : "badge-low"; }}
    function mergedRanges(indices) {{ const ranges = []; [...(indices || [])].sort((a,b)=>a[0]-b[0]).forEach(([start,end]) => {{ const last = ranges[ranges.length - 1]; if (last && start <= last[1] + 1) last[1] = Math.max(last[1], end); else ranges.push([start,end]); }}); return ranges; }}
    function highlightedName(result) {{ const text = String(result.item.employer_name || ""); const match = (result.matches || []).find((candidate) => candidate.key === "employer_name"); const ranges = mergedRanges(match?.indices || []); if (!ranges.length) return escapeHtml(text); let output = ""; let cursor = 0; ranges.forEach(([start,end]) => {{ output += escapeHtml(text.slice(cursor, start)); output += "<strong>" + escapeHtml(text.slice(start, end + 1)) + "</strong>"; cursor = end + 1; }}); output += escapeHtml(text.slice(cursor)); return output; }}
    function setPanelOpen(isOpen) {{ panel.hidden = !isOpen; input.setAttribute("aria-expanded", String(isOpen)); }}
    function selectResult(result) {{ if (!result?.item?.employer_name) return; const target = new URL(window.parent.location.href); target.searchParams.set("selected_employer", result.item.employer_name); window.parent.location.href = target.toString(); }}
    function renderResults() {{ const query = input.value.trim(); activeIndex = 0; currentResults = []; if (query.length < 2 || !fuse) {{ list.innerHTML = ""; setPanelOpen(false); return; }} currentResults = fuse.search(query).slice(0, MAX_RESULTS); setPanelOpen(true); if (!currentResults.length) {{ list.innerHTML = '<div class="command-empty">No matches — try a shorter or different name</div>'; return; }} list.innerHTML = currentResults.map((result,index) => {{ const item = result.item; const confidence = confidenceFor(result, query); const sizeLabel = planSizeLabel(item.plan_size); const metaParts = [item.recordkeeper || "Recordkeeper unavailable", sizeLabel].filter(Boolean); return `<button type="button" class="command-item" role="option" data-index="${{index}}" data-active="${{index === activeIndex}}"><span><span class="command-name">${{highlightedName(result)}}</span><span class="command-meta">${{escapeHtml(metaParts.join(" · "))}}</span></span><span class="command-badge ${{badgeClass(confidence)}}">${{confidence}}</span></button>`; }}).join(""); }}
    function updateActiveItem(nextIndex) {{ if (!currentResults.length) return; activeIndex = (nextIndex + currentResults.length) % currentResults.length; document.querySelectorAll(".command-item").forEach((item,index) => {{ item.dataset.active = String(index === activeIndex); if (index === activeIndex) item.scrollIntoView({{ block:"nearest" }}); }}); }}
    function initializeCommand() {{ if (!window.Papa || !window.Fuse) {{ window.setTimeout(initializeCommand, 40); return; }} const parsed = Papa.parse(CSV_DATA, {{ header:true, dynamicTyping:true, skipEmptyLines:true }}); const database = parsed.data.filter((row) => row.employer_name).sort((a,b) => (Number(b.plan_size) || 0) - (Number(a.plan_size) || 0)); fuse = new Fuse(database, {{ keys:[{{ name:"employer_name", weight:1.0 }}], threshold:.4, includeMatches:true, includeScore:true, minMatchCharLength:2, ignoreLocation:true, shouldSort:false }}); input.value = INITIAL_EMPLOYER || ""; input.focus(); }}
    input.addEventListener("input", renderResults);
    input.addEventListener("focus", renderResults);
    input.addEventListener("keydown", (event) => {{ if (event.key === "Escape") {{ setPanelOpen(false); input.blur(); return; }} if (event.key === "ArrowDown") {{ event.preventDefault(); updateActiveItem(activeIndex + 1); return; }} if (event.key === "ArrowUp") {{ event.preventDefault(); updateActiveItem(activeIndex - 1); return; }} if (event.key === "Enter" && currentResults.length && !panel.hidden) {{ event.preventDefault(); selectResult(currentResults[activeIndex]); }} }});
    list.addEventListener("mousedown", (event) => {{ const item = event.target.closest(".command-item"); if (!item) return; event.preventDefault(); selectResult(currentResults[Number(item.dataset.index)]); }});
    document.addEventListener("mousedown", (event) => {{ if (!root.contains(event.target)) setPanelOpen(false); }});
    root.addEventListener("focusout", () => {{ window.setTimeout(() => {{ if (!root.contains(document.activeElement)) setPanelOpen(false); }}, 80); }});
    initializeCommand();
  </script>
</body>
</html>
"""
    components.html(component_html, height=430)


st.markdown(
    '<div class="tool-header">'
    '<div class="tool-kicker"><span class="tool-kicker-dot"></span>PensionBee internal</div>'
    '<h1 class="tool-title">5500 Recordkeeper Lookup</h1>'
    '<div class="tool-subtitle">Find the 401(k) recordkeeper for an employer using DOL Form 5500 data.</div>'
    '</div>',
    unsafe_allow_html=True,
)

lookup_employer = selected_employer_from_query_params()
render_command_search(lookup_employer)

if lookup_employer:
    with st.spinner("Looking up..."):
        lookup_error = ""
        try:
            results = match(lookup_employer, top_n=4)
        except NotImplementedError:
            lookup_error = "Matcher logic not yet implemented."
            st.error(
                "Matcher logic not yet implemented. "
                "Paste your v4 Colab logic into `src/matcher.py` to enable lookups."
            )
            results = []
        except Exception as exc:
            lookup_error = str(exc)
            st.error(f"Error running matcher: {exc}")
            results = []

    lookup_signature = (
        lookup_employer,
        lookup_error,
        tuple(
            (
                result.matched_employer_name,
                result.recordkeeper,
                round(result.confidence, 4),
                result.match_method,
            )
            for result in results
        ),
    )
    if st.session_state.get("last_logged_lookup_signature") != lookup_signature:
        try:
            append_lookup_attempt(lookup_employer, results, error=lookup_error)
            st.session_state["last_logged_lookup_signature"] = lookup_signature
        except Exception as exc:
            st.warning(f"Lookup completed, but the attempt log could not be updated: {exc}")

    if not results:
        escaped_lookup = html.escape(lookup_employer)
        st.markdown(
            '<div class="result-card no-match">'
            '<div class="result-eyebrow">No provider returned</div>'
            '<div class="result-recordkeeper">No match found</div>'
            f'<div class="result-employer">No candidate matches for "{escaped_lookup}" in the 5500 dataset.</div>'
            '<div style="font-size: 0.88rem; color: #667085; margin-top: 0.5rem; line-height: 1.6;">'
            "This could mean the employer's plan is not in the latest DOL release, "
            "the employer name is spelled differently in filings, or the plan is below the 5500 filing threshold."
            "</div>"
            "</div>",
            unsafe_allow_html=True,
        )
    else:
        top = results[0]
        near_misses = results[1:]
        card_class = result_card_class(top)
        tier_label, tier_class, tier_note = confidence_tier(top)
        tier_note_html = (
            f'<span class="confidence-note">{html.escape(tier_note)}</span>'
            if tier_note
            else ""
        )
        recordkeeper = html.escape(top.recordkeeper)
        matched_employer = html.escape(top.matched_employer_name)

        st.markdown(
            f'<div class="{card_class}">'
            '<div class="result-eyebrow">Likely recordkeeper</div>'
            f'<div class="result-recordkeeper">{recordkeeper}</div>'
            f'<div class="result-source">{result_source_line(top)}</div>'
            f'<div class="result-employer">Matched employer: <strong>{matched_employer}</strong></div>'
            f'<span class="result-confidence {tier_class}">'
            f'{tier_label}'
            "</span>"
            f"{tier_note_html}"
            "</div>",
            unsafe_allow_html=True,
        )

        st.button(
            "No, this is not my provider",
            key="show_provider_feedback_button",
            on_click=show_provider_feedback_form,
            help="Open a short correction form so the team can review this provider.",
        )
        if st.session_state.get("show_provider_feedback"):
            render_provider_feedback_form(lookup_employer, top)

        with st.expander("Match detail (for verification)"):
            st.markdown("**Why this name was pulled**")
            st.write(top.match_reason or top.match_method)
            detail_cols = st.columns(2)
            with detail_cols[0]:
                st.markdown("**Plan name**")
                st.write(top.plan_name or "-")
                st.markdown("**EIN**")
                st.write(top.ein or "-")
            with detail_cols[1]:
                st.markdown("**Plan year**")
                st.write(top.plan_year or "-")
                st.markdown("**Participants**")
                st.write(f"{top.plan_participants:,}" if top.plan_participants else "-")

        if near_misses:
            st.markdown("##### Other candidates")
            near_miss_html = ""
            for candidate in near_misses:
                candidate_tier, candidate_tier_class, _ = confidence_tier(candidate)
                candidate_employer = html.escape(candidate.matched_employer_name)
                candidate_recordkeeper = html.escape(candidate.recordkeeper)
                near_miss_html += (
                    '<div class="near-miss">'
                    f'<div><div class="near-miss-name">{candidate_employer}</div>'
                    f'<div class="near-miss-rk">{candidate_recordkeeper}</div></div>'
                    f'<span class="result-confidence {candidate_tier_class}">'
                    f'{candidate_tier}'
                    "</span>"
                    "</div>"
                )
            st.markdown(near_miss_html, unsafe_allow_html=True)

else:
    st.session_state.pop("last_logged_lookup_signature", None)
    st.markdown(
        """
        <div class="empty-state">
            <div class="empty-illustration" aria-hidden="true">
                <svg width="58" height="58" viewBox="0 0 58 58" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <circle cx="25" cy="25" r="15" fill="#FFB200" fill-opacity="0.32" stroke="#071426" stroke-width="2.5"/>
                    <path d="M36 36L48 48" stroke="#071426" stroke-width="4" stroke-linecap="round"/>
                    <path d="M20 23H30M20 29H35" stroke="#071426" stroke-width="2.5" stroke-linecap="round"/>
                    <path d="M42 9L47 12V18L42 21L37 18V12L42 9Z" fill="#FFB200" fill-opacity="0.55"/>
                    <path d="M11 38L16 41V47L11 50L6 47V41L11 38Z" fill="#FFB200" fill-opacity="0.35"/>
                </svg>
            </div>
            <div class="empty-title">Start with an employer name.</div>
            <p class="empty-copy">
                This lookup covers approximately 86k US employers from DOL Form 5500 filings.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with st.expander("Master list of entered attempts"):
    attempts = read_lookup_attempts()
    if attempts.empty:
        st.info("No lookup attempts have been recorded yet.")
    else:
        visible_columns = [
            "timestamp_utc",
            "input_name",
            "matched_employer",
            "recordkeeper",
            "confidence",
            "match_method",
            "match_reason",
            "candidate_count",
            "ein",
        ]
        st.dataframe(
            attempts[visible_columns].rename(
                columns={
                    "timestamp_utc": "Timestamp (UTC)",
                    "input_name": "Entered name",
                    "matched_employer": "Pulled employer name",
                    "recordkeeper": "Recordkeeper",
                    "confidence": "Confidence",
                    "match_method": "Match method",
                    "match_reason": "Why it pulled this name",
                    "candidate_count": "Candidates",
                    "ein": "EIN",
                }
            ),
            hide_index=True,
            use_container_width=True,
        )
        st.download_button(
            "Download master attempts CSV",
            attempts.to_csv(index=False).encode("utf-8"),
            file_name="lookup_attempts_master.csv",
            mime="text/csv",
        )

st.markdown(
    '<div class="footer-note">'
    "Data covers DOL Form 5500 filings 2020-2024. "
    "Recordkeeper data may lag actual plan transitions by 12-24 months."
    "</div>",
    unsafe_allow_html=True,
)

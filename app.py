"""
DOL 5500 Recordkeeper Lookup Streamlit app.

Run locally: streamlit run app.py
"""

import csv
from datetime import datetime, timezone
import html
import time

import pandas as pd
import streamlit as st

from src.lookup_log import append_lookup_attempt, read_lookup_attempts
from src.matcher import (
    DATA_DIR,
    EmployerSuggestion,
    MatchResult,
    batch_match_top_results,
    employer_search_index,
    load_dol_data,
    match,
    suggest_employers_from_index,
)


SUGGESTION_LIMIT = 10
EMPLOYER_SEARCH_INPUT_KEY = "employer_search_input"
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

    html, body, #root, [class*="css"] {
        font-family: "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        background-color: #FFF8EA !important;
    }

    .stApp,
    .stApp[data-test-script-state="running"],
    .stApp[data-test-script-state="notRunning"] {
        color: var(--pb-navy);
        background:
            radial-gradient(circle at top left, rgba(255, 178, 0, 0.16), transparent 28rem),
            linear-gradient(180deg, #FFF8EA 0%, #FFFDF7 58%, #FFF8EA 100%) !important;
    }

    .block-container {
        padding-top: 1.75rem;
        padding-bottom: 3.5rem;
        max-width: 820px;
    }

    .tool-header,
    .hero-banner {
        margin-bottom: 1.1rem;
        padding: 1.05rem 1.15rem 0.95rem;
        border: 1px solid rgba(255, 178, 0, 0.34);
        border-radius: 28px;
        background: linear-gradient(135deg, rgba(255, 252, 244, 0.98) 0%, rgba(255, 241, 209, 0.55) 100%);
        box-shadow: var(--pb-shadow);
    }

    .tool-header {
        margin-bottom: 1.25rem;
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
        font-size: clamp(2rem, 4vw, 2.65rem);
        font-weight: 800;
        color: var(--pb-navy);
        letter-spacing: -0.055em;
        margin: 0;
        line-height: 0.98;
    }

    .tool-subtitle {
        max-width: 42rem;
        font-size: 0.94rem;
        line-height: 1.5;
        color: var(--pb-muted);
        margin-top: 0.6rem;
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
        border: 1px solid rgba(255, 178, 0, 0.38);
        border-radius: 28px;
        padding: 1.55rem 1.65rem;
        margin: 1.2rem 0 1rem;
        box-shadow: var(--pb-shadow);
    }

    .result-card::before {
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 5px;
        background: linear-gradient(90deg, #FFB200 0%, #FFD24D 55%, #FFB200 100%);
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

    div[data-testid="stForm"] {
        margin: 0 0 1.15rem;
        padding: 1.15rem 1.2rem 1.05rem;
        border: 1px solid rgba(232, 220, 198, 0.95);
        border-radius: 24px;
        background: rgba(255, 252, 244, 0.92);
        box-shadow: 0 14px 34px rgba(7, 20, 38, 0.07);
    }

    div[data-testid="stForm"] > div:first-child {
        gap: 0.65rem;
    }

    .search-panel-title {
        margin: 0 0 0.2rem;
        color: var(--pb-navy);
        font-size: 1.05rem;
        font-weight: 850;
        letter-spacing: -0.02em;
    }

    .search-panel-copy {
        margin: 0 0 0.85rem;
        color: var(--pb-muted);
        font-size: 0.88rem;
        line-height: 1.55;
    }

    .stButton > button,
    .stDownloadButton > button,
    div[data-testid="stFormSubmitButton"] > button {
        border: 1px solid rgba(255, 178, 0, 0.45);
        border-radius: 999px;
        background: #FFF3CD;
        color: #3A2600;
        font-weight: 800;
        min-height: 3rem;
        padding: 0.55rem 1.1rem;
        transition: transform 120ms ease, box-shadow 120ms ease, background 120ms ease;
    }

    .stButton > button[kind="primary"],
    div[data-testid="stFormSubmitButton"] > button[kind="primaryFormSubmit"],
    div[data-testid="stFormSubmitButton"] > button[data-testid="stBaseButton-primary"] {
        border: 1px solid #E09B00;
        background: linear-gradient(180deg, #FFD24D 0%, #FFB200 100%);
        color: #2A1A00;
        box-shadow: 0 12px 28px rgba(255, 178, 0, 0.28);
    }

    .stButton > button:hover,
    .stDownloadButton > button:hover,
    div[data-testid="stFormSubmitButton"] > button:hover {
        border-color: var(--pb-gold);
        background: #FFE6A3;
        color: #241700;
        box-shadow: 0 10px 24px rgba(255, 178, 0, 0.20);
        transform: translateY(-1px);
    }

    .stButton > button[kind="primary"]:hover,
    div[data-testid="stFormSubmitButton"] > button[kind="primaryFormSubmit"]:hover,
    div[data-testid="stFormSubmitButton"] > button[data-testid="stBaseButton-primary"]:hover {
        background: linear-gradient(180deg, #FFE08A 0%, #FFC933 100%);
        box-shadow: 0 14px 30px rgba(255, 178, 0, 0.34);
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

    .best-match-card {
        margin: 0.85rem 0 1rem;
        padding: 1rem 1.05rem;
        border: 1px solid rgba(255, 178, 0, 0.46);
        border-radius: 20px;
        background: linear-gradient(180deg, #FFF8E8 0%, #FFFCF4 100%);
        box-shadow: 0 16px 36px rgba(7, 20, 38, 0.08);
    }

    .best-match-label {
        display: inline-flex;
        margin-bottom: 0.45rem;
        padding: 0.24rem 0.52rem;
        border-radius: 999px;
        background: var(--pb-gold);
        color: #2A1A00;
        font-size: 0.66rem;
        font-weight: 900;
        letter-spacing: 0.08em;
        text-transform: uppercase;
    }

    .best-match-name {
        color: var(--pb-navy);
        font-size: 1.05rem;
        font-weight: 850;
        line-height: 1.35;
    }

    .best-match-meta {
        color: var(--pb-muted);
        font-size: 0.82rem;
        font-weight: 620;
        margin-top: 0.3rem;
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


    .batch-panel {
        margin: 1.8rem 0 1.25rem;
        padding: 1.35rem 1.45rem;
        border: 1px solid rgba(232, 220, 198, 0.95);
        border-radius: 26px;
        background: rgba(255, 252, 244, 0.86);
        box-shadow: 0 16px 36px rgba(7, 20, 38, 0.07);
    }

    .batch-title {
        margin: 0 0 0.35rem;
        color: var(--pb-navy);
        font-size: 1.18rem;
        font-weight: 850;
        letter-spacing: -0.02em;
    }

    .batch-copy {
        margin: 0;
        color: var(--pb-muted);
        font-size: 0.92rem;
        line-height: 1.6;
    }

    .batch-summary {
        margin: 1rem 0;
        padding: 1rem 1.1rem;
        border: 1px solid rgba(255, 178, 0, 0.34);
        border-radius: 22px;
        background: #FFF7E6;
        color: var(--pb-navy);
        box-shadow: 0 12px 28px rgba(7, 20, 38, 0.06);
    }

    .batch-summary-title {
        margin: 0 0 0.3rem;
        font-size: 1rem;
        font-weight: 850;
    }

    .batch-summary-meta {
        color: #6B5B40;
        font-size: 0.86rem;
        font-weight: 650;
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

    [data-testid="stToolbar"],
    [data-testid="stDecoration"],
    #MainMenu,
    footer {
        visibility: hidden;
        height: 0;
        min-height: 0;
    }

    header[data-testid="stHeader"] {
        background-color: #FFF8EA !important;
        border-bottom: none;
        visibility: hidden;
        height: 0.01rem;
        min-height: 0;
    }

    div[data-testid="stForm"] {
        margin-bottom: 0.85rem;
    }

    [data-testid="stAppViewContainer"],
    [data-testid="stMain"],
    section.main,
    [data-testid="stMainBlockContainer"],
    [data-testid="stVerticalBlock"],
    [data-testid="stHorizontalBlock"],
    [data-testid="stBottomBlockContainer"] {
        background-color: #FFF8EA !important;
    }

    [data-testid="stStatusWidget"] {
        display: none !important;
    }

    .result-card {
        animation: pb-result-in 0.38s cubic-bezier(0.22, 1, 0.36, 1);
    }

    @keyframes pb-result-in {
        from {
            opacity: 0;
            transform: translateY(10px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
</style>
""",
    unsafe_allow_html=True,
)


def is_demo_mode() -> bool:
    """Clean layout for recordings: ?demo=1 hides batch, extras, and Streamlit chrome."""
    if st.session_state.get("demo_mode"):
        return True
    try:
        demo_param = st.query_params.get("demo", "")
        if isinstance(demo_param, list):
            demo_param = demo_param[0] if demo_param else ""
        if str(demo_param).lower() in ("1", "true", "yes"):
            st.session_state["demo_mode"] = True
            return True
    except Exception:
        pass
    return False


def check_password() -> bool:
    """Simple password gate backed by Streamlit secrets."""
    if st.session_state.get("authenticated"):
        return True
    if is_demo_mode():
        st.session_state["authenticated"] = True
        return True

    try:
        expected_password = st.secrets.get("app_password", "")
    except Exception:
        expected_password = ""

    st.markdown(
        '<div class="hero-banner tool-header">'
        '<div class="tool-kicker"><span class="tool-kicker-dot"></span>PensionBee internal</div>'
        '<h1 class="tool-title">5500 Recordkeeper Lookup</h1>'
        '<div class="tool-subtitle">Internal tool — sign in to continue</div>'
        '</div>',
        unsafe_allow_html=True,
    )
    if not expected_password:
        st.warning("Set `app_password` in Streamlit Cloud secrets to enable sign-in.")
        return False

    st.markdown(
        '<p class="search-panel-copy">Enter the app password, then press <strong>Enter</strong> or <strong>Sign in</strong>.</p>',
        unsafe_allow_html=True,
    )
    with st.form("login_form", clear_on_submit=False):
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Sign in", type="primary", use_container_width=True)

    if submitted:
        if password == expected_password:
            st.session_state["authenticated"] = True
            st.rerun()
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


@st.cache_data(show_spinner="Preparing employer search index...")
def load_cached_employer_index() -> pd.DataFrame:
    return employer_search_index()


@st.cache_data(show_spinner=False)
def cached_match_results(employer_query: str, top_n: int = 4) -> tuple:
    """Cache matcher results for snappy reruns during a demo session."""
    results = match(employer_query, top_n=top_n)
    return tuple(
        (
            result.employer_query,
            result.matched_employer_name,
            result.recordkeeper,
            result.confidence,
            result.plan_name,
            result.plan_year,
            result.plan_participants,
            result.ein,
            result.plan_type_code,
            result.relation_tier,
            result.match_method,
            result.match_reason,
        )
        for result in results
    )


def hydrate_match_results(cached_rows: tuple) -> list[MatchResult]:
    return [
        MatchResult(
            employer_query=row[0],
            matched_employer_name=row[1],
            recordkeeper=row[2],
            confidence=row[3],
            plan_name=row[4],
            plan_year=row[5],
            plan_participants=row[6],
            ein=row[7],
            plan_type_code=row[8],
            relation_tier=row[9],
            match_method=row[10],
            match_reason=row[11],
        )
        for row in cached_rows
    ]


def warm_runtime_caches() -> None:
    load_dol_data()
    load_cached_employer_index()


def normalize_query_param_value(value: object) -> str:
    if isinstance(value, list):
        value = value[0] if value else ""
    return str(value or "").strip()


def selected_employer_from_query_params() -> str:
    try:
        value = st.query_params.get("selected_employer", "")
    except AttributeError:
        value = st.experimental_get_query_params().get("selected_employer", [""])[0]
    return normalize_query_param_value(value)


def reset_lookup_feedback() -> None:
    st.session_state.pop("last_logged_lookup_signature", None)
    st.session_state.pop("show_provider_feedback", None)
    st.session_state.pop("provider_feedback_submitted", None)


def clear_confirmed_lookup() -> None:
    reset_lookup_feedback()
    st.session_state.pop("confirmed_lookup", None)


def suggestion_detail(suggestion: EmployerSuggestion) -> str:
    details = [suggestion.recordkeeper]
    if suggestion.ein:
        details.append(f"EIN {suggestion.ein}")
    if suggestion.plan_participants:
        details.append(f"{suggestion.plan_participants:,} participants")
    return " | ".join(details)


def confirm_lookup(employer_name: str, *, sync_search_box: bool = True) -> None:
    """Run a lookup for this employer (Enter, Search, or Select)."""
    cleaned = str(employer_name or "").strip()
    if not cleaned:
        return
    reset_lookup_feedback()
    st.session_state["confirmed_lookup"] = cleaned
    if sync_search_box:
        st.session_state[EMPLOYER_SEARCH_INPUT_KEY] = cleaned


def seed_lookup_from_url_if_needed() -> None:
    """Apply ?selected_employer= once per session to support shared deep links."""
    if st.session_state.get("_url_employer_seeded"):
        return
    st.session_state["_url_employer_seeded"] = True
    param_employer = selected_employer_from_query_params()
    if not param_employer:
        return
    st.session_state["confirmed_lookup"] = param_employer
    st.session_state[EMPLOYER_SEARCH_INPUT_KEY] = param_employer


def select_employer_suggestion(employer_name: str) -> None:
    """Callback for filing-name Select buttons (runs before results render)."""
    confirm_lookup(employer_name, sync_search_box=True)


def render_employer_search_bar() -> str:
    """Search box; Enter or Search runs a lookup on the typed name."""
    display_query = str(
        st.session_state.get(EMPLOYER_SEARCH_INPUT_KEY)
        or st.session_state.get("confirmed_lookup")
        or ""
    ).strip()

    search_copy = "Type a company name, then <strong>Enter</strong> or <strong>Search</strong>."
    st.markdown(
        '<div class="search-panel-title">Employer lookup</div>'
        f'<p class="search-panel-copy">{search_copy}</p>',
        unsafe_allow_html=True,
    )
    with st.form("employer_lookup_form", clear_on_submit=False, border=False):
        input_col, button_col = st.columns([0.8, 0.2], vertical_alignment="bottom")
        with input_col:
            # No session-state key inside the form: keyed form widgets fight
            # submit handling and can take several Enter/Search presses to stick.
            query = st.text_input(
                "Employer name",
                value=display_query,
                placeholder="e.g. Disney, Nike, Walmart",
                label_visibility="visible",
            )
        with button_col:
            submitted = st.form_submit_button("Search", type="primary", use_container_width=True)
    if submitted:
        submitted_query = str(query or "").strip()
        if submitted_query:
            st.session_state[EMPLOYER_SEARCH_INPUT_KEY] = submitted_query
            confirm_lookup(submitted_query, sync_search_box=False)
    return str(st.session_state.get(EMPLOYER_SEARCH_INPUT_KEY, "") or "").strip()


def render_employer_suggestions(query: str, *, below_results: bool = False) -> None:
    """Filing-name suggestions — shown below the result card after Enter/Search."""
    if len(query) < 3:
        if not below_results:
            st.info("Type at least 3 letters, then press Enter to search.")
        return

    try:
        suggestions = suggest_employers_from_index(
            query,
            load_cached_employer_index(),
            limit=SUGGESTION_LIMIT,
        )
    except Exception as exc:
        st.warning(f"Suggestions could not be loaded: {exc}")
        return

    if not suggestions:
        if not below_results:
            st.info("No matches — try a shorter or different name")
        return

    if below_results:
        st.markdown(
            '<div class="suggestions-panel" style="margin-top: 1.25rem;">'
            '<div class="suggestions-kicker">Other filing names</div>'
            '<div class="suggestions-header">Pick a different DOL employer if the match above looks wrong</div>'
            '<div class="suggestions-caption">These are similar names from Form 5500 filings — selecting one re-runs the lookup.</div>'
            '</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<div class="suggestions-panel">'
            '<div class="suggestions-kicker">Employer matches</div>'
            '<div class="suggestions-header">Press Enter to search, or choose a filing name</div>'
            '<div class="suggestions-caption">Up to 10 similar employer or plan names from DOL data.</div>'
            '</div>',
            unsafe_allow_html=True,
        )

    top_suggestion = suggestions[0]
    has_best_match = top_suggestion.confidence >= 0.95
    other_suggestions = suggestions[1:] if has_best_match else suggestions

    if has_best_match and not below_results:
        name = html.escape(top_suggestion.employer_name)
        details = html.escape(suggestion_detail(top_suggestion))
        info_col, action_col = st.columns([0.78, 0.22], vertical_alignment="center")
        with info_col:
            st.markdown(
                '<div class="best-match-card">'
                '<div class="best-match-label">Best filing match</div>'
                f'<div class="best-match-name">{name}</div>'
                f'<div class="best-match-meta">{details}</div>'
                '</div>',
                unsafe_allow_html=True,
            )
        with action_col:
            st.button(
                "Select",
                key=f"best_employer_suggestion_{top_suggestion.employer_name}",
                on_click=select_employer_suggestion,
                args=(top_suggestion.employer_name,),
                use_container_width=True,
            )
    elif not below_results:
        st.warning("Press Enter to search this name, or pick a filing name below.")

    if other_suggestions:
        expander_label = "Other similar names"
        expanded = not has_best_match and not below_results
        with st.expander(expander_label, expanded=expanded):
            suggestion_slice = other_suggestions[
                : SUGGESTION_LIMIT - 1 if has_best_match and not below_results else SUGGESTION_LIMIT
            ]
            if below_results and has_best_match:
                best = top_suggestion
                name = html.escape(best.employer_name)
                details = html.escape(suggestion_detail(best))
                info_col, action_col = st.columns([0.76, 0.24], vertical_alignment="center")
                with info_col:
                    st.markdown(
                        '<div class="suggestion-row">'
                        f'<div class="suggestion-name">{name}</div>'
                        f'<div class="suggestion-meta">{details}</div>'
                        '</div>',
                        unsafe_allow_html=True,
                    )
                with action_col:
                    st.button(
                        "Select",
                        key=f"below_best_suggestion_{best.employer_name}",
                        on_click=select_employer_suggestion,
                        args=(best.employer_name,),
                        use_container_width=True,
                    )
            for index, suggestion in enumerate(suggestion_slice):
                name = html.escape(suggestion.employer_name)
                details = html.escape(suggestion_detail(suggestion))
                info_col, action_col = st.columns([0.76, 0.24], vertical_alignment="center")
                with info_col:
                    st.markdown(
                        '<div class="suggestion-row">'
                        f'<div class="suggestion-name">{name}</div>'
                        f'<div class="suggestion-meta">{details}</div>'
                        '</div>',
                        unsafe_allow_html=True,
                    )
                with action_col:
                    st.button(
                        "Select",
                        key=f"employer_suggestion_{index}_{suggestion.employer_name}",
                        on_click=select_employer_suggestion,
                        args=(suggestion.employer_name,),
                        use_container_width=True,
                    )


def render_lookup_results(lookup_employer: str) -> None:
    lookup_error = ""
    try:
        results = hydrate_match_results(cached_match_results(lookup_employer, top_n=4))
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
        return

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

    if not is_demo_mode():
        st.button(
            "No, this is not my provider",
            key="show_provider_feedback_button",
            on_click=show_provider_feedback_form,
            help="Open a short correction form so the team can review this provider.",
        )
        if st.session_state.get("show_provider_feedback"):
            render_provider_feedback_form(lookup_employer, top)

    if is_demo_mode():
        return

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
        st.markdown("##### Other recordkeeper candidates")
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


from src.batch_columns import detect_employer_column

BATCH_CHUNK_SIZE = 100
BATCH_MAX_ROWS = 2500


def batch_result_row(input_name: str, top: MatchResult | None) -> dict[str, object]:
    cleaned_name = str(input_name or "").strip()
    if not cleaned_name:
        return {
            "Input name": "",
            "Matched employer": "",
            "Recordkeeper": "No match found",
            "Confidence": "none",
            "Plan participants": "",
            "Data year": "",
        }

    if top is None:
        return {
            "Input name": cleaned_name,
            "Matched employer": "",
            "Recordkeeper": "No match found",
            "Confidence": "none",
            "Plan participants": "",
            "Data year": "",
        }

    confidence_label, _, _ = confidence_tier(top)
    return {
        "Input name": cleaned_name,
        "Matched employer": top.matched_employer_name,
        "Recordkeeper": top.recordkeeper or "No match found",
        "Confidence": confidence_label,
        "Plan participants": top.plan_participants or "",
        "Data year": filing_year(top) or "",
    }


def confidence_dot_label(value: object) -> str:
    value_text = str(value or "none").upper()
    if value_text == "HIGH":
        return "● HIGH"
    if value_text == "MEDIUM":
        return "● MEDIUM"
    if value_text == "LOW":
        return "● LOW"
    return "none"


def style_batch_results(results: pd.DataFrame):
    display_results = results.copy()
    display_results["Confidence"] = display_results["Confidence"].apply(confidence_dot_label)

    def style_row(row: pd.Series) -> list[str]:
        if row.get("Recordkeeper") == "No match found":
            return ["color: #8A8F9C; background-color: #F7F8FA"] * len(row)
        return [""] * len(row)

    def style_confidence(value: object) -> str:
        value_text = str(value)
        if "HIGH" in value_text:
            return "color: #9A6200; font-weight: 800"
        if "MEDIUM" in value_text:
            return "color: #B5762B; font-weight: 800"
        if "LOW" in value_text:
            return "color: #667085; font-weight: 800"
        return "color: #8A8F9C"

    styled = display_results.style.apply(style_row, axis=1)
    if hasattr(styled, "map"):
        return styled.map(style_confidence, subset=["Confidence"])
    return styled.applymap(style_confidence, subset=["Confidence"])


def render_batch_results(results: pd.DataFrame) -> None:
    total_count = len(results)
    matched_count = int((results["Recordkeeper"] != "No match found").sum())
    match_rate = (matched_count / total_count * 100) if total_count else 0.0
    confidence_counts = results["Confidence"].value_counts().to_dict()
    high_count = int(confidence_counts.get("HIGH", 0))
    medium_count = int(confidence_counts.get("MEDIUM", 0))
    low_count = int(confidence_counts.get("LOW", 0))
    no_match_count = int(confidence_counts.get("none", 0))

    st.markdown(
        '<div class="batch-summary">'
        f'<div class="batch-summary-title">Matched {matched_count:,} of {total_count:,} employers ({match_rate:.1f}%)</div>'
        f'<div class="batch-summary-meta">{high_count:,} high confidence · {medium_count:,} medium · {low_count:,} low · {no_match_count:,} no match</div>'
        '</div>',
        unsafe_allow_html=True,
    )
    try:
        st.dataframe(style_batch_results(results), hide_index=True, use_container_width=True)
    except Exception:
        display = results.copy()
        display["Confidence"] = display["Confidence"].apply(confidence_dot_label)
        st.dataframe(display, hide_index=True, use_container_width=True)
    st.download_button(
        "Download results as CSV",
        results.to_csv(index=False).encode("utf-8"),
        file_name="batch_recordkeeper_lookup_results.csv",
        mime="text/csv",
        key="download_batch_lookup_results",
    )


def render_batch_lookup() -> None:
    st.markdown(
        '<div class="batch-panel">'
        '<div class="batch-title">Batch lookup</div>'
        '<p class="batch-copy">Upload a CSV with employer names. We\'ll match each one against the DOL database.</p>'
        '</div>',
        unsafe_allow_html=True,
    )
    uploaded_file = st.file_uploader(
        "Upload employer CSV",
        type=["csv"],
        key="batch_lookup_upload",
        help="CSV only. We will auto-detect the employer-name column.",
    )
    if uploaded_file is None:
        st.session_state.pop("batch_lookup_upload_signature", None)
        st.session_state.pop("batch_lookup_results", None)
        return

    upload_signature = (uploaded_file.name, getattr(uploaded_file, "size", None))
    if st.session_state.get("batch_lookup_upload_signature") != upload_signature:
        st.session_state["batch_lookup_upload_signature"] = upload_signature
        st.session_state.pop("batch_lookup_results", None)

    try:
        uploaded = pd.read_csv(uploaded_file, dtype=str).fillna("")
    except Exception as exc:
        st.error(f"Could not read CSV: {exc}")
        return

    if uploaded.empty or len(uploaded.columns) == 0:
        st.warning("The uploaded CSV appears to be empty.")
        return

    employer_column = detect_employer_column(list(uploaded.columns))
    employer_names = uploaded[employer_column].fillna("").astype(str).tolist()
    total_count = len(employer_names)
    st.caption(f"Using `{employer_column}` as the employer-name column. {total_count:,} rows found.")
    if total_count > BATCH_MAX_ROWS:
        st.error(
            f"Batch lookup supports up to {BATCH_MAX_ROWS:,} rows. "
            f"Split the file or trim to the first {BATCH_MAX_ROWS:,} employers."
        )
        return

    if not st.button("Run batch lookup", key="run_batch_lookup", type="primary"):
        existing_results = st.session_state.get("batch_lookup_results")
        if isinstance(existing_results, pd.DataFrame) and not existing_results.empty:
            render_batch_results(existing_results)
        return

    progress = st.progress(0, text=f"Matching 0 / {total_count:,}...")
    rows: list[dict[str, object]] = []
    for start in range(0, total_count, BATCH_CHUNK_SIZE):
        chunk_names = employer_names[start : start + BATCH_CHUNK_SIZE]
        chunk_results = batch_match_top_results(chunk_names)
        rows.extend(
            batch_result_row(name, result)
            for name, result in zip(chunk_names, chunk_results, strict=True)
        )
        matched_so_far = min(start + len(chunk_names), total_count)
        progress.progress(
            matched_so_far / total_count if total_count else 1.0,
            text=f"Matching {matched_so_far:,} / {total_count:,}...",
        )
    progress.empty()

    results = pd.DataFrame(
        rows,
        columns=[
            "Input name",
            "Matched employer",
            "Recordkeeper",
            "Confidence",
            "Plan participants",
            "Data year",
        ],
    )
    st.session_state["batch_lookup_results"] = results
    render_batch_results(results)


_demo = is_demo_mode()
st.markdown(
    '<div class="hero-banner tool-header">'
    '<div class="tool-kicker"><span class="tool-kicker-dot"></span>PensionBee internal</div>'
    '<h1 class="tool-title">5500 Recordkeeper Lookup</h1>'
    '<div class="tool-subtitle">401(k) recordkeeper lookup from public DOL Form 5500 filings.</div>'
    '</div>',
    unsafe_allow_html=True,
)

seed_lookup_from_url_if_needed()

if not st.session_state.get("runtime_cache_warmed"):
    st.markdown(
        '<div class="empty-state">'
        '<div class="empty-title">Loading employer database</div>'
        '<p class="empty-copy">First sign-in may take 1–2 minutes while DOL data loads. Please wait…</p>'
        '</div>',
        unsafe_allow_html=True,
    )
    with st.spinner("Preparing employer search index…"):
        warm_runtime_caches()
    st.session_state["runtime_cache_warmed"] = True
    st.rerun()

search_query = render_employer_search_bar()
confirmed_lookup = str(st.session_state.get("confirmed_lookup", "") or "").strip()

if confirmed_lookup:
    render_lookup_results(confirmed_lookup)
    if not _demo:
        render_employer_suggestions(search_query or confirmed_lookup, below_results=True)
else:
    st.session_state.pop("last_logged_lookup_signature", None)
    if len(search_query) >= 3 and not _demo:
        render_employer_suggestions(search_query, below_results=False)
    else:
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
                <div class="empty-title">Type a company name and press Enter.</div>
                <p class="empty-copy">
                    We search ~86k US employers from DOL Form 5500 filings. Enter at least 3 letters, then press Enter or Search.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

if not _demo:
    render_batch_lookup()


if not _demo:
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

if not _demo:
    st.markdown(
        '<div class="footer-note">'
        "Data covers DOL Form 5500 filings 2020-2024. "
        "Recordkeeper data may lag actual plan transitions by 12-24 months."
        "</div>",
        unsafe_allow_html=True,
    )

"""
DOL 5500 Recordkeeper Lookup Streamlit app.

Run locally: streamlit run app.py
"""

import streamlit as st

from src.lookup_log import append_lookup_attempt, read_lookup_attempts
from src.matcher import (
    EmployerSuggestion,
    employer_search_index,
    match,
    suggest_employers_from_index,
)


TYPEAHEAD_LIMIT = 8
SELECTBOX_MAX_OPTIONS = 1000


st.set_page_config(
    page_title="5500 Recordkeeper Lookup",
    page_icon="Search",
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
<style>
    .block-container {
        padding-top: 2.5rem;
        padding-bottom: 4rem;
        max-width: 760px;
    }
    .tool-header {
        border-bottom: 2px solid #C4913A;
        padding-bottom: 0.75rem;
        margin-bottom: 1.5rem;
    }
    .tool-title {
        font-size: 1.75rem;
        font-weight: 700;
        color: #0C0F1A;
        margin: 0;
        line-height: 1.2;
    }
    .tool-subtitle {
        font-size: 0.95rem;
        color: #5B6173;
        margin-top: 0.25rem;
    }
    .result-card {
        background: #FFFFFF;
        border: 1px solid #E5E2DA;
        border-left: 4px solid #0E8F78;
        border-radius: 6px;
        padding: 1.25rem 1.5rem;
        margin-bottom: 1rem;
    }
    .result-card.low-confidence {
        border-left-color: #C4913A;
    }
    .result-card.no-match {
        border-left-color: #B53A2F;
    }
    .result-recordkeeper {
        font-size: 1.4rem;
        font-weight: 700;
        color: #0C0F1A;
        margin: 0 0 0.25rem 0;
    }
    .result-employer {
        font-size: 0.95rem;
        color: #5B6173;
        margin: 0 0 0.75rem 0;
    }
    .result-confidence {
        display: inline-block;
        font-size: 0.8rem;
        font-weight: 600;
        padding: 0.2rem 0.6rem;
        border-radius: 12px;
        letter-spacing: 0.02em;
    }
    .confidence-high {
        background: #E6F3F0;
        color: #0E8F78;
    }
    .confidence-medium {
        background: #FBF1E0;
        color: #B5762B;
    }
    .confidence-low {
        background: #FCE6E3;
        color: #B53A2F;
    }
    .near-miss {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0.6rem 0.75rem;
        border-bottom: 1px solid #F2EDE4;
        font-size: 0.92rem;
    }
    .near-miss:last-child {
        border-bottom: none;
    }
    .near-miss-name {
        color: #0C0F1A;
    }
    .near-miss-rk {
        color: #5B6173;
        font-size: 0.85rem;
    }
    .suggestions-header {
        margin-top: 0.6rem;
        margin-bottom: 0.25rem;
        font-size: 0.86rem;
        font-weight: 700;
        color: #0C0F1A;
    }
    .suggestions-caption {
        margin-bottom: 0.4rem;
        font-size: 0.8rem;
        color: #5B6173;
    }
    .footer-note {
        margin-top: 3rem;
        padding-top: 1rem;
        border-top: 1px solid #E5E2DA;
        font-size: 0.78rem;
        color: #8A8F9C;
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


def confidence_class(label: str) -> str:
    return {
        "High": "confidence-high",
        "Medium": "confidence-medium",
        "Low": "confidence-low",
    }.get(label, "confidence-low")


@st.cache_data(show_spinner="Loading employer search index...")
def load_cached_employer_index():
    return employer_search_index()


def reset_selected_employer() -> None:
    st.session_state.pop("selected_employer_name", None)
    st.session_state.pop("last_logged_lookup_signature", None)


def select_employer_suggestion(employer_name: str) -> None:
    st.session_state["employer_input"] = employer_name
    st.session_state["selected_employer_name"] = employer_name
    st.session_state.pop("last_logged_lookup_signature", None)


def suggestion_detail(suggestion: EmployerSuggestion) -> str:
    details = [suggestion.recordkeeper]
    if suggestion.ein:
        details.append(f"EIN {suggestion.ein}")
    if suggestion.plan_participants:
        details.append(f"{suggestion.plan_participants:,} participants")
    return " | ".join(details)


def render_employer_suggestions(
    suggestions: list[EmployerSuggestion],
) -> None:
    if not suggestions:
        st.info("No matching employer found.")
        return

    st.markdown(
        '<div class="suggestions-header">Suggestions in our 5500 data</div>'
        '<div class="suggestions-caption">Pick one to search the exact employer name we have on file.</div>',
        unsafe_allow_html=True,
    )
    for index, suggestion in enumerate(suggestions):
        label = f"{suggestion.employer_name} - {suggestion_detail(suggestion)}"
        st.button(
            label,
            key=f"employer_suggestion_{index}_{suggestion.employer_name}",
            on_click=select_employer_suggestion,
            args=(suggestion.employer_name,),
            use_container_width=True,
        )


st.markdown(
    '<div class="tool-header">'
    '<h1 class="tool-title">5500 Recordkeeper Lookup</h1>'
    '<div class="tool-subtitle">Find the 401(k) recordkeeper for an employer using DOL Form 5500 data.</div>'
    '</div>',
    unsafe_allow_html=True,
)

try:
    employer_index = load_cached_employer_index()
    employer_count = len(employer_index)
except Exception as exc:
    employer_index = None
    employer_count = 0
    st.error(f"Error loading employer search index: {exc}")

selected_employer = ""

if employer_index is not None:
    if employer_count <= SELECTBOX_MAX_OPTIONS:
        employer_options = employer_index["EMPLOYER"].dropna().tolist()
        selected_employer = st.selectbox(
            "Employer name",
            options=employer_options,
            index=None,
            placeholder="Start typing an employer name...",
        ) or ""
    else:
        st.caption(
            f"Searches {employer_count:,} canonical employers. "
            "Because the list is large, this box returns the best fuzzy matches "
            "instead of loading every employer into a dropdown."
        )
        employer_query = st.text_input(
            "Employer name",
            placeholder="Start typing an employer name...",
            label_visibility="visible",
            key="employer_input",
            on_change=reset_selected_employer,
        )
        selected_employer = st.session_state.get("selected_employer_name", "")

        if employer_query.strip() and not selected_employer:
            suggestions = suggest_employers_from_index(
                employer_query,
                employer_index,
                limit=TYPEAHEAD_LIMIT,
            )
            render_employer_suggestions(suggestions)
        elif employer_query.strip() and selected_employer:
            st.caption(f"Selected employer: {selected_employer}")

if selected_employer:
    with st.spinner("Looking up..."):
        lookup_error = ""
        try:
            results = match(selected_employer, top_n=4)
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
        selected_employer.strip(),
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
            append_lookup_attempt(selected_employer, results, error=lookup_error)
            st.session_state["last_logged_lookup_signature"] = lookup_signature
        except Exception as exc:
            st.warning(f"Lookup completed, but the attempt log could not be updated: {exc}")

    if not results:
        st.markdown(
            '<div class="result-card no-match">'
            '<div class="result-recordkeeper">No match found</div>'
            f'<div class="result-employer">No candidate matches for "{selected_employer}" in the 5500 dataset.</div>'
            '<div style="font-size: 0.88rem; color: #5B6173; margin-top: 0.5rem;">'
            "This could mean the employer's plan is not in the latest DOL release, "
            "the employer name is spelled differently in filings, or the plan is below the 5500 filing threshold."
            "</div>"
            "</div>",
            unsafe_allow_html=True,
        )
    else:
        top = results[0]
        near_misses = results[1:]
        card_class = "result-card" if top.confidence >= 0.85 else "result-card low-confidence"

        st.markdown(
            f'<div class="{card_class}">'
            f'<div class="result-recordkeeper">{top.recordkeeper}</div>'
            f'<div class="result-employer">Matched to: <strong>{top.matched_employer_name}</strong></div>'
            f'<span class="result-confidence {confidence_class(top.confidence_label)}">'
            f'{top.confidence_label} confidence - {int(top.confidence * 100)}%'
            "</span>"
            "</div>",
            unsafe_allow_html=True,
        )

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
                near_miss_html += (
                    '<div class="near-miss">'
                    f'<div><div class="near-miss-name">{candidate.matched_employer_name}</div>'
                    f'<div class="near-miss-rk">{candidate.recordkeeper}</div></div>'
                    f'<span class="result-confidence {confidence_class(candidate.confidence_label)}">'
                    f'{int(candidate.confidence * 100)}%'
                    "</span>"
                    "</div>"
                )
            st.markdown(near_miss_html, unsafe_allow_html=True)
else:
    st.session_state.pop("last_logged_lookup_signature", None)

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
    "Data source: DOL Form 5500 filings (Schedule C, service codes 15 and 64). "
    "Internal use only."
    "</div>",
    unsafe_allow_html=True,
)

"""
DOL 5500 Recordkeeper Lookup Streamlit app.

Run locally: streamlit run app.py
"""

import streamlit as st

from src.matcher import match


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

    st.markdown(
        '<div class="tool-header"><h1 class="tool-title">5500 Recordkeeper Lookup</h1>'
        '<div class="tool-subtitle">Internal tool - sign in to continue</div></div>',
        unsafe_allow_html=True,
    )
    password = st.text_input("Password", type="password", key="password_input")
    if password:
        expected_password = st.secrets.get("app_password", "")
        if expected_password and password == expected_password:
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


st.markdown(
    '<div class="tool-header">'
    '<h1 class="tool-title">5500 Recordkeeper Lookup</h1>'
    '<div class="tool-subtitle">Find the 401(k) recordkeeper for an employer using DOL Form 5500 data.</div>'
    '</div>',
    unsafe_allow_html=True,
)

employer_query = st.text_input(
    "Employer name",
    placeholder="e.g. Microsoft, Walmart, Acme Corp",
    label_visibility="visible",
    key="employer_input",
)

if employer_query:
    with st.spinner("Looking up..."):
        try:
            results = match(employer_query, top_n=4)
        except NotImplementedError:
            st.error(
                "Matcher logic not yet implemented. "
                "Paste your v4 Colab logic into `src/matcher.py` to enable lookups."
            )
            results = []
        except Exception as exc:
            st.error(f"Error running matcher: {exc}")
            results = []

    if not results:
        st.markdown(
            '<div class="result-card no-match">'
            '<div class="result-recordkeeper">No match found</div>'
            f'<div class="result-employer">No candidate matches for "{employer_query}" in the 5500 dataset.</div>'
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

st.markdown(
    '<div class="footer-note">'
    "Data source: DOL Form 5500 filings (Schedule C, service codes 15 and 64). "
    "Internal use only."
    "</div>",
    unsafe_allow_html=True,
)

"""
DOL 5500 Recordkeeper Lookup — Streamlit app.

Run locally:    streamlit run app.py
Deploy:         see DEPLOYMENT.md
"""

import streamlit as st

from src.matcher import find_recordkeeper, load_data


# ---------- Page config ----------

st.set_page_config(
    page_title="5500 Recordkeeper Lookup",
    page_icon="🔍",
    layout="centered",
    initial_sidebar_state="collapsed",
)


# ---------- Brand styling ----------

st.markdown("""
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
    .result-card.no-match {
        border-left-color: #B53A2F;
    }
    .result-card.partial {
        border-left-color: #C4913A;
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
    .confidence-none {
        background: #FCE6E3;
        color: #B53A2F;
    }
    .confidence-partial {
        background: #FBF1E0;
        color: #B5762B;
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
""", unsafe_allow_html=True)


# ---------- Authentication ----------

def check_password() -> bool:
    """Simple password gate. Stores access in session state after first success."""
    if st.session_state.get("authenticated"):
        return True

    st.markdown(
        '<div class="tool-header">'
        '<h1 class="tool-title">5500 Recordkeeper Lookup</h1>'
        '<div class="tool-subtitle">Internal tool — sign in to continue</div>'
        '</div>',
        unsafe_allow_html=True,
    )
    password = st.text_input("Password", type="password", key="password_input")
    if password:
        if password == st.secrets.get("app_password", ""):
            st.session_state["authenticated"] = True
            st.rerun()
        else:
            st.error("Incorrect password.")
    return False


if not check_password():
    st.stop()


# ---------- Data warm-up (first run only) ----------

@st.cache_resource(show_spinner=False)
def _warm_data():
    """Load data once per Streamlit process. Subsequent calls are no-ops."""
    with st.spinner("Loading DOL data (first run only, ~30s)..."):
        load_data()
    return True


_warm_data()


# ---------- Header ----------

st.markdown(
    '<div class="tool-header">'
    '<h1 class="tool-title">5500 Recordkeeper Lookup</h1>'
    '<div class="tool-subtitle">Find the 401(k) recordkeeper for an employer using DOL Form 5500 data.</div>'
    '</div>',
    unsafe_allow_html=True,
)


# ---------- Input ----------

employer_query = st.text_input(
    "Employer name",
    placeholder="e.g. Microsoft, Walmart, JP Morgan Chase",
    label_visibility="visible",
    key="employer_input",
)


# ---------- Run match ----------

if employer_query:
    with st.spinner("Looking up..."):
        try:
            result = find_recordkeeper(employer_query)
        except Exception as e:
            st.error(f"Error running matcher: {e}")
            result = None

    if result is None:
        pass

    elif result["confidence"] == "High":
        st.markdown(
            f'<div class="result-card">'
            f'<div class="result-recordkeeper">{result["recordkeeper"]}</div>'
            f'<div class="result-employer">Matched to: <strong>{result["matched_employer"]}</strong></div>'
            f'<span class="result-confidence confidence-high">High confidence</span>'
            f'</div>',
            unsafe_allow_html=True,
        )

        with st.expander("Match detail (for verification)"):
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("**EIN**")
                st.write(result.get("ein") or "—")
                st.markdown("**Top plan participants**")
                participants = result.get("participants_top_plan")
                st.write(f"{participants:,}" if participants else "—")
            with c2:
                st.markdown("**Filings matched**")
                st.write(result.get("num_filings_found") or "—")
                st.markdown("**Signal**")
                st.write(result.get("signals") or "—")

            raw = result.get("recordkeeper_raw")
            canonical = result.get("recordkeeper")
            if raw and raw != canonical:
                st.markdown("**Raw provider name(s) on filing**")
                st.write(raw)

    elif result["matched_employer"] and result["confidence"] == "None":
        # Found the employer but no recordkeeper code attached
        st.markdown(
            f'<div class="result-card partial">'
            f'<div class="result-recordkeeper">Employer found, recordkeeper unclear</div>'
            f'<div class="result-employer">Matched to: <strong>{result["matched_employer"]}</strong></div>'
            f'<span class="result-confidence confidence-partial">Partial match</span>'
            f'</div>',
            unsafe_allow_html=True,
        )
        st.caption(
            f"A pension filing for this employer was found, but no service "
            f"providers were listed under codes 15 (Recordkeeping) or 64 "
            f"(Recordkeeping & Information Mgmt fees). "
            f"This can happen when the recordkeeper is reported under a "
            f"different code or under the plan's master trust filing."
        )

    else:
        st.markdown(
            f'<div class="result-card no-match">'
            f'<div class="result-recordkeeper">No match found</div>'
            f'<div class="result-employer">No pension plan filing found for "{result["query"]}".</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
        st.caption(
            "This could mean the employer's plan isn't in the latest DOL "
            "release, the employer name is spelled differently in filings, "
            "or the plan is below the 5500 filing threshold (100+ participants)."
        )


# ---------- Footer ----------

st.markdown(
    '<div class="footer-note">'
    'Data source: DOL Form 5500 filings, 2023 (Schedule C, service codes 15 & 64). '
    'Internal use only.'
    '</div>',
    unsafe_allow_html=True,
)

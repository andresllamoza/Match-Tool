"""
DOL 5500 Recordkeeper Lookup Streamlit app.

Run locally: streamlit run app.py
"""

import pandas as pd
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


BULK_LOOKUP_LIMIT = 100
BULK_NAME_COLUMNS = (
    "employer_name",
    "employer",
    "company_name",
    "company",
    "name",
)


def candidate_name_column(columns: list[str]) -> str | None:
    normalized_columns = {column.strip().lower(): column for column in columns}
    for candidate in BULK_NAME_COLUMNS:
        if candidate in normalized_columns:
            return normalized_columns[candidate]
    return columns[0] if columns else None


def clean_names(raw_names: list[object]) -> list[str]:
    return [str(name).strip() for name in raw_names if str(name).strip()]


def bulk_lookup_row(input_name: str) -> dict[str, object]:
    try:
        results = match(input_name, top_n=1)
    except NotImplementedError:
        return {
            "input_name": input_name,
            "matched_employer": "",
            "recordkeeper": "",
            "confidence": "",
            "confidence_label": "",
            "ein": "",
            "plan_name": "",
            "plan_year": "",
            "plan_participants": "",
            "status": "Matcher logic not implemented",
        }
    except Exception as exc:
        return {
            "input_name": input_name,
            "matched_employer": "",
            "recordkeeper": "",
            "confidence": "",
            "confidence_label": "",
            "ein": "",
            "plan_name": "",
            "plan_year": "",
            "plan_participants": "",
            "status": f"Error: {exc}",
        }

    if not results:
        return {
            "input_name": input_name,
            "matched_employer": "",
            "recordkeeper": "",
            "confidence": "",
            "confidence_label": "",
            "ein": "",
            "plan_name": "",
            "plan_year": "",
            "plan_participants": "",
            "status": "No match found",
        }

    top = results[0]
    return {
        "input_name": input_name,
        "matched_employer": top.matched_employer_name,
        "recordkeeper": top.recordkeeper,
        "confidence": round(top.confidence, 3),
        "confidence_label": top.confidence_label,
        "ein": top.ein or "",
        "plan_name": top.plan_name or "",
        "plan_year": top.plan_year or "",
        "plan_participants": top.plan_participants or "",
        "status": "Matched",
    }


st.markdown(
    '<div class="tool-header">'
    '<h1 class="tool-title">5500 Recordkeeper Lookup</h1>'
    '<div class="tool-subtitle">Find the 401(k) recordkeeper for an employer using DOL Form 5500 data.</div>'
    '</div>',
    unsafe_allow_html=True,
)

single_tab, bulk_tab = st.tabs(["Single lookup", "Bulk CSV lookup"])

with single_tab:
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

with bulk_tab:
    st.markdown(
        "Upload a CSV of employer names or paste one name per line. "
        "The output is a clean downloadable sheet with the input name and recordkeeper found."
    )
    uploaded_file = st.file_uploader(
        "Employer CSV",
        type=["csv"],
        help=(
            "Use a column named employer_name if possible. The app can also use "
            "employer, company_name, company, or name."
        ),
    )
    pasted_names = st.text_area(
        "Or paste employer names",
        placeholder="Walmart\nMicrosoft\nAcme Corp",
        height=120,
    )

    csv_names: list[str] = []
    if uploaded_file is not None:
        try:
            uploaded_df = pd.read_csv(uploaded_file, dtype=str, keep_default_na=False)
            if uploaded_df.empty or not uploaded_df.columns.tolist():
                st.warning("The uploaded CSV is empty.")
            else:
                columns = [str(column) for column in uploaded_df.columns]
                default_column = candidate_name_column(columns)
                default_index = columns.index(default_column) if default_column in columns else 0
                selected_column = st.selectbox(
                    "Employer name column",
                    columns,
                    index=default_index,
                )
                csv_names = clean_names(uploaded_df[selected_column].tolist())
                st.caption(f"Found {len(csv_names):,} non-empty names in the CSV.")
        except Exception as exc:
            st.error(f"Could not read CSV: {exc}")

    pasted_name_list = clean_names(pasted_names.splitlines())
    lookup_names = csv_names or pasted_name_list
    if csv_names and pasted_name_list:
        st.caption("Using the uploaded CSV. Remove it to run the pasted list instead.")

    if lookup_names:
        if len(lookup_names) > BULK_LOOKUP_LIMIT:
            st.warning(
                f"Showing the first {BULK_LOOKUP_LIMIT} names to keep the demo responsive."
            )
        lookup_names = lookup_names[:BULK_LOOKUP_LIMIT]

    run_bulk = st.button(
        "Run bulk lookup",
        disabled=not lookup_names,
        type="primary",
    )
    if run_bulk:
        with st.spinner(f"Looking up {len(lookup_names):,} employers..."):
            st.session_state["bulk_lookup_results"] = pd.DataFrame(
                [bulk_lookup_row(name) for name in lookup_names]
            )

    result_df = st.session_state.get("bulk_lookup_results")
    if result_df is not None:
        st.dataframe(result_df, use_container_width=True, hide_index=True)
        st.download_button(
            "Download clean CSV",
            data=result_df.to_csv(index=False).encode("utf-8"),
            file_name="recordkeeper_lookup_results.csv",
            mime="text/csv",
        )

st.markdown(
    '<div class="footer-note">'
    "Data source: DOL Form 5500 filings (Schedule C, service codes 15 and 64). "
    "Internal use only."
    "</div>",
    unsafe_allow_html=True,
)

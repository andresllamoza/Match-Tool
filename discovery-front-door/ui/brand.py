"""PensionBee discovery brand tokens + Streamlit chrome hiding."""

from __future__ import annotations

import streamlit as st

# Verified against pensionbee.com/us + existing Match-Tool brand tokens (app.py).
PB_CREAM = "#FBF6EC"
PB_CREAM_DEEP = "#F5EDD8"
PB_CARD = "#FFFFFF"
PB_NAVY = "#071426"
PB_BLUE = "#1A56DB"
PB_BLUE_HOVER = "#1548BD"
PB_BLUE_SOFT = "#E8F0FF"
PB_MUTED = "#5C6B7A"
PB_BORDER = "#E8DFCF"
PB_SUCCESS = "#0D7A4A"
PB_AMBER = "#9A6200"


def inject_brand_css() -> None:
    st.markdown(
        f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    :root {{
        --pb-cream: {PB_CREAM};
        --pb-card: {PB_CARD};
        --pb-navy: {PB_NAVY};
        --pb-blue: {PB_BLUE};
        --pb-muted: {PB_MUTED};
        --pb-border: {PB_BORDER};
        --pb-radius: 16px;
        --pb-shadow: 0 18px 48px rgba(7, 20, 38, 0.08);
    }}

    /* Hide default Streamlit chrome */
    #MainMenu, footer, header[data-testid="stHeader"],
    [data-testid="stToolbar"], .stDeployButton,
    [data-testid="stStatusWidget"], .viewerBadge_container {{
        visibility: hidden !important;
        display: none !important;
        height: 0 !important;
        max-height: 0 !important;
        overflow: hidden !important;
    }}

    html, body, #root, .stApp, [data-testid="stAppViewContainer"] {{
        font-family: "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        background: {PB_CREAM} !important;
        color: {PB_NAVY};
    }}

    .stApp {{
        background:
            radial-gradient(circle at 12% 0%, rgba(26, 86, 219, 0.06), transparent 42%),
            linear-gradient(180deg, {PB_CREAM} 0%, #FDF9F2 100%) !important;
    }}

    .block-container {{
        padding-top: 1.25rem;
        padding-bottom: 2.5rem;
        max-width: 28rem;
        padding-left: 1rem;
        padding-right: 1rem;
    }}

    /* Branded shell */
    .pb-shell {{
        max-width: 28rem;
        margin: 0 auto;
    }}

    .pb-logo {{
        font-size: 0.78rem;
        font-weight: 800;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        color: {PB_BLUE};
        margin-bottom: 1.5rem;
    }}

    .pb-headline {{
        font-size: clamp(1.75rem, 5vw, 2.15rem);
        font-weight: 800;
        line-height: 1.15;
        color: {PB_NAVY};
        margin: 0 0 0.5rem 0;
        letter-spacing: -0.02em;
    }}

    .pb-subcopy {{
        font-size: 1.02rem;
        line-height: 1.55;
        color: {PB_MUTED};
        margin: 0 0 1.5rem 0;
    }}

    .pb-card {{
        background: {PB_CARD};
        border: 1px solid {PB_BORDER};
        border-radius: var(--pb-radius);
        box-shadow: var(--pb-shadow);
        padding: 1.25rem 1.2rem;
        margin-bottom: 1rem;
    }}

    .pb-card-hero {{
        background: linear-gradient(145deg, #FFFFFF 0%, {PB_BLUE_SOFT} 100%);
        border: 1px solid rgba(26, 86, 219, 0.18);
    }}

    .pb-provider-name {{
        font-size: 1.35rem;
        font-weight: 800;
        color: {PB_NAVY};
        margin: 0.35rem 0 0.15rem;
        line-height: 1.25;
    }}

    .pb-confidence {{
        display: inline-flex;
        align-items: center;
        gap: 0.35rem;
        font-size: 0.78rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: {PB_SUCCESS};
        background: rgba(13, 122, 74, 0.1);
        border-radius: 999px;
        padding: 0.28rem 0.65rem;
    }}

    .pb-confidence.medium {{
        color: {PB_AMBER};
        background: rgba(154, 98, 0, 0.1);
    }}

    .pb-match-label {{
        font-size: 0.82rem;
        font-weight: 600;
        color: {PB_MUTED};
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.25rem;
    }}

    .pb-match-value {{
        font-size: 1.75rem;
        font-weight: 800;
        color: {PB_BLUE};
        line-height: 1.1;
        margin: 0;
    }}

    .pb-disclaimer {{
        font-size: 0.78rem;
        line-height: 1.45;
        color: {PB_MUTED};
        margin-top: 0.5rem;
    }}

    .pb-next-step {{
        font-size: 0.95rem;
        line-height: 1.5;
        color: {PB_NAVY};
        margin: 0;
    }}

    .pb-warm {{
        background: #FFF8EE;
        border: 1px solid #F0E2C8;
        border-radius: var(--pb-radius);
        padding: 1.1rem 1.15rem;
        color: {PB_NAVY};
        line-height: 1.55;
    }}

    .pb-error {{
        background: #FFF5F5;
        border: 1px solid #F5D0D0;
        border-radius: var(--pb-radius);
        padding: 1.1rem 1.15rem;
        color: {PB_NAVY};
    }}

    /* Streamlit inputs */
    .stTextInput input, .stSelectbox div[data-baseweb="select"] > div {{
        border-radius: 12px !important;
        border-color: {PB_BORDER} !important;
        min-height: 3rem;
        font-size: 1rem !important;
    }}

    label[data-testid="stWidgetLabel"] p {{
        font-weight: 600 !important;
        color: {PB_NAVY} !important;
        font-size: 0.92rem !important;
    }}

    /* Primary button */
    .stButton > button {{
        width: 100%;
        min-height: 3.1rem;
        border-radius: 999px !important;
        background: {PB_BLUE} !important;
        color: white !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
        border: none !important;
        box-shadow: 0 10px 24px rgba(26, 86, 219, 0.28);
    }}

    .stButton > button:hover {{
        background: {PB_BLUE_HOVER} !important;
        color: white !important;
        border: none !important;
    }}

    .stButton > button:focus {{
        box-shadow: 0 0 0 3px rgba(26, 86, 219, 0.25);
    }}

    /* Secondary link-style */
    div[data-testid="stHorizontalBlock"] .stButton > button {{
        box-shadow: none;
    }}

    .pb-secondary .stButton > button {{
        background: transparent !important;
        color: {PB_BLUE} !important;
        box-shadow: none !important;
        border: 1.5px solid rgba(26, 86, 219, 0.35) !important;
        min-height: 2.75rem !important;
    }}

    .pb-text-action .stButton > button {{
        background: transparent !important;
        color: {PB_BLUE} !important;
        box-shadow: none !important;
        border: none !important;
        min-height: 2rem !important;
        font-size: 0.92rem !important;
        font-weight: 600 !important;
        margin-top: 0.35rem;
    }}

    @media (max-width: 480px) {{
        .block-container {{
            padding-left: 0.85rem;
            padding-right: 0.85rem;
        }}
        .pb-headline {{
            font-size: 1.65rem;
        }}
    }}
</style>
        """,
        unsafe_allow_html=True,
    )

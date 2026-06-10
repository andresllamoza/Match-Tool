"""PensionBee US design tokens for Streamlit — canvas, bee yellow, charcoal CTAs."""

from __future__ import annotations

import streamlit as st

# Authentic PensionBee US palette (matches rollover-companion/web)
CANVAS = "#FAF8F5"
CANVAS_DEEP = "#F3EDE4"
CARD = "#FFFFFF"
CHARCOAL = "#111111"
INK = "#1E242B"
MUTED = "#6B6560"
BORDER = "#EAE5DC"
YELLOW = "#FFC72C"
YELLOW_SOFT = "#FFF4D6"
PERK_BG = "#FFF9E6"
INPUT_BORDER = "#D1C9BC"
SUBCOPY = "#555555"
GREEN = "#1B7F4B"
GREEN_SOFT = "#E8F5EE"
RADIUS = "16px"


def inject_brand_css() -> None:
    st.markdown(
        f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700;1,9..40,400&display=swap');

    :root {{
        --canvas: {CANVAS};
        --card: {CARD};
        --charcoal: {CHARCOAL};
        --ink: {INK};
        --muted: {MUTED};
        --border: {BORDER};
        --yellow: {YELLOW};
        --radius: {RADIUS};
    }}

    #MainMenu, footer, header[data-testid="stHeader"],
    [data-testid="stToolbar"], .stDeployButton,
    [data-testid="stStatusWidget"], .viewerBadge_container {{
        visibility: hidden !important;
        display: none !important;
        height: 0 !important;
        overflow: hidden !important;
    }}

    html, body, #root, .stApp, [data-testid="stAppViewContainer"] {{
        font-family: "DM Sans", system-ui, sans-serif !important;
        background: {CANVAS} !important;
        color: {INK} !important;
    }}

    .stApp {{
        background:
            radial-gradient(ellipse 80% 50% at 50% -10%, rgba(255, 199, 44, 0.09), transparent),
            radial-gradient(ellipse 60% 40% at 100% 100%, rgba(255, 199, 44, 0.05), transparent),
            {CANVAS} !important;
    }}

    [data-testid="stSidebar"] {{
        background: {CANVAS} !important;
        border-right: 1px solid {BORDER} !important;
    }}

    .block-container {{
        padding-top: 1.5rem;
        padding-bottom: 2.5rem;
        max-width: 28rem;
        padding-left: 1rem;
        padding-right: 1rem;
    }}

    /* ── Brand header ── */
    .pb-brand-row {{
        display: flex;
        align-items: center;
        gap: 0.65rem;
        margin-bottom: 1.5rem;
    }}
    .pb-bee-icon {{
        width: 2.5rem;
        height: 2.5rem;
        border-radius: 999px;
        background: {YELLOW};
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.15rem;
        flex-shrink: 0;
    }}
    .pb-wordmark {{
        font-size: 1.15rem;
        font-weight: 700;
        color: {CHARCOAL};
        letter-spacing: -0.02em;
    }}
    .pb-product-tag {{
        font-size: 0.8rem;
        color: {MUTED};
        margin-top: 0.1rem;
    }}

    .pb-logo {{ display: none; }}

    .pb-headline {{
        font-size: clamp(1.65rem, 5vw, 2rem);
        font-weight: 700;
        line-height: 1.2;
        color: {CHARCOAL};
        margin: 0 0 0.5rem 0;
        letter-spacing: -0.02em;
    }}

    .pb-subcopy {{
        font-size: 1rem;
        line-height: 1.55;
        color: {MUTED};
        margin: 0 0 1.25rem 0;
    }}

    .pb-card {{
        background: {CARD};
        border: 1px solid {BORDER};
        border-radius: var(--radius);
        box-shadow: 0 2px 12px rgba(17, 17, 17, 0.06);
        padding: 1.25rem 1.2rem;
        margin-bottom: 1rem;
    }}

    .pb-card-hero {{
        background: linear-gradient(145deg, #FFFFFF 0%, {YELLOW_SOFT} 100%);
        border: 1px solid rgba(255, 199, 44, 0.35);
    }}

    .pb-promo {{
        background: {YELLOW_SOFT};
        border: 1px solid rgba(255, 199, 44, 0.4);
        border-radius: var(--radius);
        padding: 1rem 1.1rem;
        margin-bottom: 1rem;
        font-size: 0.92rem;
        line-height: 1.5;
        color: {INK};
    }}
    .pb-promo strong {{ color: {CHARCOAL}; }}

    .pb-provider-name {{
        font-size: 1.25rem;
        font-weight: 700;
        color: {CHARCOAL};
        margin: 0.35rem 0 0.15rem;
    }}

    .pb-confidence {{
        display: inline-flex;
        font-size: 0.72rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: {GREEN};
        background: {GREEN_SOFT};
        border-radius: 999px;
        padding: 0.28rem 0.65rem;
        margin-bottom: 0.5rem;
    }}
    .pb-confidence.medium {{ color: #9A6200; background: #FFF4D6; }}

    .pb-match-label {{
        font-size: 0.75rem;
        font-weight: 600;
        color: {MUTED};
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.25rem;
    }}
    .pb-match-value {{ font-size: 1.65rem; font-weight: 700; color: {CHARCOAL}; margin: 0; }}
    .pb-disclaimer {{ font-size: 0.78rem; color: {MUTED}; margin-top: 0.5rem; line-height: 1.45; }}
    .pb-next-step {{ font-size: 0.95rem; line-height: 1.5; color: {INK}; margin: 0; }}

    .pb-warm {{
        background: {YELLOW_SOFT};
        border: 1px solid rgba(255, 199, 44, 0.35);
        border-radius: var(--radius);
        padding: 1rem;
        line-height: 1.55;
    }}
    .pb-error {{
        background: #FFF5F5;
        border: 1px solid #F5D0D0;
        border-radius: var(--radius);
        padding: 1rem;
    }}

    /* ── Minimal step tracker (find screen) ── */
    .pb-step-nav {{
        display: flex;
        gap: 1.5rem;
        margin: 0 0 2rem 0;
        text-align: left;
    }}
    .pb-step-item {{
        display: flex;
        flex-direction: column;
        align-items: flex-start;
    }}
    .pb-step-label {{
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        color: #9CA3AF;
    }}
    .pb-step-label.active, .pb-step-label.done {{
        color: {CHARCOAL};
    }}
    .pb-step-pill {{
        width: 1.5rem;
        height: 0.25rem;
        border-radius: 999px;
        background: {YELLOW};
        margin-top: 0.25rem;
    }}

    /* ── Premium find card ── */
    .pb-find-shell {{
        background: {CARD};
        border: 1px solid {BORDER};
        border-radius: 1rem;
        box-shadow: 0 1px 3px rgba(17, 17, 17, 0.06);
        padding: 2rem;
        margin: 2rem auto 0;
        max-width: 32rem;
        text-align: left;
    }}
    .pb-find-shell [data-testid="stForm"] {{
        margin: 0;
        padding: 0;
        border: none;
        background: transparent;
    }}
    .pb-find-card {{
        text-align: left;
    }}
    .pb-find-h1 {{
        font-size: clamp(1.875rem, 5vw, 2.25rem);
        font-weight: 700;
        letter-spacing: -0.025em;
        color: {CHARCOAL};
        margin: 0 0 0.5rem 0;
        line-height: 1.15;
    }}
    .pb-find-sub {{
        font-size: 1rem;
        line-height: 1.625;
        color: {SUBCOPY};
        margin: 0 0 1.5rem 0;
    }}
    .pb-perk-below {{
        background: {PERK_BG};
        border: 1px solid {BORDER};
        border-radius: 0.75rem;
        padding: 1.25rem;
        margin: 1rem auto 0;
        max-width: 32rem;
        text-align: left;
    }}
    .pb-perk-below .pb-perk-kicker {{
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        color: {MUTED};
        margin: 0;
    }}
    .pb-perk-below .pb-perk-body {{
        font-size: 0.875rem;
        font-weight: 600;
        line-height: 1.55;
        color: {CHARCOAL};
        margin: 0.35rem 0 0;
    }}
    .pb-find-links {{
        border-top: 1px solid {BORDER};
        margin-top: 1rem;
        padding-top: 1rem;
    }}

    /* ── Journey-specific ── */
    .pb-phase-bar {{ display: flex; gap: 4px; margin-bottom: 1.25rem; }}
    .pb-phase {{ flex: 1; text-align: center; font-size: 0.72rem; font-weight: 600; color: {MUTED}; }}
    .pb-phase.active {{ color: {CHARCOAL}; font-weight: 700; }}
    .pb-phase-dot {{ height: 4px; border-radius: 999px; background: {BORDER}; margin-bottom: 6px; }}
    .pb-phase-dot.done, .pb-phase-dot.active {{ background: {YELLOW}; }}
    .pb-card-j {{
        background: {CARD};
        border: 1px solid {BORDER};
        border-radius: var(--radius);
        padding: 1.35rem 1.25rem;
        box-shadow: 0 2px 12px rgba(17, 17, 17, 0.06);
    }}
    .pb-h1 {{ font-size: 1.65rem; font-weight: 700; color: {CHARCOAL}; line-height: 1.2; margin: 0 0 0.5rem; }}
    .pb-body {{ color: {INK}; line-height: 1.55; margin-bottom: 1rem; font-size: 1rem; }}
    .pb-badge-ok {{
        display: inline-block; background: {GREEN_SOFT}; color: {GREEN};
        font-size: 0.72rem; font-weight: 700; padding: 0.3rem 0.7rem; border-radius: 999px;
        margin-bottom: 0.75rem;
    }}
    .pb-badge-warn {{
        border: 2px solid #F59E0B; background: #FFFBEB; border-radius: 12px;
        padding: 0.75rem 1rem; font-size: 0.88rem; margin-bottom: 1rem;
    }}
    .pb-say {{
        border: 2px solid rgba(255, 199, 44, 0.45); border-radius: 12px;
        padding: 1rem; background: #fff; margin: 0.75rem 0;
    }}
    .pb-helper {{
        font-size: 0.88rem; color: {MUTED}; line-height: 1.5; margin: 0.35rem 0 1rem;
    }}

    /* ── Inputs: white cards, never dark ── */
    .stTextInput input,
    .stSelectbox div[data-baseweb="select"] > div,
    div[data-baseweb="input"] > div,
    textarea {{
        background-color: {CARD} !important;
        color: {CHARCOAL} !important;
        border: 1px solid {INPUT_BORDER} !important;
        border-radius: 0.75rem !important;
        min-height: 3.5rem !important;
        font-size: 1.125rem !important;
        box-shadow: none !important;
        transition: border-color 0.15s ease !important;
    }}
    .stTextInput input:focus {{
        border: 2px solid {CHARCOAL} !important;
        box-shadow: none !important;
        outline: none !important;
    }}

    label[data-testid="stWidgetLabel"] p {{
        font-weight: 600 !important;
        color: {CHARCOAL} !important;
        font-size: 0.9rem !important;
    }}

    /* Ensure widgets stay clickable above decorative layers */
    .stButton > button,
    .stTextInput input,
    [data-testid="stFormSubmitButton"] > button,
    .stLinkButton > a {{
        pointer-events: auto !important;
        cursor: pointer !important;
        position: relative !important;
        z-index: 2 !important;
    }}

    /* Primary CTA — charcoal (form submit + type=primary) */
    [data-testid="stFormSubmitButton"] > button,
    .stButton > button[kind="primary"],
    .stButton > button[data-testid="stBaseButton-primary"] {{
        width: 100% !important;
        min-height: 3.5rem !important;
        border-radius: 0.75rem !important;
        background: {CHARCOAL} !important;
        color: #fff !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        border: none !important;
        box-shadow: 0 2px 8px rgba(17, 17, 17, 0.15) !important;
    }}

    /* Selection blocks — secondary only (explicit kind) */
    .stButton > button[kind="secondary"],
    .stButton > button[data-testid="stBaseButton-secondary"] {{
        width: 100% !important;
        min-height: 4rem !important;
        border-radius: {RADIUS} !important;
        background: {CARD} !important;
        color: {CHARCOAL} !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        border: 2px solid {BORDER} !important;
        box-shadow: none !important;
        text-align: left !important;
        white-space: pre-wrap !important;
        line-height: 1.35 !important;
    }}

    /* Link buttons */
    .stLinkButton > a {{
        border-radius: {RADIUS} !important;
        font-weight: 600 !important;
    }}

    /* Text-link escape hatches on find screen */
    .stButton > button[kind="tertiary"],
    .stButton > button[data-testid="stBaseButton-tertiary"] {{
        width: 100% !important;
        min-height: auto !important;
        padding: 0.35rem 0 !important;
        margin: 0 !important;
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        color: {SUBCOPY} !important;
        font-size: 0.875rem !important;
        font-weight: 600 !important;
        text-align: left !important;
        white-space: normal !important;
        line-height: 1.4 !important;
    }}
    .stButton > button[kind="tertiary"]:hover,
    .stButton > button[data-testid="stBaseButton-tertiary"]:hover {{
        color: {CHARCOAL} !important;
        background: transparent !important;
    }}

    div[data-testid="stProgressBar"] > div > div {{
        background-color: {YELLOW} !important;
    }}

    @media (max-width: 480px) {{
        .block-container {{ padding-left: 0.85rem; padding-right: 0.85rem; }}
    }}
</style>
        """,
        unsafe_allow_html=True,
    )

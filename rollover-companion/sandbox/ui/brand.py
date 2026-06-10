"""PensionBee sandbox design tokens — wide 3-column layout, no absolute positioning."""

from __future__ import annotations

import streamlit as st

CANVAS = "#FAF8F5"
CARD = "#FFFFFF"
CHARCOAL = "#111111"
INK = "#1E242B"
MUTED = "#6B6560"
BORDER = "#EAE5DC"
YELLOW = "#FFC72C"
CANVAS_DEEP = "#F3EDE4"
SUBCOPY = "#555555"
GREEN = "#1B7F4B"
GREEN_SOFT = "#E8F5EE"


def inject_sandbox_css() -> None:
    st.markdown(
        f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&display=swap');

#MainMenu, footer, header[data-testid="stHeader"],
[data-testid="stToolbar"], .stDeployButton {{ visibility: hidden !important; display: none !important; height: 0 !important; }}

html, body, .stApp {{
    font-family: "DM Sans", system-ui, sans-serif !important;
    background: {CANVAS} !important;
    color: {INK} !important;
}}

.block-container {{
    padding-top: 1.25rem;
    padding-bottom: 2rem;
    max-width: 92rem !important;
    padding-left: 1.25rem;
    padding-right: 1.25rem;
}}

.sandbox-surface-label {{
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: {MUTED};
    margin: 0 0 0.75rem 0;
}}

.sandbox-col-card {{
    background: {CARD};
    border: 1px solid {BORDER};
    border-radius: 1rem;
    padding: 1.25rem 1.15rem;
    margin-bottom: 0.5rem;
    box-shadow: 0 1px 4px rgba(17,17,17,0.05);
}}

.sandbox-embed-minimal .stApp {{ background: #fff !important; }}
.sandbox-embed-dark .stApp {{ background: #1a1a1a !important; color: #f5f5f5 !important; }}

.pb-welcome-banner {{
    background: {CARD};
    border: 1px solid {BORDER};
    border-radius: 1rem;
    padding: 1rem 1.25rem;
    margin-bottom: 1rem;
    animation: pb-slide-in 0.45s ease-out;
}}
@keyframes pb-slide-in {{
    from {{ opacity: 0; transform: translateY(12px); }}
    to {{ opacity: 1; transform: translateY(0); }}
}}
.pb-welcome-kicker {{ font-size: 0.72rem; font-weight: 700; text-transform: uppercase; color: #9A6200; margin: 0; }}
.pb-welcome-body {{ margin: 0.35rem 0 0; font-size: 1rem; line-height: 1.5; }}

.pb-phase-bar {{ display: flex; gap: 4px; margin-bottom: 1rem; }}
.pb-phase {{ flex: 1; text-align: center; font-size: 0.68rem; font-weight: 600; color: {MUTED}; }}
.pb-phase.active {{ color: {CHARCOAL}; font-weight: 700; }}
.pb-phase-dot {{ height: 4px; border-radius: 999px; background: {BORDER}; margin-bottom: 4px; }}
.pb-phase-dot.done, .pb-phase-dot.active {{ background: {YELLOW}; }}

.pb-headline {{ font-size: 1.35rem; font-weight: 700; color: {CHARCOAL}; line-height: 1.2; margin: 0 0 0.5rem; }}
.pb-body {{ color: {SUBCOPY}; line-height: 1.55; margin: 0 0 1rem; font-size: 0.95rem; }}

.pb-channel-header {{ margin: 0 0 1.25rem 0; }}
.pb-channel-step-id {{ font-size: 1.05rem; font-weight: 500; color: #6B7280; margin: 0 0 0.5rem; }}
.pb-channel-track {{ height: 0.45rem; border-radius: 999px; background: {CANVAS_DEEP}; overflow: hidden; }}
.pb-channel-track-fill {{ height: 100%; background: {YELLOW}; border-radius: 999px; }}

.pb-call-script {{
    border: 1px solid {BORDER}; border-left: 4px solid {YELLOW};
    border-radius: 1rem; background: {CARD}; padding: 1.25rem 1.35rem; margin: 0.75rem 0;
}}
.pb-call-intro {{ font-size: 0.85rem; color: {SUBCOPY}; margin: 0 0 0.5rem; }}
.pb-channel-kicker {{ font-size: 0.68rem; font-weight: 700; text-transform: uppercase; color: {MUTED}; margin: 0; }}
.pb-channel-action {{ font-size: 1rem; font-weight: 600; color: {CHARCOAL}; margin: 0.25rem 0 0; }}

.pb-phone-cta {{
    display: flex; align-items: center; justify-content: space-between;
    background: {CHARCOAL}; color: #fff; border-radius: 0.85rem;
    padding: 1rem 1.15rem; text-decoration: none; margin: 0.5rem 0 0.75rem;
}}
.pb-phone-kicker {{ font-size: 0.68rem; font-weight: 600; text-transform: uppercase; opacity: 0.85; }}
.pb-phone-num {{ font-size: 1.1rem; font-weight: 700; }}

.pb-fbo-header {{ display: flex; gap: 0.65rem; margin-bottom: 0.75rem; }}
.pb-fbo-lock {{
    width: 2.25rem; height: 2.25rem; border-radius: 999px; background: {CHARCOAL};
    color: #fff; display: flex; align-items: center; justify-content: center; flex-shrink: 0;
}}
.pb-fbo-kicker {{ font-size: 0.68rem; font-weight: 700; text-transform: uppercase; color: #9A6200; margin: 0; }}
.pb-fbo-sub {{ font-size: 0.82rem; color: {SUBCOPY}; margin: 0.2rem 0 0; }}

.pb-security-compound {{
    border: 2px solid {CHARCOAL}; border-radius: 0.85rem; overflow: hidden; background: #FDFDFD;
}}
.pb-security-compound .pb-security-row + .pb-security-row {{ border-top: 1px solid #F0E6D2; }}
.pb-security-row {{
    display: flex; align-items: flex-start; justify-content: space-between;
    gap: 0.75rem; padding: 1rem 1.15rem;
}}
.pb-security-label {{ font-size: 0.68rem; font-weight: 700; text-transform: uppercase; color: {MUTED}; margin: 0; }}
.pb-security-value {{ font-size: 0.95rem; font-weight: 600; margin: 0.35rem 0 0; word-break: break-word; }}
.pb-security-value--prominent {{ font-size: 1.35rem; font-weight: 700; font-family: ui-monospace, monospace; color: {CHARCOAL}; }}
.pb-copy-micro {{
    border: 1px solid {BORDER}; background: #fff; border-radius: 0.5rem;
    font-size: 0.72rem; font-weight: 600; color: {MUTED}; padding: 0.3rem 0.55rem; cursor: pointer;
}}
.pb-copy-micro.pb-copy-success {{ color: {GREEN}; border-color: #A7F3D0; background: {GREEN_SOFT}; }}

.pb-agent-meta {{
    background: {CANVAS}; border: 1px solid {BORDER}; border-radius: 0.75rem;
    padding: 0.75rem 0.85rem; margin-bottom: 0.65rem; font-size: 0.82rem;
}}
.pb-agent-meta strong {{ color: {CHARCOAL}; }}
.pb-agent-meta-kicker {{
    font-size: 0.65rem; font-weight: 700; text-transform: uppercase; color: {MUTED}; margin: 0 0 0.25rem;
}}

.pb-agent-note {{
    border: 1px dashed {BORDER}; border-radius: 0.75rem; padding: 0.75rem;
    font-size: 0.82rem; margin-top: 0.75rem;
}}
.pb-agent-note-kicker {{ font-size: 0.65rem; font-weight: 700; text-transform: uppercase; color: {MUTED}; margin: 0; }}

.stTextInput input {{
    min-height: 3.25rem !important; font-size: 1.05rem !important;
    border-radius: 0.75rem !important; border: 1px solid {BORDER} !important;
}}
.stButton > button[kind="primary"], [data-testid="stFormSubmitButton"] button {{
    min-height: 3.25rem !important; background: {CHARCOAL} !important; color: #fff !important;
    border-radius: 0.75rem !important; font-weight: 600 !important; width: 100% !important;
}}
.stButton > button[kind="secondary"] {{
    min-height: 3rem !important; border: 2px solid {BORDER} !important;
    border-radius: 0.75rem !important; background: {CARD} !important; width: 100% !important;
    text-align: left !important; white-space: pre-wrap !important;
}}
</style>
        """,
        unsafe_allow_html=True,
    )

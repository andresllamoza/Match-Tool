"""Rollover Companion — Streamlit production demo (Customer / BeeKeeper / Funnel).

    cd rollover-companion && streamlit run sandbox/app.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from adapters.advizorpro import AdvizorProAdapter  # noqa: E402
from adapters.matcher5500 import Local5500Adapter  # noqa: E402
from engine.enrichment import build_enrichment  # noqa: E402
from engine.journey import JourneyEngine  # noqa: E402
from engine.knowledge import KnowledgeBase  # noqa: E402
from engine.lookup import LookupService  # noqa: E402
from engine.models import JourneyChannel, JourneyState  # noqa: E402
from sandbox.persistence import SessionStore  # noqa: E402

CREAM = "#FAF8F5"
YELLOW = "#FFC72C"
INK = "#111111"
MUTED = "#8A857B"
BORDER = "#EEE9DF"

st.set_page_config(page_title="Rollover Companion", page_icon="🐝", layout="centered")

st.markdown(
    f"""<style>
    .stApp {{ background: {CREAM}; }}
    .block-container {{
        padding-top: 1rem; padding-bottom: 2rem; max-width: 30rem;
    }}
    html, body, [class*="st-"] {{
        color: {INK};
        font-family: "Inter", -apple-system, "Segoe UI", Roboto, sans-serif;
    }}
    h1 {{
        font-size: clamp(1.75rem, 5vw, 2.125rem) !important;
        font-weight: 800 !important; letter-spacing: -0.02em !important;
        line-height: 1.2 !important;
    }}
    #MainMenu, footer, header {{ visibility: hidden; }}

    .stButton > button {{
        min-height: 3rem !important;
    }}
    .stButton > button[kind="primary"] {{
        background: {INK}; color: #fff; border: none; border-radius: 12px;
        padding: 0.75rem 1.25rem; font-weight: 700; font-size: 1.0625rem; width: 100%;
    }}
    .stButton > button[kind="primary"]:hover {{ background: #2b2b2b; color: #fff; }}
    .stButton > button[kind="secondary"] {{
        background: transparent; color: {INK}; border: 1.5px solid #d9d4cb;
        border-radius: 12px; padding: 0.7rem 1.2rem; font-weight: 600; width: 100%;
        text-align: left; white-space: pre-wrap; line-height: 1.35;
    }}
    .stTextInput input {{
        min-height: 3rem; font-size: 1.0625rem; border-radius: 12px;
        border: 1px solid {BORDER};
    }}

    .rail {{ display: flex; gap: 6px; margin: 4px 0 26px 0; }}
    .rail .seg {{
        flex: 1; text-align: center; font-size: 0.72rem; font-weight: 700;
        letter-spacing: 0.06em; text-transform: uppercase; color: #9b958a;
        padding: 7px 0 9px; border-top: 3px solid #e7e2d8;
    }}
    .rail .seg.done {{ color: {INK}; border-top-color: {INK}; }}
    .rail .seg.active {{
        color: {INK}; border-top-color: {YELLOW};
        background: linear-gradient(180deg, rgba(255,199,44,0.18), transparent);
    }}

    .card {{
        background: #fff; border: 1px solid {BORDER}; border-radius: 16px;
        padding: 24px; margin-bottom: 14px;
        box-shadow: 0 1px 3px rgba(17,17,17,0.04);
        font-size: 1.0625rem; line-height: 1.55;
    }}
    .card.warn {{ border-left: 4px solid {YELLOW}; }}
    .welcome {{
        background: #fff; border: 1px solid {BORDER}; border-radius: 16px;
        padding: 20px 24px; margin-bottom: 14px;
        animation: slideIn 0.45s ease-out;
    }}
    @keyframes slideIn {{
        from {{ opacity: 0; transform: translateY(10px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}
    .welcome-kicker {{
        font-size: 0.72rem; font-weight: 800; letter-spacing: 0.08em;
        text-transform: uppercase; color: #9A6200;
    }}

    .fbo {{
        background: #fff; border: 2px solid {INK}; border-radius: 16px;
        padding: 24px; margin: 18px 0;
    }}
    .fbo .label {{
        font-size: 0.72rem; font-weight: 800; letter-spacing: 0.1em;
        text-transform: uppercase; color: #6f6a60; margin-bottom: 6px;
    }}
    .fbo .line {{
        font-size: 1.35rem; font-weight: 800; color: {INK};
        font-family: ui-monospace, "SF Mono", Menlo, monospace;
        word-break: break-word;
    }}
    .fbo .mail {{ font-size: 1.02rem; font-weight: 600; margin-top: 10px; word-break: break-word; }}

    div[data-testid="stCode"] {{
        margin-top: 10px;
    }}
    div[data-testid="stCode"] pre,
    div[data-testid="stCodeBlock"] pre {{
        background: #fff !important;
        border: 2px solid {INK} !important;
        border-radius: 14px !important;
        font-size: 1.1rem !important;
        color: {INK} !important;
        font-family: ui-monospace, Menlo, monospace !important;
        padding: 14px 16px !important;
    }}
    div[data-testid="stCode"] button {{
        opacity: 0.55;
    }}
    div[data-testid="stCode"]:hover button {{
        opacity: 1;
    }}

    .agent {{
        background: {INK}; color: #f4f1ea; border-radius: 16px;
        padding: 20px 22px; font-size: 0.92rem; line-height: 1.55;
        margin-top: 14px;
    }}
    .agent h4 {{
        color: {YELLOW}; font-size: 0.72rem; font-weight: 800;
        letter-spacing: 0.1em; text-transform: uppercase;
        margin: 14px 0 6px;
    }}
    .agent h4:first-child {{ margin-top: 0; }}
    .agent .say-next {{ font-size: 1.05rem; line-height: 1.5; }}
    .agent-debug {{
        max-height: 8rem; overflow: auto; font-family: monospace;
        font-size: 0.75rem; background: rgba(255,255,255,0.06);
        padding: 8px; border-radius: 8px; margin-top: 6px;
    }}

    .topbar {{ display: flex; justify-content: space-between; align-items: center;
        flex-wrap: wrap; gap: 8px; margin-bottom: 6px; }}
    .brand {{ font-weight: 800; color: {INK}; font-size: 1.02rem; }}
    .muted {{ color: {MUTED}; font-size: 0.86rem; }}
    .channel-hint {{ font-size: 0.82rem; color: {MUTED}; margin-top: -6px; margin-bottom: 8px; }}

    @media (max-width: 390px) {{
        .block-container {{ padding-left: 0.85rem; padding-right: 0.85rem; }}
        .rail .seg {{ font-size: 0.62rem; }}
        .stButton > button {{ min-height: 3rem !important; }}
        .fbo .line {{ font-size: 1.1rem; }}
        .topbar {{ flex-direction: column; align-items: flex-start; }}
    }}
    </style>""",
    unsafe_allow_html=True,
)


@st.cache_resource
def boot():
    from adapters.hybrid5500 import Hybrid5500Adapter

    kb = KnowledgeBase.from_dir()
    chain = [Local5500Adapter.from_synthetic()]
    index = Local5500Adapter.from_employer_index()
    if index:
        chain.append(index)
    lookup = LookupService(kb, Hybrid5500Adapter(chain), AdvizorProAdapter())
    return JourneyEngine(kb, lookup), SessionStore()


engine, store = boot()

try:
    _expected = st.secrets.get("app_password", "")
except Exception:
    _expected = ""
if _expected:
    if not st.session_state.get("_authed"):
        st.markdown('<div class="brand">🐝 PensionBee · Rollover Companion</div>', unsafe_allow_html=True)
        pw = st.text_input("Password", type="password")
        if st.button("Sign in", type="primary"):
            if pw == _expected:
                st.session_state["_authed"] = True
                st.rerun()
            st.error("That's not it — try again.")
        st.stop()

qp_journey = st.query_params.get("journey")
if "ctx" not in st.session_state:
    restored = store.load(qp_journey) if qp_journey else None
    st.session_state.ctx = restored or engine.start()
    st.session_state.restored = restored is not None
ctx = st.session_state.ctx
if st.query_params.get("journey") != ctx.journey_id:
    st.query_params["journey"] = ctx.journey_id
store.save(ctx)


def act(method: str, *args) -> None:
    getattr(engine, method)(ctx, *args)
    store.save(ctx)
    st.session_state.restored = False
    st.query_params["journey"] = ctx.journey_id
    st.rerun()


def new_journey() -> None:
    st.session_state.ctx = engine.start()
    st.session_state.restored = False
    store.save(st.session_state.ctx)
    st.query_params["journey"] = st.session_state.ctx.journey_id
    st.rerun()


SURFACES = ["Customer", "BeeKeeper", "Funnel"]
tb1, tb2 = st.columns([3, 2])
with tb1:
    st.markdown('<div class="brand">🐝 PensionBee · Rollover Companion</div>', unsafe_allow_html=True)
with tb2:
    try:
        surface = st.segmented_control("Surface", SURFACES, default="Customer", label_visibility="collapsed")
    except (AttributeError, TypeError):
        surface = st.radio("Surface", SURFACES, horizontal=True, label_visibility="collapsed")
surface = surface or "Customer"

screen = engine.render(ctx)

if surface == "Funnel":
    from engine.funnel import load_funnel_summary

    st.title("Journey funnel")
    st.caption("Stall points and handoff demand from the event stream.")
    summary = load_funnel_summary()
    if summary.total_journeys == 0 and not summary.by_state:
        st.markdown(
            '<div class="card">No journeys yet — run one from the <b>Customer</b> surface, '
            "then come back here.</div>",
            unsafe_allow_html=True,
        )
    else:
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Journeys", summary.total_journeys)
        m2.metric("Handoffs offered", summary.handoff_offered_count)
        m3.metric("Handoffs taken", summary.handoff_taken_count)
        m4.metric("Not covered", summary.provider_not_covered_count)
        if summary.by_state:
            st.markdown("##### Events by state")
            st.bar_chart({k: v for k, v in summary.by_state.items() if v > 0})
        if summary.stall_points:
            st.markdown("##### Stall points by provider")
            rows = [
                {"Provider": sp.provider or "—", "State": sp.state, "Count": sp.count}
                for sp in summary.stall_points
            ]
            st.dataframe(rows, use_container_width=True, hide_index=True)
    st.stop()

PHASES = ["find", "access", "rollover", "track"]
PHASE_LABELS = {"find": "Find", "access": "Access", "rollover": "Roll over", "track": "Track"}
current = screen.phase.value if screen.phase else "find"
segs = []
for p in PHASES:
    idx = PHASES.index(p)
    cur_idx = PHASES.index(current) if current in PHASES else 0
    cls = "active" if p == current else ("done" if idx < cur_idx else "")
    segs.append(f'<div class="seg {cls}">{PHASE_LABELS[p]}</div>')
st.markdown(f'<div class="rail">{"".join(segs)}</div>', unsafe_allow_html=True)

if st.session_state.get("restored"):
    provider = ctx.provider or ctx.uncovered_provider or "your provider"
    stage = screen.headline or ctx.state.value.replace("_", " ")
    st.markdown(
        f'<div class="welcome" role="status">'
        f'<p class="welcome-kicker">🐝 Welcome back — we saved your spot</p>'
        f"<p style='margin:8px 0 0;font-size:1.0625rem;line-height:1.55'>"
        f"Continuing your <strong>{provider}</strong> rollover — {stage}.</p></div>",
        unsafe_allow_html=True,
    )
    st.session_state.restored = False

_title = screen.headline
if ctx.state == JourneyState.ACCESS_RECOVERED and not ctx.tax_fund_type:
    _title = "What kind of money is it?"
st.title(_title)
if screen.body and _title == screen.headline:
    st.markdown(
        f'<p class="muted" style="font-size:1.0625rem;line-height:1.55;margin-bottom:14px">{screen.body}</p>',
        unsafe_allow_html=True,
    )

if screen.provenance_warning:
    st.markdown(f'<div class="card warn">⚠️ {screen.provenance_warning}</div>', unsafe_allow_html=True)

enr = build_enrichment(engine.knowledge, ctx, screen)
cc = enr.channel_context
in_channel = ctx.state in (JourneyState.PHONE_IN_PROGRESS, JourneyState.FORMS_IN_PROGRESS)


def fbo_card() -> None:
    payable = cc.check_payable if cc else None
    mail_to = (cc.mailing_address if cc else None) or enr.mailing_address or None
    if not payable:
        return
    mail_html = f'<div class="mail">Mail to: {mail_to}</div>' if mail_to else ""
    st.markdown(
        f"""<div class="fbo">
        <div class="label">Make the check payable to — exactly</div>
        <div class="line">{payable}</div>{mail_html}
        <div class="muted" style="margin-top:10px;font-size:0.85rem">
        If a check ever arrives payable to <b>you personally</b>, don't cash it —
        that's a withdrawal, not a rollover. Your BeeKeeper will fix it.</div></div>""",
        unsafe_allow_html=True,
    )
    st.code(payable, language=None)


if ctx.state in (
    JourneyState.ONLINE_IN_PROGRESS,
    JourneyState.PHONE_IN_PROGRESS,
    JourneyState.FORMS_IN_PROGRESS,
):
    for g in screen.guidance:
        flag = ' <span class="muted">· double-check this screen</span>' if g.reconstructed else ""
        st.markdown(f'<div class="card">{g.text}{flag}</div>', unsafe_allow_html=True)
    if cc and ctx.state == JourneyState.PHONE_IN_PROGRESS and cc.rep_questions:
        for rq in cc.rep_questions:
            st.markdown(
                f'<div class="card"><span class="muted" style="font-size:0.74rem;font-weight:800;'
                f'letter-spacing:0.08em;text-transform:uppercase">They ask: {rq.question}</span>'
                f"<br/>{rq.answer}</div>",
                unsafe_allow_html=True,
            )
    if in_channel:
        fbo_card()
elif ctx.state == JourneyState.INITIATED:
    for g in screen.guidance:
        st.markdown(f'<div class="card">{g.text}</div>', unsafe_allow_html=True)
    fbo_card()
    if screen.sla_note:
        st.markdown(f'<div class="card">⏱ {screen.sla_note}</div>', unsafe_allow_html=True)

s = ctx.state

if s == JourneyState.PROVIDER_UNKNOWN:
    if ctx.disambiguation_options:
        st.markdown(f'<div class="card warn">{ctx.disambiguation_question}</div>', unsafe_allow_html=True)
        pick = st.radio("Pick one", ctx.disambiguation_options, label_visibility="collapsed")
        if st.button("That's the one", type="primary"):
            act("disambiguate", pick)
    else:
        emp = st.text_input(
            "Former employer — or the provider, if you know it",
            placeholder="e.g. Target, Costco, Citi",
        )
        if st.button("Find my 401(k)", type="primary") and emp.strip():
            act("lookup_employer", emp.strip())

elif s == JourneyState.PROVIDER_IDENTIFIED:
    if st.button(screen.primary_action or "Yes, I can log in", type="primary"):
        act("submit_access", True)
    if st.button("No / not sure", type="secondary"):
        act("submit_access", False)

elif s == JourneyState.ACCESS_BLOCKED:
    for g in screen.guidance:
        st.markdown(f'<div class="card">{g.text}</div>', unsafe_allow_html=True)
    if st.button("I'm back in — continue", type="primary"):
        act("submit_access_recovered")
    if st.button("Still locked out — bring in my BeeKeeper", type="secondary"):
        act("escalate", "locked_out")

elif s == JourneyState.ACCESS_RECOVERED:
    if not ctx.tax_fund_type:
        st.markdown(
            '<div class="card">Pre-tax goes to a Traditional IRA, Roth to a Roth IRA.</div>',
            unsafe_allow_html=True,
        )
        tax = st.radio(
            "My old 401(k) money is…",
            ["pre_tax", "roth", "both"],
            format_func=lambda x: {"pre_tax": "Pre-tax (most common)", "roth": "Roth", "both": "Both"}[x],
        )
        if st.button("Continue", type="primary"):
            act("submit_tax_type", tax)
    else:
        sla = screen.sla_note or ""
        if sla:
            st.markdown(f'<div class="card warn">⏱ {sla}</div>', unsafe_allow_html=True)
        pb = engine.knowledge.playbook_for(ctx) if ctx.provider else None
        is_two_hop = pb and pb.mechanism.value == "two_hop_acat"
        online_label = "Do it online — usually 2–5 business days" if is_two_hop else "Do it online — usually fastest"
        if st.button(online_label, type="primary"):
            act("choose_channel", JourneyChannel.ONLINE)
        if is_two_hop and sla:
            st.markdown(f'<p class="channel-hint">vs 7–10 by check · {sla}</p>', unsafe_allow_html=True)
        if st.button("By phone, with a read-along script", type="secondary"):
            act("choose_channel", JourneyChannel.PHONE)
        if sla and not is_two_hop:
            st.markdown(f'<p class="channel-hint">{sla}</p>', unsafe_allow_html=True)
        if st.button("I have paper forms", type="secondary"):
            act("choose_channel", JourneyChannel.FORMS)

elif s in (
    JourneyState.ONLINE_IN_PROGRESS,
    JourneyState.PHONE_IN_PROGRESS,
    JourneyState.FORMS_IN_PROGRESS,
):
    if st.button("Done — next", type="primary"):
        act("advance_step", "done")
    if st.button("I'm stuck", type="secondary"):
        act("advance_step", "stuck")

elif s == JourneyState.STUCK:
    for g in screen.guidance:
        st.markdown(f'<div class="card">{g.text}</div>', unsafe_allow_html=True)
    if st.button("That fixed it — resume", type="primary"):
        act("resume_from_stuck")
    if st.button("Bring in my BeeKeeper", type="secondary"):
        act("escalate", "stuck_again")

elif s == JourneyState.INITIATED:
    if st.button("Track my transfer", type="primary"):
        act("confirm_in_flight")

elif s == JourneyState.IN_FLIGHT:
    if screen.sla_note:
        st.markdown(f'<div class="card">⏱ {screen.sla_note}</div>', unsafe_allow_html=True)
    if st.button("It arrived 🎉", type="primary"):
        act("mark_complete")
    if st.button("Nothing yet — past the window", type="secondary"):
        act("escalate", "sla_breach")

elif s == JourneyState.COMPLETE:
    st.balloons()
    st.markdown(
        '<div class="card">One account, one place — your old 401(k) is home. '
        "PensionBee adds 1% on eligible rollovers · terms apply.</div>",
        unsafe_allow_html=True,
    )
    if st.button("Start another rollover", type="primary"):
        new_journey()

elif s in (JourneyState.PROVIDER_NOT_COVERED, JourneyState.ESCALATED):
    prov = ctx.provider or ctx.uncovered_provider or "your provider"
    st.markdown(
        f'<div class="card warn">Found it — it\'s at <b>{prov}</b>. Your BeeKeeper will '
        "guide this one personally.</div>",
        unsafe_allow_html=True,
    )
    if st.button("Talk to your BeeKeeper", type="primary"):
        act("take_handoff", "sandbox_handoff")
    if st.button("Start over", type="secondary"):
        new_journey()

if s not in (JourneyState.COMPLETE, JourneyState.ESCALATED, JourneyState.PROVIDER_NOT_COVERED):
    if st.button("🐝 Talk to your BeeKeeper", type="tertiary"):
        engine.log_handoff_taken(ctx, f"voluntary:{s.value}")
        store.save(ctx)
        st.toast("Your BeeKeeper has the full context of this journey.")

if surface == "BeeKeeper":
    notes = "".join(f"<li>{n}</li>" for n in screen.agent_notes) or "<li>—</li>"
    esc = "".join(f"<li>{e.action}</li>" for e in screen.active_escalations)
    edge = "".join(f"<li>{e}</li>" for e in screen.edge_cases)
    say = screen.next_beekeeper_script or "—"
    st.markdown(
        f"""<div class="agent">
        <h4>Say next</h4><div class="say-next">{say}</div>
        <h4>Agent notes</h4><ul>{notes}</ul>
        {f'<h4>Active escalations</h4><ul>{esc}</ul>' if esc else ''}
        {f'<h4>Edge cases</h4><ul>{edge}</ul>' if edge else ''}
        <h4>State debug</h4>
        <div class="agent-debug">{ctx.state.value} · {ctx.provider or "?"} · step {ctx.step_index}
        · stuck×{ctx.stuck_count} · {ctx.journey_id}</div></div>""",
        unsafe_allow_html=True,
    )
    st.code(say, language=None)

with st.expander("Demo: customer name", expanded=False):
    from engine.customer_copy import DEFAULT_FIRST_NAME, DEFAULT_LAST_NAME

    c1, c2 = st.columns(2)
    demo_first = c1.text_input("First", value=ctx.customer_first_name or DEFAULT_FIRST_NAME)
    demo_last = c2.text_input("Last", value=ctx.customer_last_name or DEFAULT_LAST_NAME)
    if st.button("Apply name", key="demo_apply_name") and demo_first.strip() and demo_last.strip():
        ctx.customer_first_name = demo_first.strip()
        ctx.customer_last_name = demo_last.strip()
        store.save(ctx)
        st.rerun()

with st.expander("Resume a saved journey"):
    rows = store.recent()
    if not rows:
        st.caption("No saved journeys yet.")
    for r in rows:
        c1, c2 = st.columns([4, 1])
        c1.markdown(
            f"`{r['journey_id']}` — **{r['state']}**"
            + (f" · {r['provider']}" if r["provider"] else "")
            + f" · {r['updated_at'][:16]}"
        )
        if c2.button("Resume", key=f"res_{r['journey_id']}"):
            restored = store.load(r["journey_id"])
            if restored:
                st.session_state.ctx = restored
                st.session_state.restored = True
                st.query_params["journey"] = restored.journey_id
                st.rerun()
    if st.button("＋ New journey", type="secondary"):
        new_journey()

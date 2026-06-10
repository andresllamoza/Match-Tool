# CURSOR OVERNIGHT BRIEF — make the Rollover Companion demo-ready by morning

You have the repo. Work top to bottom. After EVERY part: run
`python -m pytest -q` from `rollover-companion/` and keep the suite green.
Commit each part separately. Do not wait for human input.

**Context:** Tomorrow's demo runs on the DEPLOYED Streamlit app —
`match-tool ∙ main ∙ discovery-front-door/app.py` (the 3-surface workspace,
bridged to rollover-companion/engine + rollover-knowledge-layer). Everything
below lands on `main` (or a PR you merge to main tonight).

---

## PART 1 — COMPLIANCE HOTFIX (do this first; the deployed app is wrong today)

Every direct-rollover check, for EVERY provider, is payable to
**PensionBee FBO [user's name]**. Payable-to-participant = withdrawal/cashout
(taxable), NOT a rollover. Only the MAILING destination varies by provider.
The deployed app currently renders the wrong payee for Empower + Fidelity.

Apply these exact edits:

**`rollover-companion/rollover-knowledge-layer/Empower_Rollover_Guide.md`**
- Replace: `check_payable: "Participant name"`
  With: `check_payable: "PensionBee FBO [your name]"`
- Replace the rep_question answer
  `"Payable to you (participant); you forward to PensionBee at PO Box 72, New York, NY 10272."`
  With: `"Payable to PensionBee FBO [your name] — that keeps it a direct rollover. Mail it to my address on file; I'll forward it to PensionBee."`
- Append to `edge_cases:` list:
  `- "If the check arrives payable to YOU personally (not 'PensionBee FBO …'), stop — that's a withdrawal/cashout, not a rollover, and taxes/penalties may apply. Don't cash it; contact your BeeKeeper."`

**`rollover-companion/rollover-knowledge-layer/Fidelity_Rollover_Guide.md`**
- Replace: `check_payable: "Participant name (phone/check fallback only)"`
  With: `check_payable: "PensionBee FBO [your name]"`
- Replace the rep_question answer
  `"For phone/check path: payable to you; you forward to PensionBee. Prefer online Express rollover to avoid a check."`
  With: `"Payable to PensionBee FBO [your name] — that keeps it a direct rollover. (Prefer the online Express rollover to avoid a check entirely.)"`
- Append the same cashout edge case as Empower.

**`rollover-companion/rollover-knowledge-layer/Check_Destination_Matrix.md`**
- At the top of the `## Rules` section, add this bullet FIRST:
  `- **PAYEE vs DESTINATION — never confuse them.** Every rollover check, for every provider, is payable to **PensionBee FBO [user's name]**. "Check destination" above is only WHERE the check is MAILED. A check made payable to the participant personally is a **withdrawal/cashout** (taxable event), not a rollover — stop and escalate to a BeeKeeper before anything is cashed.`

**Verify:** in the deployed/local app, Citi → phone channel must show
`PensionBee FBO <user's name>` and never "Participant name". Also confirm no
other file contains `Participant name`: `grep -rn "Participant name" .`

## PART 2 — ENGINE ROBUSTNESS (new/changed files, full contents below)

Replace/create these four files exactly as given in the appendix:
1. `rollover-companion/adapters/matcher5500.py` — REPLACE. `from_matcher()` now
   falls back to the bundled 89k employer index instead of raising when the
   DOL cache is absent (this previously crashed the API at import on any fresh
   machine). After this, the FULL suite runs: expect **195 passed** plus the
   new tests in (4).
2. `rollover-companion/sandbox/persistence.py` — CREATE. SQLite write-through
   session store (RAM-purge guardrail).
3. `rollover-companion/sandbox/app.py` — CREATE. Branded internal/backup
   Streamlit surface (customer/BeeKeeper/funnel) over the same engine.
4. `rollover-companion/tests/test_sandbox_persistence.py` — CREATE. Adds the
   payee compliance invariants (all 7 providers must yield the personalized
   FBO line) + persistence round-trip tests.
Also: ensure `streamlit>=1.50` is in `rollover-companion/requirements.txt`.

## PART 3 — MERGE + POLISH THE DEPLOYED SURFACE

1. Merge `cursor/premium-channel-step-9f5f` into main if its QA is green
   (5 polish commits ahead).
2. Then work these on `discovery-front-door/` (journey/ + ui/), one commit each:
   - FBO security card: 2px charcoal (#111111) border, uppercase kicker
     "MAKE THE CHECK PAYABLE TO — EXACTLY", large monospace payee, mail-to
     line, copy-to-clipboard, and the warning: "If a check ever arrives
     payable to you personally, don't cash it — that's a withdrawal, not a
     rollover. Your BeeKeeper will fix it." Payee value ALWAYS from
     enrichment.channel_context — never hardcoded.
   - Design tokens everywhere: cream #FAF8F5 canvas, charcoal #111111 type +
     primary buttons, yellow #FFC72C ONLY on the active momentum-rail segment.
   - Channel screen: online button framed "usually 2–5 business days" vs
     "7–10 by check" for two-hop providers (values from the engine payload).
   - Mobile pass at 390px: full-width ≥48px buttons, FBO line wraps, rail
     legible.
   - Funnel: friendly empty state; per-provider stall table when data exists.
   - Welcome-back/resume moment styled as a warm card.
3. Final QA walk on the deployed app: Target→online · Citi→phone (FBO card!) ·
   Costco (one clarifying question) · Walmart (concierge handoff) ·
   hard-refresh mid-journey · all three surfaces · 390px. Fix what's off.

## DEFINITION OF DONE (morning checklist)
- [ ] `grep -rn "Participant name"` → zero hits
- [ ] Full suite green (195+ passed) on a clean checkout
- [ ] Deployed app: Citi→phone shows personalized PensionBee FBO card
- [ ] Hard refresh mid-journey resumes
- [ ] DEMO_SCRIPT_COMPANION.md walkthrough passes end-to-end on the live URL

---

# APPENDIX — full file contents (create/replace exactly)

## `rollover-companion/adapters/matcher5500.py`
```python
from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Optional

from engine.models import LookupResult

from .synthetic_data import SYNTHETIC_EMPLOYERS


def master_cache_available(repo_root: Path | None = None) -> bool:
    root = repo_root or Path(__file__).resolve().parents[2]
    data = root / "data"
    return (data / "recordkeeper_master.csv").is_file() and (
        data / "recordkeeper_master.version"
    ).is_file()


class Local5500Adapter:
    """5500 matcher adapter — synthetic or real `src.matcher.match`."""

    name = "matcher5500"

    def __init__(self, lookup_fn):
        self._lookup = lookup_fn

    @classmethod
    def from_synthetic(cls) -> Local5500Adapter:
        def _lookup(employer_name: str, years=None, state=None) -> LookupResult:
            key = employer_name.strip().lower()
            for row in SYNTHETIC_EMPLOYERS:
                if row["employer"].lower() == key or key in row.get("aliases", []):
                    matcher = row.get("matcher")
                    if matcher is None:
                        return LookupResult(source="matcher5500", provider=None, confidence=0.0)
                    conf = row.get("matcher_confidence", 0.9)
                    return LookupResult(
                        source="matcher5500",
                        provider=matcher,
                        confidence=conf,
                        matched_employer_name=row["employer"],
                        raw_confidence_label=row.get("matcher_label"),
                    )
            return LookupResult(source="matcher5500", provider=None, confidence=0.0)

        return cls(_lookup)

    @classmethod
    def matcher_deps_available(cls) -> tuple[bool, str | None]:
        try:
            import numpy  # noqa: F401
            import pandas  # noqa: F401
            import rapidfuzz  # noqa: F401
        except ImportError as exc:
            return False, exc.name
        return True, None

    @classmethod
    def from_employer_index(cls) -> Local5500Adapter | None:
        """Bundled ~89k-employer index — real lookups with no DOL download."""
        from .employer_index import EmployerIndexAdapter

        csv_path = Path(__file__).resolve().parents[1] / "data" / "employer_rk_index.csv"
        index = EmployerIndexAdapter.from_csv(csv_path)
        return cls(index.lookup) if index else None

    @classmethod
    def from_matcher(cls, repo_root: Path | None = None) -> Local5500Adapter:
        ok, missing = cls.matcher_deps_available()
        if not ok:
            return cls.from_synthetic()

        root = repo_root or Path(__file__).resolve().parents[2]
        if not master_cache_available(root):
            # Fresh checkout / CI / cloud: the full DOL cache isn't built yet.
            # Fall back to the bundled employer index instead of crashing the
            # engine (and the API) at import time.
            return cls.from_employer_index() or cls.from_synthetic()
        if str(root) not in sys.path:
            sys.path.insert(0, str(root))

        try:
            from src.matcher import match as matcher_match  # noqa: WPS433
        except ImportError:
            return cls.from_synthetic()

        def _lookup(employer_name: str, years=None, state=None) -> LookupResult:
            results = matcher_match(employer_name, top_n=1)
            if not results:
                return LookupResult(source="matcher5500", provider=None, confidence=0.0)
            best = results[0]
            return LookupResult(
                source="matcher5500",
                provider=best.recordkeeper,
                confidence=best.confidence,
                matched_employer_name=best.matched_employer_name,
                raw_confidence_label=best.confidence_label,
            )

        return cls(_lookup)

    def lookup(
        self,
        employer_name: str,
        years: Optional[list[int]] = None,
        state: Optional[str] = None,
    ) -> LookupResult:
        return self._lookup(employer_name, years, state)
```

## `rollover-companion/sandbox/persistence.py`
```python
"""Session persistence — the RAM-purge guardrail.

Streamlit's ``st.session_state`` dies on hard refresh / connection drop. Every
state transition writes the full JourneyContext (pydantic JSON) to a local
SQLite database so an interrupted journey re-hydrates seamlessly on reload.

SQLite over JSONL: atomic single-row upserts, indexable resume list, and one
file (``rollover_sessions.db``) that survives Streamlit reruns and restarts.
WAL mode keeps concurrent rerun writes safe.
"""

from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from engine.models import JourneyContext

DEFAULT_DB = Path(__file__).resolve().parent.parent / "data" / "rollover_sessions.db"

_SCHEMA = """
CREATE TABLE IF NOT EXISTS sessions (
    journey_id  TEXT PRIMARY KEY,
    state       TEXT NOT NULL,
    provider    TEXT,
    channel     TEXT,
    surface     TEXT NOT NULL DEFAULT 'customer',
    context_json TEXT NOT NULL,
    updated_at  TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_sessions_updated ON sessions (updated_at DESC);
"""


class SessionStore:
    def __init__(self, db_path: Path | str = DEFAULT_DB):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with self._conn() as conn:
            conn.executescript(_SCHEMA)

    def _conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, timeout=5)
        conn.execute("PRAGMA journal_mode=WAL")
        return conn

    def save(self, ctx: JourneyContext, surface: str = "customer") -> None:
        """Write-through on every transition. Cheap (one row), atomic."""
        with self._conn() as conn:
            conn.execute(
                """INSERT INTO sessions
                   (journey_id, state, provider, channel, surface, context_json, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?)
                   ON CONFLICT(journey_id) DO UPDATE SET
                     state=excluded.state, provider=excluded.provider,
                     channel=excluded.channel, surface=excluded.surface,
                     context_json=excluded.context_json, updated_at=excluded.updated_at""",
                (
                    ctx.journey_id,
                    ctx.state.value if hasattr(ctx.state, "value") else str(ctx.state),
                    ctx.provider,
                    ctx.channel.value if ctx.channel else None,
                    surface,
                    ctx.model_dump_json(),
                    datetime.now(timezone.utc).isoformat(),
                ),
            )

    def load(self, journey_id: str) -> Optional[JourneyContext]:
        with self._conn() as conn:
            row = conn.execute(
                "SELECT context_json FROM sessions WHERE journey_id = ?", (journey_id,)
            ).fetchone()
        return JourneyContext.model_validate_json(row[0]) if row else None

    def recent(self, limit: int = 8) -> list[dict]:
        """Resumable sessions for the sandbox resume drawer (newest first)."""
        with self._conn() as conn:
            rows = conn.execute(
                """SELECT journey_id, state, provider, channel, updated_at
                   FROM sessions ORDER BY updated_at DESC LIMIT ?""",
                (limit,),
            ).fetchall()
        return [
            {"journey_id": r[0], "state": r[1], "provider": r[2],
             "channel": r[3], "updated_at": r[4]}
            for r in rows
        ]

    def delete(self, journey_id: str) -> None:
        with self._conn() as conn:
            conn.execute("DELETE FROM sessions WHERE journey_id = ?", (journey_id,))
```

## `rollover-companion/sandbox/app.py`
```python
"""Rollover Companion — multi-surface Streamlit sandbox (production draft).

One journey engine, three surfaces (Customer / BeeKeeper / Funnel) in a single
sandbox workspace. Every state transition write-throughs to SQLite AND syncs
the journey id into the URL query params, so a hard refresh or connection drop
re-hydrates the exact screen the user was on.

    streamlit run sandbox/app.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from adapters.advizorpro import AdvizorProAdapter
from adapters.matcher5500 import Local5500Adapter
from engine.enrichment import build_enrichment
from engine.journey import JourneyEngine
from engine.knowledge import KnowledgeBase
from engine.lookup import LookupService
from engine.models import JourneyChannel, JourneyState
from sandbox.persistence import SessionStore

# ---------------------------------------------------------------- brand -----
CREAM = "#FAF8F5"
YELLOW = "#FFC72C"      # active momentum ONLY
INK = "#111111"

st.set_page_config(page_title="Rollover Companion", page_icon="🐝", layout="centered")

st.markdown(
    f"""<style>
    /* canvas + typography */
    .stApp {{ background: {CREAM}; }}
    html, body, [class*="st-"] {{ color: {INK}; font-family: -apple-system, "Inter",
        "Segoe UI", Roboto, "Helvetica Neue", sans-serif; }}
    h1 {{ font-weight: 800; letter-spacing: -0.02em; }}
    #MainMenu, footer, header {{ visibility: hidden; }}

    /* primary actions: dominant charcoal */
    .stButton > button[kind="primary"] {{
        background: {INK}; color: #FFFFFF; border: none; border-radius: 12px;
        padding: 0.7rem 1.4rem; font-weight: 700; font-size: 1.02rem; width: 100%;
    }}
    .stButton > button[kind="primary"]:hover {{ background: #2b2b2b; color: #fff; }}
    .stButton > button[kind="secondary"] {{
        background: transparent; color: {INK}; border: 1.5px solid #d9d4cb;
        border-radius: 12px; padding: 0.65rem 1.3rem; font-weight: 600; width: 100%;
    }}

    /* momentum rail — yellow strictly marks the ACTIVE step */
    .rail {{ display: flex; gap: 6px; margin: 4px 0 26px 0; }}
    .rail .seg {{ flex: 1; text-align: center; font-size: 0.72rem; font-weight: 700;
        letter-spacing: 0.06em; text-transform: uppercase; color: #9b958a;
        padding: 7px 0 9px 0; border-top: 3px solid #e7e2d8; }}
    .rail .seg.done {{ color: {INK}; border-top-color: {INK}; }}
    .rail .seg.active {{ color: {INK}; border-top-color: {YELLOW};
        background: linear-gradient(180deg, rgba(255,199,44,0.18), transparent); }}

    /* cards */
    .card {{ background: #FFFFFF; border: 1px solid #eee9df; border-radius: 16px;
        padding: 22px 24px; margin-bottom: 14px;
        box-shadow: 0 2px 10px rgba(17,17,17,0.04); }}
    .card.warn {{ border-left: 4px solid {YELLOW}; }}

    /* FBO security card — impossible to miss */
    .fbo {{ background: #FFFFFF; border: 2px solid {INK}; border-radius: 16px;
        padding: 22px 24px; margin: 18px 0; }}
    .fbo .label {{ font-size: 0.72rem; font-weight: 800; letter-spacing: 0.1em;
        text-transform: uppercase; color: #6f6a60; margin-bottom: 6px; }}
    .fbo .line {{ font-size: 1.35rem; font-weight: 800; color: {INK};
        font-family: ui-monospace, "SF Mono", Menlo, monospace; }}
    .fbo .mail {{ font-size: 1.02rem; font-weight: 600; margin-top: 10px; }}

    .agent {{ background: {INK}; color: #f4f1ea; border-radius: 16px;
        padding: 18px 20px; font-size: 0.92rem; }}
    .agent h4 {{ color: {YELLOW}; font-size: 0.72rem; letter-spacing: 0.1em;
        text-transform: uppercase; margin: 12px 0 4px 0; }}
    .agent h4:first-child {{ margin-top: 0; }}

    .topbar {{ display: flex; justify-content: space-between; align-items: center;
        margin-bottom: 6px; }}
    .brand {{ font-weight: 800; color: {INK}; font-size: 1.02rem; }}
    .muted {{ color: #8a857b; font-size: 0.86rem; }}
    </style>""",
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------- boot ------
@st.cache_resource
def boot():
    from adapters.hybrid5500 import Hybrid5500Adapter

    kb = KnowledgeBase.from_dir()
    # Demo determinism first (curated employers incl. low-confidence cases),
    # then the bundled ~89k-employer index for everything else. No DOL download.
    chain = [Local5500Adapter.from_synthetic()]
    index = Local5500Adapter.from_employer_index()
    if index:
        chain.append(index)
    lookup = LookupService(kb, Hybrid5500Adapter(chain), AdvizorProAdapter())
    return JourneyEngine(kb, lookup), SessionStore()


engine, store = boot()

# ------------------------------------------------- optional password gate ---
# Same pattern as the Match-Tool app: set `app_password` in Streamlit secrets
# to require sign-in (production deploys). No secret set = open (local demo).
try:
    _expected = st.secrets.get("app_password", "")
except Exception:
    _expected = ""
if _expected:
    if not st.session_state.get("_authed"):
        st.markdown('<div class="brand">🐝 PensionBee · Rollover Companion</div>',
                    unsafe_allow_html=True)
        pw = st.text_input("Password", type="password")
        if st.button("Sign in", type="primary"):
            if pw == _expected:
                st.session_state["_authed"] = True
                st.rerun()
            st.error("That's not it — try again.")
        st.stop()

# ------------------------------------------------- session re-hydration -----
# The URL is the recovery key: ?journey=<id>. Survives hard refresh & drops.
qp_journey = st.query_params.get("journey")

if "ctx" not in st.session_state:
    restored = store.load(qp_journey) if qp_journey else None
    st.session_state.ctx = restored or engine.start()
    st.session_state.restored = restored is not None
ctx = st.session_state.ctx
if st.query_params.get("journey") != ctx.journey_id:
    st.query_params["journey"] = ctx.journey_id
store.save(ctx)  # write-through even on first paint


def act(method: str, *args) -> None:
    """Single gateway for every transition: engine call -> SQLite -> URL -> rerun."""
    getattr(engine, method)(ctx, *args)
    store.save(ctx)
    st.query_params["journey"] = ctx.journey_id
    st.rerun()


def new_journey() -> None:
    st.session_state.ctx = engine.start()
    st.session_state.restored = False
    store.save(st.session_state.ctx)
    st.query_params["journey"] = st.session_state.ctx.journey_id
    st.rerun()


# ------------------------------------------------------------- top bar ------
SURFACES = ["Customer", "BeeKeeper", "Funnel"]
tb1, tb2 = st.columns([3, 2])
with tb1:
    st.markdown('<div class="brand">🐝 PensionBee · Rollover Companion</div>',
                unsafe_allow_html=True)
with tb2:
    surface = st.segmented_control("Surface", SURFACES, default="Customer",
                                   label_visibility="collapsed")
surface = surface or "Customer"

screen = engine.render(ctx)

# -------------------------------------------------------------- funnel ------
if surface == "Funnel":
    from engine.funnel import load_funnel_summary

    st.title("Journey funnel")
    st.caption("Stall points, handoffs, and not-covered demand — straight from the event stream.")
    s = load_funnel_summary()
    d = s.model_dump() if hasattr(s, "model_dump") else dict(s.__dict__)
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Events", d.get("total_events", d.get("events", 0)))
    m2.metric("Handoffs offered", d.get("handoff_offered_count", 0))
    m3.metric("Handoffs taken", d.get("handoff_taken_count", 0))
    m4.metric("Not covered", d.get("provider_not_covered_count", 0))
    by_state = d.get("by_state") or d.get("state_counts") or {}
    if by_state:
        st.markdown("##### Sessions by state")
        st.bar_chart(by_state)
    with st.expander("Raw summary"):
        st.json(d)
    st.stop()

# ------------------------------------------------------- momentum rail ------
PHASES = ["find", "access", "rollover", "track"]
PHASE_LABELS = {"find": "Find", "access": "Access", "rollover": "Roll over", "track": "Track"}
current = screen.phase.value if screen.phase else "find"
segs = []
for p in PHASES:
    cls = "active" if p == current else ("done" if PHASES.index(p) < PHASES.index(current) else "")
    segs.append(f'<div class="seg {cls}">{PHASE_LABELS[p]}</div>')
st.markdown(f'<div class="rail">{"".join(segs)}</div>', unsafe_allow_html=True)

if st.session_state.get("restored"):
    st.markdown('<div class="card warn">Welcome back — we saved your spot. '
                'Pick up right where you left off.</div>', unsafe_allow_html=True)
    st.session_state.restored = False

# ------------------------------------------------------------- screen -------
# Title follows the actual sub-decision, not just the engine state — during
# name/tax capture the state is still access_recovered but the question differs.
_title = screen.headline
if ctx.state == JourneyState.ACCESS_RECOVERED:
    if not ctx.customer_first_name:
        _title = "Who are we making this out to?"
    elif not ctx.tax_fund_type:
        _title = "What kind of money is it?"
st.title(_title)
if screen.body and _title == screen.headline:
    st.markdown(f'<div class="muted" style="font-size:1.05rem; margin-bottom:14px">'
                f'{screen.body}</div>', unsafe_allow_html=True)

if screen.provenance_warning:
    st.markdown(f'<div class="card warn">⚠️ {screen.provenance_warning}</div>',
                unsafe_allow_html=True)

enr = build_enrichment(engine.knowledge, ctx, screen)
cc = enr.channel_context
in_channel = ctx.state in (
    JourneyState.PHONE_IN_PROGRESS, JourneyState.FORMS_IN_PROGRESS,
)


def fbo_card() -> None:
    """The check-routing block: dominant, bordered, copy-ready. Never a bullet.

    Payee is ALWAYS the FBO line; only the mailing destination varies by
    provider. Payable-to-you personally = withdrawal/cashout, not a rollover.
    """
    payable = (cc.check_payable if cc else None) or None
    mail_to = (cc.mailing_address if cc else None) or enr.mailing_address or None
    if not payable:
        return
    mail_html = f'<div class="mail">Mail to: {mail_to}</div>' if mail_to else ""
    st.markdown(
        f"""<div class="fbo">
        <div class="label">Make the check payable to — exactly</div>
        <div class="line">{payable}</div>{mail_html}
        <div class="muted" style="margin-top:10px; font-size:0.85rem">
        If a check ever arrives payable to <b>you personally</b>, don't cash it —
        that's a withdrawal, not a rollover. Your BeeKeeper will fix it.</div></div>""",
        unsafe_allow_html=True,
    )
    st.code(payable, language=None)  # built-in copy button — tap to copy exactly


# guidance for the active step only (one decision per screen, low noise)
if ctx.state in (JourneyState.ONLINE_IN_PROGRESS, JourneyState.PHONE_IN_PROGRESS,
                 JourneyState.FORMS_IN_PROGRESS):
    for g in screen.guidance:
        flag = ' <span class="muted">· double-check this screen</span>' if g.reconstructed else ""
        st.markdown(f'<div class="card">{g.text}{flag}</div>', unsafe_allow_html=True)
    if cc and ctx.state == JourneyState.PHONE_IN_PROGRESS and cc.rep_questions:
        for rq in cc.rep_questions:
            st.markdown(
                f'<div class="card"><span class="muted" style="font-size:0.74rem; '
                f'font-weight:800; letter-spacing:0.08em; text-transform:uppercase">'
                f'They ask: {rq.question}</span><br/>{rq.answer}</div>',
                unsafe_allow_html=True)
    if in_channel:
        fbo_card()
elif ctx.state == JourneyState.INITIATED:
    for g in screen.guidance:
        st.markdown(f'<div class="card">{g.text}</div>', unsafe_allow_html=True)
    fbo_card()
    if screen.sla_note:
        st.markdown(f'<div class="card">⏱ {screen.sla_note}</div>', unsafe_allow_html=True)

# ------------------------------------------------- one choice per screen ----
s = ctx.state

if s == JourneyState.PROVIDER_UNKNOWN:
    if ctx.disambiguation_options:
        st.markdown(f'<div class="card warn">{ctx.disambiguation_question}</div>',
                    unsafe_allow_html=True)
        pick = st.radio("Pick one", ctx.disambiguation_options, label_visibility="collapsed")
        if st.button("That's the one", type="primary"):
            act("disambiguate", pick)
    else:
        emp = st.text_input("Former employer — or the provider, if you know it",
                            placeholder="e.g. Amazon, Target, Fidelity")
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
    # decision 1 of 3: who the check is for (powers the FBO line)
    if not ctx.customer_first_name:
        st.markdown('<div class="card">Checks get made out to you by name — '
                    'we print it exactly.</div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        first = c1.text_input("First name")
        last = c2.text_input("Last name")
        if st.button("Save my name", type="primary") and first.strip() and last.strip():
            ctx.customer_first_name = first.strip()
            ctx.customer_last_name = last.strip()
            store.save(ctx)
            st.rerun()
    # decision 2 of 3: money type
    elif not ctx.tax_fund_type:
        st.markdown('<div class="card">Pre-tax goes to a Traditional IRA, Roth to a '
                    'Roth IRA — automatic once we know.</div>', unsafe_allow_html=True)
        tax = st.radio("My old 401(k) money is…",
                       ["pre_tax", "roth", "both"],
                       format_func={"pre_tax": "Pre-tax (most common)", "roth": "Roth",
                                    "both": "Both"}.get)
        if st.button("Continue", type="primary"):
            act("submit_tax_type", tax)
    # decision 3 of 3: channel
    else:
        if screen.sla_note:
            st.markdown(f'<div class="card warn">⏱ {screen.sla_note}</div>',
                        unsafe_allow_html=True)
        if st.button("Do it online — usually fastest", type="primary"):
            act("choose_channel", JourneyChannel.ONLINE)
        if st.button("By phone, with a read-along script", type="secondary"):
            act("choose_channel", JourneyChannel.PHONE)
        if st.button("I have paper forms", type="secondary"):
            act("choose_channel", JourneyChannel.FORMS)

elif s in (JourneyState.ONLINE_IN_PROGRESS, JourneyState.PHONE_IN_PROGRESS,
           JourneyState.FORMS_IN_PROGRESS):
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
    st.markdown('<div class="card">One account, one place — your old 401(k) is home. '
                'That\'s one less thing to track.</div>', unsafe_allow_html=True)
    if st.button("Start another rollover", type="primary"):
        new_journey()

elif s in (JourneyState.PROVIDER_NOT_COVERED, JourneyState.ESCALATED):
    st.markdown('<div class="card warn">Prefer a person? This is exactly what your '
                'BeeKeeper is for — they do these every day.</div>', unsafe_allow_html=True)
    if st.button("Talk to your BeeKeeper", type="primary"):
        act("take_handoff", "sandbox_handoff")
    if st.button("Start over", type="secondary"):
        new_journey()

# universal escape hatch (never a failure state)
if s not in (JourneyState.COMPLETE, JourneyState.ESCALATED, JourneyState.PROVIDER_NOT_COVERED):
    st.markdown('<div style="text-align:center; margin-top:10px">', unsafe_allow_html=True)
    if st.button("🐝 Talk to your BeeKeeper", type="tertiary"):
        engine.log_handoff_taken(ctx, f"voluntary:{s.value}")
        store.save(ctx)
        st.toast("Your BeeKeeper has the full context of this journey.")
    st.markdown("</div>", unsafe_allow_html=True)

# -------------------------------------------------------- agent surface -----
if surface == "BeeKeeper":
    notes = "".join(f"<li>{n}</li>" for n in screen.agent_notes) or "<li>—</li>"
    esc = "".join(f"<li>{e.action}</li>" for e in screen.active_escalations)
    edge = "".join(f"<li>{e}</li>" for e in screen.edge_cases)
    say = screen.next_beekeeper_script or "—"
    st.markdown(
        f"""<div class="agent">
        <h4>Say next</h4><div>{say}</div>
        <h4>Agent notes</h4><ul>{notes}</ul>
        {f'<h4>Active escalations</h4><ul>{esc}</ul>' if esc else ''}
        {f'<h4>Edge cases</h4><ul>{edge}</ul>' if edge else ''}
        <h4>State</h4><code>{ctx.state.value} · {ctx.provider or "?"} · step {ctx.step_index}
        · stuck×{ctx.stuck_count} · {ctx.journey_id}</code></div>""",
        unsafe_allow_html=True,
    )

# ---------------------------------------------------------- resume drawer ---
with st.expander("Resume a saved journey"):
    rows = store.recent()
    if not rows:
        st.caption("No saved journeys yet.")
    for r in rows:
        c1, c2 = st.columns([4, 1])
        c1.markdown(f"`{r['journey_id']}` — **{r['state']}**"
                    + (f" · {r['provider']}" if r["provider"] else "")
                    + f" · {r['updated_at'][:16]}")
        if c2.button("Resume", key=f"res_{r['journey_id']}"):
            restored = store.load(r["journey_id"])
            if restored:
                st.session_state.ctx = restored
                st.query_params["journey"] = restored.journey_id
                st.rerun()
    if st.button("＋ New journey", type="secondary"):
        new_journey()
```

## `rollover-companion/tests/test_sandbox_persistence.py`
```python
"""Sandbox guardrails: SQLite write-through survives a simulated RAM purge,
and the FBO payee line is present + personalized on check-bearing screens."""

from __future__ import annotations

from engine.enrichment import build_enrichment
from engine.models import JourneyChannel, JourneyState
from sandbox.persistence import SessionStore


def _store(tmp_path):
    return SessionStore(tmp_path / "rollover_sessions.db")


def test_every_transition_survives_hard_refresh(engine, tmp_path):
    store = _store(tmp_path)
    ctx = engine.start()
    store.save(ctx)

    engine.set_provider_direct(ctx, "Empower")
    store.save(ctx)
    engine.submit_access(ctx, can_login=True)
    store.save(ctx)
    engine.submit_tax_type(ctx, "pre_tax")
    store.save(ctx)
    engine.choose_channel(ctx, JourneyChannel.PHONE)
    store.save(ctx)

    # --- simulated RAM purge: all we have left is the URL's journey id ------
    restored = store.load(ctx.journey_id)
    assert restored is not None
    assert restored.state == JourneyState.PHONE_IN_PROGRESS
    assert restored.provider == ctx.provider
    assert restored.tax_fund_type == "pre_tax"
    assert restored.channel == JourneyChannel.PHONE

    # journey continues from the restored context, not a fresh one
    engine.advance_step(restored, "done")
    store.save(restored)
    again = store.load(ctx.journey_id)
    assert again.step_index == restored.step_index


def _phone_enrichment(engine, provider):
    ctx = engine.start()
    engine.set_provider_direct(ctx, provider)
    engine.submit_access(ctx, can_login=True)
    ctx.customer_first_name, ctx.customer_last_name = "Avery", "Quinn"
    engine.submit_tax_type(ctx, "pre_tax")
    engine.choose_channel(ctx, JourneyChannel.PHONE)
    return build_enrichment(engine.knowledge, ctx, engine.render(ctx))


# Compliance invariant: a direct-rollover check is ALWAYS payable to
# "PensionBee FBO <user>". A check payable to the participant personally is a
# withdrawal/cashout — a different (taxable) transaction. Only the MAILING
# destination varies by provider.
ALL_PROVIDERS = ["Fidelity", "Empower", "Vanguard", "Voya",
                 "Alight Solutions", "Merrill Lynch", "Principal"]


def test_payee_is_always_fbo_never_participant(engine):
    from engine.customer_copy import is_fbo_payable_line

    for provider in ALL_PROVIDERS:
        enr = _phone_enrichment(engine, provider)
        payable = (enr.channel_context and enr.channel_context.check_payable) or ""
        assert payable == "PensionBee FBO Avery Quinn", provider
        assert is_fbo_payable_line(payable), provider
        assert "participant" not in payable.lower(), provider


def test_mailing_destination_varies_by_mechanism(engine):
    # Empower: check mails to the USER (who forwards); Voya/Vanguard: straight
    # to PensionBee's PO Box. Payee is identical either way.
    empower = _phone_enrichment(engine, "Empower")
    assert "address on file" in (empower.channel_context.mailing_address or "").lower()
    for provider in ("Voya", "Vanguard"):
        enr = _phone_enrichment(engine, provider)
        assert "PO Box 72" in (enr.channel_context.mailing_address or ""), provider


def test_resume_list_is_newest_first(engine, tmp_path):
    store = _store(tmp_path)
    a = engine.start()
    store.save(a)
    b = engine.start()
    store.save(b)
    rows = store.recent()
    assert rows[0]["journey_id"] == b.journey_id
    assert {r["journey_id"] for r in rows} >= {a.journey_id, b.journey_id}
```


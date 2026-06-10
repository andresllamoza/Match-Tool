#!/usr/bin/env python3
"""Three shell states at 390px — chrome must look identical."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COMPANION = ROOT.parent / "rollover-companion"
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(COMPANION))

import streamlit as st

st.markdown = lambda html, **_: None  # noqa: E731

from journey.engine_bridge import apply_action, current_view, get_engine, save_context
from ui.brand import inject_brand_css


def _css() -> str:
    captured: list[str] = []

    def _capture(html: str, **_kwargs) -> None:
        captured.append(html)

    st.markdown = _capture
    inject_brand_css()
    return captured[0]


def _rail(phase: str) -> str:
    phases = [("find", "Find"), ("access", "Access"), ("rollover", "Roll over"), ("track", "Track")]
    ids = [p[0] for p in phases]
    idx = ids.index(phase) if phase in ids else 0
    parts = ['<div class="pb-phase-bar">']
    for i, (_, label) in enumerate(phases):
        done = i < idx
        active = i == idx
        dot = "done" if done else ("active" if active else "")
        cls = "active" if active else ""
        parts.append(
            f'<div class="pb-phase {cls}"><div class="pb-phase-dot {dot}"></div>{label}</div>'
        )
    parts.append("</div>")
    return "".join(parts)


def _state_html(title: str, phase: str, body: str, footer_primary: str | None) -> str:
    footer = ""
    if footer_primary:
        footer = (
            '<div class="pb-shell-footer">'
            f'<button class="mock-primary">{footer_primary}</button>'
            '<p class="pb-shell-bk-copy">🐝 Talk to your BeeKeeper</p>'
            "</div>"
        )
    return (
        f"{_css()}"
        '<div class="main" style="max-width:390px;margin:0 auto;padding:16px;background:#FAF8F5;min-height:720px;">'
        '<div class="pb-shell-top">'
        '<span style="font-size:0.875rem">← Back</span>'
        '<p class="pb-shell-brand">🐝 PensionBee</p>'
        '<span style="font-size:0.875rem;text-align:right">Save & exit</span>'
        "</div>"
        f"{_rail(phase)}"
        f'<div class="pb-shell-body"><h1 class="pb-headline">{title}</h1>{body}</div>'
        f"{footer}"
        "</div>"
    )


def main() -> None:
    from playwright.sync_api import sync_playwright

    get_engine()
    out = ROOT.parent / "artifacts" / "screenshots"
    out.mkdir(parents=True, exist_ok=True)

    states = [
        ("access", "Can you log in?", "access", '<p class="pb-body">Choice cards in body.</p>', None),
        ("channel", "How would you like to start?", "rollover", "", None),
        (
            "phone-step",
            "Step 1 of 3",
            "rollover",
            '<p class="pb-body">Phone script content.</p>',
            "Done — next step",
        ),
    ]

    save_context(get_engine().start())
    apply_action({"type": "provider_direct", "provider": "Vanguard"})
    views = {
        "access": current_view(),
    }
    apply_action({"type": "access", "can_login": True})
    apply_action({"type": "tax_type", "tax_type": "pre_tax"})
    views["channel"] = current_view()
    apply_action({"type": "channel", "channel": "phone"})
    views["phone-step"] = current_view()

    with sync_playwright() as p:
        browser = p.chromium.launch()
        for slug, title, phase, body, primary in states:
            page = browser.new_page(viewport={"width": 390, "height": 800})
            page.set_content(_state_html(title, phase, body, primary), wait_until="networkidle")
            path = out / f"shell-{slug}-390px.png"
            page.screenshot(path=str(path), full_page=True)
            print(path)
        browser.close()


if __name__ == "__main__":
    main()

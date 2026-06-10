#!/usr/bin/env python3
"""Render Vanguard/Empower phone steps at 390px for acceptance screenshots."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import streamlit as st

st.markdown = lambda html, **_: None  # noqa: E731

from journey.engine_bridge import apply_action, current_view, get_engine, save_context
from ui.brand import inject_brand_css
from ui.channel_step import call_card, call_script_card, channel_step_header, routing_security_card


def _css() -> str:
    captured: list[str] = []

    def _capture(html: str, **_kwargs) -> None:
        captured.append(html)

    st.markdown = _capture
    inject_brand_css()
    return captured[0]


def _phone_view(provider: str):
    get_engine()
    save_context(get_engine().start())
    apply_action({"type": "provider_direct", "provider": provider})
    for action in (
        {"type": "access", "can_login": True},
        {"type": "tax_type", "tax_type": "traditional"},
        {"type": "channel", "channel": "phone"},
    ):
        apply_action(action)
    return current_view()


def _html_for(provider: str) -> str:
    view = _phone_view(provider)
    ctx = view.enrichment.channel_context
    assert ctx and ctx.phone
    parts = [
        _css(),
        '<div class="main" style="max-width:390px;margin:0 auto;padding:16px;background:#FAF8F5;">',
        '<span class="pb-badge-ok">✓ Verified Transfer Path</span>',
        channel_step_header(view.step_index, view.total_steps, provider, "by phone"),
        call_card(ctx.phone),
        call_script_card("phone", ctx.say_this),
    ]
    payable = ctx.check_payable or ""
    mail = ctx.mailing_address or view.enrichment.mailing_address
    if payable or mail:
        parts.append(f'<div class="pb-routing-panel">{routing_security_card(payable or None, mail or None)}</div>')
    parts.append(
        '<div class="pb-bk-handoff"><p>Prefer a person? Your BeeKeeper can take it from here.</p></div>'
    )
    parts.append("</div>")
    return "\n".join(parts)


def main() -> None:
    from playwright.sync_api import sync_playwright

    out_dir = ROOT.parent / "artifacts" / "screenshots"
    out_dir.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch()
        for provider in ("Vanguard", "Empower"):
            page = browser.new_page(viewport={"width": 390, "height": 900})
            page.set_content(_html_for(provider), wait_until="networkidle")
            slug = provider.lower()
            path = out_dir / f"{slug}-by-phone-390px.png"
            page.screenshot(path=str(path), full_page=True)
            print(path)
        browser.close()


if __name__ == "__main__":
    main()

"""HTML component helpers — PensionBee branded."""

from __future__ import annotations

import html

import streamlit as st

from discovery.models import ConfidenceTier, ValueReveal


def brand_header(subtitle: str = "Rollover Companion") -> None:
    st.markdown(
        f"""
<div class="pb-brand-row">
  <div class="pb-bee-icon" aria-hidden="true">🐝</div>
  <div>
    <div class="pb-wordmark">PensionBee</div>
    <div class="pb-product-tag">{html.escape(subtitle)}</div>
  </div>
</div>
        """,
        unsafe_allow_html=True,
    )


def brand_header_bar(subtitle: str = "Rollover Companion") -> None:
    """Unified top bar: logo left (restart button rendered in sibling column)."""
    st.markdown(
        f"""
<div class="pb-header-bar">
  <div class="pb-brand-row pb-brand-row--inline">
    <div class="pb-bee-icon" aria-hidden="true">🐝</div>
    <div>
      <div class="pb-wordmark">PensionBee</div>
      <div class="pb-product-tag">{html.escape(subtitle)}</div>
    </div>
  </div>
</div>
        """,
        unsafe_allow_html=True,
    )


def logo_mark() -> None:
    brand_header("Rollover Companion")


def headline(text: str, subcopy: str | None = None) -> None:
    st.markdown(f'<h1 class="pb-headline">{html.escape(text)}</h1>', unsafe_allow_html=True)
    if subcopy:
        st.markdown(f'<p class="pb-subcopy">{html.escape(subcopy)}</p>', unsafe_allow_html=True)


def promo_card(title: str, body: str) -> None:
    st.markdown(
        f'<div class="pb-promo"><strong>{html.escape(title)}</strong><br/>{html.escape(body)}</div>',
        unsafe_allow_html=True,
    )


def provider_result_card(provider: str, employer: str, tier: ConfidenceTier) -> None:
    tier_class = "" if tier == ConfidenceTier.HIGH else "medium"
    tier_label = {
        ConfidenceTier.HIGH: "High confidence match",
        ConfidenceTier.MEDIUM: "Likely match",
        ConfidenceTier.LOW: "We're still narrowing it down",
    }[tier]
    st.markdown(
        f"""
<div class="pb-card pb-card-hero">
  <span class="pb-confidence {tier_class}">{html.escape(tier_label)}</span>
  <p class="pb-provider-name">Your 401(k) is most likely with {html.escape(provider)}</p>
  <p class="pb-disclaimer">Based on public plan filings for {html.escape(employer)}.</p>
</div>
        """,
        unsafe_allow_html=True,
    )


def value_reveal_card(value: ValueReveal) -> None:
    st.markdown(
        f"""
<div class="pb-card">
  <div class="pb-match-label">Estimated 1% match when you roll over</div>
  <p class="pb-match-value">${value.match_low:,}–${value.match_high:,}</p>
  <p class="pb-disclaimer">{html.escape(value.disclaimer)}</p>
</div>
        """,
        unsafe_allow_html=True,
    )


def next_step_card(action: str) -> None:
    st.markdown(
        f"""
<div class="pb-card">
  <div class="pb-match-label">Your next step</div>
  <p class="pb-next-step">{html.escape(action)}</p>
</div>
        """,
        unsafe_allow_html=True,
    )


def warm_message(title: str, body: str) -> None:
    st.markdown(
        f"""
<div class="pb-warm">
  <strong>{html.escape(title)}</strong><br/>
  {html.escape(body)}
</div>
        """,
        unsafe_allow_html=True,
    )


def error_card() -> None:
    st.markdown(
        """
<div class="pb-error">
  <strong>Something went wrong on our side.</strong><br/>
  A BeeKeeper can help you find your old 401(k) — we're real humans, not a dead end.
</div>
        """,
        unsafe_allow_html=True,
    )


def format_balance_label(key: str) -> str:
    labels = {
        "0_10k": "Under $10,000",
        "10_50k": "$10,000 – $50,000",
        "50_100k": "$50,000 – $100,000",
        "100_250k": "$100,000 – $250,000",
        "250k_plus": "$250,000+",
    }
    return labels.get(key, key)

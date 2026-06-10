"""Premium channel HTML fragments — no absolute positioning."""

from __future__ import annotations

import html
import json

from engine.customer_copy import is_fbo_payable_line

_CHANNEL_INTROS = {
    "phone": "When speaking with your provider, use these exact phrases:",
    "online": "Follow these steps in your provider portal:",
    "forms": "Enter this on your distribution form:",
}

_CHANNEL_LABELS = {
    "phone": "Say this",
    "online": "Do this now",
    "forms": "Fill in this field",
}

def _copy_onclick(value: str) -> str:
    payload = json.dumps(value)
    return (
        "(function(b,t){navigator.clipboard.writeText(t);"
        "b.textContent='\\u2713';b.classList.add('pb-copy-success');"
        "setTimeout(function(){b.textContent='Copy';b.classList.remove('pb-copy-success');},2000);})(this,"
        + payload
        + ")"
    )


def _esc(text: str) -> str:
    return html.escape(text, quote=True)


def channel_step_header(step_index: int, total_steps: int, provider: str, channel_label: str) -> str:
    progress = round(((step_index + 1) / total_steps) * 100) if total_steps > 0 else 0
    subtitle = f" · {_esc(provider)} {_esc(channel_label)}".strip() if provider else ""
    return (
        f'<header class="pb-channel-header">'
        f'<p class="pb-channel-step-id">Step {step_index + 1} of {total_steps}{subtitle}</p>'
        f'<div class="pb-channel-track" role="progressbar" '
        f'aria-valuenow="{step_index + 1}" aria-valuemin="1" aria-valuemax="{total_steps}">'
        f'<div class="pb-channel-track-fill" style="width:{progress}%"></div>'
        f"</div></header>"
    )


def call_script_card(channel: str, script: str, *, field_label: str | None = None) -> str:
    intro = _CHANNEL_INTROS.get(channel, "")
    label = field_label if channel == "forms" and field_label else _CHANNEL_LABELS.get(channel, "")
    quote = f"&ldquo;{_esc(script)}&rdquo;" if channel == "phone" else _esc(script)
    intro_html = f'<p class="pb-call-intro">{_esc(intro)}</p>' if intro else ""
    return (
        f'<div class="pb-call-script">'
        f"{intro_html}"
        f'<p class="pb-channel-kicker">{_esc(label)}</p>'
        f'<p class="pb-channel-action">{quote}</p>'
        f"</div>"
    )


def _security_row(label: str, value: str, *, prominent: bool = False) -> str:
    onclick = _copy_onclick(value)
    value_cls = "pb-security-value pb-security-value--prominent" if prominent else "pb-security-value"
    return (
        f'<div class="pb-security-row">'
        f'<div class="pb-security-row-body">'
        f'<p class="pb-security-label">{_esc(label)}</p>'
        f'<p class="{value_cls}">{_esc(value)}</p>'
        f"</div>"
        f'<button type="button" class="pb-copy-micro" onclick="{onclick}">Copy</button>'
        f"</div>"
    )


def routing_security_card(payee_line: str | None, mailing_address: str | None) -> str:
    if not payee_line and not mailing_address:
        return ""
    show_fbo = is_fbo_payable_line(payee_line or "")
    parts = ['<div class="pb-routing-security" role="region" aria-label="Check routing security">']
    if show_fbo:
        parts.append(
            '<div class="pb-fbo-header">'
            '<span class="pb-fbo-lock" aria-hidden="true">🔒</span>'
            "<div>"
            '<p class="pb-fbo-kicker">Critical — check payable to</p>'
            '<p class="pb-fbo-sub">Use these exact details or your rollover may be rejected.</p>'
            "</div></div>"
        )
    parts.append('<div class="pb-security-compound">')
    if payee_line:
        label = "Check payable to" if show_fbo else "Payee name"
        parts.append(_security_row(label, payee_line, prominent=show_fbo))
    if mailing_address:
        parts.append(_security_row("Mailing address", mailing_address))
    parts.append("</div></div>")
    return "".join(parts)


def phone_routing_intro() -> str:
    return (
        '<div class="pb-routing-intro">'
        '<p class="pb-routing-kicker">Check routing</p>'
        "<p class=\"pb-routing-body\">When the rep asks how to make the check payable, "
        "use the exact payee line below.</p></div>"
    )


def agent_custodian_note(check_destination: str, *, forward_step_required: bool) -> str:
    if not check_destination:
        return ""
    suffix = (
        " — participant-forward pattern; pre-empt prepaid envelope expectations."
        if forward_step_required
        else " — direct-to-custodian mailing supported."
    )
    return (
        f'<div class="pb-agent-note">'
        f'<p class="pb-agent-note-kicker">BeeKeeper — routing rationale</p>'
        f'<p class="pb-agent-note-body"><strong>{_esc(check_destination)}</strong>{_esc(suffix)}</p>'
        f"</div>"
    )

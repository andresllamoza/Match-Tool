"""Premium HTML fragments for in-channel rollover steps (Streamlit)."""

from __future__ import annotations

import html
import json

from engine.customer_copy import is_fbo_payable_line as _is_fbo_payable_line

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

_COPY_FEEDBACK_JS = (
    "(function(b,t){navigator.clipboard.writeText(t);"
    "b.textContent='\\u2713';b.classList.add('pb-copy-success');"
    "setTimeout(function(){b.textContent='Copy';b.classList.remove('pb-copy-success');},2000);})(this,{payload})"
)


def _esc(text: str) -> str:
    return html.escape(text, quote=True)


def channel_step_header(
    step_index: int,
    total_steps: int,
    provider: str,
    channel_label: str,
) -> str:
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
    payload = json.dumps(value)
    onclick = _COPY_FEEDBACK_JS.format(payload=payload)
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


def routing_security_card(
    payee_line: str | None,
    mailing_address: str | None,
) -> str:
    has_payee = bool(payee_line)
    has_mail = bool(mailing_address)
    if not has_payee and not has_mail:
        return ""

    show_fbo = _is_fbo_payable_line(payee_line or "")
    parts: list[str] = ['<div class="pb-routing-security" role="region" aria-label="Check routing security">']

    if show_fbo:
        parts.append(
            '<div class="pb-fbo-header pb-fbo-header--card">'
            '<span class="pb-fbo-lock" aria-hidden="true">🔒</span>'
            "<div>"
            '<p class="pb-fbo-kicker">Make the check payable to — exactly</p>'
            '<p class="pb-fbo-sub">If a check ever arrives payable to <strong>you personally</strong>, '
            "don't cash it — that's a withdrawal, not a rollover. Your BeeKeeper will fix it.</p>"
            "</div></div>"
        )

    compound_cls = "pb-security-compound pb-security-compound--fbo" if show_fbo else "pb-security-compound"
    parts.append(f'<div class="{compound_cls}">')
    if has_payee:
        label = "Check payable to" if show_fbo else "Payee name"
        parts.append(_security_row(label, payee_line or "", prominent=show_fbo))
    if has_mail:
        parts.append(_security_row("Mailing address", mailing_address or ""))
    parts.append("</div></div>")
    return "".join(parts)


def phone_routing_intro() -> str:
    return (
        '<div class="pb-routing-intro">'
        '<p class="pb-routing-kicker">Check routing</p>'
        "<p class=\"pb-routing-body\">When the rep asks how to make the check payable, "
        "use the exact payee line below — then confirm where they will mail it.</p>"
        "</div>"
    )


def financial_copy_field(label: str, value: str, field_id: str) -> str:
    payload = json.dumps(value)
    onclick = _COPY_FEEDBACK_JS.format(payload=payload)
    return (
        f'<div class="pb-financial-standalone" id="{field_id}">'
        f'<div class="pb-security-row-body">'
        f'<p class="pb-security-label">{_esc(label)}</p>'
        f'<p class="pb-security-value">{_esc(value)}</p>'
        f"</div>"
        f'<button type="button" class="pb-copy-micro" onclick="{onclick}">Copy</button>'
        f"</div>"
    )


def agent_custodian_note(
    check_destination: str,
    *,
    forward_step_required: bool,
    mechanism: str | None = None,
) -> str:
    if not check_destination:
        return ""
    if forward_step_required:
        mech = (mechanism or "unknown").replace("_", " ")
        rationale = (
            f" — participant-forward pattern required ({mech}). "
            "Pre-empt with prepaid envelope expectations before the user initiates."
        )
    else:
        rationale = (
            " — this provider supports direct-to-custodian mailing. "
            "Do not coach participant forwarding unless the rep insists on mailing to the member first."
        )
    return (
        f'<div class="pb-agent-note">'
        f'<p class="pb-agent-note-kicker">BeeKeeper — routing rationale</p>'
        f'<p class="pb-agent-note-body">'
        f"<strong>{_esc(check_destination)}</strong>{_esc(rationale)}"
        f"</p></div>"
    )

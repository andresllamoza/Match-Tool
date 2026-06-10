"""Premium HTML fragments for in-channel rollover steps (Streamlit)."""

from __future__ import annotations

import html
import json


def _is_fbo_payable_line(text: str) -> bool:
    lower = text.lower()
    return "fbo" in lower and "pensionbee" in lower

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


def fbo_security_card(payable_line: str) -> str:
    if not payable_line or not _is_fbo_payable_line(payable_line):
        return ""
    safe = _esc(payable_line)
    payload = json.dumps(payable_line)
    return (
        f'<div class="pb-fbo-card" role="region" aria-label="Check payable-to security instruction">'
        f'<div class="pb-fbo-card-top">'
        f'<div class="pb-fbo-lock-row">'
        f'<span class="pb-fbo-lock" aria-hidden="true">🔒</span>'
        f"<div>"
        f'<p class="pb-fbo-kicker">Critical — check payable to</p>'
        f'<p class="pb-fbo-sub">Use this exact wording or your rollover may be rejected.</p>'
        f"</div></div>"
        f'<button type="button" class="pb-fbo-copy" '
        f"onclick=\"navigator.clipboard.writeText({payload})\">Copy</button>"
        f"</div>"
        f'<p class="pb-fbo-line">{safe}</p>'
        f"</div>"
    )


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
    return (
        f'<div class="pb-financial-field">'
        f'<p class="pb-financial-label">{_esc(label)}</p>'
        f'<div class="pb-financial-row">'
        f'<p class="pb-financial-value" id="{field_id}">{_esc(value)}</p>'
        f'<button type="button" class="pb-financial-copy" '
        f"onclick=\"navigator.clipboard.writeText({payload})\">Copy</button>"
        f"</div></div>"
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

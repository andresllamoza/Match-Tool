from __future__ import annotations

from .journey import JourneyEngine
from .models import JourneyChannel, JourneyState


def walk_employer(
    engine: JourneyEngine,
    employer: str,
    channel: JourneyChannel | None = None,
    *,
    verbose: bool = True,
) -> dict:
    """Headless end-to-end walk for demos, CLI, and tests."""
    ctx = engine.start()
    trail: list[dict] = []

    def record(label: str, screen) -> None:
        trail.append(
            {
                "label": label,
                "state": ctx.state.value,
                "headline": screen.headline,
                "body": screen.body,
                "has_reconstructed_content": screen.has_reconstructed_content,
                "guidance": [g.text for g in screen.guidance],
            }
        )
        if verbose:
            print(f"→ {ctx.state.value} ({label})")

    screen = engine.lookup_employer(ctx, employer)
    record("lookup", screen)

    if ctx.state == JourneyState.PROVIDER_UNKNOWN:
        return _summary(ctx, employer, trail)

    screen = engine.submit_access(ctx, can_login=True)
    record("access", screen)

    screen = engine.submit_tax_type(ctx, "pre_tax")
    record("tax_type", screen)

    ch = channel or JourneyChannel.ONLINE
    screen = engine.choose_channel(ctx, ch)
    record("channel", screen)

    while ctx.state in {
        JourneyState.ONLINE_IN_PROGRESS,
        JourneyState.PHONE_IN_PROGRESS,
        JourneyState.FORMS_IN_PROGRESS,
    }:
        screen = engine.render(ctx)
        record(f"step_{ctx.step_index + 1}", screen)
        engine.advance_step(ctx, "done")

    screen = engine.render(ctx)
    record("channel_complete", screen)

    if ctx.state == JourneyState.INITIATED:
        screen = engine.confirm_in_flight(ctx)
        record("in_flight", screen)
        screen = engine.mark_complete(ctx)
        record("complete", screen)

    return _summary(ctx, employer, trail)


def _summary(ctx, employer: str, trail: list[dict]) -> dict:
    all_text = " ".join(
        t["body"] + " " + " ".join(t.get("guidance", [])) for t in trail
    )
    return {
        "employer": employer,
        "state": ctx.state.value,
        "provider": ctx.provider,
        "uncovered_provider": ctx.uncovered_provider,
        "channel": ctx.channel.value if ctx.channel else None,
        "stuck_count": ctx.stuck_count,
        "trail": trail,
        "rendered_text": all_text,
        "has_reconstructed_content": any(t["has_reconstructed_content"] for t in trail),
    }

"""Every provider must support a complete journey through all channels."""

import pytest

from engine.journey import JourneyEngine
from engine.models import JourneyChannel, JourneyState


@pytest.mark.parametrize(
    "provider",
    ["Fidelity", "Empower", "Vanguard", "Voya", "Alight Solutions", "Merrill Lynch", "Principal"],
)
def test_complete_journey_all_channels(engine: JourneyEngine, provider: str):
    for channel in JourneyChannel:
        ctx = engine.start()
        engine.set_provider_direct(ctx, provider)
        engine.submit_access(ctx, can_login=True)
        engine.submit_tax_type(ctx, "pre_tax")
        engine.choose_channel(ctx, channel)
        in_progress = {
            JourneyChannel.ONLINE: JourneyState.ONLINE_IN_PROGRESS,
            JourneyChannel.PHONE: JourneyState.PHONE_IN_PROGRESS,
            JourneyChannel.FORMS: JourneyState.FORMS_IN_PROGRESS,
        }[channel]
        assert ctx.state == in_progress.value or ctx.state == in_progress
        while ctx.state in {
            JourneyState.ONLINE_IN_PROGRESS,
            JourneyState.PHONE_IN_PROGRESS,
            JourneyState.FORMS_IN_PROGRESS,
        }:
            engine.advance_step(ctx, "done")
        assert ctx.state == JourneyState.INITIATED
        engine.confirm_in_flight(ctx)
        engine.mark_complete(ctx)
        assert ctx.state == JourneyState.COMPLETE

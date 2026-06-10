from pathlib import Path

from engine.enrichment import build_enrichment
from engine.journey import JourneyEngine
from engine.models import JourneyChannel
from engine.payee import resolve_check_payable

_BANNED = "Participant" + " name"


def test_grep_participant_name_zero_in_repo():
    root = Path(__file__).resolve().parents[2]
    hits = []
    for folder in ("rollover-companion", "discovery-front-door"):
        for path in (root / folder).rglob("*"):
            if path.suffix not in {".md", ".py", ".tsx", ".ts"}:
                continue
            if path.name == Path(__file__).name:
                continue
            text = path.read_text(encoding="utf-8", errors="ignore")
            if _BANNED in text:
                hits.append(str(path.relative_to(root)))
    assert hits == [], f"Found banned payee string in: {hits}"


def test_empower_phone_payable_is_fbo(engine):
    ctx = engine.start()
    ctx.participant_name = "Jordan Lee"
    engine.set_provider_direct(ctx, "Empower")
    engine.submit_access(ctx, can_login=True)
    engine.submit_tax_type(ctx, "pre_tax")
    engine.choose_channel(ctx, JourneyChannel.PHONE)
    screen = engine.render(ctx)
    enrichment = build_enrichment(engine.knowledge, ctx, screen)
    assert enrichment.channel_context is not None
    assert enrichment.channel_context.check_payable == "PensionBee FBO Jordan Lee"
    assert _BANNED not in (enrichment.channel_context.check_payable or "")


def test_resolve_check_payable_default_name(engine):
    ctx = engine.start()
    payable = resolve_check_payable(engine.knowledge, ctx)
    assert payable == "PensionBee FBO Jordan Rivera"

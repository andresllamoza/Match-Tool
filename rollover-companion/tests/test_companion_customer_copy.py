from engine.knowledge import KnowledgeBase
from engine.models import FunnelStage

OPS_PHRASES = ("Guide the user", "Have the user", "BeeKeeper tracks", "Confirm Empower mails")


def test_every_provider_has_customer_messages():
    kb = KnowledgeBase.from_dir()
    for name in kb.list_providers():
        pb = kb.get(name)
        for stage in FunnelStage:
            na = pb.next_actions[stage]
            assert na.customer_message.strip(), f"{name}/{stage}: missing customer_message"
            assert not any(p in na.customer_message for p in OPS_PHRASES), (
                f"{name}/{stage}: customer_message contains ops phrasing"
            )


def test_empower_customer_message_mentions_check_to_user():
    kb = KnowledgeBase.from_dir()
    na = kb.get("Empower").next_actions[FunnelStage.PROVIDER_IDENTIFIED]
    assert "home address" in na.customer_message.lower() or "mail" in na.customer_message.lower()
    assert "Guide the user" in na.action

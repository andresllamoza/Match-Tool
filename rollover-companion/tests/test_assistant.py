from engine.assistant import ScopedAssistant
from engine.models import JourneyState


def test_in_scope_mailing_address(knowledge):
    assistant = ScopedAssistant(knowledge)
    result = assistant.answer(
        "What is the mailing address for the check?",
        JourneyState.FORMS_IN_PROGRESS,
        "Vanguard",
    )
    assert result["in_scope"] is True
    assert "PO Box 72" in result["answer"]


def test_refuses_out_of_scope(knowledge):
    assistant = ScopedAssistant(knowledge)
    result = assistant.answer(
        "What's the weather in New York?",
        JourneyState.ONLINE_IN_PROGRESS,
        "Fidelity",
    )
    assert result["in_scope"] is False
    assert result["escalation_suggested"] is True
    assert "BeeKeeper" in result["answer"]


def test_refuses_fabricated_balance(knowledge):
    assistant = ScopedAssistant(knowledge)
    result = assistant.answer(
        "My balance is $50,000 — what should I do?",
        JourneyState.PROVIDER_IDENTIFIED,
        "Empower",
    )
    assert result["in_scope"] is False

from discovery.add_transfer import ACCOUNT_TYPE_401K, run_add_transfer
from discovery.adapters.advizorpro import AdvizorProAdapter
from discovery.knowledge_bridge import KnowledgeBridge
from discovery.models import ConfidenceTier
from discovery.synthetic import build_adapters


def test_add_transfer_happy_path():
    _, matcher = build_adapters()
    knowledge = KnowledgeBridge.from_dir()
    result = run_add_transfer("Amazon.com Services LLC", ACCOUNT_TYPE_401K, matcher, knowledge)
    assert result.provider == "Fidelity"
    assert result.confidence_tier == ConfidenceTier.HIGH
    assert result.next_step is not None
    assert "rollover" in result.next_step.action.lower() or "Express" in result.next_step.action


def test_add_transfer_low_confidence_question():
    _, matcher = build_adapters()
    knowledge = KnowledgeBridge.from_dir()
    result = run_add_transfer("Northwind Traders", ACCOUNT_TYPE_401K, matcher, knowledge)
    assert result.confidence_tier == ConfidenceTier.LOW
    assert result.disambiguation_question is not None


def test_add_transfer_uses_advizorpro_adapter():
    adv = AdvizorProAdapter()
    knowledge = KnowledgeBridge.from_dir()
    result = run_add_transfer("Frostline Analytics", ACCOUNT_TYPE_401K, adv, knowledge)
    assert result.provider == "Fidelity"


def test_unsupported_account_type():
    _, matcher = build_adapters()
    knowledge = KnowledgeBridge.from_dir()
    result = run_add_transfer("Amazon.com Services LLC", "IRA", matcher, knowledge)
    assert result.provider is None
    assert "401(k)" in result.disambiguation_question

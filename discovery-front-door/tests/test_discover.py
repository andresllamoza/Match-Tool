from discovery.discover import discover_employer
from discovery.models import ConfidenceTier
from discovery.synthetic import build_adapters


def test_high_confidence_amazon():
    adv, matcher = build_adapters()
    result = discover_employer("Amazon.com Services LLC", matcher, adv)
    assert result.resolved_provider == "Fidelity"
    assert result.confidence_tier == ConfidenceTier.HIGH


def test_low_confidence_returns_one_question():
    adv, matcher = build_adapters()
    result = discover_employer("Northwind Traders", matcher, adv)
    assert result.confidence_tier == ConfidenceTier.LOW
    assert result.disambiguation_question is not None
    assert "state" in result.disambiguation_question.lower()
    assert "?" in result.disambiguation_question


def test_disambiguation_is_single_question_not_list():
    adv, matcher = build_adapters()
    result = discover_employer("Pinnacle Sports LLC", matcher, adv)
    assert result.disambiguation_question.count("?") == 1


def test_matcher_only_employer():
    adv, matcher = build_adapters()
    result = discover_employer("Acme Robotics Inc", matcher, adv)
    assert result.resolved_provider == "Empower"
    assert result.matcher_result.provider == "Empower"
    assert result.advizorpro_result.provider is None

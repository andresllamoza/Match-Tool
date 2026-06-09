from engine.lookup import LookupService
from engine.models import ConfidenceTier


def test_high_confidence_agreement(lookup_service: LookupService):
    outcome = lookup_service.lookup("Amazon.com Services LLC")
    assert outcome.resolved_provider == "Fidelity"
    assert outcome.confidence_tier == ConfidenceTier.HIGH
    assert outcome.agreement is True


def test_disagreement_requires_disambiguation(lookup_service: LookupService):
    outcome = lookup_service.lookup("Jetstream Airlines")
    assert outcome.disambiguation_question is not None
    assert set(outcome.disambiguation_options) == {"Empower", "Fidelity"}
    assert outcome.resolved_provider is None


def test_low_confidence_no_match(lookup_service: LookupService):
    outcome = lookup_service.lookup("Northwind Traders")
    assert outcome.confidence_tier == ConfidenceTier.LOW
    assert outcome.resolved_provider is None


def test_target_maps_to_alight_solutions(lookup_service: LookupService):
    outcome = lookup_service.lookup("Target Corporation")
    assert outcome.resolved_provider is None
    assert outcome.uncovered_provider == "Alight Solutions"
    assert outcome.confidence_tier == ConfidenceTier.HIGH
    assert outcome.agreement is True


def test_target_alias_maps_to_alight(lookup_service: LookupService):
    outcome = lookup_service.lookup("Target")
    assert outcome.uncovered_provider == "Alight Solutions"


def test_comparison_event_every_lookup(lookup_service, tmp_logs):
    lookup_service.lookup("Target Corporation")
    lookup_service.lookup("Unknown Corp XYZ")
    lines = tmp_logs.comparison_path.read_text().strip().splitlines()
    assert len(lines) == 2

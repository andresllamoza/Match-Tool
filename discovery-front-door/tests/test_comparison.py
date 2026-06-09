from discovery.comparison import comparison_from_discovery, summarize
from discovery.discover import discover_employer
from discovery.synthetic import SYNTHETIC_EMPLOYERS, build_adapters


def test_agreement_event():
    adv, matcher = build_adapters()
    disc = discover_employer("Walmart Inc", matcher, adv)
    event = comparison_from_discovery(disc)
    assert event.agreement is True
    assert event.matcher_provider == "Fidelity"


def test_summarize_synthetic_harness_stats():
    adv, matcher = build_adapters()
    events = [
        comparison_from_discovery(discover_employer(row["employer"], matcher, adv))
        for row in SYNTHETIC_EMPLOYERS
    ]
    stats = summarize(events)
    assert stats["n"] == 30
    assert stats["agreement_rate"] == 0.57
    assert stats["matcher_coverage"] == 0.8
    assert stats["advizorpro_coverage"] == 0.77
    assert stats["matcher_only"] == 5
    assert stats["advizorpro_only"] == 4


def test_thirty_synthetic_employers():
    assert len(SYNTHETIC_EMPLOYERS) == 30

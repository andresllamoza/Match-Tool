from discovery.flow import DiscoveryFlow
from discovery.knowledge_bridge import KnowledgeBridge
from discovery.models import BalanceRange
from discovery.synthetic import build_adapters


def test_full_flow_outcome():
    adv, matcher = build_adapters()
    flow = DiscoveryFlow(adv, matcher, KnowledgeBridge.from_dir())
    outcome = flow.run("Target Corporation", BalanceRange.R_100_250K)
    assert outcome.discovery.resolved_provider == "Alight Solutions"
    assert outcome.value_reveal is not None
    assert outcome.value_reveal.match_low == 1000
    assert outcome.next_step is not None
    assert outcome.next_step.action


def test_flow_without_balance_skips_value_reveal():
    adv, matcher = build_adapters()
    flow = DiscoveryFlow(adv, matcher, KnowledgeBridge.from_dir())
    outcome = flow.run("UPS Inc")
    assert outcome.value_reveal is None

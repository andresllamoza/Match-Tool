from discovery.adapters.advizorpro import AdvizorProAdapter
from discovery.adapters.matcher5500 import Local5500Adapter


def test_advizorpro_stub_lookup():
    adv = AdvizorProAdapter()
    result = adv.lookup("Granite Ridge Staffing")
    assert result.source == "advizorpro"
    assert result.provider == "Empower"


def test_matcher_synthetic_lookup():
    matcher = Local5500Adapter.from_synthetic()
    result = matcher.lookup("Echo Valley Health")
    assert result.provider == "Fidelity"


def test_matcher_miss():
    matcher = Local5500Adapter.from_synthetic()
    result = matcher.lookup("Totally Unknown LLC")
    assert result.provider is None

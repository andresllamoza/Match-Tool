from discovery.ports import ProviderLookupPort
from discovery.synthetic import build_adapters


def test_adapters_implement_port():
    adv, matcher = build_adapters()
    assert hasattr(adv, "lookup") and hasattr(adv, "name")
    assert hasattr(matcher, "lookup") and hasattr(matcher, "name")


def test_port_is_structural():
    adv, _ = build_adapters()

    def use_port(port: ProviderLookupPort):
        return port.lookup("Walmart Inc").provider

    assert use_port(adv) == "Fidelity"

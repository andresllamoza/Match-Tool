from discovery.knowledge_bridge import KnowledgeBridge


def test_bridge_returns_fidelity_next_step():
    bridge = KnowledgeBridge.from_dir()
    step = bridge.next_step_for_provider("Fidelity")
    assert step is not None
    assert step.owner == "user"
    assert "Express rollover" in step.action or "rollover" in step.action.lower()


def test_bridge_unknown_provider():
    bridge = KnowledgeBridge.from_dir()
    assert bridge.next_step_for_provider("Unknown Corp") is None

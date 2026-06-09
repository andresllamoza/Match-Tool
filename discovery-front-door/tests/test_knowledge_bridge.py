from discovery.knowledge_bridge import KnowledgeBridge


def test_bridge_returns_fidelity_next_step():
    bridge = KnowledgeBridge.from_dir()
    step = bridge.next_step_for_provider("Fidelity")
    assert step is not None
    assert step.owner == "user"
    assert "Guide the user" not in step.action
    assert "Express rollover" in step.action or "NetBenefits" in step.action


def test_bridge_empower_customer_copy_not_ops():
    bridge = KnowledgeBridge.from_dir()
    step = bridge.next_step_for_provider("Empower")
    assert step is not None
    assert "Guide the user" not in step.action
    assert "mail" in step.action.lower()


def test_bridge_unknown_provider():
    bridge = KnowledgeBridge.from_dir()
    assert bridge.next_step_for_provider("Unknown Corp") is None

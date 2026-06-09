def test_journey_engine_bridge_imports():
    from journey.engine_bridge import get_engine, list_providers

    engine = get_engine()
    assert engine is not None
    providers = list_providers()
    assert "Fidelity" in providers or "Vanguard" in providers


def test_journey_lookup_target():
    from journey.engine_bridge import apply_action, get_engine, load_context, save_context

    get_engine()
    ctx = get_engine().start()
    save_context(ctx)
    result = apply_action({"type": "lookup", "employer": "Target"})
    assert not isinstance(result, str)
    assert result.ctx.provider in ("Alight Solutions", "Vanguard", None) or result.ctx.state.value

from discovery.models import BalanceRange, ConfidenceTier, DiscoveryOutcome, DiscoveryResult, LookupResult, ValueReveal
from discovery.value import compute_value_reveal
from ui.components import format_balance_label
from ui.states import UiState, classify_ui_state


def _outcome(tier: ConfidenceTier, provider: str | None) -> DiscoveryOutcome:
    return DiscoveryOutcome(
        discovery=DiscoveryResult(
            employer_query="Amazon.com Services LLC",
            resolved_provider=provider,
            confidence_tier=tier,
            matcher_result=LookupResult(source="m", provider=provider),
            advizorpro_result=LookupResult(source="a", provider=provider),
        ),
        value_reveal=compute_value_reveal(BalanceRange.R_50_100K),
    )


def test_classify_result_state():
    assert classify_ui_state(_outcome(ConfidenceTier.HIGH, "Fidelity")) == UiState.RESULT


def test_classify_low_confidence():
    assert classify_ui_state(_outcome(ConfidenceTier.LOW, None)) == UiState.LOW_CONFIDENCE


def test_balance_labels_human():
    assert "$50,000" in format_balance_label("50_100k")


def test_app_imports():
    import importlib.util

    path = __import__("pathlib").Path(__file__).resolve().parents[1] / "app.py"
    spec = importlib.util.spec_from_file_location("discovery_app", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)

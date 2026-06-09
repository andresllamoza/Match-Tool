from pathlib import Path

from engine.funnel import load_funnel_summary


def test_empty_funnel():
    summary = load_funnel_summary(Path("/nonexistent/path.jsonl"))
    assert summary.total_journeys == 0

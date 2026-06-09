import json
import os
from pathlib import Path

from engine import FunnelStage, RolloverEngine


def test_log_invocation_writes_jsonl(tmp_path, monkeypatch):
    log_file = tmp_path / "invocations.jsonl"
    monkeypatch.setenv("ROLLOVER_LOG_PATH", str(log_file))
    eng = RolloverEngine()
    eng.recommend("Fidelity", FunnelStage.PROVIDER_IDENTIFIED)
    lines = log_file.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 1
    record = json.loads(lines[0])
    assert record["provider"] == "Fidelity"
    assert record["funnel_stage"] == "provider_identified"
    assert "outcome" in record
    assert "ts" in record

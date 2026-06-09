#!/usr/bin/env python3
"""CLI for the rollover playbook engine."""

from __future__ import annotations

import argparse
import json
import sys

from engine import FunnelStage, RolloverEngine


def _parse_flags(values: list[str]) -> dict[str, bool]:
    return {v: True for v in values}


def _print_response(resp) -> None:
    print(f"Provider: {resp.provider}")
    print(f"Stage: {resp.funnel_stage.value}")
    print(f"Next action ({resp.next_action.owner.value}): {resp.next_action.action}")
    print(f"Mechanism: {resp.mechanism.value}")
    print(f"Check destination: {resp.check_destination}")
    if resp.active_escalations:
        print("Active escalations:", [e.flag for e in resp.active_escalations])
    if resp.active_failure_modes:
        print("Active failure modes:", [f.flag for f in resp.active_failure_modes])
    if resp.provenance_warning:
        print(f"⚠ {resp.provenance_warning}")
    if resp.sla_gap:
        print(f"SLA: not quantified — {resp.sla_note}")


def run_demo(eng: RolloverEngine) -> None:
    cases = [
        ("Fidelity", FunnelStage.PROVIDER_IDENTIFIED, {}),
        ("Empower", FunnelStage.PROVIDER_IDENTIFIED, {"notary_required": True}),
        ("Voya", FunnelStage.ROLLOVER_INITIATED, {"phone_verify_required": True}),
    ]
    for provider, stage, flags in cases:
        print("=" * 60)
        resp = eng.recommend(provider, stage, flags)
        _print_response(resp)
        print()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Rollover playbook decision engine")
    parser.add_argument("--demo", action="store_true", help="Run three contrasting mechanisms")
    parser.add_argument("--provider", default="Fidelity")
    parser.add_argument(
        "--stage",
        default="provider_identified",
        choices=[s.value for s in FunnelStage],
    )
    parser.add_argument("--flag", action="append", default=[], help="Active escalation/failure flag")
    parser.add_argument("--json", action="store_true", help="Emit JSON")
    args = parser.parse_args(argv)

    eng = RolloverEngine()
    if args.demo:
        run_demo(eng)
        return 0

    stage = FunnelStage(args.stage)
    flags = _parse_flags(args.flag)
    resp = eng.recommend(args.provider, stage, flags)
    if args.json:
        print(resp.model_dump_json(indent=2))
    else:
        _print_response(resp)
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""CLI for discovery front door flows."""

from __future__ import annotations

import argparse
import sys

from discovery.comparison import comparison_from_discovery, summarize
from discovery.discover import discover_employer
from discovery.flow import DiscoveryFlow
from discovery.knowledge_bridge import KnowledgeBridge
from discovery.models import BalanceRange
from discovery.synthetic import SYNTHETIC_EMPLOYERS, build_adapters


def run_compare() -> None:
    adv, matcher = build_adapters()
    events = []
    for row in SYNTHETIC_EMPLOYERS:
        disc = discover_employer(row["employer"], matcher, adv)
        events.append(comparison_from_discovery(disc))
    stats = summarize(events)
    print(f"MATCHER vs ADVIZORPRO  (n={stats['n']} synthetic employers)")
    print(f"  agreement rate      : {int(stats['agreement_rate'] * 100)}%")
    print(f"  matcher coverage    : {int(stats['matcher_coverage'] * 100)}%      "
          f"advizorpro coverage : {int(stats['advizorpro_coverage'] * 100)}%")
    print(f"  matcher ONLY (wins) : {stats['matcher_only']}        "
          f"<- free 5500 found what the paid DB missed")
    print(f"  advizorpro ONLY     : {stats['advizorpro_only']}        "
          f"<- remaining gap to close")


def run_demo() -> None:
    adv, matcher = build_adapters()
    flow = DiscoveryFlow(adv, matcher, KnowledgeBridge.from_dir())
    outcome = flow.run("Amazon.com Services LLC", BalanceRange.R_50_100K)
    print("Employer:", outcome.discovery.employer_query)
    print("Provider:", outcome.discovery.resolved_provider)
    print("Confidence:", outcome.discovery.confidence_tier.value)
    if outcome.value_reveal:
        print(f"Match: ${outcome.value_reveal.match_low:,}–${outcome.value_reveal.match_high:,}")
        print(outcome.value_reveal.disclaimer)
    if outcome.next_step:
        print("Next step:", outcome.next_step.action)
    print()
    run_compare()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Discovery front door CLI")
    parser.add_argument("--demo", action="store_true")
    parser.add_argument("--compare", action="store_true")
    parser.add_argument("--discover", metavar="EMPLOYER")
    parser.add_argument("--balance-range", default="50_100k", choices=[b.value for b in BalanceRange])
    args = parser.parse_args(argv)

    if args.compare:
        run_compare()
        return 0
    if args.demo:
        run_demo()
        return 0
    if args.discover:
        adv, matcher = build_adapters()
        flow = DiscoveryFlow(adv, matcher, KnowledgeBridge.from_dir())
        outcome = flow.run(args.discover, BalanceRange(args.balance_range))
        print(outcome.model_dump_json(indent=2))
        return 0

    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())

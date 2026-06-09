#!/usr/bin/env python3
"""Rollover Companion CLI — demo, lookup, walkthroughs, funnel analytics."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict

from engine import JourneyEngine, ScopedAssistant
from engine.data_needed import report as data_needed_report
from engine.funnel import load_funnel_summary
from engine.journey import valid_transitions
from engine.models import JourneyChannel
from engine.walk import walk_employer


def _default_engine() -> JourneyEngine:
    return JourneyEngine()


def cmd_demo(_: argparse.Namespace) -> int:
    engine = _default_engine()
    ctx = engine.start()
    screen = engine.render(ctx)
    print(f"State: {screen.state.value}")
    print(f"Headline: {screen.headline}")
    print(f"Body:\n{screen.body}")
    print("Primary:", screen.primary_action)
    print("Secondary:", screen.secondary_actions)
    return 0


def cmd_lookup(args: argparse.Namespace) -> int:
    engine = _default_engine()
    outcome = engine.lookup_service.lookup(args.employer)
    print(
        json.dumps(
            {
                "employer": outcome.employer_query,
                "provider": outcome.resolved_provider,
                "uncovered_provider": outcome.uncovered_provider,
                "confidence_tier": outcome.confidence_tier.value,
                "agreement": outcome.agreement,
                "disambiguation_question": outcome.disambiguation_question,
            },
            indent=2,
        )
    )
    return 0


def cmd_transitions(_: argparse.Namespace) -> int:
    by_state: dict[str, list[str]] = defaultdict(list)
    for src, action, _dst in valid_transitions():
        by_state[src.value].append(action)
    for state in sorted(by_state):
        print(f"{state}: {', '.join(sorted(set(by_state[state])))}")
    return 0


def cmd_ask(args: argparse.Namespace) -> int:
    engine = _default_engine()
    ctx = engine.start()
    engine.lookup_employer(ctx, args.employer)
    if ctx.provider:
        engine.submit_access(ctx, can_login=True)
        engine.submit_tax_type(ctx, "pre_tax")
        engine.choose_channel(ctx, JourneyChannel.PHONE)
    assistant = ScopedAssistant(engine.knowledge)
    result = assistant.answer(args.question, ctx.state, ctx.provider)
    print(json.dumps(result, indent=2))
    return 0


def cmd_screen(args: argparse.Namespace) -> int:
    engine = _default_engine()
    ctx = engine.start()
    screen = engine.render(ctx)

    for step in args.steps:
        if "=" in step:
            action, _, value = step.partition("=")
            if action == "lookup":
                screen = engine.lookup_employer(ctx, value)
            elif action == "tax_type":
                screen = engine.submit_tax_type(ctx, value)
            elif action == "channel":
                screen = engine.choose_channel(ctx, JourneyChannel(value))
            elif action == "provider":
                screen = engine.set_provider_direct(ctx, value)
            else:
                raise SystemExit(f"Unknown keyed action: {action}")
        elif step == "confirm_provider":
            if not ctx.provider:
                raise SystemExit("No provider set")
            screen = engine.submit_access(ctx, can_login=True)
        elif step in {"access_yes", "can_access_yes"}:
            screen = engine.submit_access(ctx, can_login=True)
        elif step in {"access_no", "can_access_no"}:
            screen = engine.submit_access(ctx, can_login=False)
        elif step == "step_done":
            screen = engine.advance_step(ctx, "done")
        elif step == "step_stuck":
            screen = engine.advance_step(ctx, "stuck")
        elif step == "confirm_in_flight":
            screen = engine.confirm_in_flight(ctx)
        elif step == "mark_complete":
            screen = engine.mark_complete(ctx)
        elif step == "handoff":
            screen = engine.take_handoff(ctx)
        else:
            raise SystemExit(f"Unknown action: {step}")

    print(json.dumps(screen.model_dump(mode="json"), indent=2))
    return 0


def cmd_walk(args: argparse.Namespace) -> int:
    engine = _default_engine()
    channel = JourneyChannel(args.channel) if args.channel else None
    result = walk_employer(engine, args.employer, channel=channel, verbose=True)
    print(json.dumps(result, indent=2))
    return 0


def cmd_funnel(_: argparse.Namespace) -> int:
    summary = load_funnel_summary()
    payload = summary.model_dump()
    if summary.handoff_offered_count:
        payload["handoff_rate"] = round(
            summary.handoff_taken_count / summary.handoff_offered_count, 3
        )
    else:
        payload["handoff_rate"] = 0.0
    print(json.dumps(payload, indent=2))
    return 0


def cmd_data_needed(_: argparse.Namespace) -> int:
    print(data_needed_report())
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Rollover Companion CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("demo", help="Start journey and print first screen").set_defaults(func=cmd_demo)

    p_lookup = sub.add_parser("lookup", help="Lookup employer plan provider")
    p_lookup.add_argument("employer")
    p_lookup.set_defaults(func=cmd_lookup)

    sub.add_parser("transitions", help="Print state machine transitions").set_defaults(func=cmd_transitions)

    p_ask = sub.add_parser("ask", help="Scoped assistant Q&A in phone channel")
    p_ask.add_argument("employer")
    p_ask.add_argument("question")
    p_ask.set_defaults(func=cmd_ask)

    p_screen = sub.add_parser("screen", help="Run scripted action sequence")
    p_screen.add_argument(
        "steps",
        nargs="+",
        help="Actions like lookup=Acme provider=Fidelity access_yes tax_type=pre_tax",
    )
    p_screen.set_defaults(func=cmd_screen)

    p_walk = sub.add_parser("walk", help="Walk employer through journey (v2 demo)")
    p_walk.add_argument("employer")
    p_walk.add_argument("--channel", choices=["online", "phone", "forms"], default=None)
    p_walk.set_defaults(func=cmd_walk)

    sub.add_parser("funnel", help="Funnel analytics from event log").set_defaults(func=cmd_funnel)
    sub.add_parser("data-needed", help="List pending verification data keys").set_defaults(func=cmd_data_needed)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())

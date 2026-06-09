#!/usr/bin/env python3
"""Headless CLI for the Rollover Companion journey engine."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine import (  # noqa: E402
    JourneyChannel,
    JourneyEngine,
    JourneyState,
    ScopedAssistant,
    valid_transitions,
)


def _print_screen(screen) -> None:
    print(f"\n{'─' * 60}")
    print(f"State: {screen.state.value}  |  Phase: {screen.phase.value}")
    if screen.provider:
        print(f"Provider: {screen.provider}")
    print(f"\n{screen.headline}")
    if screen.body:
        print(f"\n{screen.body}")
    if screen.disambiguation_question:
        print(f"\n? {screen.disambiguation_question}")
        for opt in screen.disambiguation_options:
            print(f"  • {opt}")
    for item in screen.guidance:
        flag = " [reconstructed]" if item.reconstructed else ""
        print(f"  → {item.text}{flag}")
    if screen.provenance_warning:
        print(f"\n⚠ {screen.provenance_warning}")
    if screen.edge_cases:
        print("\nEdge cases:")
        for ec in screen.edge_cases:
            print(f"  • {ec}")
    if screen.agent_notes:
        print("\nAgent notes:")
        for note in screen.agent_notes:
            print(f"  • {note}")
    print(f"\nPrimary: {screen.primary_action}")
    if screen.secondary_actions:
        print(f"Also: {', '.join(screen.secondary_actions)}")


def run_demo(engine: JourneyEngine) -> None:
    print("=" * 60)
    print("ROLLOVER COMPANION — headless demo (Fidelity, online path)")
    print("=" * 60)

    ctx = engine.start()
    screen = engine.render(ctx)
    _print_screen(screen)

    screen = engine.set_provider_direct(ctx, "Fidelity")
    _print_screen(screen)

    screen = engine.submit_access(ctx, can_login=True)
    _print_screen(screen)

    screen = engine.choose_channel(ctx, JourneyChannel.ONLINE)
    _print_screen(screen)

    while ctx.state == JourneyState.ONLINE_IN_PROGRESS:
        screen = engine.advance_step(ctx, "done")
        _print_screen(screen)

    screen = engine.confirm_in_flight(ctx)
    _print_screen(screen)

    screen = engine.mark_complete(ctx)
    _print_screen(screen)

    print("\n✓ Demo complete — journey reached 'complete' state.")


def run_lookup(engine: JourneyEngine, employer: str) -> None:
    ctx = engine.start()
    screen = engine.lookup_employer(ctx, employer)
    _print_screen(screen)
    print(f"\nMatcher: {screen.provider or 'pending'}")
    if ctx.disambiguation_question:
        print("Disambiguation required before proceeding.")


def run_transitions() -> None:
    print("Valid state transitions:")
    for src, action, dst in valid_transitions():
        print(f"  {src.value} --[{action}]--> {dst.value}")


def run_assistant(engine: JourneyEngine, question: str, provider: str, state: str) -> None:
    assistant = ScopedAssistant(engine.knowledge)
    result = assistant.answer(question, JourneyState(state), provider)
    print(json.dumps(result, indent=2))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Rollover Companion journey engine")
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("demo", help="Run a full headless journey demo")
    sub.add_parser("transitions", help="List valid state transitions")

    lookup_p = sub.add_parser("lookup", help="Lookup employer/provider")
    lookup_p.add_argument("employer", help="Employer or provider name")

    ask_p = sub.add_parser("ask", help="Scoped assistant query")
    ask_p.add_argument("question")
    ask_p.add_argument("--provider", default="Fidelity")
    ask_p.add_argument("--state", default="online_in_progress")

    screen_p = sub.add_parser("screen", help="Render a screen JSON snapshot")
    screen_p.add_argument("--provider", default="Fidelity")
    screen_p.add_argument("--json", action="store_true")

    args = parser.parse_args(argv)
    engine = JourneyEngine()

    if args.command == "demo":
        run_demo(engine)
        return 0
    if args.command == "transitions":
        run_transitions()
        return 0
    if args.command == "lookup":
        run_lookup(engine, args.employer)
        return 0
    if args.command == "ask":
        run_assistant(engine, args.question, args.provider, args.state)
        return 0
    if args.command == "screen":
        ctx = engine.start()
        engine.set_provider_direct(ctx, args.provider)
        screen = engine.render(ctx)
        if args.json:
            print(screen.model_dump_json(indent=2))
        else:
            _print_screen(screen)
        return 0

    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())

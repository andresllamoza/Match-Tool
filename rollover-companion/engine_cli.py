#!/usr/bin/env python3
"""Headless journey engine CLI (spec entry point).

Walk the state machine from the terminal; prints JSON state on every step.
Delegates to cli.py — use either `python3 engine_cli.py` or `python3 cli.py`.
"""

from cli import main

if __name__ == "__main__":
    raise SystemExit(main())

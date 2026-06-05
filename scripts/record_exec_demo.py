#!/usr/bin/env python3
"""Automated brisk executive demo walkthrough for screen recording."""

from __future__ import annotations

import time
from pathlib import Path

from playwright.sync_api import sync_playwright

APP_URL = "http://localhost:8501"
PASSWORD = "demo"
BATCH_CSV = Path(__file__).resolve().parents[1] / "demo" / "fortune_demo_batch_25.csv"

SINGLE_LOOKUPS = [
    "Walmart",
    "Nike",
    "Alphabet",
    "JP Morgan Chase",
    "State Farm Insurance Cos.",
    "Microsoft",
]


def pause(seconds: float) -> None:
    time.sleep(seconds)


def run_lookup(page, name: str) -> None:
    field = page.get_by_role("textbox", name="Employer name")
    field.click()
    field.fill(name)
    page.get_by_role("button", name="Search").click()
    page.wait_for_timeout(14000)


def main() -> None:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page(viewport={"width": 1280, "height": 900})
        page.goto(APP_URL, wait_until="networkidle")
        pause(1.5)

        pwd = page.get_by_role("textbox", name="Password")
        pwd.fill(PASSWORD)
        pwd.press("Enter")
        page.get_by_role("textbox", name="Employer name").wait_for(timeout=20000)
        page.wait_for_timeout(5000)

        for name in SINGLE_LOOKUPS:
            run_lookup(page, name)

        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        pause(3.0)

        page.locator('input[type="file"]').set_input_files(str(BATCH_CSV))
        pause(3.0)
        page.get_by_role("button", name="Run batch lookup").click()
        page.wait_for_selector("text=Matched", timeout=120000)
        pause(6.0)

        for _ in range(12):
            page.mouse.wheel(0, 200)
            pause(1.6)

        pause(6.0)
        browser.close()


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Polished demo: cream empty screen → letter-by-letter typing → Enter."""

from __future__ import annotations

import argparse
import subprocess
import time
from pathlib import Path

from playwright.sync_api import Locator, Page, sync_playwright

APP_URL = "http://localhost:8501/?demo=1"
SINGLE_LOOKUPS: list[tuple[str, str]] = [
    ("Nike", "Fidelity Workplace"),
    ("Alphabet", "Vanguard"),
    ("JP Morgan Chase", "Empower"),
    ("State Farm Insurance Cos.", "Alight"),
    ("Walmart", "Merrill"),
]

PER_CHAR_MS = 195
EMPTY_HOLD_MS = 3_000
PRE_ENTER_MS = 700
RESULT_HOLD_MS = 7_500
CREAM_STABLE_MS = 2_000


def wait_for_cream_ui(page: Page) -> None:
    """Wait until the gold/cream demo UI is fully painted — no gray flash."""
    page.goto(APP_URL, wait_until="domcontentloaded")
    page.get_by_role("textbox", name="Employer name").wait_for(timeout=30_000)
    page.wait_for_selector(".hero-banner, .tool-header", timeout=15_000)
    page.wait_for_selector(".empty-state", timeout=15_000)
    page.wait_for_function(
        """
        () => {
            const app = document.querySelector('.stApp');
            const empty = document.querySelector('.empty-state');
            const banner = document.querySelector('.hero-banner, .tool-header');
            if (!app || !empty || !banner) return false;
            return app.getAttribute('data-test-script-state') !== 'running';
        }
        """,
        timeout=20_000,
    )
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(CREAM_STABLE_MS)


def clear_field_human(field: Locator, page: Page) -> None:
    field.click()
    page.wait_for_timeout(250)
    value = field.input_value()
    if not value:
        return
    field.press("End")
    for _ in value:
        field.press("Backspace")
        page.wait_for_timeout(55)


def type_name_human(field: Locator, page: Page, name: str) -> None:
    clear_field_human(field, page)
    page.wait_for_timeout(350)
    for char in name:
        if char == " ":
            field.press("Space")
        else:
            field.press(char)
        page.wait_for_timeout(PER_CHAR_MS)
    page.wait_for_timeout(PRE_ENTER_MS)


def wait_for_rerun_done(page: Page) -> None:
    page.wait_for_function(
        """
        () => {
            const app = document.querySelector('.stApp');
            return app && app.getAttribute('data-test-script-state') !== 'running';
        }
        """,
        timeout=30_000,
    )
    page.wait_for_timeout(400)


def type_and_search(page: Page, name: str, expect_text: str) -> None:
    page.evaluate("window.scrollTo(0, 0)")
    field = page.get_by_role("textbox", name="Employer name")
    type_name_human(field, page, name)
    field.press("Enter")
    wait_for_rerun_done(page)
    page.locator(".result-recordkeeper").filter(has_text=expect_text).wait_for(timeout=60_000)
    page.wait_for_timeout(RESULT_HOLD_MS)


def run_flow(page: Page) -> None:
    wait_for_cream_ui(page)
    page.wait_for_timeout(EMPTY_HOLD_MS)
    for name, expect in SINGLE_LOOKUPS:
        type_and_search(page, name, expect)
    page.evaluate("window.scrollTo(0, 0)")
    page.wait_for_timeout(1_000)


def trim_video(src: Path, dst: Path) -> None:
    subprocess.run(
        [
            "ffmpeg", "-y", "-i", str(src),
            "-c:v", "libx264", "-preset", "fast", "-crf", "21", "-pix_fmt", "yuv420p",
            str(dst),
        ],
        check=True,
        capture_output=True,
    )


def record_with_ffmpeg(out_path: Path) -> None:
    raw_path = out_path.with_name(out_path.stem + "_raw.mp4")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page(viewport={"width": 1280, "height": 900})
        wait_for_cream_ui(page)
        page.wait_for_timeout(EMPTY_HOLD_MS)
        ffmpeg = subprocess.Popen(
            [
                "ffmpeg", "-y",
                "-f", "x11grab", "-video_size", "1280x900", "-framerate", "30",
                "-i", ":1.0+0,0",
                "-c:v", "libx264", "-preset", "fast", "-crf", "21", "-pix_fmt", "yuv420p",
                str(raw_path),
            ],
        )
        time.sleep(0.5)
        try:
            for name, expect in SINGLE_LOOKUPS:
                type_and_search(page, name, expect)
            page.wait_for_timeout(1_000)
        finally:
            browser.close()
            ffmpeg.send_signal(subprocess.signal.SIGINT)
            ffmpeg.wait(timeout=30)
    trim_video(raw_path, out_path)
    raw_path.unlink(missing_ok=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--with-recording", type=Path)
    parser.add_argument("--warmup-only", action="store_true")
    args = parser.parse_args()

    if args.warmup_only:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            wait_for_cream_ui(page)
            browser.close()
        return

    if args.with_recording:
        record_with_ffmpeg(args.with_recording)
        return

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page(viewport={"width": 1280, "height": 900})
        run_flow(page)
        browser.close()


if __name__ == "__main__":
    main()

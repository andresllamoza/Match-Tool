#!/usr/bin/env python3
"""Polished demo: empty screen → visible letter-by-letter typing → Enter."""

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
EMPTY_HOLD_MS = 3_500
PRE_ENTER_MS = 700
RESULT_HOLD_MS = 7_500


def wait_for_app_ready(page: Page) -> None:
    page.goto(APP_URL, wait_until="networkidle")
    page.get_by_role("textbox", name="Employer name").wait_for(timeout=30_000)
    page.wait_for_selector(".hero-banner, .tool-header", timeout=15_000)
    page.wait_for_timeout(600)


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
    """One visible character at a time — no instant fill."""
    clear_field_human(field, page)
    page.wait_for_timeout(350)
    for char in name:
        if char == " ":
            field.press("Space")
        else:
            field.press(char)
        page.wait_for_timeout(PER_CHAR_MS)
    page.wait_for_timeout(PRE_ENTER_MS)


def type_and_search(page: Page, name: str, expect_text: str, *, show_empty_first: bool) -> None:
    if show_empty_first:
        page.wait_for_selector(".empty-state", timeout=10_000)
        page.wait_for_timeout(EMPTY_HOLD_MS)

    page.evaluate("window.scrollTo(0, 0)")
    field = page.get_by_role("textbox", name="Employer name")
    type_name_human(field, page, name)
    field.press("Enter")

    page.locator(".result-recordkeeper").filter(has_text=expect_text).wait_for(timeout=60_000)
    page.wait_for_timeout(RESULT_HOLD_MS)


def run_flow(page: Page) -> None:
    wait_for_app_ready(page)
    for index, (name, expect) in enumerate(SINGLE_LOOKUPS):
        type_and_search(page, name, expect, show_empty_first=index == 0)
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
        wait_for_app_ready(page)
        page.wait_for_selector(".empty-state", timeout=10_000)
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
        time.sleep(0.35)
        try:
            for index, (name, expect) in enumerate(SINGLE_LOOKUPS):
                type_and_search(page, name, expect, show_empty_first=index == 0)
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
            wait_for_app_ready(page)
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

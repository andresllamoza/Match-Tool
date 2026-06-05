#!/usr/bin/env python3
"""90-second demo: 5 lookups on ?demo=1 (auto-login, no batch chrome)."""

from __future__ import annotations

import argparse
import subprocess
import time
from pathlib import Path

from playwright.sync_api import Page, sync_playwright

APP_URL = "http://localhost:8501/?demo=1"
SINGLE_LOOKUPS: list[tuple[str, str]] = [
    ("Nike", "Fidelity Workplace"),
    ("Alphabet", "Vanguard"),
    ("JP Morgan Chase", "Empower"),
    ("State Farm Insurance Cos.", "Alight"),
    ("Walmart", "Merrill"),
]

RESULT_HOLD_MS = 10_000
INTRO_HOLD_MS = 2_500


def run_lookup(page: Page, name: str, expect_text: str) -> None:
    page.goto(APP_URL, wait_until="networkidle")
    page.get_by_role("textbox", name="Employer name").wait_for(timeout=20_000)
    page.wait_for_timeout(400)
    page.evaluate("window.scrollTo(0, 0)")
    field = page.get_by_role("textbox", name="Employer name")
    field.fill(name)
    page.get_by_role("button", name="Search").click()
    page.locator(".result-recordkeeper").filter(has_text=expect_text).wait_for(timeout=60_000)
    page.wait_for_timeout(RESULT_HOLD_MS)


def run_flow(page: Page, *, first_intro: bool = False) -> None:
    if first_intro:
        page.goto(APP_URL, wait_until="networkidle")
        page.get_by_role("textbox", name="Employer name").wait_for(timeout=20_000)
        page.wait_for_timeout(INTRO_HOLD_MS)
        run_lookup(page, SINGLE_LOOKUPS[0][0], SINGLE_LOOKUPS[0][1])
        lookups = SINGLE_LOOKUPS[1:]
    else:
        lookups = SINGLE_LOOKUPS
    for name, expect in lookups:
        run_lookup(page, name, expect)
    page.evaluate("window.scrollTo(0, 0)")
    page.wait_for_timeout(800)


def trim_video(src: Path, dst: Path, start_sec: float = 0.5) -> None:
    subprocess.run(
        [
            "ffmpeg", "-y", "-ss", str(start_sec), "-i", str(src),
            "-c:v", "libx264", "-preset", "fast", "-crf", "22", "-pix_fmt", "yuv420p",
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
        page.goto(APP_URL, wait_until="networkidle")
        page.get_by_role("textbox", name="Employer name").wait_for(timeout=20_000)
        page.wait_for_timeout(INTRO_HOLD_MS)
        ffmpeg = subprocess.Popen(
            [
                "ffmpeg", "-y",
                "-f", "x11grab", "-video_size", "1280x900", "-framerate", "24",
                "-i", ":1.0+0,0",
                "-c:v", "libx264", "-preset", "fast", "-crf", "22", "-pix_fmt", "yuv420p",
                str(raw_path),
            ],
        )
        time.sleep(0.4)
        try:
            for name, expect in SINGLE_LOOKUPS:
                if name == SINGLE_LOOKUPS[0][0]:
                    page.evaluate("window.scrollTo(0, 0)")
                    field = page.get_by_role("textbox", name="Employer name")
                    field.fill(name)
                    page.get_by_role("button", name="Search").click()
                    page.locator(".result-recordkeeper").filter(has_text=expect).wait_for(timeout=60_000)
                    page.wait_for_timeout(RESULT_HOLD_MS)
                else:
                    run_lookup(page, name, expect)
            page.evaluate("window.scrollTo(0, 0)")
            page.wait_for_timeout(800)
        finally:
            browser.close()
            ffmpeg.send_signal(subprocess.signal.SIGINT)
            ffmpeg.wait(timeout=30)
    trim_video(raw_path, out_path, start_sec=0.3)
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
            page.goto(APP_URL, wait_until="networkidle")
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

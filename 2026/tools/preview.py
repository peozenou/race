#!/usr/bin/env python3
"""Render preview.png (1200x630), the image WhatsApp shows with the link.

Usage: serve the repository locally, then
  python3 tools/preview.py http://127.0.0.1:8765/
"""
import asyncio
import pathlib
import sys

from playwright.async_api import async_playwright

ROOT = pathlib.Path(__file__).resolve().parent.parent


async def main(url: str) -> None:
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={"width": 1200, "height": 630}, device_scale_factor=1, color_scheme="light")
        await page.goto(url, wait_until="networkidle")
        await page.add_style_tag(content=".site{padding:2.25rem 2rem 0!important} .tr-head-note,.tr-tabs{display:none!important}")
        await page.wait_for_timeout(1500)
        await page.screenshot(path=str(ROOT / "preview.png"), clip={"x": 0, "y": 0, "width": 1200, "height": 630})
        await browser.close()


asyncio.run(main(sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8765/"))

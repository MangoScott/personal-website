#!/usr/bin/env python3
"""Render the social sharing card to images/og-image.jpg.

Renders og-card.html in headless Chromium at 2x, downsamples to 1200x630 for
crisp text, and writes a 4:4:4 progressive JPEG.

    pip install playwright pillow && playwright install chromium
    python3 tools/og/render.py

Pass --out to write somewhere else (used for the per-page cards):

    python3 tools/og/render.py --card tools/og/card-travel.html --out images/og-travel.jpg
"""

import argparse
import glob
import os
import pathlib
import sys

from PIL import Image, ImageFilter
from playwright.sync_api import sync_playwright

WIDTH, HEIGHT, SCALE = 1200, 630, 2
QUALITY = 92
HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent.parent


def find_chromium():
    """Prefer a preinstalled browser, else let Playwright use its own."""
    base = os.environ.get("PLAYWRIGHT_BROWSERS_PATH")
    if base:
        for pat in ("chromium-*/chrome-linux/chrome", "chromium-*/chrome-mac/Chromium.app/Contents/MacOS/Chromium"):
            hits = sorted(glob.glob(os.path.join(base, pat)))
            if hits:
                return hits[-1]
    return None


def render(card: pathlib.Path, out: pathlib.Path) -> None:
    card, out = card.resolve(), out.resolve()
    raw = HERE / ".render-2x.png"
    with sync_playwright() as pw:
        exe = find_chromium()
        browser = pw.chromium.launch(
            executable_path=exe,
            args=["--no-sandbox", "--font-render-hinting=none"],
        )
        page = browser.new_context(
            viewport={"width": WIDTH, "height": HEIGHT},
            device_scale_factor=SCALE,
        ).new_page()
        page.goto(card.as_uri())
        page.wait_for_function("document.fonts.ready.then(() => true)")

        missing = page.evaluate(
            """() => ['800 78px Inter', 'italic 31px "Playfair Display"']
                       .filter(f => !document.fonts.check(f))"""
        )
        if missing:
            sys.exit(f"webfonts did not load: {missing} (need network for Google Fonts)")

        overflow = page.evaluate(
            """() => {
                const bad = [];
                for (const sel of ['.name', '.tag', '.proof', '.eyebrow', '.big', '.label', '.head', '.sub']) {
                    const el = document.querySelector(sel);
                    if (!el) continue;
                    const box = el.parentElement;
                    if (el.scrollWidth > box.clientWidth + 1) bad.push(sel + ' wider than its column');
                    const r = el.getBoundingClientRect();
                    if (r.right > 1200.5 || r.bottom > 630.5 || r.left < -0.5 || r.top < -0.5)
                        bad.push(sel + ' outside the card');
                }
                const imgs = [...document.images].filter(i => !i.complete || i.naturalWidth === 0);
                if (imgs.length) bad.push('images failed to load: ' + imgs.map(i => i.getAttribute('src')).join(', '));
                return bad;
            }"""
        )
        if overflow:
            sys.exit("card layout problem: " + "; ".join(overflow))

        page.locator(".card").screenshot(path=str(raw))
        browser.close()

    im = Image.open(raw)
    if im.size != (WIDTH * SCALE, HEIGHT * SCALE):
        sys.exit(f"unexpected render size {im.size}")
    im = (
        im.convert("RGB")
        .resize((WIDTH, HEIGHT), Image.LANCZOS)
        .filter(ImageFilter.UnsharpMask(radius=1, percent=26, threshold=3))
    )
    out.parent.mkdir(parents=True, exist_ok=True)
    im.save(out, quality=QUALITY, subsampling=0, progressive=True, optimize=True)
    raw.unlink(missing_ok=True)
    print(f"{os.path.relpath(out, ROOT)}  {im.width}x{im.height}  {out.stat().st_size // 1024}KB")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--card", default=str(HERE / "og-card.html"))
    ap.add_argument("--out", default=str(ROOT / "images" / "og-image.jpg"))
    args = ap.parse_args()
    render(pathlib.Path(args.card), pathlib.Path(args.out))

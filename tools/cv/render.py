#!/usr/bin/env python3
"""Render cv.html to Scott_Glasgow_CV.pdf.

Prints cv.html in headless Chromium using the page's own @media print rules,
so the PDF is the same document the site shows, set in the same typeface.

    pip install playwright pymupdf && playwright install chromium
    python3 tools/cv/render.py

Inter is fetched from Google Fonts here in Python (which honours HTTPS_PROXY
and the usual CA variables) and handed to the browser, so the PDF is set in the
site's typeface even where headless Chromium has no network of its own. Fails
loudly if the font still did not load, or if the result runs past two pages.
"""

import argparse
import glob
import os
import pathlib
import sys
import urllib.request

from playwright.sync_api import sync_playwright

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent.parent
MAX_PAGES = 2

METADATA = {
    "title": "Scott Glasgow — CV",
    "author": "Scott Glasgow",
    "subject": "Curriculum vitae",
    "creator": "sglasgow.com",
    "producer": "sglasgow.com",
}


FONT_HOSTS = ("fonts.googleapis.com", "fonts.gstatic.com")
# Google picks the font format from the User-Agent. Asking as an old browser gets
# one plain static WOFF per weight, which Chromium embeds in the PDF as a real
# TrueType font; the modern unicode-range WOFF2 subsets come out as Type 3 glyph
# outlines, which some viewers and parsers handle badly.
FONT_UA = "Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko"


def serve_fonts(route):
    """Fulfil a Google Fonts request from Python instead of the browser's network stack."""
    req = urllib.request.Request(route.request.url, headers={"User-Agent": FONT_UA})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            route.fulfill(status=resp.status, body=resp.read(),
                          headers={"content-type": resp.headers.get("content-type", "")})
    except Exception as exc:  # let the browser report it; the font check below fails loudly
        print(f"font fetch failed: {route.request.url}: {exc}", file=sys.stderr)
        route.abort()


def find_chromium():
    """Prefer a preinstalled browser, else let Playwright use its own."""
    base = os.environ.get("PLAYWRIGHT_BROWSERS_PATH")
    if base:
        for pat in ("chromium-*/chrome-linux/chrome", "chromium-*/chrome-mac/Chromium.app/Contents/MacOS/Chromium"):
            hits = sorted(glob.glob(os.path.join(base, pat)))
            if hits:
                return hits[-1]
    return None


def render(src: pathlib.Path, out: pathlib.Path) -> None:
    src, out = src.resolve(), out.resolve()
    with sync_playwright() as pw:
        browser = pw.chromium.launch(executable_path=find_chromium(), args=["--no-sandbox"])
        page = browser.new_page()
        page.route(lambda url: any(h in url for h in FONT_HOSTS), serve_fonts)
        page.goto(src.as_uri())
        page.wait_for_function("document.fonts.ready.then(() => true)")

        # document.fonts.check() says "true" when no matching face exists at all,
        # so count the faces that actually loaded instead.
        loaded = page.evaluate(
            """() => [...document.fonts].filter(f => f.family.replace(/["']/g, '') === 'Inter'
                                                     && f.status === 'loaded').length"""
        )
        if not loaded:
            sys.exit("Inter did not load; the PDF would fall back to a system font (need network for Google Fonts)")

        page.emulate_media(media="print")
        page.pdf(path=str(out), format="Letter", prefer_css_page_size=True, print_background=True)
        browser.close()

    pages = stamp_metadata(out)
    if pages and pages > MAX_PAGES:
        sys.exit(f"CV runs to {pages} pages; trim cv.html or its print rules so it fits {MAX_PAGES}")
    print(f"{os.path.relpath(out, ROOT)}  {pages or '?'} pages  {out.stat().st_size // 1024}KB")


def stamp_metadata(out: pathlib.Path):
    """Set title/author on the PDF. Returns the page count, or None without pymupdf."""
    try:
        import pymupdf
    except ImportError:
        print("pymupdf not installed; PDF metadata left as Chromium wrote it", file=sys.stderr)
        return None
    doc = pymupdf.open(out)
    md = doc.metadata or {}
    md.update(METADATA)
    doc.set_metadata(md)
    pages = len(doc)
    doc.save(out, incremental=True, encryption=pymupdf.PDF_ENCRYPT_KEEP)
    doc.close()
    return pages


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default=str(ROOT / "cv.html"))
    ap.add_argument("--out", default=str(ROOT / "Scott_Glasgow_CV.pdf"))
    args = ap.parse_args()
    render(pathlib.Path(args.src), pathlib.Path(args.out))

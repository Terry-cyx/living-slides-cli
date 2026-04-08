"""HTML → PDF helper (Phase D2).

This module exposes `render_to_pdf()` as a *helper function*, not a
slive CLI command. Rationale: shipping a Playwright dependency in the
default install doubles the dependency closure for a feature most users
won't want, and Playwright requires a one-time `playwright install`
shell step that the slive CLI shouldn't try to manage. Users who need
PDF can either run their own Playwright/Puppeteer/wkhtmltopdf script,
or import this helper from their own code.

Adapted from `frontend-slides/scripts/export-pdf.sh` (MIT) by
zarazhangrui — the 1920×1080 viewport, full-page screenshot strategy,
and `print` media-type emulation all originate there.
"""

from __future__ import annotations

from pathlib import Path


_MISSING_DEP_MESSAGE = (
    "PDF export requires Playwright. Install it with:\n"
    "    pip install playwright\n"
    "    playwright install chromium\n"
    "Then call living_slides.exporters.pdf.render_to_pdf() from your script."
)


def render_to_pdf(
    html_path: str,
    pdf_path: str | None = None,
    *,
    width: int = 1920,
    height: int = 1080,
    landscape: bool = True,
) -> str:
    """Render an HTML deck to a PDF using Playwright.

    Returns the path to the generated PDF. The default 1920×1080 landscape
    viewport matches frontend-slides' export convention so a slive deck
    looks the same in PDF as it does in the browser.

    This is intentionally not wired into the slive CLI — Playwright is too
    heavy for the default install. Users invoke this from their own scripts:

        from living_slides.exporters.pdf import render_to_pdf
        render_to_pdf("deck.html", "deck.pdf")
    """
    src = Path(html_path).resolve()
    if not src.exists():
        raise FileNotFoundError(f"HTML file not found: {src}")

    try:
        from playwright.sync_api import sync_playwright
    except ImportError as e:
        raise RuntimeError(_MISSING_DEP_MESSAGE) from e

    if pdf_path is None:
        pdf_path = str(src.with_suffix(".pdf"))
    out = Path(pdf_path).resolve()

    with sync_playwright() as p:
        browser = p.chromium.launch()
        try:
            context = browser.new_context(viewport={"width": width, "height": height})
            page = context.new_page()
            page.goto(src.as_uri(), wait_until="networkidle")
            page.emulate_media(media="print")
            page.pdf(
                path=str(out),
                width=f"{width}px",
                height=f"{height}px",
                landscape=landscape,
                print_background=True,
                margin={"top": "0", "right": "0", "bottom": "0", "left": "0"},
            )
        finally:
            browser.close()
    return str(out)

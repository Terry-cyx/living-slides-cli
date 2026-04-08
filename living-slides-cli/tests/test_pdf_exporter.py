"""Tests for the PDF exporter helper (Phase D2).

Playwright is not a dependency of slive — it's an opt-in extra users
install themselves. These tests verify the contract surface (function
signature, error message when missing, FileNotFoundError on bad input)
without actually rendering a PDF.
"""

from __future__ import annotations

import importlib.util

import pytest

from living_slides.exporters.pdf import render_to_pdf


PLAYWRIGHT_AVAILABLE = importlib.util.find_spec("playwright") is not None


def test_render_to_pdf_missing_html_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        render_to_pdf(str(tmp_path / "nope.html"))


@pytest.mark.skipif(PLAYWRIGHT_AVAILABLE, reason="Playwright is installed; skipping the missing-dep test")
def test_render_to_pdf_without_playwright_emits_install_hint(tmp_path):
    f = tmp_path / "deck.html"
    f.write_text("<html></html>", encoding="utf-8")
    with pytest.raises(RuntimeError) as ei:
        render_to_pdf(str(f))
    msg = str(ei.value)
    assert "playwright" in msg.lower()
    assert "pip install" in msg.lower()


def test_pdf_helper_not_exposed_via_cli():
    """D2 ships as a helper, not a CLI command."""
    from click.testing import CliRunner
    from living_slides.cli import main

    result = CliRunner().invoke(main, ["--help"])
    assert "pdf" not in result.output.lower()
    assert "export" not in result.output.lower()

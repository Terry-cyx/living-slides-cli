"""Tests for `slive verify` (Phase C3)."""

from __future__ import annotations

from pathlib import Path

from click.testing import CliRunner

from living_slides.verify import verify_html
from living_slides.cli import main


def _write(tmp_path: Path, name: str, content: str = "") -> Path:
    p = tmp_path / name
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    return p


# ---------- core ----------

def test_verify_no_references(tmp_path):
    deck = _write(tmp_path, "deck.html", "<html><body><p>hi</p></body></html>")
    issues = verify_html(str(deck))
    assert issues == []


def test_verify_resolved_local_refs(tmp_path):
    _write(tmp_path, "deck-assets/img.png", "fake")
    deck = _write(tmp_path, "deck.html",
                  '<html><body><img src="deck-assets/img.png"></body></html>')
    assert verify_html(str(deck)) == []


def test_verify_missing_image(tmp_path):
    deck = _write(tmp_path, "deck.html",
                  '<html><body><img src="missing.png"></body></html>')
    issues = verify_html(str(deck))
    assert len(issues) == 1
    assert issues[0]["src"] == "missing.png"
    assert issues[0]["tag"] == "img"


def test_verify_includes_oid_when_present(tmp_path):
    deck = _write(tmp_path, "deck.html",
                  '<img data-oid="s5-chart" src="missing.png">')
    issues = verify_html(str(deck))
    assert issues[0]["oid"] == "s5-chart"


def test_verify_skips_external_urls(tmp_path):
    deck = _write(tmp_path, "deck.html", """
<html><body>
<img src="https://cdn.example.com/x.png">
<img src="//cdn.example.com/y.png">
<script src="http://example.com/x.js"></script>
<a href="https://example.com">link</a>
</body></html>""")
    assert verify_html(str(deck)) == []


def test_verify_skips_data_urls(tmp_path):
    deck = _write(tmp_path, "deck.html",
                  '<img src="data:image/png;base64,iVBORw0KG">')
    assert verify_html(str(deck)) == []


def test_verify_checks_link_and_script(tmp_path):
    deck = _write(tmp_path, "deck.html", """
<html><head>
<link rel="stylesheet" href="missing.css">
<script src="missing.js"></script>
</head></html>""")
    issues = verify_html(str(deck))
    tags = sorted(i["tag"] for i in issues)
    assert tags == ["link", "script"]


def test_verify_skips_anchor_only_hrefs(tmp_path):
    deck = _write(tmp_path, "deck.html", '<a href="#section-2">jump</a>')
    assert verify_html(str(deck)) == []


# ---------- CLI ----------

def test_cli_verify_clean(tmp_path):
    _write(tmp_path, "deck-assets/x.png", "fake")
    deck = _write(tmp_path, "deck.html", '<img src="deck-assets/x.png">')
    result = CliRunner().invoke(main, ["verify", str(deck)])
    assert result.exit_code == 0
    assert "ok" in result.output.lower() or "clean" in result.output.lower() or "0" in result.output


def test_cli_verify_broken_exits_nonzero(tmp_path):
    deck = _write(tmp_path, "deck.html", '<img src="missing.png">')
    result = CliRunner().invoke(main, ["verify", str(deck)])
    assert result.exit_code == 1
    assert "missing.png" in result.output

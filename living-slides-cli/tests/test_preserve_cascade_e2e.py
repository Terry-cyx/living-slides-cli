"""End-to-end validation: preserve+cascade across multiple rounds.

This is the Phase E regression test. It simulates the *full iteration
loop* an AI client would drive:

  1. start with a deck
  2. user hand-edits → save → changelog round 1 appended
  3. user hand-edits something else → save → changelog round 2 appended
  4. AI calls `slive diff --touched` to get the do-not-stomp set
  5. AI calls `slive diff` to see the latest cascade trigger
  6. assert: every round-1 oid is still in --touched after round 2
  7. assert: --touched is the *union* across all rounds, not just the latest

If this test ever fails, the wedge is broken.
"""

from __future__ import annotations

import json

from click.testing import CliRunner

from living_slides.cli import main
from living_slides.differ import compute_changelog
from living_slides.history import (
    append_changelog_history,
    history_path_for,
    touched_oids,
)


STARTER_HTML = """<!DOCTYPE html>
<html><body>
<section class="slide" data-oid="s0-slide" id="slide-1">
  <h1 data-oid="s0-title">Original Title</h1>
  <p data-oid="s0-subtitle">Original subtitle</p>
</section>
<section class="slide" data-oid="s1-slide" id="slide-2">
  <h2 data-oid="s1-title">Numbers</h2>
  <p data-oid="s1-metric">$2.4M ARR</p>
  <p data-oid="s1-runway">18 months runway</p>
</section>
</body></html>"""


def _save_round(deck_path, old_html, new_html):
    """Simulate /api/save: compute changelog and append to history."""
    cl = compute_changelog(old_html, new_html, deck_path.name)
    if cl["changes"]:
        append_changelog_history(str(deck_path), cl)
    deck_path.write_text(new_html, encoding="utf-8")
    return cl


def test_preserve_compounds_across_rounds(tmp_path):
    deck = tmp_path / "deck.html"
    deck.write_text(STARTER_HTML, encoding="utf-8")

    # Round 1: user fixes the title.
    round1 = STARTER_HTML.replace("Original Title", "Q1 2026 Review")
    _save_round(deck, STARTER_HTML, round1)
    assert touched_oids(str(deck)) == {"s0-title"}

    # Round 2: user fixes the metric.
    round2 = round1.replace("$2.4M ARR", "$3.1M ARR")
    _save_round(deck, round1, round2)
    # CRITICAL: round 1's oid must still be in the touched set.
    assert touched_oids(str(deck)) == {"s0-title", "s1-metric"}

    # Round 3: user moves the runway line up.
    round3 = round2.replace("18 months runway", "24 months runway")
    _save_round(deck, round2, round3)
    assert touched_oids(str(deck)) == {"s0-title", "s1-metric", "s1-runway"}


def test_diff_touched_cli_returns_union(tmp_path):
    deck = tmp_path / "deck.html"
    deck.write_text(STARTER_HTML, encoding="utf-8")

    round1 = STARTER_HTML.replace("Original Title", "Q1")
    _save_round(deck, STARTER_HTML, round1)
    round2 = round1.replace("$2.4M ARR", "$3.1M ARR")
    _save_round(deck, round1, round2)

    runner = CliRunner()
    result = runner.invoke(main, ["diff", str(deck), "--touched"])
    assert result.exit_code == 0
    assert "s0-title" in result.output
    assert "s1-metric" in result.output


def test_diff_history_cli_shows_all_rounds(tmp_path):
    deck = tmp_path / "deck.html"
    deck.write_text(STARTER_HTML, encoding="utf-8")

    round1 = STARTER_HTML.replace("Original Title", "Round1")
    _save_round(deck, STARTER_HTML, round1)
    round2 = round1.replace("Round1", "Round2")
    _save_round(deck, round1, round2)

    runner = CliRunner()
    result = runner.invoke(main, ["diff", str(deck), "--history"])
    assert result.exit_code == 0
    assert "Round 1" in result.output
    assert "Round 2" in result.output


def test_history_jsonl_is_one_line_per_round(tmp_path):
    deck = tmp_path / "deck.html"
    deck.write_text(STARTER_HTML, encoding="utf-8")
    round1 = STARTER_HTML.replace("Original Title", "A")
    _save_round(deck, STARTER_HTML, round1)
    round2 = round1.replace("A", "B")
    _save_round(deck, round1, round2)

    hist = history_path_for(str(deck))
    lines = [l for l in hist.read_text(encoding="utf-8").splitlines() if l.strip()]
    assert len(lines) == 2
    # Each line is a complete JSON document
    for line in lines:
        data = json.loads(line)
        assert "changes" in data
        assert "summary" in data


def test_adopt_then_iterate_no_data_loss(tmp_path):
    """Bring a no-oid deck in via adopt, then run two edit rounds."""
    deck = tmp_path / "imported.html"
    raw = """<section class="slide"><h1>Hello</h1><p>world</p></section>
<section class="slide"><h1>Goodbye</h1><p>moon</p></section>"""
    deck.write_text(raw, encoding="utf-8")

    runner = CliRunner()
    runner.invoke(main, ["adopt", str(deck)])
    after_adopt = deck.read_text(encoding="utf-8")
    assert 'data-oid' in after_adopt

    # Edit round 1
    edited = after_adopt.replace("Hello", "Greetings")
    _save_round(deck, after_adopt, edited)
    touched1 = touched_oids(str(deck))
    assert len(touched1) >= 1

    # Edit round 2
    edited2 = edited.replace("moon", "stars")
    _save_round(deck, edited, edited2)
    touched2 = touched_oids(str(deck))
    # Round 2's set must be a superset of round 1's — preserve compounds.
    assert touched1.issubset(touched2)


def test_verify_catches_broken_ref_after_edit(tmp_path):
    deck = tmp_path / "deck.html"
    deck.write_text(
        '<section class="slide" data-oid="s0">'
        '<img data-oid="s0-img" src="missing.png">'
        '</section>',
        encoding="utf-8",
    )
    runner = CliRunner()
    result = runner.invoke(main, ["verify", str(deck)])
    assert result.exit_code == 1
    assert "missing.png" in result.output
    assert "s0-img" in result.output

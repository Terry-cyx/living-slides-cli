"""Tests for changelog history (Phase C2)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from living_slides.history import (
    append_changelog_history,
    history_path_for,
    load_history,
    touched_oids,
)


def _make_changelog(changes):
    return {
        "file": "deck.html",
        "timestamp": "2026-04-08T00:00:00+00:00",
        "changes": changes,
        "diff": "",
        "summary": "test",
    }


def test_history_path_naming(tmp_path):
    deck = tmp_path / "deck.html"
    p = history_path_for(str(deck))
    assert p.name == "deck.changelog.history.jsonl"
    assert p.parent == tmp_path


def test_append_creates_file_with_one_line(tmp_path):
    deck = tmp_path / "deck.html"
    cl = _make_changelog([
        {"type": "text_edit", "selector": '[data-oid="s0-title"]',
         "before": "A", "after": "B"},
    ])
    append_changelog_history(str(deck), cl)
    hist = history_path_for(str(deck))
    lines = hist.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 1
    assert json.loads(lines[0])["changes"][0]["after"] == "B"


def test_append_appends_multiple_rounds(tmp_path):
    deck = tmp_path / "deck.html"
    for i in range(3):
        cl = _make_changelog([
            {"type": "text_edit", "selector": f"[data-oid=\"s0-o{i}\"]",
             "before": "x", "after": str(i)},
        ])
        append_changelog_history(str(deck), cl)
    rounds = load_history(str(deck))
    assert len(rounds) == 3
    assert [r["changes"][0]["after"] for r in rounds] == ["0", "1", "2"]


def test_load_history_missing_file_returns_empty(tmp_path):
    assert load_history(str(tmp_path / "nope.html")) == []


def test_touched_oids_unions_across_rounds(tmp_path):
    deck = tmp_path / "deck.html"
    append_changelog_history(str(deck), _make_changelog([
        {"type": "text_edit", "selector": '[data-oid="s0-title"]',
         "before": "A", "after": "B"},
    ]))
    append_changelog_history(str(deck), _make_changelog([
        {"type": "attribute_change", "selector": '[data-oid="s1-image"]',
         "attribute": "src", "before": "a.png", "after": "b.png"},
    ]))
    append_changelog_history(str(deck), _make_changelog([
        {"type": "element_added", "selector": '[data-oid="s2-text"]',
         "tag": "p"},
    ]))
    oids = touched_oids(str(deck))
    assert oids == {"s0-title", "s1-image", "s2-text"}


def test_touched_oids_ignores_selectors_without_oid(tmp_path):
    deck = tmp_path / "deck.html"
    append_changelog_history(str(deck), _make_changelog([
        {"type": "text_edit", "selector": "h1.banner",
         "before": "A", "after": "B"},
        {"type": "text_edit", "selector": '[data-oid="s0-keep"]',
         "before": "X", "after": "Y"},
    ]))
    assert touched_oids(str(deck)) == {"s0-keep"}


# ---- CLI integration ----

def _runner_invoke(args):
    from click.testing import CliRunner
    from living_slides.cli import main
    return CliRunner().invoke(main, args)


def test_cli_diff_history_prints_all_rounds(tmp_path):
    deck = tmp_path / "deck.html"
    deck.write_text("<html></html>", encoding="utf-8")
    for i in range(2):
        append_changelog_history(str(deck), _make_changelog([
            {"type": "text_edit", "selector": f'[data-oid="s0-o{i}"]',
             "before": "x", "after": str(i)},
        ]))
    # Also write the latest changelog so plain `slive diff` still works.
    latest = tmp_path / "deck.changelog.json"
    latest.write_text(json.dumps(_make_changelog([])), encoding="utf-8")

    result = _runner_invoke(["diff", str(deck), "--history"])
    assert result.exit_code == 0, result.output
    assert "Round 1" in result.output
    assert "Round 2" in result.output


def test_cli_diff_touched_lists_oids(tmp_path):
    deck = tmp_path / "deck.html"
    deck.write_text("<html></html>", encoding="utf-8")
    append_changelog_history(str(deck), _make_changelog([
        {"type": "text_edit", "selector": '[data-oid="s0-title"]',
         "before": "A", "after": "B"},
        {"type": "text_edit", "selector": '[data-oid="s1-text"]',
         "before": "C", "after": "D"},
    ]))
    latest = tmp_path / "deck.changelog.json"
    latest.write_text(json.dumps(_make_changelog([])), encoding="utf-8")

    result = _runner_invoke(["diff", str(deck), "--touched"])
    assert result.exit_code == 0, result.output
    assert "s0-title" in result.output
    assert "s1-text" in result.output


def test_cli_diff_touched_no_history(tmp_path):
    deck = tmp_path / "deck.html"
    deck.write_text("<html></html>", encoding="utf-8")
    result = _runner_invoke(["diff", str(deck), "--touched"])
    # Should not crash; should report no history.
    assert result.exit_code == 0

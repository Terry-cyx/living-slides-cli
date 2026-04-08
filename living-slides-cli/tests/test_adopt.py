"""Tests for `slive adopt` — retrofit data-oid into existing HTML."""

from __future__ import annotations

import re

import pytest

from living_slides.adopt import adopt_html


# ---------- helpers ----------

def _oids(html: str) -> list[str]:
    return re.findall(r'data-oid="([^"]+)"', html)


# ---------- basic behavior ----------

def test_adopt_assigns_oid_to_meaningful_elements():
    html = """<!DOCTYPE html>
<html><body>
<section class="slide"><h1>Title</h1><p>Body text</p></section>
</body></html>"""
    out = adopt_html(html)
    oids = _oids(out)
    # slide + h1 + p = 3 oids minimum
    assert len(oids) >= 3
    assert all(oid for oid in oids)


def test_adopt_skips_unmeaningful_elements():
    html = "<html><head><title>x</title></head><body><div></div></body></html>"
    out = adopt_html(html)
    # title is in head, empty div has no content — neither should get an oid
    assert 'data-oid' not in out


def test_adopt_is_idempotent():
    html = '<section class="slide"><h1>Title</h1></section>'
    once = adopt_html(html)
    twice = adopt_html(once)
    assert once == twice


def test_adopt_preserves_existing_oids():
    html = '<section class="slide" data-oid="custom-slide"><h1>Title</h1></section>'
    out = adopt_html(html)
    # The custom oid must survive
    assert 'data-oid="custom-slide"' in out
    # And only one slide oid should exist (we didn't add a new one to the section)
    assert out.count('data-oid="custom-slide"') == 1


def test_adopt_unique_oids_within_document():
    html = """<section class="slide"><h1>A</h1><p>p1</p><p>p2</p></section>
<section class="slide"><h1>B</h1><p>p3</p></section>"""
    out = adopt_html(html)
    oids = _oids(out)
    assert len(oids) == len(set(oids)), f"oids not unique: {oids}"


# ---------- strategies ----------

def test_adopt_sequential_strategy_format():
    html = '<section class="slide"><h1>A</h1><p>x</p></section>'
    out = adopt_html(html, strategy="sequential")
    oids = _oids(out)
    # Sequential: s0-o0, s0-o1, ...
    assert all(re.match(r"s\d+-o\d+$", oid) for oid in oids), oids


def test_adopt_role_strategy_uses_role_hint():
    html = '<section class="slide"><h1>A</h1><img src="x.png"></section>'
    out = adopt_html(html, strategy="role")
    oids = _oids(out)
    joined = " ".join(oids)
    # Role strategy should mention semantic roles like title/image/slide
    assert "slide" in joined
    assert "title" in joined or "h1" in joined
    assert "image" in joined or "img" in joined


def test_adopt_hash_strategy_stable_across_runs():
    html = '<section class="slide"><h1>Hello</h1></section>'
    a = adopt_html(html, strategy="hash")
    b = adopt_html(html, strategy="hash")
    assert a == b
    # Same content → same oid
    assert _oids(a) == _oids(b)


def test_adopt_hash_strategy_changes_with_content():
    a = adopt_html('<section class="slide"><h1>Hello</h1></section>', strategy="hash")
    b = adopt_html('<section class="slide"><h1>World</h1></section>', strategy="hash")
    # The h1 oid should differ because the text differs
    assert _oids(a) != _oids(b)


def test_adopt_unknown_strategy_raises():
    with pytest.raises(ValueError):
        adopt_html("<section class='slide'></section>", strategy="bogus")


# ---------- frontend-slides retrofit ----------

def test_adopt_handles_frontend_slides_style_deck():
    """A deck like frontend-slides outputs — many slides, no data-oid anywhere."""
    html = """<!DOCTYPE html>
<html><head><style>.slide{height:100vh}</style></head><body>
<section class="slide" id="slide-1"><h1>Cover</h1><p>subtitle</p></section>
<section class="slide" id="slide-2"><h2>Agenda</h2><ul><li>A</li><li>B</li></ul></section>
<section class="slide" id="slide-3"><h2>Done</h2></section>
</body></html>"""
    out = adopt_html(html)
    oids = _oids(out)
    assert len(oids) >= 6  # 3 slides + at least h1, h2x2, p, li x2
    assert len(oids) == len(set(oids))


# ---------- CLI integration ----------

def test_cli_adopt_writes_back_in_place(tmp_path):
    from click.testing import CliRunner
    from living_slides.cli import main

    f = tmp_path / "deck.html"
    f.write_text(
        '<section class="slide"><h1>Title</h1></section>',
        encoding="utf-8",
    )
    runner = CliRunner()
    result = runner.invoke(main, ["adopt", str(f)])
    assert result.exit_code == 0, result.output
    assert 'data-oid' in f.read_text(encoding="utf-8")


def test_cli_adopt_dry_run_does_not_write(tmp_path):
    from click.testing import CliRunner
    from living_slides.cli import main

    f = tmp_path / "deck.html"
    original = '<section class="slide"><h1>Title</h1></section>'
    f.write_text(original, encoding="utf-8")
    runner = CliRunner()
    result = runner.invoke(main, ["adopt", str(f), "--dry-run"])
    assert result.exit_code == 0
    assert f.read_text(encoding="utf-8") == original
    # Output should preview the changes
    assert "data-oid" in result.output or "would" in result.output.lower()

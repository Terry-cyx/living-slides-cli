"""Tests for granular differ change types (Phase C4).

New change types:
  element_moved      element kept its data-oid but changed parent or sibling order
  element_resized    style attr changed only left/top/width/height
  slides_reordered   <section class="slide"> elements reshuffled
"""

from __future__ import annotations

from living_slides.differ import compute_changelog


def _types(changelog):
    return [c["type"] for c in changelog["changes"]]


def _by_type(changelog, t):
    return [c for c in changelog["changes"] if c["type"] == t]


# ---------- element_resized ----------

def test_style_change_left_top_classifies_as_resized():
    old = '<div data-oid="s0-card" style="left:10%;top:20%;width:30%;height:40%">x</div>'
    new = '<div data-oid="s0-card" style="left:50%;top:60%;width:30%;height:40%">x</div>'
    cl = compute_changelog(old, new, "deck.html")
    assert "element_resized" in _types(cl)
    # Must NOT also emit a generic attribute_change for the same attr.
    attr_changes = [c for c in _by_type(cl, "attribute_change") if c.get("attribute") == "style"]
    assert attr_changes == []


def test_style_change_only_width_height_classifies_as_resized():
    old = '<div data-oid="x" style="width:100px;height:50px">x</div>'
    new = '<div data-oid="x" style="width:200px;height:100px">x</div>'
    cl = compute_changelog(old, new, "deck.html")
    assert "element_resized" in _types(cl)


def test_style_change_other_property_stays_attribute_change():
    old = '<div data-oid="x" style="color:red;left:10%">x</div>'
    new = '<div data-oid="x" style="color:blue;left:10%">x</div>'
    cl = compute_changelog(old, new, "deck.html")
    # Color changed → not a pure resize → fall back to attribute_change
    assert "element_resized" not in _types(cl)
    assert any(c.get("attribute") == "style" for c in _by_type(cl, "attribute_change"))


# ---------- slides_reordered ----------

def test_slides_reordered_emitted_when_slide_order_changes():
    old = """<section class="slide" data-oid="s0"><h1>A</h1></section>
<section class="slide" data-oid="s1"><h1>B</h1></section>
<section class="slide" data-oid="s2"><h1>C</h1></section>"""
    new = """<section class="slide" data-oid="s2"><h1>C</h1></section>
<section class="slide" data-oid="s0"><h1>A</h1></section>
<section class="slide" data-oid="s1"><h1>B</h1></section>"""
    cl = compute_changelog(old, new, "deck.html")
    reorders = _by_type(cl, "slides_reordered")
    assert len(reorders) == 1
    assert reorders[0]["before"] == ["s0", "s1", "s2"]
    assert reorders[0]["after"] == ["s2", "s0", "s1"]


def test_no_slides_reordered_when_order_unchanged():
    html = """<section class="slide" data-oid="s0"><h1>A</h1></section>
<section class="slide" data-oid="s1"><h1>B</h1></section>"""
    cl = compute_changelog(html, html, "deck.html")
    assert "slides_reordered" not in _types(cl)


def test_no_slides_reordered_when_oids_missing():
    old = '<section class="slide"><h1>A</h1></section>'
    new = '<section class="slide"><h1>B</h1></section>'
    cl = compute_changelog(old, new, "deck.html")
    # Without oids we cannot identify slides — no reorder claim.
    assert "slides_reordered" not in _types(cl)


# ---------- element_moved ----------

def test_element_moved_when_sibling_order_changes():
    old = """<div class="card-row">
<div data-oid="c1">one</div>
<div data-oid="c2">two</div>
<div data-oid="c3">three</div>
</div>"""
    new = """<div class="card-row">
<div data-oid="c2">two</div>
<div data-oid="c1">one</div>
<div data-oid="c3">three</div>
</div>"""
    cl = compute_changelog(old, new, "deck.html")
    moved = _by_type(cl, "element_moved")
    moved_oids = {m["selector"] for m in moved}
    # c1 and c2 swapped — at least one of them should be reported as moved.
    assert moved_oids & {'[data-oid="c1"]', '[data-oid="c2"]'}

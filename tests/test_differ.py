import json
from htmlcli.differ import compute_changelog


def test_no_changes():
    html = "<div><h1>Hello</h1></div>"
    result = compute_changelog(html, html, "test.html")
    assert result["changes"] == []
    assert result["file"] == "test.html"


def test_text_change():
    old = '<div><h1 class="title">Hello</h1></div>'
    new = '<div><h1 class="title">World</h1></div>'
    result = compute_changelog(old, new, "test.html")
    assert len(result["changes"]) > 0
    assert result["changes"][0]["type"] == "text_edit"


def test_attribute_change():
    old = '<div style="color: red;">Hello</div>'
    new = '<div style="color: blue;">Hello</div>'
    result = compute_changelog(old, new, "test.html")
    assert len(result["changes"]) > 0


def test_element_added():
    old = "<div><p>Hello</p></div>"
    new = "<div><p>Hello</p><p>World</p></div>"
    result = compute_changelog(old, new, "test.html")
    assert len(result["changes"]) > 0


def test_changelog_has_summary():
    old = "<div><p>Hello</p></div>"
    new = "<div><p>World</p></div>"
    result = compute_changelog(old, new, "test.html")
    assert "summary" in result
    assert isinstance(result["summary"], str)
    assert len(result["summary"]) > 0


def test_changelog_has_timestamp():
    old = "<div><p>Hello</p></div>"
    new = "<div><p>World</p></div>"
    result = compute_changelog(old, new, "test.html")
    assert "timestamp" in result


def test_data_oid_used_as_selector():
    """data-oid on the text-bearing element takes precedence over tag/class selectors."""
    old = '<div class="x"><h1 data-oid="s1-title" class="big">Hello</h1></div>'
    new = '<div class="x"><h1 data-oid="s1-title" class="big">World</h1></div>'
    result = compute_changelog(old, new, "test.html")
    assert any(
        c["selector"] == '[data-oid="s1-title"]'
        for c in result["changes"]
    ), f"Expected [data-oid=\"s1-title\"] selector, got: {[c['selector'] for c in result['changes']]}"


def test_data_oid_survives_dom_path_change():
    """When DOM-path drifts (extra wrapper added), data-oid still locates the same logical object."""
    old = '<div><p data-oid="s2-lede">Original text</p></div>'
    # User wraps the paragraph in a new section — CSS path changes, data-oid does not
    new = '<div><section><p data-oid="s2-lede">Updated text</p></section></div>'
    result = compute_changelog(old, new, "test.html")
    text_edits = [c for c in result["changes"] if c["type"] == "text_edit"]
    assert any(
        c["selector"] == '[data-oid="s2-lede"]' and c["after"] == "Updated text"
        for c in text_edits
    ), f"Expected stable [data-oid=\"s2-lede\"] text_edit, got: {text_edits}"


def test_save_changelog(tmp_path):
    from htmlcli.differ import save_changelog

    old = '<h1 class="title">Hello</h1>'
    new = '<h1 class="title">World</h1>'
    changelog = compute_changelog(old, new, "test.html")

    out_file = tmp_path / "test.changelog.json"
    save_changelog(changelog, str(out_file))

    loaded = json.loads(out_file.read_text(encoding="utf-8"))
    assert loaded["file"] == "test.html"
    assert len(loaded["changes"]) > 0

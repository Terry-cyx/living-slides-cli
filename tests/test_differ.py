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

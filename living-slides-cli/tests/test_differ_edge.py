"""Edge case tests for the differ module — ensuring robustness with real-world HTML."""

from living_slides.differ import compute_changelog


class TestDuplicateElements:
    """Multiple elements with the same tag but no class/id — common in real HTML."""

    def test_multiple_paragraphs_different_text(self):
        old = "<div><p>First</p><p>Second</p><p>Third</p></div>"
        new = "<div><p>First</p><p>Modified</p><p>Third</p></div>"
        result = compute_changelog(old, new, "test.html")
        text_edits = [c for c in result["changes"] if c["type"] == "text_edit"]
        assert len(text_edits) >= 1
        assert any("Modified" in c["after"] for c in text_edits)

    def test_multiple_list_items(self):
        old = "<ul><li>Apple</li><li>Banana</li><li>Cherry</li></ul>"
        new = "<ul><li>Apple</li><li>Blueberry</li><li>Cherry</li></ul>"
        result = compute_changelog(old, new, "test.html")
        text_edits = [c for c in result["changes"] if c["type"] == "text_edit"]
        assert len(text_edits) >= 1
        assert any("Blueberry" in c["after"] for c in text_edits)

    def test_add_list_item(self):
        old = "<ul><li>Apple</li><li>Banana</li></ul>"
        new = "<ul><li>Apple</li><li>Banana</li><li>Cherry</li></ul>"
        result = compute_changelog(old, new, "test.html")
        assert len(result["changes"]) > 0


class TestNestedElements:
    """Deeply nested elements — common in real presentation HTML."""

    def test_nested_div_text_change(self):
        old = '<div class="card"><div class="body"><h3>Title</h3><p>Old text</p></div></div>'
        new = '<div class="card"><div class="body"><h3>Title</h3><p>New text</p></div></div>'
        result = compute_changelog(old, new, "test.html")
        text_edits = [c for c in result["changes"] if c["type"] == "text_edit"]
        assert len(text_edits) >= 1
        assert any("New text" in c["after"] for c in text_edits)

    def test_nested_style_change(self):
        old = '<div class="hero" style="background: red;"><h1>Hello</h1></div>'
        new = '<div class="hero" style="background: blue;"><h1>Hello</h1></div>'
        result = compute_changelog(old, new, "test.html")
        attr_changes = [c for c in result["changes"] if c["type"] == "attribute_change"]
        assert len(attr_changes) >= 1


class TestEmptyAndMinimal:
    """Edge cases with empty content."""

    def test_empty_to_content(self):
        old = "<div></div>"
        new = "<div><p>Hello World</p></div>"
        result = compute_changelog(old, new, "test.html")
        assert len(result["changes"]) > 0

    def test_content_to_empty(self):
        old = "<div><p>Hello</p></div>"
        new = "<div></div>"
        result = compute_changelog(old, new, "test.html")
        assert len(result["changes"]) > 0

    def test_completely_empty(self):
        result = compute_changelog("", "", "test.html")
        assert result["changes"] == []
        assert result["summary"] == "No changes detected"

    def test_whitespace_only_difference(self):
        """Whitespace-only differences in text should not generate changes."""
        old = "<p>  Hello  </p>"
        new = "<p>Hello</p>"
        result = compute_changelog(old, new, "test.html")
        # Both should parse to "Hello" after strip
        text_edits = [c for c in result["changes"] if c["type"] == "text_edit"]
        assert len(text_edits) == 0


class TestComplexStructures:
    """Real-world complex HTML structures from presentations."""

    def test_table_cell_edit(self):
        old = "<table><tr><td>Old</td><td>B</td></tr></table>"
        new = "<table><tr><td>New</td><td>B</td></tr></table>"
        result = compute_changelog(old, new, "test.html")
        text_edits = [c for c in result["changes"] if c["type"] == "text_edit"]
        assert len(text_edits) >= 1

    def test_multiple_class_element(self):
        old = '<div class="kpi-card metric highlight">100</div>'
        new = '<div class="kpi-card metric highlight">200</div>'
        result = compute_changelog(old, new, "test.html")
        text_edits = [c for c in result["changes"] if c["type"] == "text_edit"]
        assert len(text_edits) >= 1
        assert text_edits[0]["before"] == "100"
        assert text_edits[0]["after"] == "200"

    def test_class_change(self):
        old = '<span class="badge badge-get">GET</span>'
        new = '<span class="badge badge-post">POST</span>'
        result = compute_changelog(old, new, "test.html")
        # Should detect both class change and text change
        assert len(result["changes"]) >= 1


class TestSummaryQuality:
    """Summary should accurately describe what changed."""

    def test_summary_mentions_text_edits(self):
        old = "<p>Hello</p>"
        new = "<p>World</p>"
        result = compute_changelog(old, new, "test.html")
        assert "text" in result["summary"].lower()

    def test_summary_mentions_added_elements(self):
        old = "<div></div>"
        new = "<div><p>New</p></div>"
        result = compute_changelog(old, new, "test.html")
        assert "added" in result["summary"].lower()

    def test_summary_mentions_removed_elements(self):
        old = "<div><p>Old</p></div>"
        new = "<div></div>"
        result = compute_changelog(old, new, "test.html")
        assert "removed" in result["summary"].lower()

    def test_summary_combines_multiple_change_types(self):
        old = '<div><p class="a">Hello</p></div>'
        new = '<div><p class="a">World</p><span>New</span></div>'
        result = compute_changelog(old, new, "test.html")
        # Should mention both text edits and additions
        assert ";" in result["summary"] or len(result["changes"]) >= 2

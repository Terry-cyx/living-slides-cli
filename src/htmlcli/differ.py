"""HTML diff and changelog generation for Claude Code integration."""

from __future__ import annotations

import json
import difflib
from datetime import datetime, timezone
from html.parser import HTMLParser


class _TagExtractor(HTMLParser):
    """Extract tags with their attributes and text content."""

    def __init__(self):
        super().__init__()
        self.elements: list[dict] = []
        self._stack: list[dict] = []

    def handle_starttag(self, tag, attrs):
        elem = {
            "tag": tag,
            "attrs": dict(attrs),
            "text": "",
            "children": [],
            "selector": self._make_selector(tag, dict(attrs)),
        }
        if self._stack:
            self._stack[-1]["children"].append(elem)
        else:
            self.elements.append(elem)
        self._stack.append(elem)

    def handle_endtag(self, tag):
        if self._stack and self._stack[-1]["tag"] == tag:
            self._stack.pop()

    def handle_data(self, data):
        text = data.strip()
        if text and self._stack:
            self._stack[-1]["text"] += text

    def _make_selector(self, tag: str, attrs: dict) -> str:
        # `data-oid` is htmlcli's stable object identifier (adapted from
        # frontend-slides-editable's editor-runtime DOM contract). When present,
        # it is the most reliable selector — it survives DOM-path drift after
        # the user moves elements around in the visual editor.
        if "data-oid" in attrs:
            return f'[data-oid="{attrs["data-oid"]}"]'
        sel = tag
        if "id" in attrs:
            sel += f"#{attrs['id']}"
        if "class" in attrs:
            classes = attrs["class"].split()
            sel += "".join(f".{c}" for c in classes)
        return sel


def _flatten_elements(elements: list[dict]) -> list[dict]:
    """Flatten nested element tree into a list."""
    result = []
    for elem in elements:
        result.append(elem)
        result.extend(_flatten_elements(elem.get("children", [])))
    return result


def _parse_html(html: str) -> list[dict]:
    parser = _TagExtractor()
    parser.feed(html)
    elements = _flatten_elements(parser.elements)
    # Disambiguate duplicate selectors by appending an index
    seen: dict[str, int] = {}
    for elem in elements:
        sel = elem["selector"]
        if sel in seen:
            seen[sel] += 1
            elem["selector"] = f"{sel}:nth({seen[sel]})"
        else:
            seen[sel] = 0
    return elements


def compute_changelog(old_html: str, new_html: str, filename: str) -> dict:
    """Compare two HTML strings and produce a structured changelog."""
    changes: list[dict] = []

    old_elements = _parse_html(old_html)
    new_elements = _parse_html(new_html)

    # Build lookup by selector
    old_by_sel = {}
    for elem in old_elements:
        sel = elem["selector"]
        if sel not in old_by_sel:
            old_by_sel[sel] = elem

    new_by_sel = {}
    for elem in new_elements:
        sel = elem["selector"]
        if sel not in new_by_sel:
            new_by_sel[sel] = elem

    # Detect text changes
    for sel, new_elem in new_by_sel.items():
        if sel in old_by_sel:
            old_elem = old_by_sel[sel]
            if old_elem["text"] != new_elem["text"] and (old_elem["text"] or new_elem["text"]):
                changes.append({
                    "type": "text_edit",
                    "selector": sel,
                    "before": old_elem["text"],
                    "after": new_elem["text"],
                })
            # Detect attribute changes
            old_attrs = old_elem["attrs"]
            new_attrs = new_elem["attrs"]
            if old_attrs != new_attrs:
                for key in set(list(old_attrs.keys()) + list(new_attrs.keys())):
                    old_val = old_attrs.get(key, "")
                    new_val = new_attrs.get(key, "")
                    if old_val != new_val:
                        changes.append({
                            "type": "attribute_change",
                            "selector": sel,
                            "attribute": key,
                            "before": old_val,
                            "after": new_val,
                        })
        else:
            changes.append({
                "type": "element_added",
                "selector": sel,
                "tag": new_elem["tag"],
            })

    for sel in old_by_sel:
        if sel not in new_by_sel:
            changes.append({
                "type": "element_removed",
                "selector": sel,
                "tag": old_by_sel[sel]["tag"],
            })

    # Also include a unified diff for completeness
    diff_lines = list(difflib.unified_diff(
        old_html.splitlines(keepends=True),
        new_html.splitlines(keepends=True),
        fromfile=f"a/{filename}",
        tofile=f"b/{filename}",
    ))

    # Generate summary
    summary_parts = []
    text_edits = [c for c in changes if c["type"] == "text_edit"]
    attr_changes = [c for c in changes if c["type"] == "attribute_change"]
    added = [c for c in changes if c["type"] == "element_added"]
    removed = [c for c in changes if c["type"] == "element_removed"]

    if text_edits:
        summary_parts.append(f"Modified text in {len(text_edits)} element(s)")
    if attr_changes:
        summary_parts.append(f"Changed attributes in {len(attr_changes)} element(s)")
    if added:
        summary_parts.append(f"Added {len(added)} element(s)")
    if removed:
        summary_parts.append(f"Removed {len(removed)} element(s)")

    summary = "; ".join(summary_parts) if summary_parts else "No changes detected"

    return {
        "file": filename,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "changes": changes,
        "diff": "".join(diff_lines),
        "summary": summary,
    }


def save_changelog(changelog: dict, path: str) -> None:
    """Save changelog to a JSON file."""
    with open(path, "w", encoding="utf-8") as f:
        json.dump(changelog, f, ensure_ascii=False, indent=2)

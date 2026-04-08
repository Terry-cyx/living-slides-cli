"""HTML diff and changelog generation for Claude Code integration.

The granular `element_moved`, `element_resized`, and `slides_reordered`
change types are inspired by the editable-deck-reference.html undo
command taxonomy (frontend-slides-editable, MIT). Adopted here so the
changelog gives AI more semantic info for cascade reasoning.
"""

from __future__ import annotations

import json
import difflib
import re
from datetime import datetime, timezone
from html.parser import HTMLParser


# Style properties that count as a "resize/reposition" rather than a styling edit.
_RESIZE_PROPS = {"left", "top", "width", "height"}


class _TagExtractor(HTMLParser):
    """Extract tags with their attributes, text, and structural position."""

    def __init__(self):
        super().__init__()
        self.elements: list[dict] = []
        self._stack: list[dict] = []
        # Sibling counters keyed by parent id (id() of parent dict, or None for root).
        self._sibling_counters: dict[int, int] = {}

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        parent = self._stack[-1] if self._stack else None
        parent_key = id(parent) if parent is not None else 0
        idx = self._sibling_counters.get(parent_key, 0)
        self._sibling_counters[parent_key] = idx + 1
        elem = {
            "tag": tag,
            "attrs": attrs_dict,
            "text": "",
            "children": [],
            "selector": self._make_selector(tag, attrs_dict),
            "oid": attrs_dict.get("data-oid"),
            "parent_oid": parent.get("oid") if parent else None,
            "sibling_index": idx,
        }
        if parent is not None:
            parent["children"].append(elem)
        else:
            self.elements.append(elem)
        self._stack.append(elem)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        self.handle_endtag(tag)

    def handle_endtag(self, tag):
        if self._stack and self._stack[-1]["tag"] == tag:
            self._stack.pop()

    def handle_data(self, data):
        text = data.strip()
        if text and self._stack:
            self._stack[-1]["text"] += text

    def _make_selector(self, tag: str, attrs: dict) -> str:
        # `data-oid` is living-slides' stable object identifier (adapted from
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


def _parse_style(style: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for part in style.split(";"):
        if ":" not in part:
            continue
        k, v = part.split(":", 1)
        k = k.strip().lower()
        v = v.strip()
        if k:
            out[k] = v
    return out


def _is_pure_resize(old_style: str, new_style: str) -> bool:
    """True if the only differences between two style strings are resize props."""
    old = _parse_style(old_style)
    new = _parse_style(new_style)
    diff_keys = {k for k in set(old) | set(new) if old.get(k) != new.get(k)}
    if not diff_keys:
        return False
    return diff_keys.issubset(_RESIZE_PROPS)


def _slide_oids_in_order(elements: list[dict]) -> list[str]:
    """Return data-oid values of `<section|article class*=slide>` in document order."""
    oids: list[str] = []
    for el in elements:
        if el["tag"] not in ("section", "article"):
            continue
        if not el["oid"]:
            continue
        cls = (el["attrs"].get("class") or "").split()
        if "slide" in cls:
            oids.append(el["oid"])
    return oids


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

    # Slides reordered? Compare oid sequences for top-level slide containers.
    old_slide_order = _slide_oids_in_order(old_elements)
    new_slide_order = _slide_oids_in_order(new_elements)
    slides_reordered_oids: set[str] = set()
    if (
        old_slide_order
        and set(old_slide_order) == set(new_slide_order)
        and old_slide_order != new_slide_order
    ):
        changes.append({
            "type": "slides_reordered",
            "selector": "",
            "before": old_slide_order,
            "after": new_slide_order,
        })
        slides_reordered_oids = set(old_slide_order)

    # Detect text/attribute/move/resize on shared elements; added/removed otherwise.
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

            # element_moved: same oid, different parent or different sibling index.
            # Skip top-level slide containers already covered by slides_reordered.
            if (
                new_elem["oid"]
                and new_elem["oid"] not in slides_reordered_oids
                and (
                    old_elem["parent_oid"] != new_elem["parent_oid"]
                    or old_elem["sibling_index"] != new_elem["sibling_index"]
                )
            ):
                changes.append({
                    "type": "element_moved",
                    "selector": sel,
                    "from_parent": old_elem["parent_oid"],
                    "to_parent": new_elem["parent_oid"],
                    "from_index": old_elem["sibling_index"],
                    "to_index": new_elem["sibling_index"],
                })

            # Attribute changes — but classify pure style resizes specially.
            old_attrs = old_elem["attrs"]
            new_attrs = new_elem["attrs"]
            if old_attrs != new_attrs:
                for key in set(list(old_attrs.keys()) + list(new_attrs.keys())):
                    old_val = old_attrs.get(key, "")
                    new_val = new_attrs.get(key, "")
                    if old_val == new_val:
                        continue
                    if key == "style" and _is_pure_resize(old_val, new_val):
                        changes.append({
                            "type": "element_resized",
                            "selector": sel,
                            "before": old_val,
                            "after": new_val,
                        })
                        continue
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
    by_type: dict[str, int] = {}
    for c in changes:
        by_type[c["type"]] = by_type.get(c["type"], 0) + 1

    if by_type.get("text_edit"):
        summary_parts.append(f"Modified text in {by_type['text_edit']} element(s)")
    if by_type.get("attribute_change"):
        summary_parts.append(f"Changed attributes in {by_type['attribute_change']} element(s)")
    if by_type.get("element_resized"):
        summary_parts.append(f"Resized/repositioned {by_type['element_resized']} element(s)")
    if by_type.get("element_moved"):
        summary_parts.append(f"Moved {by_type['element_moved']} element(s)")
    if by_type.get("slides_reordered"):
        summary_parts.append("Reordered slides")
    if by_type.get("element_added"):
        summary_parts.append(f"Added {by_type['element_added']} element(s)")
    if by_type.get("element_removed"):
        summary_parts.append(f"Removed {by_type['element_removed']} element(s)")

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

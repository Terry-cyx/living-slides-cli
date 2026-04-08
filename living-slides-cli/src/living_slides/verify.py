"""Asset/reference checker (Phase C3).

`slive verify` walks an HTML file and reports any `<img src>`,
`<script src>`, or `<link href>` that points to a local file that does
not exist. Common P1 failure mode: AI generates a deck that references
images it never produced; user opens it and sees broken alt text.
"""

from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path


# (tag, attribute) pairs whose value is a URL we should resolve.
_REF_ATTRS = {
    "img": "src",
    "script": "src",
    "link": "href",
    "video": "src",
    "audio": "src",
    "source": "src",
}


class _RefCollector(HTMLParser):
    def __init__(self):
        super().__init__()
        self.refs: list[dict] = []
        self._stack: list[str] = []

    def handle_starttag(self, tag, attrs):
        self._stack.append(tag)
        attr = _REF_ATTRS.get(tag)
        if attr is None:
            return
        attrs_dict = dict(attrs)
        url = attrs_dict.get(attr)
        if not url:
            return
        line, _ = self.getpos()
        self.refs.append({
            "tag": tag,
            "src": url,
            "oid": attrs_dict.get("data-oid"),
            "line": line,
        })

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if self._stack:
            self._stack.pop()

    def handle_endtag(self, tag):
        if self._stack and self._stack[-1] == tag:
            self._stack.pop()


def _is_external(url: str) -> bool:
    if url.startswith(("http://", "https://", "//", "data:", "mailto:", "tel:", "javascript:")):
        return True
    if url.startswith("#"):
        return True
    return False


def verify_html(html_path: str) -> list[dict]:
    """Return a list of broken-reference issues for `html_path`."""
    path = Path(html_path)
    html = path.read_text(encoding="utf-8")
    parser = _RefCollector()
    parser.feed(html)

    base = path.parent
    issues: list[dict] = []
    for ref in parser.refs:
        url = ref["src"]
        if _is_external(url):
            continue
        # Strip query strings / fragments before resolving on disk.
        clean = url.split("?", 1)[0].split("#", 1)[0]
        if not clean:
            continue
        target = (base / clean).resolve()
        if not target.exists():
            issues.append(ref)
    return issues

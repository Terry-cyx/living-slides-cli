# HTML CLI Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Python CLI tool that launches a GrapesJS visual HTML editor in the browser and tracks changes for Claude Code integration.

**Architecture:** Python CLI (click) starts an aiohttp web server serving a GrapesJS-based editor page. The editor loads HTML files, lets users edit visually, and saves back with a structured changelog that Claude Code can read.

**Tech Stack:** Python 3.13, uv, click, aiohttp, GrapesJS (CDN), difflib

---

### Task 1: Project Scaffolding with uv

**Files:**
- Create: `pyproject.toml`
- Create: `src/htmlcli/__init__.py`

- [ ] **Step 1: Initialize uv project**

```bash
cd E:/HTML_CLI
uv init --lib --name htmlcli
```

If uv init creates files in wrong locations, manually adjust. The goal is this structure:
```
pyproject.toml
src/htmlcli/__init__.py
```

- [ ] **Step 2: Configure pyproject.toml**

Replace `pyproject.toml` with:

```toml
[project]
name = "htmlcli"
version = "0.1.0"
description = "Visual HTML editor CLI for AI-assisted workflows"
requires-python = ">=3.11"
dependencies = [
    "click>=8.1",
    "aiohttp>=3.9",
]

[project.scripts]
htmlcli = "htmlcli.cli:main"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.backends"

[tool.hatch.build.targets.wheel]
packages = ["src/htmlcli"]

[tool.pytest.ini_options]
testpaths = ["tests"]
```

- [ ] **Step 3: Install dependencies**

```bash
cd E:/HTML_CLI
uv sync
```

- [ ] **Step 4: Create __init__.py**

```python
"""HTML CLI - Visual HTML editor for AI-assisted workflows."""
```

- [ ] **Step 5: Verify installation**

```bash
cd E:/HTML_CLI
uv run python -c "import htmlcli; print('OK')"
```

Expected: `OK`

- [ ] **Step 6: Initialize git and commit**

```bash
cd E:/HTML_CLI
git init
echo -e ".venv/\n__pycache__/\n*.egg-info/\n.superpowers/" > .gitignore
git add pyproject.toml src/htmlcli/__init__.py .gitignore CLAUDE.md
git commit -m "chore: initialize htmlcli project with uv"
```

---

### Task 2: Change Tracker (differ.py)

**Files:**
- Create: `src/htmlcli/differ.py`
- Create: `tests/test_differ.py`

- [ ] **Step 1: Write failing tests**

Create `tests/__init__.py` (empty) and `tests/test_differ.py`:

```python
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
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd E:/HTML_CLI
uv run pytest tests/test_differ.py -v
```

Expected: FAIL — `ModuleNotFoundError: No module named 'htmlcli.differ'`

- [ ] **Step 3: Implement differ.py**

Create `src/htmlcli/differ.py`:

```python
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
    return _flatten_elements(parser.elements)


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
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
cd E:/HTML_CLI
uv run pytest tests/test_differ.py -v
```

Expected: All tests PASS

- [ ] **Step 5: Commit**

```bash
cd E:/HTML_CLI
git add src/htmlcli/differ.py tests/
git commit -m "feat: add HTML diff and changelog tracker"
```

---

### Task 3: GrapesJS Frontend Editor

**Files:**
- Create: `src/htmlcli/static/editor.html`
- Create: `src/htmlcli/static/editor.js`

- [ ] **Step 1: Create editor.html**

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>HTML CLI Editor</title>
    <link rel="stylesheet" href="https://unpkg.com/grapesjs/dist/css/grapes.min.css">
    <style>
        body, html { margin: 0; padding: 0; height: 100%; }
        .gjs-cv-canvas { top: 0; width: 100%; height: 100%; }
        #gjs { height: 100vh; }
        .save-status {
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: #238636;
            color: white;
            padding: 8px 16px;
            border-radius: 6px;
            font-family: sans-serif;
            font-size: 14px;
            z-index: 10000;
            display: none;
            transition: opacity 0.3s;
        }
    </style>
</head>
<body>
    <div id="gjs"></div>
    <div id="save-status" class="save-status">Saved!</div>
    <script src="https://unpkg.com/grapesjs"></script>
    <script src="/static/editor.js"></script>
</body>
</html>
```

- [ ] **Step 2: Create editor.js**

```javascript
(function() {
    const editor = grapesjs.init({
        container: '#gjs',
        fromElement: false,
        storageManager: false,
        plugins: [],
        canvas: {
            styles: [],
            scripts: [],
        },
        panels: { defaults: [] },
    });

    // Add save button to toolbar
    editor.Panels.addButton('options', {
        id: 'save-btn',
        className: 'fa fa-floppy-o',
        command: 'save-html',
        attributes: { title: 'Save (Ctrl+S)' },
        label: '💾 Save',
    });

    // Load HTML from server on init
    fetch('/api/load')
        .then(r => r.json())
        .then(data => {
            if (data.html) {
                editor.setComponents(data.html);
                if (data.css) {
                    editor.setStyle(data.css);
                }
            }
        })
        .catch(err => console.error('Failed to load HTML:', err));

    // Save command
    editor.Commands.add('save-html', {
        run: function(editor) {
            const html = editor.getHtml();
            const css = editor.getCss();
            
            fetch('/api/save', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ html, css }),
            })
            .then(r => r.json())
            .then(data => {
                const status = document.getElementById('save-status');
                if (data.ok) {
                    status.textContent = 'Saved! ' + (data.summary || '');
                    status.style.background = '#238636';
                } else {
                    status.textContent = 'Save failed: ' + (data.error || 'unknown');
                    status.style.background = '#da3633';
                }
                status.style.display = 'block';
                setTimeout(() => { status.style.display = 'none'; }, 3000);
            })
            .catch(err => {
                console.error('Save failed:', err);
            });
        },
    });

    // Ctrl+S shortcut
    document.addEventListener('keydown', function(e) {
        if ((e.ctrlKey || e.metaKey) && e.key === 's') {
            e.preventDefault();
            editor.runCommand('save-html');
        }
    });
})();
```

- [ ] **Step 3: Commit**

```bash
cd E:/HTML_CLI
git add src/htmlcli/static/
git commit -m "feat: add GrapesJS frontend editor"
```

---

### Task 4: Web Server (server.py)

**Files:**
- Create: `src/htmlcli/server.py`
- Create: `tests/test_server.py`

- [ ] **Step 1: Write failing tests**

Create `tests/test_server.py`:

```python
import json
import asyncio
import pytest
from aiohttp import web
from aiohttp.test_utils import AioHTTPTestCase, unittest_run_loop
from pathlib import Path
from htmlcli.server import create_app


@pytest.fixture
def html_file(tmp_path):
    f = tmp_path / "test.html"
    f.write_text("<div><h1>Hello World</h1></div>", encoding="utf-8")
    return f


@pytest.fixture
def app(html_file):
    return create_app(str(html_file))


async def test_load_html(aiohttp_client, app):
    client = await aiohttp_client(app)
    resp = await client.get("/api/load")
    assert resp.status == 200
    data = await resp.json()
    assert "html" in data
    assert "Hello World" in data["html"]


async def test_save_html(aiohttp_client, app, html_file):
    client = await aiohttp_client(app)
    new_html = "<div><h1>Updated</h1></div>"
    resp = await client.post("/api/save", json={"html": new_html, "css": ""})
    assert resp.status == 200
    data = await resp.json()
    assert data["ok"] is True

    # Verify file was updated
    content = html_file.read_text(encoding="utf-8")
    assert "Updated" in content


async def test_save_creates_changelog(aiohttp_client, app, html_file):
    client = await aiohttp_client(app)
    resp = await client.post("/api/save", json={
        "html": "<div><h1>Changed</h1></div>",
        "css": "",
    })
    data = await resp.json()
    assert data["ok"] is True
    assert "summary" in data

    # Check changelog file exists
    changelog_path = html_file.parent / "test.changelog.json"
    assert changelog_path.exists()


async def test_editor_page(aiohttp_client, app):
    client = await aiohttp_client(app)
    resp = await client.get("/")
    assert resp.status == 200
    text = await resp.text()
    assert "grapesjs" in text.lower() or "gjs" in text.lower()
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd E:/HTML_CLI
uv run pytest tests/test_server.py -v
```

Expected: FAIL — `ModuleNotFoundError: No module named 'htmlcli.server'`

- [ ] **Step 3: Install pytest-aiohttp**

```bash
cd E:/HTML_CLI
uv add --dev pytest pytest-aiohttp
```

- [ ] **Step 4: Implement server.py**

Create `src/htmlcli/server.py`:

```python
"""Local web server for GrapesJS HTML editor."""

from __future__ import annotations

import os
from pathlib import Path
from aiohttp import web

from htmlcli.differ import compute_changelog, save_changelog

STATIC_DIR = Path(__file__).parent / "static"


def create_app(html_path: str) -> web.Application:
    """Create the aiohttp application for serving the editor."""
    app = web.Application()
    app["html_path"] = os.path.abspath(html_path)
    app["original_html"] = ""

    # Load original HTML on startup
    path = Path(app["html_path"])
    if path.exists():
        app["original_html"] = path.read_text(encoding="utf-8")

    app.router.add_get("/", handle_editor)
    app.router.add_get("/api/load", handle_load)
    app.router.add_post("/api/save", handle_save)
    app.router.add_static("/static", STATIC_DIR)

    return app


async def handle_editor(request: web.Request) -> web.Response:
    """Serve the GrapesJS editor page."""
    editor_path = STATIC_DIR / "editor.html"
    return web.FileResponse(editor_path)


async def handle_load(request: web.Request) -> web.Response:
    """Return the current HTML file content."""
    html_path = Path(request.app["html_path"])
    if not html_path.exists():
        return web.json_response({"html": "", "css": ""})

    content = html_path.read_text(encoding="utf-8")

    # Try to extract inline CSS from <style> tags
    html = content
    css = ""

    return web.json_response({"html": html, "css": css})


async def handle_save(request: web.Request) -> web.Response:
    """Save edited HTML and generate changelog."""
    try:
        data = await request.json()
    except Exception:
        return web.json_response({"ok": False, "error": "Invalid JSON"}, status=400)

    html = data.get("html", "")
    css = data.get("css", "")

    html_path = Path(request.app["html_path"])
    filename = html_path.name

    # Combine HTML with CSS if present
    if css and css.strip():
        full_html = f"<style>\n{css}\n</style>\n{html}"
    else:
        full_html = html

    # Generate changelog
    original = request.app["original_html"]
    changelog = compute_changelog(original, full_html, filename)

    # Write HTML file
    html_path.write_text(full_html, encoding="utf-8")

    # Write changelog
    changelog_name = html_path.stem + ".changelog.json"
    changelog_path = html_path.parent / changelog_name
    save_changelog(changelog, str(changelog_path))

    # Update original for next diff
    request.app["original_html"] = full_html

    return web.json_response({
        "ok": True,
        "summary": changelog["summary"],
        "changes_count": len(changelog["changes"]),
    })


def run_server(html_path: str, port: int = 8432) -> None:
    """Start the web server (blocking)."""
    app = create_app(html_path)
    web.run_app(app, host="127.0.0.1", port=port, print=lambda msg: None)
```

- [ ] **Step 5: Run tests to verify they pass**

```bash
cd E:/HTML_CLI
uv run pytest tests/test_server.py -v
```

Expected: All tests PASS

- [ ] **Step 6: Commit**

```bash
cd E:/HTML_CLI
git add src/htmlcli/server.py tests/test_server.py
git commit -m "feat: add aiohttp web server with load/save API"
```

---

### Task 5: CLI Entry Point (cli.py)

**Files:**
- Create: `src/htmlcli/cli.py`
- Create: `tests/test_cli.py`

- [ ] **Step 1: Write failing tests**

Create `tests/test_cli.py`:

```python
from click.testing import CliRunner
from htmlcli.cli import main
from pathlib import Path


def test_cli_help():
    runner = CliRunner()
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0
    assert "htmlcli" in result.output.lower() or "html" in result.output.lower()


def test_create_command(tmp_path):
    runner = CliRunner()
    filepath = str(tmp_path / "newpage.html")
    result = runner.invoke(main, ["create", filepath])
    assert result.exit_code == 0
    assert Path(filepath).exists()
    content = Path(filepath).read_text(encoding="utf-8")
    assert "<html" in content.lower()


def test_create_refuses_overwrite(tmp_path):
    filepath = tmp_path / "existing.html"
    filepath.write_text("<p>existing</p>", encoding="utf-8")
    runner = CliRunner()
    result = runner.invoke(main, ["create", str(filepath)])
    assert result.exit_code != 0 or "already exists" in result.output.lower() or "exists" in result.output.lower()


def test_diff_no_changelog(tmp_path):
    filepath = tmp_path / "test.html"
    filepath.write_text("<p>hello</p>", encoding="utf-8")
    runner = CliRunner()
    result = runner.invoke(main, ["diff", str(filepath)])
    assert "no changelog" in result.output.lower() or "not found" in result.output.lower()


def test_diff_with_changelog(tmp_path):
    import json

    filepath = tmp_path / "test.html"
    filepath.write_text("<p>hello</p>", encoding="utf-8")
    changelog = tmp_path / "test.changelog.json"
    changelog.write_text(json.dumps({
        "file": "test.html",
        "timestamp": "2026-04-04T00:00:00",
        "changes": [{"type": "text_edit", "selector": "p", "before": "old", "after": "new"}],
        "summary": "Modified text in 1 element(s)",
    }), encoding="utf-8")

    runner = CliRunner()
    result = runner.invoke(main, ["diff", str(filepath)])
    assert result.exit_code == 0
    assert "text_edit" in result.output or "Modified" in result.output
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd E:/HTML_CLI
uv run pytest tests/test_cli.py -v
```

Expected: FAIL — `ModuleNotFoundError: No module named 'htmlcli.cli'`

- [ ] **Step 3: Implement cli.py**

Create `src/htmlcli/cli.py`:

```python
"""CLI entry point for htmlcli."""

from __future__ import annotations

import json
import sys
import threading
import webbrowser
from pathlib import Path

import click


TEMPLATE = """\
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{
            font-family: -apple-system, 'Segoe UI', sans-serif;
            max-width: 960px;
            margin: 0 auto;
            padding: 2rem;
            color: #333;
        }}
        h1 {{ color: #1a1a2e; }}
    </style>
</head>
<body>
    <h1>{title}</h1>
    <p>This page was created by htmlcli. Edit it visually or with AI.</p>
</body>
</html>
"""

PID_FILE = Path.home() / ".htmlcli" / "server.pid"


@click.group()
@click.version_option(version="0.1.0")
def main():
    """htmlcli - Visual HTML editor for AI-assisted workflows."""
    pass


@main.command()
@click.argument("filepath")
@click.option("--port", default=8432, help="Server port (default: 8432)")
def open(filepath: str, port: int):
    """Open an HTML file in the visual editor."""
    path = Path(filepath).resolve()
    if not path.exists():
        click.echo(f"Error: File not found: {path}", err=True)
        sys.exit(1)

    click.echo(f"Opening {path.name} in visual editor...")
    click.echo(f"Editor URL: http://127.0.0.1:{port}")
    click.echo("Press Ctrl+C to stop the server.")

    # Open browser after a short delay
    def open_browser():
        import time
        time.sleep(1)
        webbrowser.open(f"http://127.0.0.1:{port}")

    threading.Thread(target=open_browser, daemon=True).start()

    from htmlcli.server import run_server
    try:
        run_server(str(path), port=port)
    except KeyboardInterrupt:
        click.echo("\nServer stopped.")


@main.command()
@click.argument("filepath")
def create(filepath: str):
    """Create a new HTML file from template."""
    path = Path(filepath).resolve()
    if path.exists():
        click.echo(f"Error: File already exists: {path}", err=True)
        sys.exit(1)

    title = path.stem.replace("-", " ").replace("_", " ").title()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(TEMPLATE.format(title=title), encoding="utf-8")
    click.echo(f"Created: {path}")
    click.echo(f"Run 'htmlcli open {filepath}' to edit visually.")


@main.command()
@click.argument("filepath")
def diff(filepath: str):
    """Show the changelog from the last visual editing session."""
    path = Path(filepath).resolve()
    changelog_path = path.parent / (path.stem + ".changelog.json")

    if not changelog_path.exists():
        click.echo(f"No changelog found for {path.name}")
        click.echo("Edit the file with 'htmlcli open' first.")
        sys.exit(0)

    data = json.loads(changelog_path.read_text(encoding="utf-8"))
    click.echo(f"File: {data['file']}")
    click.echo(f"Time: {data['timestamp']}")
    click.echo(f"Summary: {data['summary']}")
    click.echo(f"Changes ({len(data['changes'])}):")
    for change in data["changes"]:
        ctype = change["type"]
        sel = change.get("selector", "")
        if ctype == "text_edit":
            click.echo(f"  [{ctype}] {sel}: '{change['before']}' -> '{change['after']}'")
        elif ctype == "attribute_change":
            click.echo(f"  [{ctype}] {sel} @{change['attribute']}: '{change['before']}' -> '{change['after']}'")
        elif ctype == "element_added":
            click.echo(f"  [{ctype}] {sel} ({change['tag']})")
        elif ctype == "element_removed":
            click.echo(f"  [{ctype}] {sel} ({change['tag']})")
        else:
            click.echo(f"  [{ctype}] {sel}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
cd E:/HTML_CLI
uv run pytest tests/test_cli.py -v
```

Expected: All tests PASS

- [ ] **Step 5: Run full test suite**

```bash
cd E:/HTML_CLI
uv run pytest -v
```

Expected: All tests PASS

- [ ] **Step 6: Verify CLI works end-to-end**

```bash
cd E:/HTML_CLI
uv run htmlcli --help
uv run htmlcli create test_page.html
uv run htmlcli diff test_page.html
rm test_page.html
```

Expected: Help text shows commands, create produces a file, diff says no changelog.

- [ ] **Step 7: Commit**

```bash
cd E:/HTML_CLI
git add src/htmlcli/cli.py tests/test_cli.py
git commit -m "feat: add CLI with open, create, and diff commands"
```

---

### Task 6: Update CLAUDE.md

**Files:**
- Modify: `CLAUDE.md`

- [ ] **Step 1: Update CLAUDE.md with project info**

```markdown
# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

htmlcli is a Python CLI tool that bridges GrapesJS visual HTML editor with Claude Code. It enables a round-trip workflow: AI generates HTML -> user edits visually in browser -> AI reads the changelog and refines.

## Commands

```bash
# Install dependencies
uv sync

# Run CLI
uv run htmlcli --help
uv run htmlcli create mypage.html     # Create new HTML from template
uv run htmlcli open mypage.html       # Open visual editor in browser
uv run htmlcli diff mypage.html       # Show changelog from last edit

# Run tests
uv run pytest -v
uv run pytest tests/test_differ.py -v  # Single test file
uv run pytest -k "test_name" -v        # Single test by name
```

## Architecture

Four modules in `src/htmlcli/`:

- **cli.py** — Click-based CLI entry point. Commands: `open`, `create`, `diff`.
- **server.py** — aiohttp web server. Serves GrapesJS editor, provides `/api/load` and `/api/save` endpoints. Runs on port 8432 by default.
- **differ.py** — HTML diff engine. Compares old/new HTML, produces structured changelog (`.changelog.json`) that Claude Code can read to understand what the user changed.
- **static/** — GrapesJS frontend. `editor.html` loads GrapesJS from CDN, `editor.js` handles init/load/save.

## AI Integration Workflow

When user runs `htmlcli open`, the server tracks the original HTML. On save, it diffs against the original and writes `<filename>.changelog.json` alongside the HTML file. Claude Code should read both the HTML and changelog to understand user intent.
```

- [ ] **Step 2: Commit**

```bash
cd E:/HTML_CLI
git add CLAUDE.md
git commit -m "docs: update CLAUDE.md with project architecture and commands"
```

---

### Task 7: End-to-End Smoke Test

- [ ] **Step 1: Create a test HTML and open editor**

```bash
cd E:/HTML_CLI
uv run htmlcli create demo.html
uv run htmlcli open demo.html
```

Open browser at http://127.0.0.1:8432, make some visual edits, click Save (or Ctrl+S), then Ctrl+C the server.

- [ ] **Step 2: Verify changelog**

```bash
cd E:/HTML_CLI
uv run htmlcli diff demo.html
cat demo.changelog.json
```

Expected: Shows structured changes from the visual editing session.

- [ ] **Step 3: Clean up and final commit**

```bash
cd E:/HTML_CLI
rm -f demo.html demo.changelog.json
git add -A
git commit -m "chore: complete initial htmlcli implementation"
```

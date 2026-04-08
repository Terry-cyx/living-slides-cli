"""Local web server for GrapesJS HTML editor."""

from __future__ import annotations

import os
from pathlib import Path
from aiohttp import web

from living_slides.differ import compute_changelog, save_changelog

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
    return web.json_response({"html": content, "css": ""})


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

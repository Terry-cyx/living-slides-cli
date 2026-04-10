"""Local web server for GrapesJS HTML editor."""

from __future__ import annotations

import json
import os
import re
import shutil
import time
from datetime import datetime, timezone
from pathlib import Path
from aiohttp import web

SNAPSHOT_LIMIT = 50  # keep the N most recent snapshots per deck


def _snapshot_dir(html_path: Path) -> Path:
    d = html_path.parent / (html_path.stem + ".snapshots")
    d.mkdir(exist_ok=True)
    return d


def take_snapshot(html_path: Path, origin: str = "unknown") -> Path | None:
    """Copy the current HTML file to the snapshots folder.

    Called right before any mutation that would overwrite the file, so that
    the snapshot captures the *pre-change* state. Ctrl+Shift+Z in the browser
    reverts the main file to the most recent snapshot.
    """
    if not html_path.exists():
        return None
    snap_dir = _snapshot_dir(html_path)
    ts = int(time.time() * 1000)
    dest = snap_dir / f"{ts}_{origin}.html"
    shutil.copy2(html_path, dest)
    # Trim old snapshots
    snaps = sorted(snap_dir.glob("*.html"))
    for old in snaps[:-SNAPSHOT_LIMIT]:
        try:
            old.unlink()
        except OSError:
            pass
    return dest

from living_slides.differ import compute_changelog, save_changelog
from living_slides.history import append_changelog_history

STATIC_DIR = Path(__file__).parent / "static"


def create_app(html_path: str) -> web.Application:
    """Create the aiohttp application for serving the editor."""
    app = web.Application(middlewares=[no_cache_middleware])
    app["html_path"] = os.path.abspath(html_path)
    app["original_html"] = ""

    # Load original HTML on startup
    path = Path(app["html_path"])
    if path.exists():
        app["original_html"] = path.read_text(encoding="utf-8")

    app.router.add_get("/", handle_editor)
    app.router.add_get("/api/load", handle_load)
    app.router.add_get("/api/version", handle_version)
    app.router.add_post("/api/save", handle_save)
    app.router.add_post("/api/pin", handle_pin)
    app.router.add_get("/api/chat", handle_chat_get)
    app.router.add_post("/api/chat", handle_chat_post)
    app.router.add_post("/api/upload", handle_upload)
    app.router.add_post("/api/snapshot", handle_snapshot)
    app.router.add_post("/api/revert", handle_revert)
    app.router.add_get("/api/snapshots", handle_list_snapshots)
    app.router.add_static("/static", STATIC_DIR)
    # Serve the deck's asset folder so uploaded images render in the editor.
    html_path_obj = Path(app["html_path"])
    assets_dir = html_path_obj.parent / (html_path_obj.stem + "-assets")
    assets_dir.mkdir(exist_ok=True)
    app.router.add_static(
        "/" + html_path_obj.stem + "-assets",
        assets_dir,
    )

    return app


_NO_CACHE_HEADERS = {
    "Cache-Control": "no-cache, no-store, must-revalidate",
    "Pragma": "no-cache",
    "Expires": "0",
}


async def handle_editor(request: web.Request) -> web.Response:
    """Serve the GrapesJS editor page with no-cache headers."""
    editor_path = STATIC_DIR / "editor.html"
    return web.FileResponse(editor_path, headers=_NO_CACHE_HEADERS)


@web.middleware
async def no_cache_middleware(request: web.Request, handler):
    """Disable caching for /static/* so local edits show up on refresh."""
    response = await handler(request)
    if request.path.startswith("/static/"):
        for k, v in _NO_CACHE_HEADERS.items():
            response.headers[k] = v
    return response


async def handle_version(request: web.Request) -> web.Response:
    """Return the HTML file's modification time.

    The browser polls this endpoint to detect when the deck was modified
    by something other than the GrapesJS editor itself (e.g. Claude editing
    the file via chat). On change, the browser reloads the canvas.
    """
    html_path = Path(request.app["html_path"])
    mtime = html_path.stat().st_mtime if html_path.exists() else 0
    return web.json_response({"mtime": mtime})


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

    # Take a snapshot of the current file BEFORE overwriting, so Ctrl+Shift+Z
    # can revert this edit.
    take_snapshot(html_path, origin="editor")

    # Write HTML file
    html_path.write_text(full_html, encoding="utf-8")

    # Write changelog
    changelog_name = html_path.stem + ".changelog.json"
    changelog_path = html_path.parent / changelog_name
    save_changelog(changelog, str(changelog_path))

    # Append to history (preserve+cascade across rounds).
    if changelog["changes"]:
        append_changelog_history(str(html_path), changelog)

    # Update original for next diff
    request.app["original_html"] = full_html

    return web.json_response({
        "ok": True,
        "summary": changelog["summary"],
        "changes_count": len(changelog["changes"]),
    })


async def handle_pin(request: web.Request) -> web.Response:
    """Persist the user's current selection hierarchy so the AI can address it.

    Writes ``<deck>.selection.json`` next to the deck HTML. The payload is
    a three-layer hierarchy emitted by the editor JS:

        { page: {index, oid, title, eyebrow},
          frames: [{role, oid, tag, classes, preview}, ...],
          element: {oid, tag, classes, text} }

    The AI reads this file when the user says "change this" / "add something
    here" and wants to know *where* "this" / "here" actually is.
    """
    try:
        data = await request.json()
    except Exception:
        return web.json_response({"ok": False, "error": "Invalid JSON"}, status=400)

    html_path = Path(request.app["html_path"])
    selection_name = html_path.stem + ".selection.json"
    selection_path = html_path.parent / selection_name

    payload = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "file": html_path.name,
        **(data or {}),
    }
    selection_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return web.json_response({"ok": True, "path": str(selection_path)})


async def handle_upload(request: web.Request) -> web.Response:
    """Receive an image file and save it to <deck_stem>-assets/.

    Returns ``{ok, path}`` where ``path`` is the relative URL the editor
    can use in an ``<img src>``. Non-image files are rejected.
    """
    reader = await request.multipart()
    field = await reader.next()
    if field is None or field.name != "file":
        return web.json_response({"ok": False, "error": "No file field"}, status=400)

    orig_name = field.filename or "image"
    # Keep the extension, sanitize the rest
    ext = ""
    if "." in orig_name:
        ext = "." + orig_name.rsplit(".", 1)[-1].lower()
    # Allow only common image formats
    if ext not in {".png", ".jpg", ".jpeg", ".webp", ".gif", ".svg"}:
        return web.json_response(
            {"ok": False, "error": f"Unsupported image type: {ext}"},
            status=400,
        )

    stem = re.sub(r"[^a-zA-Z0-9._-]", "_", orig_name.rsplit(".", 1)[0])[:40] or "image"
    safe = f"{int(time.time() * 1000)}_{stem}{ext}"

    html_path = Path(request.app["html_path"])
    assets_dir = html_path.parent / (html_path.stem + "-assets")
    assets_dir.mkdir(exist_ok=True)

    target = assets_dir / safe
    with target.open("wb") as f:
        size = 0
        while True:
            chunk = await field.read_chunk()
            if not chunk:
                break
            size += len(chunk)
            if size > 20 * 1024 * 1024:  # 20 MB ceiling
                target.unlink(missing_ok=True)
                return web.json_response(
                    {"ok": False, "error": "File too large (>20MB)"},
                    status=413,
                )
            f.write(chunk)

    rel_url = f"/{html_path.stem}-assets/{safe}"
    return web.json_response({"ok": True, "path": rel_url, "name": safe})


async def handle_snapshot(request: web.Request) -> web.Response:
    """Take a snapshot of the current HTML file.

    Called by external agents (e.g. Claude's chat processing) right before
    they modify the file, so the user can Ctrl+Shift+Z to revert.
    """
    try:
        data = await request.json()
        origin = (data or {}).get("origin", "external")
    except Exception:
        origin = "external"
    html_path = Path(request.app["html_path"])
    snap = take_snapshot(html_path, origin=origin)
    if snap is None:
        return web.json_response({"ok": False, "error": "file missing"}, status=404)
    return web.json_response({"ok": True, "snapshot": snap.name})


async def handle_list_snapshots(request: web.Request) -> web.Response:
    """Return the list of available snapshots, newest first."""
    html_path = Path(request.app["html_path"])
    snap_dir = _snapshot_dir(html_path)
    snaps = sorted(snap_dir.glob("*.html"), reverse=True)
    return web.json_response({
        "snapshots": [
            {"name": s.name, "size": s.stat().st_size, "mtime": s.stat().st_mtime}
            for s in snaps
        ],
    })


async def handle_revert(request: web.Request) -> web.Response:
    """Revert the main HTML to the most recent snapshot, then delete it.

    Each call walks one step back. Returns 404 when there's nothing left
    to revert.
    """
    html_path = Path(request.app["html_path"])
    snap_dir = _snapshot_dir(html_path)
    snaps = sorted(snap_dir.glob("*.html"), reverse=True)
    if not snaps:
        return web.json_response({"ok": False, "error": "no snapshots"}, status=404)
    latest = snaps[0]
    # Before overwriting, also snapshot the CURRENT state so a ctrl+shift+y
    # (redo) could in theory recover it. For now we just save a .redo file.
    try:
        redo_dir = html_path.parent / (html_path.stem + ".redo")
        redo_dir.mkdir(exist_ok=True)
        ts = int(time.time() * 1000)
        shutil.copy2(html_path, redo_dir / f"{ts}_undone.html")
    except Exception:
        pass
    # Apply revert
    shutil.copy2(latest, html_path)
    # Update the in-memory baseline so the next diff is computed from the reverted state
    request.app["original_html"] = html_path.read_text(encoding="utf-8")
    # Delete the snapshot we just restored (so next revert goes further back)
    try:
        latest.unlink()
    except OSError:
        pass
    return web.json_response({
        "ok": True,
        "reverted_from": latest.name,
        "remaining": len(snaps) - 1,
    })


def _chat_path(html_path: Path) -> Path:
    return html_path.parent / (html_path.stem + ".chat.jsonl")


async def handle_chat_get(request: web.Request) -> web.Response:
    """Return the full chat history for the deck."""
    html_path = Path(request.app["html_path"])
    chat_file = _chat_path(html_path)
    messages = []
    if chat_file.exists():
        for line in chat_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                messages.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return web.json_response({"messages": messages})


async def handle_chat_post(request: web.Request) -> web.Response:
    """Append a user message (with optional selection context) to chat.jsonl.

    The message is then picked up by the Claude agent running in the terminal:
    it reads the file, understands the user intent plus the attached selection
    hierarchy (page / frames / element), makes the requested edit, and appends
    its own reply as a new line with ``role: "assistant"``.
    """
    try:
        data = await request.json()
    except Exception:
        return web.json_response({"ok": False, "error": "Invalid JSON"}, status=400)

    text = (data.get("text") or "").strip()
    if not text:
        return web.json_response({"ok": False, "error": "Empty message"}, status=400)

    message = {
        "role": "user",
        "text": text,
        "selection": data.get("selection"),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    html_path = Path(request.app["html_path"])
    chat_file = _chat_path(html_path)
    with chat_file.open("a", encoding="utf-8") as f:
        f.write(json.dumps(message, ensure_ascii=False) + "\n")

    return web.json_response({"ok": True})


def run_server(html_path: str, port: int = 8432) -> None:
    """Start the web server (blocking)."""
    app = create_app(html_path)
    web.run_app(app, host="127.0.0.1", port=port, print=lambda msg: None)

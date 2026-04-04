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

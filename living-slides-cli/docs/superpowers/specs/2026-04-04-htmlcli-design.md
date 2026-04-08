# HTML CLI Design Spec

## Vision
CLI tool that bridges GrapesJS visual HTML editor with Claude Code, enabling a round-trip workflow: AI generates HTML -> user visually edits in browser -> AI reads changes and refines.

## Architecture
- **Python CLI** (click) with commands: `open`, `create`, `diff`, `stop`
- **Local web server** (aiohttp) serving GrapesJS editor
- **GrapesJS from CDN** — no npm build step needed
- **File-based communication** — .html files + .changelog.json for Claude Code integration
- **Package management** via uv

## Core Workflow
1. Claude Code generates HTML file
2. User runs `htmlcli open file.html`
3. Browser opens with GrapesJS visual editor
4. User edits visually (drag, text, styles)
5. User saves -> HTML updated + changelog generated
6. User returns to Claude Code, AI reads file + changelog, refines

## Modules
1. **CLI entry** (click): `open`, `create`, `diff`, `stop` commands
2. **Web server** (aiohttp): serves editor, API for load/save
3. **GrapesJS frontend**: editor.html + editor.js, loaded from CDN
4. **Change tracker** (differ.py): HTML diff, changelog generation

## Changelog Format
Structured JSON recording: selector, change type, before/after values, human-readable summary.

## Constraints
- Pure Python (no Node.js build required)
- GrapesJS loaded from CDN
- Local-only deployment
- uv for package management

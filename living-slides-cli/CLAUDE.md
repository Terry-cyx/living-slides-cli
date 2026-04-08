# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**living-slides-cli** (CLI command: `slive`) is a Python CLI tool that closes the iteration loop for AI-generated HTML slide decks. The user generates a deck with any AI (frontend-slides, Claude direct, etc.), hand-edits some elements visually, and `slive` produces a structured changelog so AI on the next refinement turn knows exactly what the user touched (preserve) and what to update across the rest of the deck (cascade).

**Slogan**: Your slides stay. The rest catches up.

**Naming**:
- GitHub repo / project: `living-slides-cli`
- PyPI package: `living-slides`
- CLI command: `slive`
- Python import: `living_slides`

## Commands

```bash
# Install dependencies
uv sync

# Run CLI
uv run slive --help
uv run slive create deck.html --preset bold-signal     # Create from visual style preset
uv run slive create deck.html --template presentation  # Create from content template
uv run slive open deck.html                            # Open visual editor in browser
uv run slive diff deck.html                            # Show changelog from last edit
uv run slive presets                                   # List visual style presets
uv run slive templates                                 # List content templates

# Asset / chart pipeline
uv run slive asset gen-chart deck.html --name revenue --type bar \
  --data '{"labels":["Q1","Q2","Q3"],"values":[100,200,300]}'
uv run slive asset import deck.html --name hero --from ./generated.png
uv run slive asset list deck.html

# Run tests
uv run pytest -v
uv run pytest tests/test_differ.py -v  # Single test file
uv run pytest -k "test_name" -v        # Single test by name
```

## Architecture

Five modules in `src/living_slides/`:

- **cli.py** — Click-based CLI entry point. Commands: `create`, `open`, `diff`, `templates`, `presets`, `asset {list,gen-chart,import}`.
- **server.py** — aiohttp web server. Serves GrapesJS editor, provides `/api/load` and `/api/save` endpoints. Runs on port 8432 by default. On save, computes the diff against the original HTML and writes `<deck>.changelog.json`.
- **differ.py** — HTML diff engine. Compares old/new HTML, produces structured changelog with selector-level change tracking. **Recognizes `data-oid` attributes as the canonical stable selector** (preferred over CSS path) — this is what makes the iteration loop survive DOM-path drift across rounds.
- **templates.py** — Two registries: `TEMPLATES` (content shape: presentation/business/tech) and `PRESETS` (visual style: bold-signal/dark-botanical/terminal-green). Presets adapted from frontend-slides STYLE_PRESETS.md (MIT) — see Acknowledgements in README.
- **assets.py** — matplotlib chart pipeline (bar/hbar/line/pie/scatter) + external image import. Convention: assets for `deck.html` live in `deck-assets/` next to it.
- **static/** — GrapesJS frontend. `editor.html` loads GrapesJS from CDN, `editor.js` handles init/load/save.

## AI Integration Workflow (preserve + cascade)

The whole point of this tool: when the user hand-edits a deck and asks AI to refine, AI should:

1. **Read the changelog first** (`<deck>.changelog.json`) — this is a 200-token summary of what the user changed, vs. rereading the 2000-line file.
2. **Identify the touched set** — every element bearing a `data-oid` that appears in the changelog is "user judgment, do not regenerate."
3. **Cascade the user's edits** — when the user changes one number/word/style, find every other slide element that depends on it and update them. The user's edit is the source of truth for the cascade.
4. **Never stomp** — any element in the touched set must be left exactly as the user left it, unless the user explicitly says otherwise in the next prompt.

The structured changelog contains: `text_edit`, `attribute_change`, `element_added`, `element_removed`, plus a unified diff and human-readable summary.

See `docs/PRD.md` for the full product framing and `docs/refactor-plan.md` for the v0.2 refactor in progress.

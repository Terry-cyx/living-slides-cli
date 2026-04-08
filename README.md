# html-cli

Visual HTML editor CLI for AI-assisted workflows. Bridge between [GrapesJS](https://grapesjs.com/) drag-and-drop editor and AI coding assistants like Claude Code.

**Why?** AI generates HTML easily but PPT poorly. html-cli lets you visually edit AI-generated HTML in a browser, then send structured change descriptions back to AI for refinement.

## Workflow

```
AI generates HTML  -->  htmlcli open  -->  Visual edit in browser  -->  Save
                                                                        |
                   <--  AI reads changelog  <--  htmlcli diff  <--------+
```

1. AI (Claude Code) generates an HTML file
2. `htmlcli open mypage.html` — opens GrapesJS visual editor in your browser
3. Drag, resize, edit text, change styles — all visually
4. Press **Ctrl+S** — saves HTML + generates `.changelog.json`
5. Back in Claude Code: AI reads the file and changelog, understands what you changed, and refines

## Install

```bash
# With uv (recommended)
uv tool install htmlcli

# With pip
pip install htmlcli
```

## Usage

```bash
# Create a new HTML file
htmlcli create mypage.html                              # default empty page
htmlcli create deck.html  --template presentation      # by content shape
htmlcli create qbr.html   --template business
htmlcli create talk.html  --template tech
htmlcli create pitch.html --preset bold-signal         # by visual style
htmlcli create story.html --preset dark-botanical
htmlcli create infra.html --preset terminal-green

# List options
htmlcli templates           # content templates
htmlcli presets             # visual style presets

# Open visual editor in browser
htmlcli open mypage.html

# Show what changed in the last editing session
htmlcli diff mypage.html

# Generate charts (matplotlib pipeline)
htmlcli asset gen-chart deck.html --name revenue --type bar \
  --data '{"labels":["Q1","Q2","Q3"],"values":[100,200,300]}'
```

## Templates vs Presets

`htmlcli create` accepts **either** `--template` (pick by content shape) **or** `--preset` (pick by visual aesthetic). Pass neither for an empty page.

### Content templates

| Template | Description |
|----------|-------------|
| `default` | Simple single-page HTML |
| `presentation` | Multi-slide presentation with keyboard navigation |
| `business` | Business review deck with KPI cards, charts, SWOT analysis |
| `tech` | Technical presentation with code blocks, architecture diagrams, comparison tables |

### Visual style presets

| Preset | Best for |
|--------|----------|
| `bold-signal` | High-impact pitch / launch decks (dark gradient + bold colored card) |
| `dark-botanical` | Premium / investor / luxury decks (elegant serif on dark with soft gradient circles) |
| `terminal-green` | DevTools / infra / open-source decks (mono + scan lines + GitHub-dark green) |

Nine more presets — Electric Studio, Creative Voltage, Notebook Tabs, Pastel Geometry, Split Pastel, Vintage Editorial, Neon Cyber, Swiss Modern, Paper & Ink — are documented in [`skills/htmlcli/references/style-presets.md`](skills/htmlcli/references/style-presets.md). AI can generate any of them on demand following the spec.

## Claude Code Plugin

html-cli is also available as a Claude Code plugin:

```
/plugin install html-cli
```

This adds the `/htmlcli` slash command and automatic changelog awareness.

## Stable selectors via `data-oid`

The differ recognizes a `data-oid` attribute as the **canonical stable selector** for a slide object. When generating decks, put `data-oid="sN-<role>"` on every meaningful element (slide root, title, lede, card, image wrapper). The changelog will then reference each object by its `data-oid` instead of a fragile CSS path:

```json
{"type": "text_edit", "selector": "[data-oid=\"s2-title\"]", "before": "Welcome", "after": "Q1 Review"}
```

This selector survives DOM-path drift — moving, wrapping, or reordering elements in the visual editor won't break the AI's ability to find the same logical object on the next refinement pass. See [`skills/htmlcli/references/slide-template.md`](skills/htmlcli/references/slide-template.md) for the full convention.

## How the Changelog Works

When you save in the visual editor, html-cli generates a structured changelog like:

```json
{
  "file": "mypage.html",
  "timestamp": "2026-04-05T10:30:00+00:00",
  "changes": [
    {
      "type": "text_edit",
      "selector": "h1",
      "before": "Welcome",
      "after": "Hello World"
    },
    {
      "type": "attribute_change",
      "selector": "div.hero",
      "attribute": "style",
      "before": "background: red;",
      "after": "background: blue;"
    }
  ],
  "summary": "Modified text in 1 element(s); Changed attributes in 1 element(s)",
  "diff": "--- a/mypage.html\n+++ b/mypage.html\n..."
}
```

AI assistants can read this to understand exactly what you changed and why, enabling intelligent refinement.

## Architecture

```
src/htmlcli/
  cli.py        — Click CLI: create, open, diff, templates, presets, asset commands
  server.py     — aiohttp local server with /api/load and /api/save (writes .changelog.json on save)
  differ.py     — HTML diff engine; recognizes data-oid as the stable selector
  templates.py  — Content templates (presentation/business/tech) + visual presets (bold-signal/dark-botanical/terminal-green)
  assets.py     — matplotlib chart pipeline (bar/hbar/line/pie/scatter) + external image import
  static/       — GrapesJS editor (loaded from CDN)

skills/htmlcli/
  SKILL.md                       — Claude Code skill entry point
  references/
    slide-template.md            — base HTML template + data-oid convention
    design-tokens.md             — CSS tokens (spacing, type, color)
    style-presets.md             — 12 visual presets (adapted from frontend-slides)
    viewport-base.md             — mandatory base CSS (adapted from frontend-slides)
    animation-patterns.md        — motion recipes (adapted from frontend-slides)
    layout-patterns.md           — slide layout grammar
    typography-system.md         — font / size / line-height rules
    color-systems.md             — palette / contrast / dark-light
    data-visualization.md        — charts / tables / metrics
    copywriting-formulas.md      — PAS / AIDA / FAB headlines
    presentation-strategies.md   — deck structures by context
    image-generation.md          — chart pipeline + AI image integration
    common-mistakes.md           — amateur HTML-slide pitfalls to avoid
```

## Development

```bash
git clone https://github.com/YOUR_USERNAME/html-cli.git
cd html-cli
uv sync
uv run pytest -v          # Run all tests (70 tests)
uv run htmlcli --help     # Test CLI
```

## Acknowledgements — what we borrowed and why it helps

html-cli has its own engineering core (the `differ.py` changelog protocol, the `server.py` editing loop, the `assets.py` matplotlib pipeline, the GrapesJS integration), but the **visual / aesthetic layer** stands on the shoulders of two excellent open-source projects. Both are MIT-licensed; we adapt the relevant assets into `skills/htmlcli/references/` rather than vendoring code, with attribution kept inline in each file.

### From [`zarazhangrui/frontend-slides`](https://github.com/zarazhangrui/frontend-slides) (13.1k★, MIT)

| Borrowed asset | Where it lives in html-cli | What it gives us |
|---|---|---|
| **`STYLE_PRESETS.md`** — 12 curated visual styles with vibe / fonts / colors / signature elements | [`skills/htmlcli/references/style-presets.md`](skills/htmlcli/references/style-presets.md) | A real style menu instead of "AI default indigo." Three are wired into `htmlcli create --preset`; the rest are generation-ready specs. Closes the biggest gap our v2 testing identified — *aesthetic variety*. |
| **`viewport-base.css`** — mandatory `clamp()`-based base styles that make per-slide overflow physically impossible | [`skills/htmlcli/references/viewport-base.md`](skills/htmlcli/references/viewport-base.md) + inlined as `PRESET_VIEWPORT_BASE` in `templates.py` | Eliminates the #1 generated-deck failure mode (content overflowing the viewport on smaller screens). Every preset deck now ships with this base layer. |
| **`animation-patterns.md`** — effect-to-feeling table + entrance / stagger / background CSS recipes | [`skills/htmlcli/references/animation-patterns.md`](skills/htmlcli/references/animation-patterns.md) | Gives AI a *restraint guide* for motion (one motion idea per deck) instead of animating everything. |

### From [`archlizheng/frontend-slides-editable`](https://github.com/archlizheng/frontend-slides-editable) (MIT fork)

| Borrowed asset | Where it lives in html-cli | What it gives us |
|---|---|---|
| **`editor-runtime.md` DOM contract** — the idea that every editable object carries a unique `data-oid` independent of CSS path | `differ.py::_TagExtractor._make_selector` (treats `data-oid` as the canonical selector) + `references/slide-template.md` § "data-oid" + every built-in preset emits `data-oid` | Solves the **stale-selector problem** v2 testing flagged: when a user wraps or moves an element in the visual editor, the CSS path changes but the `data-oid` does not. Changelog selectors now stay valid across refinement rounds, so AI can confidently locate the same logical object on its next pass. |

### What we deliberately did *not* borrow

- **Their generation prompts / Phase pipeline.** html-cli intentionally exposes a CLI surface (`create`, `open`, `diff`, `asset`) so the workflow can be driven by any AI / IDE / human, not just Claude Code skill invocations.
- **Their localStorage-only persistence.** html-cli writes through to disk via the local server and emits a structured changelog — that's the differentiator. Browser-only persistence would defeat the round-trip protocol.
- **Their PPTX extraction script** (we may add it later as `htmlcli import --from pptx`, but it's not borrowed yet).

### What stays uniquely ours

- The structured changelog protocol (`text_edit` / `attribute_change` / `element_added` / `element_removed`) — neither upstream project has any diff mechanism.
- The local-server `/api/save` write-back loop — both upstream projects are pure browser + manual export.
- The `htmlcli asset gen-chart` matplotlib pipeline (bar / hbar / line / pie / scatter) — neither upstream project generates data charts.
- The published CLI surface itself — both upstream projects are skill directories without an installable CLI entry point.

## License

MIT. Borrowed assets retain their original MIT terms; attributions live inline in each `references/*.md` file.

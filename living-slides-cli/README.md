# living-slides-cli

> **Your slides stay. The rest catches up.**

You generate an HTML deck with any AI. You hand-edit a few elements that
matter — a number, a headline, a brand color. Then you ask the AI to
"refine the rest." The AI either stomps your edit or fails to update
the five other slides that depend on it.

`slive` closes that loop. It tracks every hand edit in a structured
changelog and hands AI two lists on the next refinement turn:

1. **Preserve** — `data-oid` values you've ever touched. Off-limits.
2. **Cascade** — what you just changed, so AI can update everything else
   that depends on it.

The whole protocol is local files. No cloud, no lock-in, no opinion
about which AI you use.

## The 60-second tour

```bash
# 1. Create a starter deck (or bring your own — see `slive adopt`)
slive create deck.html --template starter

# 2. Open the visual editor in your browser
slive open deck.html
#    edit a headline, drag a card, change a color, Ctrl+S

# 3. Ask AI to refine. Before touching the file, AI runs:
slive diff deck.html --touched     # the do-not-stomp set
slive diff deck.html               # what just changed → cascade

# 4. Catch broken references before declaring done
slive verify deck.html
```

That's the whole loop. Round 2, round 3, round 10 — `slive diff
--touched` keeps growing, and your edits never get stomped.

## Install

```bash
# With uv (recommended)
uv tool install living-slides

# With pip
pip install living-slides
```

## Commands

```bash
slive create <file> [--template starter | --preset bold-signal]
slive open <file>                          # GrapesJS visual editor
slive diff <file>                          # latest changelog
slive diff <file> --history                # every recorded round
slive diff <file> --touched                # union of touched data-oid values
slive adopt <file>                         # retrofit data-oid into existing HTML
slive verify <file>                        # check img/script/link references
slive templates                            # list templates
slive presets                              # list visual style presets

slive asset gen-chart <file> --name N --type bar --data '{...}'
slive asset import <file> --name hero --from ./image.png
slive asset list <file>
```

### Bringing an existing deck into the loop

Have a deck from frontend-slides, an AI tool, or hand-written HTML
without `data-oid`? Run `slive adopt` once and it joins the iteration
loop forever:

```bash
slive adopt my-deck.html              # role-based, default
slive adopt my-deck.html -s hash      # content-hash, stable across regenerations
slive adopt my-deck.html --dry-run    # preview only
```

`adopt` is idempotent — running it twice does nothing.

## How is this different from frontend-slides / v0 / Cursor?

These tools are genuinely good, and `slive` is not trying to replace
them. It plays a different role.

- **frontend-slides** is the best generator we know. Use it to *make*
  the deck. But it's a Claude Code skill — when you hand-edit a slide
  in your browser, the next AI turn has no record of what you touched.
  `slive adopt` brings frontend-slides decks into the iteration loop.
- **v0 / Cursor / bolt** are AI-first editors. They will happily rewrite
  your file from scratch on the next prompt and overwrite your hand
  edits. `slive` is the opposite: AI is the cascade, you are the
  source of truth.
- **Lovable** preserves edits well, but pulls AI mostly out of the loop
  — you cannot hand it a screenshot and say "cascade this." `slive` is
  CLI-shaped specifically so any AI client can drive it.

The wedge is the **preserve + cascade** combination, kept local, and
agnostic to which AI you use. See [`docs/PRD.md`](docs/PRD.md) for the
first-principles framing.

## The `data-oid` contract

Every meaningful element in a `slive` deck carries a stable identifier
called `data-oid`. This is what makes preserve + cascade survive across
rounds — even when the DOM path drifts because you moved things in the
visual editor.

The differ recognizes `data-oid` as the canonical stable selector. The
changelog references each object by its oid:

```json
{"type": "text_edit", "selector": "[data-oid=\"s2-title\"]", "before": "Welcome", "after": "Q1 Review"}
```

This selector survives moving, wrapping, or reordering. AI can find the
same logical object on round 7 even if its CSS path has changed three
times.

## Visual style presets

Three presets ship ready to edit:

| Preset | Best for |
|--------|----------|
| `bold-signal` | High-impact pitch / launch decks |
| `dark-botanical` | Premium / investor / luxury decks |
| `terminal-green` | DevTools / infra / open-source decks |

Nine more — Electric Studio, Creative Voltage, Notebook Tabs, Pastel
Geometry, Split Pastel, Vintage Editorial, Neon Cyber, Swiss Modern,
Paper & Ink — are documented in
[`skills/living-slides/references/style-presets.md`](skills/living-slides/references/style-presets.md).
AI can generate any of them on demand.

## Claude Code plugin

`slive` ships as a Claude Code plugin too:

```
/plugin install living-slides-cli
```

This adds the `living-slides` skill, which teaches Claude to read the
changelog before touching any deck — preserve + cascade out of the box.

## Visual editor features

`slive open deck.html` launches a local GrapesJS-based editor with:

- **Toolbar** — font family/size, bold/italic/underline, text color,
  alignment, image insert, save button
- **Block resize** — click any `.block` / `.item` / `.summary` etc.
  to get top/bottom drag handles. Siblings auto-freeze so flex layouts
  don't fight you
- **Image paste / drag-drop / upload** — paste from clipboard or drag
  a file onto the canvas. Images are absolutely positioned with a
  default 500 px width. Corner + side resize handles appear on click
- **Inline text editing** — double-click any text element (including
  `<td>` / `<th>`) to edit in-place. Escape or blur to commit
- **Snapshot & revert** — every save (editor or AI) snapshots the
  previous state. `Ctrl+Shift+Z` reverts one step back (file-level
  undo). Up to 50 snapshots are kept per deck
- **Overflow detection** — slides whose content exceeds the viewport
  get a red `data-overflow="true"` badge. No auto-shrink — the user
  decides whether to trim content or adjust layout
- **Auto-reload** — the editor polls `/api/version` every 2 s. When
  an external process (e.g. Claude editing the file) changes the HTML,
  the canvas reloads automatically
- **Chat panel** — a draggable floating panel lets the user type
  messages. Messages are appended to `<deck>.chat.jsonl` as
  `{role:"user", text, selection, timestamp}`. An AI agent watching
  the file can pick up the message, edit the HTML, and append an
  `{role:"assistant"}` reply — the panel shows both sides
- **Selection pin** — clicking an element and pressing the pin button
  (or opening the chat panel) writes a three-layer selection hierarchy
  (page / frames / element) to `<deck>.selection.json`, so the AI
  knows *where* "this" / "here" actually is

### Server API endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/` | GET | Serve the editor page |
| `/api/load` | GET | Return current HTML content |
| `/api/save` | POST | Save HTML, compute changelog, take snapshot |
| `/api/version` | GET | Return file mtime (for auto-reload) |
| `/api/pin` | POST | Write selection hierarchy to `.selection.json` |
| `/api/chat` | GET/POST | Read / append to `.chat.jsonl` |
| `/api/upload` | POST | Upload image to `<deck>-assets/` |
| `/api/snapshot` | POST | Take a manual snapshot |
| `/api/revert` | POST | Revert to most recent snapshot |
| `/api/snapshots` | GET | List available snapshots |

## Architecture

```
src/living_slides/
  cli.py        — Click CLI: create, open, diff, adopt, verify, templates, presets, asset
  server.py     — aiohttp local server; on save, computes diff and appends to changelog history
                  snapshot/revert system, chat bridge, image upload, selection pin
  differ.py     — HTML diff engine (text_edit, attribute_change, element_resized, element_moved,
                  slides_reordered, element_added, element_removed); recognizes data-oid as canonical
  history.py    — append-mode .changelog.history.jsonl + touched-set computation
  adopt.py      — retrofit data-oid into any HTML (role / sequential / hash strategies)
  verify.py     — img/script/link/video/audio/source reference checker
  templates.py  — starter template + 3 visual presets (12 more available via skill references)
  assets.py     — matplotlib chart pipeline (bar / hbar / line / pie / scatter)
  static/       — GrapesJS editor frontend
    editor.html — toolbar, chat panel, editor shell
    editor.js   — GrapesJS init, save/undo/redo/revert shortcuts, block resize,
                  image paste/drag/upload, inline editing, overflow detection,
                  auto-reload, selection hierarchy, chat integration

skills/living-slides/
  SKILL.md                       — preserve + cascade rules + iteration checklist
  references/                    — design tokens, style presets, layout patterns, etc.
```

## Development

```bash
git clone https://github.com/Terry-cyx/living-slides-cli.git
cd living-slides-cli
uv sync
uv run pytest -v
uv run slive --help
```

## Acknowledgements — what we borrowed and why it helps

`slive`'s engineering core (the `differ.py` changelog protocol, the
`server.py` editing loop, the `assets.py` matplotlib pipeline, the
GrapesJS integration, `adopt`, `verify`, history) is its own. The
visual / aesthetic layer and the `data-oid` contract stand on the
shoulders of two excellent open-source projects, both MIT-licensed.

### From [`zarazhangrui/frontend-slides`](https://github.com/zarazhangrui/frontend-slides) (13.1k★, MIT)

| Borrowed asset | Where it lives | What it gives us |
|---|---|---|
| **`STYLE_PRESETS.md`** — 12 curated visual styles | [`skills/living-slides/references/style-presets.md`](skills/living-slides/references/style-presets.md) | A real style menu instead of "AI default indigo." Three are wired into `slive create --preset`; the rest are generation-ready specs. |
| **`viewport-base.css`** — `clamp()`-based base styles that make per-slide overflow physically impossible | [`skills/living-slides/references/viewport-base.md`](skills/living-slides/references/viewport-base.md) + inlined into preset builders | Eliminates the #1 generated-deck failure mode (content overflowing on smaller screens). |
| **`animation-patterns.md`** — effect-to-feeling table + CSS recipes | [`skills/living-slides/references/animation-patterns.md`](skills/living-slides/references/animation-patterns.md) | Restraint guide for motion (one motion idea per deck). |

### From [`archlizheng/frontend-slides-editable`](https://github.com/archlizheng/frontend-slides-editable) (MIT)

| Borrowed asset | Where it lives | What it gives us |
|---|---|---|
| **`data-oid` DOM contract** | `differ.py` (canonical selector) + `adopt.py` (retrofit) + `references/slide-template.md` | The whole preserve + cascade loop hangs on this. Selectors stay valid even after the DOM path drifts. |
| **Undo command type taxonomy** (`moveGroup`, `patchObject`, `reorderSlides`, `deleteSlide`) | `differ.py` granular change types: `element_moved`, `element_resized`, `slides_reordered` | More semantic info for AI to reason about cascades — "the user *moved* this card" vs. "the user changed an attribute." |

### What stays uniquely ours

- **The structured changelog protocol** + `.changelog.history.jsonl` append log + `--touched` set computation. Neither upstream has any diff mechanism.
- **`slive adopt`** — retrofitting `data-oid` into arbitrary HTML so any deck can join the iteration loop.
- **`slive verify`** — broken-reference checker. Catches the P1 failure where AI generates `<img src>` pointing at files it never made.
- **The local-server `/api/save` write-back loop** — both upstream projects are pure browser + manual export.
- **The published CLI surface itself** — `slive` is installable via `uv tool install`; both upstream projects are skill directories.

## License

MIT. Borrowed assets retain their original MIT terms; attributions live
inline in each `references/*.md` file and in source comments.

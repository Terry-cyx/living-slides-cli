# html-cli Positioning Analysis

A competitive landscape review against two open-source HTML-slide projects, with an honest assessment of where html-cli is duplicative, where it is unique, and where it should go next.

> Note: GitHub clones were blocked by the local network during this analysis. Repository details below were collected via WebFetch against the public README pages of `zarazhangrui/frontend-slides` and `archlizheng/frontend-slides-editable`. Numbers (stars, releases) reflect what those pages reported at the time of fetch.

## 1. Executive Summary

The "AI-generated single-file HTML slide deck" space is no longer empty. `frontend-slides` (13.1k stars) has effectively defined the category as a Claude Code skill that generates beautiful, dependency-free HTML decks. `frontend-slides-editable` (14 stars, very new) is a direct extension that bolts a browser-based WYSIWYG layer on top of the same style system. html-cli sits in the same category but reaches it from the opposite direction: it is a **Python CLI + local server + structured changelog** rather than a pure prompt skill, and it treats the visual editor as a *round-trip channel* back to the AI rather than as the end deliverable. html-cli is not a duplicate, but a meaningful chunk of its surface area (templates, 16:9 canvas, single-file HTML, Claude Code skill) has been done already and at higher polish. Its defensible angle is the **structured diff/changelog protocol** and the **CLI-first, file-first developer ergonomics** — neither competitor offers either.

## 2. frontend-slides (zarazhangrui)

**Repo:** https://github.com/zarazhangrui/frontend-slides
**Stars / activity:** ~13.1k stars, ~984 forks, MIT, v2.0.0 released March 2026. Highly active, mainstream traction.
**Languages reported:** Shell 75.7%, CSS 14.1%, Python 10.2%. (No JS framework — vanilla everything.)

**Architecture.** Pure Claude Code skill. The unit of execution is `SKILL.md` (~180 lines) acting as a routing map that lazily loads supporting markdown (`STYLE_PRESETS.md`, `html-template.md`, `viewport-base.css`, `animation-patterns.md`) only when needed — what the author calls "progressive disclosure". There is no app, no server, no runtime: the skill instructs Claude to write a single self-contained HTML file. Auxiliary Python (`scripts/extract-pptx.py`) handles `.pptx` ingestion via `python-pptx`, and shell scripts handle Vercel deploy and Playwright-based PDF export.

**Core features.**
- Two-phase workflow: content gathering, then visual style selection from preview thumbnails.
- 12 curated style presets (4 dark / 4 light / 4 specialty: Bold Signal, Electric Studio, Neon Cyber, Terminal Green, Swiss Modern, Paper & Ink, etc.).
- PPTX import (text + images + speaker notes).
- One-command Vercel deploy.
- PDF export at 1920×1080 via Playwright.

**Editor type.** None — it is AI-prompt-driven generation. Edits happen by talking to Claude Code again.

**AI integration.** Native Claude Code skill, installable via the plugin marketplace. The entire UX is "describe the deck, pick a look, get HTML."

**Asset handling.** Inline / base64 embedding to keep the single-file invariant; preserves images extracted from PPTX.

**File format.** Output is a single `.html` file. Optional `.pdf` export and Vercel URL.

**Distribution.** Claude Code plugin (primary) + manual clone into `~/.claude/skills`.

**Target user.** A Claude Code user who wants beautiful single-file slide decks without learning a design tool, and who is comfortable iterating purely by chatting with the AI.

**Key files.** `SKILL.md`, `STYLE_PRESETS.md`, `html-template.md`, `viewport-base.css`, `animation-patterns.md`, `scripts/extract-pptx.py`, `scripts/deploy.sh`, `scripts/export-pdf.sh`.

## 3. frontend-slides-editable (archlizheng)

**Repo:** https://github.com/archlizheng/frontend-slides-editable
**Stars / activity:** ~14 stars, only a handful of commits. Brand new, low traction.
**License:** MIT.

**Architecture.** Single self-contained HTML file with inline JS/CSS, zero dependencies, vanilla JavaScript editing runtime. The reference implementation lives at `examples/editable-deck-reference.html`. State is persisted in `localStorage` using a structured `.slides-offset` format; export emits a sanitized HTML file with edit-mode classes stripped.

**Core features.**
- Browser-based WYSIWYG with drag-positioning, corner-handle resize, snap-to-grid, multi-select via Ctrl+click.
- Inline rich-text toolbar (bold/italic/font/size).
- Full undo/redo stack (Ctrl+Z, Y, Shift+Z).
- Slide thumbnail sidebar with reordering and deletion.
- Same 12 style presets as `frontend-slides` (Bold Signal, Notebook Tabs, Neon Cyber, etc.) — clearly forked or derived from the upstream skill.
- PPTX extraction via `extract-pptx.py`.

**Editor type.** Browser WYSIWYG / drag-drop, but everything happens *inside the deck file itself* — the editor is a runtime mode of the same HTML.

**AI integration.** Designed as a Claude Code / Codex skill with a guided discovery flow (purpose, length, content, style, assets) before generation. AI is for the initial generation; the WYSIWYG handles subsequent edits.

**Asset handling.** Inherits embedded-image strategy from upstream; PPTX assets preserved.

**File format.** Single `.html`, with `localStorage` as scratch state.

**Distribution.** Direct file sharing of the HTML; no build, no server.

**Target user.** Same audience as upstream `frontend-slides`, but who wants to *tweak after generation* without going back to the AI for every nudge.

**Key files.** `examples/editable-deck-reference.html`, the same supporting markdown family as upstream.

## 4. Feature Comparison Matrix

| Dimension | frontend-slides | frontend-slides-editable | html-cli |
|---|---|---|---|
| Distribution form | Claude Code skill (markdown) | Claude Code skill + reference HTML | Python CLI (`uv tool install htmlcli`) + Claude Code skill |
| Runtime needed | None (Claude generates) | None (HTML is the app) | Local Python server (aiohttp on :8432) |
| Editing model | Re-prompt the AI | In-browser WYSIWYG inside the deck file | GrapesJS in-browser editor over a local server |
| Editor capability | n/a | Drag/resize/snap, rich text, undo/redo, thumbnails | GrapesJS: blocks, style manager, layers, drag/resize, code edit |
| Single-file HTML output | Yes | Yes | Yes (CDN-loaded GrapesJS only at edit time) |
| Templates / presets | 12 named visual styles | 12 named visual styles | 4 structural templates (default, presentation, business, tech); design tokens, no named visual presets |
| 16:9 fixed canvas | Yes | Yes | Yes (1920×1080, enforced by skill rules) |
| AI generation | Native (skill is the product) | Native (skill before edit) | Skill instructs Claude to Write the HTML using `references/slide-template.md` |
| AI re-read after edit | Manual: user describes change | Manual: user describes change | Automatic: `.changelog.json` with selectors, before/after, unified diff |
| Structured change log | No | No | Yes — `text_edit`, `attribute_change`, `element_added`, `element_removed`, summary, diff |
| PPTX import | Yes (`extract-pptx.py`) | Yes (inherited) | No |
| PDF export | Yes (Playwright) | Not documented | No |
| Vercel deploy | Yes (one command) | No | No |
| Chart pipeline | Inline CSS / per-style | Inline CSS / per-style | Chart.js in template + planned matplotlib `htmlcli asset gen-chart` pipeline |
| Asset CLI | No | No | Yes — `htmlcli asset list / gen-chart / import` |
| Persistent design system | Style preset CSS files | Same | Design tokens spec (`references/design-tokens.md`), type scale, spacing scale, color systems |
| Stars (proxy for traction) | ~13,100 | ~14 | n/a (pre-release, internal) |
| Test coverage | n/a | n/a | 53 pytest tests, includes differ + smoke |
| Primary language | Markdown + shell + Python | HTML/JS + Python | Python (Click + aiohttp) |

## 5. Overlap and Differentiation

**Overlap (the honest part).**
- All three target the same artefact: a single, dependency-free, 16:9 HTML slide deck generated by Claude.
- All three are wrapped as Claude Code skills with a guided discovery flow before generation.
- All three lock the canvas to 1920×1080 and lean on a curated visual system rather than freeform CSS.
- Both `frontend-slides-editable` and html-cli add an editing surface on top of generated HTML.
- The "professional design rules" baked into our `SKILL.md` (type scale, 6×6, contrast, single focal point, no chartjunk) are not unique — `frontend-slides`'s style presets encode the same taste implicitly.

**Differentiation (where html-cli is genuinely alone).**
1. **Structured changelog protocol.** html-cli is the only project that produces a machine-readable record of *what the human changed in the editor*. `frontend-slides-editable` lets the human edit, but the next AI turn has to re-read the whole HTML and guess what's different. Our `.changelog.json` with selector-level `text_edit` / `attribute_change` / `element_added` / `element_removed` events plus a unified diff is a real protocol, not just a file format.
2. **Round-trip workflow as the thesis.** The other two projects treat AI as a generator and the human as the editor. html-cli treats the loop itself — generate, edit, diff, refine, repeat — as the product. The `htmlcli diff` command is the missing return channel.
3. **CLI-first, file-first.** `htmlcli create`, `htmlcli open`, `htmlcli diff`, `htmlcli asset` form a Unix-style toolbox. The competitors live entirely inside Claude's chat window. CLI-first means scriptability, CI integration, and editor-agnostic use (Cursor, Codex, Aider, plain Claude API).
4. **GrapesJS instead of a hand-rolled editor.** We get a mature block/style/layer editor for free, including code view, responsive previews, and trait management. `frontend-slides-editable` will need years to reach parity.
5. **Asset pipeline as a CLI verb.** `htmlcli asset gen-chart` (matplotlib) and `htmlcli asset import` formalise an idea the others handle ad-hoc by inlining base64.
6. **Structural templates, not just visual presets.** Our `presentation` / `business` / `tech` templates ship a *deck skeleton* (KPI cards, SWOT, architecture diagrams, comparison tables). `frontend-slides`'s 12 presets are pure look-and-feel.
7. **Local server + port management.** A trivial-sounding feature, but it means edits persist to disk in real time and survive crashes — the WYSIWYG competitor relies on `localStorage`.

## 6. Has Our Project Been Done Before?

Partially yes, and we should be honest about it.

- The **AI-generates-pretty-single-file-HTML-slides** premise: solved, at scale, by `frontend-slides`. Anyone who Googles "claude code presentation skill" finds it first. We will not out-design or out-market a 13k-star project on aesthetics alone.
- The **edit-AI-generated-slides-in-the-browser** premise: claimed by `frontend-slides-editable` two months ago. Their implementation is thinner than ours, but the headline is identical.
- The **Claude Code skill with a curated visual system, 16:9 canvas, PPTX intake, and single-file output**: done.

What has **not** been done:
- A structured, selector-level changelog that lets the next AI turn reason precisely about user edits.
- A real CLI surface (`create`, `open`, `diff`, `templates`, `asset *`) usable outside Claude.
- Treating the editor as an instrumented round-trip channel instead of a destination.
- Templates that ship deck *structure* (QBR, tech talk) rather than just CSS skin.

So: the umbrella category is taken; the specific niche we should claim is open and defensible.

## 7. What We Can Learn from These Projects

1. **Named, taste-forward visual presets sell.** "Bold Signal", "Neon Cyber", "Swiss Modern" are dramatically more compelling than `--template presentation`. We should add a parallel **style preset** axis (orthogonal to structural templates) with maybe 6–8 named looks. Dark/light/specialty split is a proven UX.
2. **Progressive-disclosure skill design.** `frontend-slides`'s ~180-line `SKILL.md` that lazily loads supporting markdown is a cleaner pattern than dumping everything up front. Our `SKILL.md` is already heading this way; we should audit it for context bloat.
3. **PPTX import is a real wedge.** It is the on-ramp from "I have a deck I hate" to "I have an HTML deck I love". Adding `htmlcli import deck.pptx` (re-using `python-pptx`) would be cheap and high-leverage.
4. **PDF export via Playwright.** Trivial to add as `htmlcli export deck.html --pdf`. Customers ask for this immediately.
5. **One-command publish.** A `htmlcli publish` that uploads to Vercel, Netlify, or even just a local tunnel would close the "now what?" gap after generation.
6. **Single-file portability discipline.** We should stop loading GrapesJS from a CDN at edit time if we want the edited file to survive offline. Either bundle it or document clearly that "edit mode requires network, view mode does not."
7. **Style-preset preview gallery.** Generating a thumbnail strip of looks before commitment is much friendlier than asking the user to describe a vibe.

## 8. Recommended Positioning

> **html-cli is the round-trip protocol for AI-generated HTML decks. It is the only tool that lets a visual editor and a coding agent talk to each other in structured diffs.**

Concretely, the messaging should stop competing on "we make pretty slides" (a losing fight against a 13k-star incumbent) and start competing on "we close the loop". The three pillars:

1. **Protocol, not theme.** We sell `.changelog.json` as an open format. Any AI tool — Claude Code, Cursor, Aider, Codex, raw API — can consume it. Any editor — GrapesJS today, others tomorrow — can produce it. This is the only thing in the space that looks like a standard.
2. **CLI-first, AI-second.** html-cli works without Claude (you can edit and diff HTML in the visual editor as a standalone tool). The AI integration is a layer on top, not the substrate. This widens the addressable user from "Claude Code users" to "anyone iterating on HTML with an LLM in the loop."
3. **Decks are the first vertical, not the only one.** The same protocol works for landing pages, dashboards, email templates, marketing one-pagers. "AI-generated HTML round-trip" generalises; "AI-generated slides" doesn't.

What we should *stop* claiming as a differentiator: design taste, 16:9 canvas, single-file HTML, Claude Code skill packaging. Those are table stakes now.

## 9. Recommended Next Steps

Ordered roughly by leverage / cost ratio.

1. **Promote the changelog protocol to a first-class citizen.** Document `.changelog.json` as a versioned spec in `docs/changelog-spec.md`. Add `schemaVersion` to the file. Pitch it as adoptable by other editors.
2. **Add `htmlcli watch`.** A long-running mode that streams changelogs to stdout (or to a Unix socket) so an AI agent in another process can react in real time. This is the killer feature competitors cannot copy without rebuilding their substrate.
3. **Add named visual style presets.** 6–8 looks (`--style bold-signal`, `--style swiss-modern`, etc.), orthogonal to the structural templates. Reuses the proven naming convention without copying CSS verbatim.
4. **Add `htmlcli import deck.pptx`.** Vendor `python-pptx`, reuse the upstream `extract-pptx.py` approach. Highest-leverage on-ramp we are missing.
5. **Add `htmlcli export <file> --pdf`.** Playwright-based, 1920×1080. Users will ask for it on day one.
6. **Bundle GrapesJS locally** (or at minimum offer `htmlcli open --offline`). Single-file portability is a stated value; CDN dependency at edit time contradicts it.
7. **Ship a style-preset preview gallery** in `htmlcli create --interactive` — render thumbnails, let the user pick.
8. **Audit `SKILL.md` for progressive disclosure.** Push reference content into separately-loaded files; keep the entry skill under ~200 lines.
9. **Write a "html-cli vs frontend-slides" page** in `docs/`. Be honest. Lead with the protocol, not the aesthetics. Linking to competitors builds trust.
10. **Generalise beyond slides.** Add a `landing` and `dashboard` template to prove the protocol is not deck-specific. This is the cheapest way to defend the positioning in section 8.

## Closing Note

html-cli does *not* need to beat `frontend-slides` at making pretty single-file HTML decks — it cannot, and the attempt would be a strategic error. It needs to be the only project in the space that takes the loop seriously: the human's edits are data, the AI's regeneration is a function of that data, and the changelog is the contract between them. Everything in the roadmap should make that loop tighter, more observable, and more portable.

---
name: htmlcli
description: Create professional HTML presentations that replace PowerPoint. Use when the user asks to create a presentation, deck, slides, pitch deck, QBR, or wants to visually edit HTML. Produces production-quality 16:9 slide decks with design tokens, proper typography, and the htmlcli visual editor workflow.
---

# htmlcli — Professional HTML Presentation Creator

You have access to `htmlcli`, a CLI tool that creates, edits, and tracks HTML presentations. This skill provides the design knowledge needed to generate **professional, non-amateur** HTML slide decks that can genuinely replace PowerPoint.

## Core Principle

**Amateur HTML slides feel like web pages. Professional HTML slides feel like presentations.** The difference is discipline: fixed 16:9 canvas, strict type scale, single focal point per slide, 25% whitespace, no walls of text.

## When to Use

Trigger when the user asks to create any of these:
- Presentation, slide deck, pitch deck, PPT-style content
- QBR (quarterly business review), board deck, investor deck
- Sales pitch, product launch, demo
- Conference talk, training slides, workshop
- Data dashboard for presenting (not a live app)

## Available CLI Commands

```bash
htmlcli create <file> [--template NAME]       # Create from template
htmlcli open <file> [--port PORT]             # Open GrapesJS visual editor
htmlcli diff <file>                           # Show changelog from last edit
htmlcli templates                             # List templates

# Asset management (charts, images, diagrams)
htmlcli asset list <file>                     # List all assets for an HTML file
htmlcli asset gen-chart <file> --name N --type T --data JSON --title T
htmlcli asset import <file> --name N --from PATH
```

## The Non-Negotiable Design Rules

1. **16:9 aspect ratio, fixed canvas** — never "responsive web page" feel. Lock the slide at 1920×1080 (letterbox on wider screens).
2. **One idea per slide** — if you need "and" in the title, split the slide.
3. **Type scale, not random sizes** — pick from `{14, 16, 20, 24, 32, 40, 56, 72, 96, 120}px`. No in-between values.
4. **Maximum 6×6** — 6 bullets per slide, 6 words per bullet. Better: replace bullets with visuals.
5. **25% whitespace minimum** — generous padding (96-128px edges).
6. **One focal point per slide** — established via size (3x larger), color (only colored item), or isolation.
7. **No chartjunk** — kill gridlines, 3D effects, drop shadows on bar charts. Follow Tufte's data-ink ratio.
8. **Contrast ≥ 4.5:1** — test for projector washout, bump to 7:1 for body text when possible.
9. **Title states the insight, not the topic** — "Revenue doubled in Q3" ✅ / "Q3 Revenue" ❌
10. **Max 2 font families** — ideally 1 variable font (Inter, Geist).

## Workflow

### Step 1: Clarify the presentation
Before generating, briefly ask (if not obvious):
- **Type**: pitch deck / QBR / sales / tech talk / training / other
- **Audience**: who will see this? (investors, customers, team, board)
- **Theme**: dark (keynote/stage) or light (handouts/print)?
- **Slide count**: approximate target?

### Step 2: Pick a strategy
Load `references/presentation-strategies.md` for proven deck structures (YC Seed, Sales Pitch, QBR, etc.) and their emotion arcs.

### Step 3: Design the content
- Load `references/copywriting-formulas.md` for PAS/AIDA/FAB headlines
- Load `references/layout-patterns.md` to pick layout per slide
- Load `references/design-tokens.md` for the exact CSS tokens (spacing, typography, colors)

### Step 4: Generate the HTML
Use the base template in `references/slide-template.md`. This template includes:
- 16:9 canvas locking
- Slide navigation (arrow keys, click, progress bar, counter)
- Design token CSS variables
- Responsive fallbacks for mobile
- Chart.js CDN for data viz

**Do NOT use `htmlcli create --template` for the initial generation.** The built-in templates are placeholders. Instead, generate the full HTML with the Write tool using the professional template from `references/slide-template.md`.

### Step 5: Open for user review
```bash
htmlcli open <file>
```
Tell the user to open it in their terminal (the server blocks, so you can't run it for them).

### Step 6: Read the changelog after user edits
After the user saves in the visual editor:
```bash
# Read both the updated HTML and the changelog
cat <file>.changelog.json
```
Parse the structured changes to understand user intent. The changelog contains:
- `changes[]` — `text_edit`, `attribute_change`, `element_added`, `element_removed`
- `summary` — one-line description
- `diff` — unified diff

### Step 7: Refine intelligently
Based on the changelog:
- **Preserve** every user edit — never revert their changes
- **Cascade** related updates (if they changed a number, update dependent calculations)
- **Fix** side-effects (global replace issues, duplicate IDs, broken layouts)
- **Extend** the user's intent (if they changed language to Chinese, translate all remaining text)
- **Verify** consistency (fonts, colors, spacing stay uniform)

## Reference Files (load only when relevant)

| File | When to Load |
|------|-------------|
| `references/design-tokens.md` | Every slide generation — contains CSS tokens |
| `references/slide-template.md` | Every slide generation — base HTML template |
| `references/layout-patterns.md` | Picking slide layouts (title, split, metrics, grid, etc.) |
| `references/typography-system.md` | Font choices, sizes, line-heights |
| `references/color-systems.md` | Picking palettes, contrast, dark/light themes |
| `references/data-visualization.md` | Charts, tables, metrics presentation |
| `references/copywriting-formulas.md` | Writing slide headlines and body |
| `references/presentation-strategies.md` | Choosing deck structure by context |
| `references/common-mistakes.md` | Avoiding amateur HTML slide pitfalls |
| `references/image-generation.md` | Charts, diagrams, AI images — asset pipeline |

## Red Flags — Stop and Fix

If you catch yourself doing any of these, stop and rewrite:

- ❌ Slide title is the topic instead of the insight
- ❌ More than 6 bullets on a slide
- ❌ Pure black `#000` or pure white `#fff` (use `#0A0A0A` / `#FAFAFA`)
- ❌ Three or more font families
- ❌ Font sizes not from the type scale (e.g., `19px`, `23px`)
- ❌ Default `<ul>` bullet styling
- ❌ Emoji clipart masquerading as icons (okay sparingly, never as the focal element)
- ❌ Centered long paragraphs (left-align body text ≥ 2 lines)
- ❌ Gradient on every element
- ❌ Random padding values (use spacing tokens: 8, 16, 24, 32, 48, 64, 96, 128)
- ❌ Chart.js default colors and gridlines (theme them to the deck)
- ❌ Slide fills 100vh but content is cramped at the top

## Example Opening Response

When the user says "make me a pitch deck for my AI startup":

```
I'll create a professional 10-slide YC-style pitch deck. A few quick questions:
1. Company name and one-line description?
2. Dark theme (classic keynote) or light theme?
3. Any brand colors you want me to use?

While you answer, I'll load the design references and prepare the structure.
```

Then load `presentation-strategies.md`, `design-tokens.md`, and `slide-template.md`, and generate.

## Remember

The goal is not "HTML that looks like a slide." The goal is "HTML that could be presented to a boardroom, a stage, or a Fortune 500 client." Discipline over creativity. Tokens over intuition. Insights over topics.

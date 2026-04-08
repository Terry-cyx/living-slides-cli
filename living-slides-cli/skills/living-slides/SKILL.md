---
name: living-slides
description: Iterate on AI-generated HTML slide decks with the slive CLI. Use whenever the user has an existing HTML deck (from frontend-slides, slive, or any source) and wants to refine it after hand-editing some elements — preserve the user's edits, cascade their intent to the rest of the deck, and never stomp the touched set. Also use when the user asks to create a new HTML presentation/deck/slides/pitch deck/QBR.
---

# living-slides — The Iteration Loop for AI-Generated HTML Decks

`slive` is a CLI tool that closes the iteration loop for HTML slide decks.
The user generates a deck (with you, with frontend-slides, by hand —
doesn't matter), opens it in a visual editor, hand-edits some elements,
and asks you to refine the rest. **Your job is to honor those edits and
cascade them.**

The tool tracks every user edit in a structured changelog. **You read the
changelog first**, *not* the 2000-line HTML file.

## The Two Rules

These rules override everything else in this skill, including the
generation guidance below. If they conflict with anything else, follow
these.

### Rule 1: Preserve

**Any element bearing a `data-oid` that appears in the touched set is
user judgment. Do not regenerate it.** Treat it as frozen unless the
user's *latest* prompt explicitly says to change it.

The touched set is the union of every `data-oid` the user has touched
across the *entire history* of edits — not just the latest round. A user
who fixed a number in round 1 should never see that number stomped in
round 5.

### Rule 2: Cascade

**When the user changes one number, word, color, or style, find every
other element on every other slide that depends on it and update them
to match.** The user's edit is the source of truth for the cascade.

Examples:
- User changed "$2.4M ARR" → "$3.1M ARR" on slide 3. You must update
  the runway calculation on slide 7, the growth-rate chart label on
  slide 5, and any sentence elsewhere that quotes the old figure.
- User renamed the product from "Quill" → "Vellum" on the cover slide.
  Every other mention across the deck must be updated — *except* the
  one the user touched (it's already correct).
- User changed the brand color from teal to amber on the title bar.
  Every other element using the same color token must follow.

The cascade is not "find/replace." It is "find every element whose
meaning *depends on* the user's edit and bring it into alignment."

## The Iteration Checklist

On every refinement turn, before touching the HTML, run this checklist:

1. **Read the touched set**:
   ```bash
   slive diff <file> --touched
   ```
   This prints every `data-oid` the user has ever touched. Memorize it.
   These elements are off-limits.

2. **Read the latest changelog**:
   ```bash
   slive diff <file>
   ```
   The latest round tells you *what just changed* and therefore what
   to cascade.

3. **(Optional) Read the full history** if you need round-by-round
   reasoning:
   ```bash
   slive diff <file> --history
   ```

4. **Plan the cascade**: for each change in the latest round, list every
   other element across the deck that depends on it. Build the edit
   plan from this list.

5. **Edit the HTML**: apply your cascade. **Never touch any element
   whose `data-oid` is in the touched set** unless the user's latest
   prompt says so.

6. **Verify references** before declaring done:
   ```bash
   slive verify <file>
   ```
   Catches broken `<img>`/`<script>`/`<link>` references — a P1 failure
   mode where the deck looks fine in code but renders with broken
   images.

## Changelog Change Types

The changelog reports user edits as one of these types. Use them to
choose your cascade strategy:

| Type | Meaning | Cascade strategy |
|------|---------|------------------|
| `text_edit` | A text node changed | Find every other element quoting the same fact and update it |
| `attribute_change` | An attribute (other than style position) changed | If `src`, check for sibling references; if `href`, check link consistency; if class, check theme consistency |
| `element_resized` | Pure `left/top/width/height` change | Position-only — usually no cascade, but check if the user's intent is to align with a sibling |
| `element_moved` | Same `data-oid`, different parent or sibling order | Treat as a deliberate reordering — preserve the new structure |
| `slides_reordered` | The slide sequence was shuffled | Preserve the new order; update any "Slide N of M" references |
| `element_added` | A brand-new element appeared | The user wants this content; do not delete it |
| `element_removed` | An element disappeared | The user wants it gone; do not put it back |

## The `data-oid` Contract

Every meaningful element in a slive deck carries a stable identifier
called `data-oid`. This is what makes preserve+cascade survive across
rounds — even when the DOM path drifts because the user moved things.

**When generating new HTML for a slive deck, every meaningful element
MUST carry a unique `data-oid`.** Use the convention `s{slide}-{role}`,
e.g. `s3-title`, `s3-metric-1`, `s3-image`.

**When the user brings a deck that lacks `data-oid`** (frontend-slides
output, hand-written HTML, anything from another tool), retrofit it
once with:

```bash
slive adopt <file>            # role-based, default
slive adopt <file> -s hash    # content-hash, stable across regenerations
```

Adoption is idempotent — running it twice does nothing. After the
first run, the deck is in the iteration loop forever.

## CLI Reference

```bash
# Open the visual editor (the user's hand-edit channel)
slive open <file>

# Read the changelog (your input on every refinement turn)
slive diff <file>                  # latest round
slive diff <file> --history        # every round
slive diff <file> --touched        # the do-not-stomp set

# Bring an existing deck into the iteration loop
slive adopt <file>                 # add data-oid to every meaningful element

# Catch broken references before declaring done
slive verify <file>

# Built-in templates and presets (see Generation Guide below)
slive create <file> --preset bold-signal
slive templates
slive presets

# Asset pipeline
slive asset list <file>
slive asset gen-chart <file> --name N --type bar --data '{...}'
slive asset import <file> --name hero --from ./image.png
```

---

# Generation Guide

The rest of this skill covers **how to generate decks well** for the
case where there's no prior HTML to iterate on. This is the cold-start
path — once the user has a file open in the editor, the iteration loop
above takes over.

## Core Principle

Amateur HTML slides feel like web pages. Professional HTML slides feel
like presentations. The difference is discipline: fixed 16:9 canvas,
strict type scale, single focal point per slide, generous whitespace,
no walls of text.

## Non-Negotiable Design Rules

1. **16:9 fixed canvas** — never "responsive web page" feel.
2. **One idea per slide** — if the title needs "and", split the slide.
3. **Type scale** — pick from `{14, 16, 20, 24, 32, 40, 56, 72, 96, 120}px`.
4. **Maximum 6×6** — 6 bullets per slide, 6 words per bullet.
5. **25% whitespace minimum** — generous edge padding (96-128px).
6. **One focal point per slide** — established by size, color, or isolation.
7. **No chartjunk** — kill gridlines, 3D effects, drop shadows.
8. **Contrast ≥ 4.5:1** — bump to 7:1 for body text where possible.
9. **Title states the insight, not the topic** — "Revenue doubled in Q3" ✅ / "Q3 Revenue" ❌
10. **Max 2 font families** — ideally 1 variable font (Inter, Geist).
11. **Every meaningful element gets a `data-oid`** — non-negotiable for the iteration loop.

## Workflow

1. **Clarify** — type, audience, theme, slide count
2. **Pick a strategy** — load `references/presentation-strategies.md`
3. **Pick a visual preset** — load `references/style-presets.md` (12 presets)
4. **Design the content** — `references/copywriting-formulas.md` for headlines
5. **Generate the HTML** with `data-oid` on every meaningful element, using `references/slide-template.md` as the base
6. **Open for review**: `slive open <file>` — then enter the iteration loop above

## Reference Files

| File | When to load |
|------|-------------|
| `references/style-presets.md` | Picking visual aesthetic (12 presets, MIT-adapted) |
| `references/design-tokens.md` | CSS token values |
| `references/slide-template.md` | Base HTML template (must include `data-oid`) |
| `references/layout-patterns.md` | Picking layout per slide |
| `references/typography-system.md` | Font sizes, line heights |
| `references/color-systems.md` | Palettes, contrast, dark/light |
| `references/data-visualization.md` | Charts, tables, metrics |
| `references/copywriting-formulas.md` | Headlines and body copy |
| `references/presentation-strategies.md` | Deck structures by context |
| `references/common-mistakes.md` | Anti-patterns to avoid |
| `references/image-generation.md` | Asset pipeline (charts, AI images) |
| `references/viewport-base.md` | Mandatory clamp() base CSS |
| `references/animation-patterns.md` | Effect-to-feeling mapping |

## Red Flags — Stop and Fix

- ❌ Generated an element without a `data-oid`
- ❌ About to modify an element whose `data-oid` is in `--touched`
- ❌ Slide title is the topic instead of the insight
- ❌ More than 6 bullets on a slide
- ❌ Pure `#000` or pure `#fff` (use `#0A0A0A` / `#FAFAFA`)
- ❌ Three or more font families
- ❌ Font sizes not from the type scale
- ❌ Centered long paragraphs (left-align body text ≥ 2 lines)
- ❌ Random padding values (use spacing tokens)

## Remember

The goal is not "HTML that looks like a slide." The goal is **a deck
that survives ten rounds of refinement without losing the user's
voice**. Discipline over creativity. The touched set over your
preferences. Cascade over regenerate.

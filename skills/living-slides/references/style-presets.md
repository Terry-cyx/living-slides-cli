# Style Presets

12 curated visual styles for slide decks. Each preset is grounded in a real design reference — **no generic AI-slop aesthetics**. Pick one and stick to it for the whole deck; never mix two presets.

> **Attribution**: This catalog is adapted from [zarazhangrui/frontend-slides](https://github.com/zarazhangrui/frontend-slides) `STYLE_PRESETS.md` (MIT). Color tokens, font pairings, and signature elements are reproduced with adjustments for living-slides' design-tokens conventions. Use this list as a *style menu* — when generating, also load `design-tokens.md`, `viewport-base.md`, and `slide-template.md`.

## How to use

1. Ask the user (or pick) one preset by name from the table below.
2. Map the preset's colors into living-slides' CSS token names (`--color-bg`, `--color-fg`, `--color-primary`, `--color-accent`).
3. Load the **fonts** from the preset's font row (Google Fonts or Fontshare CDN link).
4. Apply the **signature elements** as recurring slide motifs (one or two per deck, not all at once).
5. Always include `viewport-base.md`'s base CSS.

## Quick selector

| # | Preset | Theme | Vibe | Use For |
|---|--------|-------|------|---------|
| 1 | Bold Signal | dark | Confident, high-impact | Pitch decks, product launches |
| 2 | Electric Studio | mixed | Professional, clean | Sales, B2B SaaS |
| 3 | Creative Voltage | dark | Energetic, retro-modern | Conference talks, agencies |
| 4 | Dark Botanical | dark | Elegant, premium | Investor pitches, luxury brands |
| 5 | Notebook Tabs | light | Editorial, tactile | Workshops, training, internal reports |
| 6 | Pastel Geometry | light | Friendly, approachable | Onboarding, education |
| 7 | Split Pastel | light | Playful, modern | Creative briefs, design reviews |
| 8 | Vintage Editorial | light | Witty, personality-driven | Thought leadership, manifestos |
| 9 | Neon Cyber | dark | Futuristic, techy | Hackathons, AI/crypto demos |
| 10 | Terminal Green | dark | Developer, hacker | DevTools, infra, open source |
| 11 | Swiss Modern | light | Bauhaus, precise | Architecture, design studios |
| 12 | Paper & Ink | light | Literary, thoughtful | Long-form essays, book launches |

---

## Dark Themes

### 1. Bold Signal
- **Layout**: Colored card on dark gradient. Number top-left, nav top-right, title bottom-left.
- **Fonts**: Display `Archivo Black` 900 / Body `Space Grotesk` 400-500
- **Colors**: bg `#1a1a1a`, gradient `linear-gradient(135deg,#1a1a1a,#2d2d2d,#1a1a1a)`, card `#FF5722`, fg `#ffffff`
- **Signature**: Bold colored card as focal point; large section numbers (01, 02…); navigation breadcrumbs with opacity states.

### 2. Electric Studio
- **Layout**: Vertical split — white top, blue bottom. Brand marks in corners.
- **Fonts**: `Manrope` 800 / `Manrope` 400-500
- **Colors**: bg-dark `#0a0a0a`, bg-white `#ffffff`, accent `#4361ee`
- **Signature**: Two-panel split, accent bar on panel edge, quote-as-hero typography.

### 3. Creative Voltage
- **Layout**: Split panels — electric blue left, dark right.
- **Fonts**: Display `Syne` 700-800 / Mono `Space Mono` 400-700
- **Colors**: primary `#0066ff`, dark `#1a1a2e`, neon `#d4ff00`
- **Signature**: Halftone texture, neon badges/callouts, script accents.

### 4. Dark Botanical
- **Layout**: Centered content on dark, abstract soft shapes in corner.
- **Fonts**: Display `Cormorant` 400-600 (serif) / Body `IBM Plex Sans` 300-400
- **Colors**: bg `#0f0f0f`, fg `#e8e4df`, muted `#9a9590`, accents `#d4a574` (warm), `#e8b4b8` (pink), `#c9b896` (gold)
- **Signature**: Blurred overlapping gradient circles, thin vertical accent lines, italic signatures. **Abstract CSS shapes only — no illustrations.**

### 9. Neon Cyber
- **Fonts**: `Clash Display` + `Satoshi` (Fontshare)
- **Colors**: navy `#0a0f1c`, cyan `#00ffcc`, magenta `#ff00aa`
- **Signature**: Particle backgrounds, neon glow, grid patterns.

### 10. Terminal Green
- **Fonts**: `JetBrains Mono` (mono only)
- **Colors**: GitHub dark `#0d1117`, terminal green `#39d353`
- **Signature**: Scan lines, blinking cursor, code-syntax styling. **Use for DevTools / infra decks where the medium is the message.**

---

## Light Themes

### 5. Notebook Tabs
- **Layout**: Cream paper card on dark background, colorful tabs on right edge.
- **Fonts**: Display `Bodoni Moda` 400-700 (editorial serif) / Body `DM Sans` 400-500
- **Colors**: outer `#2d2d2d`, page `#f8f6f1`, fg `#1a1a1a`, tabs `#98d4bb` (mint) `#c7b8ea` (lavender) `#f4b8c5` (pink) `#a8d8ea` (sky) `#ffe6a7` (cream)
- **Signature**: Paper container with subtle shadow, vertical-text section tabs on right, binder holes on left. Tabs scale `clamp(0.5rem,1vh,0.7rem)`.

### 6. Pastel Geometry
- **Layout**: White card on pastel bg, vertical pills on right edge with varying heights.
- **Fonts**: `Plus Jakarta Sans` 700-800 / `Plus Jakarta Sans` 400-500
- **Colors**: bg `#c8d9e6`, card `#faf9f7`, pills `#f0b4d4` (pink) `#a8d4c4` (mint) `#5a7c6a` (sage) `#9b8dc4` (lavender) `#7c6aad` (violet)
- **Signature**: Rounded card with soft shadow, pill heights short→medium→tall→medium→short pattern.

### 7. Split Pastel
- **Layout**: Two-color vertical split (peach left, lavender right).
- **Fonts**: `Outfit` 700-800 / `Outfit` 400-500
- **Colors**: peach `#f5e6dc`, lavender `#e4dff0`, badges mint `#c8f0d8` / yellow `#f0f0c8` / pink `#f0d4e0`
- **Signature**: Playful badge pills with icons, grid pattern overlay on right, rounded CTA buttons.

### 8. Vintage Editorial
- **Layout**: Centered content on cream, abstract geometric shapes as accent.
- **Fonts**: Display `Fraunces` 700-900 (distinctive serif) / Body `Work Sans` 400-500
- **Colors**: bg `#f5f3ee`, fg `#1a1a1a`, muted `#555`, accent `#e8d4c0`
- **Signature**: Circle outline + line + dot abstract shapes, bold bordered CTA boxes, witty conversational copy. **Geometric CSS shapes only.**

### 11. Swiss Modern
- **Fonts**: `Archivo` 800 + `Nunito` 400
- **Colors**: pure white, pure black, red accent `#ff3300`
- **Signature**: Visible grid, asymmetric layouts, geometric shapes.

### 12. Paper & Ink
- **Fonts**: `Cormorant Garamond` + `Source Serif 4`
- **Colors**: cream `#faf9f7`, charcoal `#1a1a1a`, crimson `#c41e3a`
- **Signature**: Drop caps, pull quotes, elegant horizontal rules.

---

## Font Pairing Quick Reference

| Preset | Display | Body | Source |
|--------|---------|------|--------|
| Bold Signal | Archivo Black | Space Grotesk | Google |
| Electric Studio | Manrope | Manrope | Google |
| Creative Voltage | Syne | Space Mono | Google |
| Dark Botanical | Cormorant | IBM Plex Sans | Google |
| Notebook Tabs | Bodoni Moda | DM Sans | Google |
| Pastel Geometry | Plus Jakarta Sans | Plus Jakarta Sans | Google |
| Split Pastel | Outfit | Outfit | Google |
| Vintage Editorial | Fraunces | Work Sans | Google |
| Neon Cyber | Clash Display | Satoshi | Fontshare |
| Terminal Green | JetBrains Mono | JetBrains Mono | Google |
| Swiss Modern | Archivo | Nunito | Google |
| Paper & Ink | Cormorant Garamond | Source Serif 4 | Google |

## DO NOT USE (generic AI patterns)

- **Fonts**: Inter, Roboto, Arial, system fonts as display
- **Colors**: `#6366f1` (default indigo), purple-on-white gradients
- **Layouts**: everything centered, generic hero, identical card grids
- **Decorations**: realistic illustrations, gratuitous glassmorphism, drop shadows without purpose

## CSS Gotcha — Negating function values

```css
/* WRONG — silently ignored, no console error */
right: -clamp(28px, 3.5vw, 44px);
margin-left: -min(10vw, 100px);

/* CORRECT — wrap in calc() */
right: calc(-1 * clamp(28px, 3.5vw, 44px));
margin-left: calc(-1 * min(10vw, 100px));
```

CSS does not allow a leading `-` before function names. The browser drops the entire declaration and the element appears in the wrong position. **Always use `calc(-1 * ...)` to negate.**

## Built-in CLI presets

A subset of these are available as `slive create --preset <name>`:
- `bold-signal`
- `dark-botanical`
- `terminal-green`

The rest are documented here so AI can generate them on demand following the spec above. Adding new built-in presets is just adding a builder function in `src/living_slides/templates.py`.

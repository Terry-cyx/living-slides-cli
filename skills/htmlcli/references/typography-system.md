# Typography System

Professional typography is the difference between "web page" and "slide."

## Type Scale (1.25 ratio — Major Third)

| Token | Size | Use |
|-------|------|-----|
| `--text-xs` | 14px | Eyebrow labels, footnotes, source citations |
| `--text-sm` | 16px | Captions, small body text |
| `--text-base` | 20px | Body text, paragraphs |
| `--text-lg` | 24px | Subtitles, h3 headings |
| `--text-xl` | 32px | Section headings |
| `--text-2xl` | 40px | Slide titles (content slides) |
| `--text-3xl` | 56px | Slide titles (emphasis) |
| `--text-4xl` | 72px | Hero titles |
| `--text-5xl` | 96px | Title slide hero |
| `--text-6xl` | 120px | Big number displays |

**Rule**: Never use a size not in the scale. If 40px is too small, use 56px — not 48px.

## Slide Title Sizing Matrix

| Slide Type | Title Size |
|-----------|-----------|
| Cover / title slide | `--text-5xl` (96px) |
| Section divider | `--text-4xl` (72px) |
| Content slide | `--text-2xl` (40px) |
| Big number slide | Number: 180-240px custom, label: `--text-xl` |
| Quote slide | Quote: `--text-2xl` |
| Data slide | Insight title: `--text-2xl` |

## Line Length

**Optimal**: 45-75 characters per line
**Ideal**: 60 characters
**Maximum**: 90 characters

Enforce with: `max-width: 60ch` on titles, `max-width: 70ch` on body text.

## Line Height

| Element | Line Height |
|---------|------------|
| Display titles (>= 56px) | 1.1 |
| H2 headings (32-48px) | 1.2 |
| Body paragraphs | 1.5-1.6 |
| Captions, small text | 1.4 |

## Letter Spacing (Tracking)

| Element | Tracking |
|---------|---------|
| Large titles (≥ 40px) | `-0.02em` to `-0.04em` (tighter) |
| Body text | `0` (normal) |
| ALL CAPS / eyebrow labels | `+0.05em` to `+0.1em` (wider) |
| Tabular numerals in data | `0` + `font-variant-numeric: tabular-nums` |

## Font Families

### Default (Inter)

Modern, neutral, highly legible. Use for 90% of decks.

```html
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
```

```css
--font-display: 'Inter', -apple-system, 'Segoe UI', sans-serif;
--font-body: 'Inter', -apple-system, 'Segoe UI', sans-serif;
```

### Tech / Developer (Geist + Geist Mono)

```html
<link href="https://fonts.googleapis.com/css2?family=Geist:wght@400;500;600;700;800&family=Geist+Mono:wght@400;500;700&display=swap" rel="stylesheet">
```

### Editorial (Fraunces + Inter)

Headlines in serif, body in sans. Premium magazine feel.

```html
<link href="https://fonts.googleapis.com/css2?family=Fraunces:wght@600;800;900&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
```

```css
--font-display: 'Fraunces', Georgia, serif;
--font-body: 'Inter', sans-serif;
```

### Chinese Decks

For Chinese content, add noto or system fallbacks:

```html
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@400;500;700;900&display=swap" rel="stylesheet">
```

```css
--font-display: 'Inter', 'Noto Sans SC', 'PingFang SC', 'Microsoft YaHei', sans-serif;
--font-body: 'Inter', 'Noto Sans SC', 'PingFang SC', 'Microsoft YaHei', sans-serif;
```

## Font Weight Usage

| Weight | Use |
|--------|-----|
| 400 (Regular) | Body text |
| 500 (Medium) | Emphasized body text, labels |
| 600 (SemiBold) | h3, small headings, buttons |
| 700 (Bold) | h2 slide titles |
| 800 (ExtraBold) | h1 hero titles |
| 900 (Black) | Big number displays only |

**Rule**: Maximum 3 weights per deck. Typically: 400, 600, 800.

## Common Typography Mistakes

- ❌ Using too many weights (400, 500, 600, 700, 800 all on one slide)
- ❌ Centered long paragraphs (left-align anything >2 lines)
- ❌ Underlining (looks like a link — use weight or color instead)
- ❌ Italic for emphasis in short text (use weight)
- ❌ Mixing 3+ font families
- ❌ Body text smaller than 18px (unreadable from distance)
- ❌ Tracking at default for 72+px titles (must be tighter)
- ❌ Large titles at 1.5 line-height (too loose — use 1.1)
- ❌ Decorative display fonts for body text

## Font Smoothing

Always include in the base CSS:

```css
html {
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
    text-rendering: optimizeLegibility;
    font-feature-settings: "ss01", "cv11", "tnum";
}
```

## Readability Test

**Squint test**: Can you read the title from across the room without glasses? If not, make it bigger.

**Grandma test**: Can someone unfamiliar with the content understand the slide from the title alone? If not, rewrite the title.

# Design Tokens

Every professional presentation uses tokens instead of hardcoded values. Copy these into the `:root` of every slide deck you generate.

## Base Token Set (Dark Theme)

```css
:root {
    /* ===== SPACING ===== */
    --s-1: 8px;
    --s-2: 16px;
    --s-3: 24px;
    --s-4: 32px;
    --s-5: 48px;
    --s-6: 64px;
    --s-7: 96px;
    --s-8: 128px;

    /* ===== TYPOGRAPHY SCALE (1.25 major third) ===== */
    --text-xs: 14px;
    --text-sm: 16px;
    --text-base: 20px;
    --text-lg: 24px;
    --text-xl: 32px;
    --text-2xl: 40px;
    --text-3xl: 56px;
    --text-4xl: 72px;
    --text-5xl: 96px;
    --text-6xl: 120px;

    /* ===== FONT FAMILIES ===== */
    --font-display: 'Inter', -apple-system, 'Segoe UI', system-ui, sans-serif;
    --font-body: 'Inter', -apple-system, 'Segoe UI', system-ui, sans-serif;
    --font-mono: 'Geist Mono', 'Cascadia Code', 'Fira Code', ui-monospace, monospace;

    /* ===== LINE HEIGHTS ===== */
    --lh-tight: 1.1;
    --lh-snug: 1.25;
    --lh-normal: 1.5;
    --lh-relaxed: 1.6;

    /* ===== LETTER SPACING ===== */
    --tracking-tight: -0.03em;
    --tracking-normal: 0;
    --tracking-wide: 0.05em;

    /* ===== COLORS — DARK THEME ===== */
    --color-bg: #0A0A0A;
    --color-bg-elevated: #161616;
    --color-bg-accent: #1F1F23;

    --color-fg: #FAFAFA;
    --color-fg-muted: #A1A1AA;
    --color-fg-subtle: #71717A;

    --color-border: #27272A;
    --color-border-subtle: #1F1F23;

    /* Brand (customize per deck) */
    --color-primary: #6366F1;
    --color-primary-hover: #818CF8;
    --color-accent: #F59E0B;

    /* Semantic */
    --color-success: #10B981;
    --color-warning: #F59E0B;
    --color-error: #EF4444;
    --color-info: #3B82F6;

    /* ===== BORDER RADIUS ===== */
    --radius-sm: 4px;
    --radius-md: 8px;
    --radius-lg: 12px;
    --radius-xl: 16px;
    --radius-2xl: 24px;
    --radius-full: 9999px;

    /* ===== SHADOWS (layered, low opacity) ===== */
    --shadow-sm: 0 1px 2px rgba(0,0,0,.06);
    --shadow-md: 0 1px 2px rgba(0,0,0,.04), 0 8px 24px rgba(0,0,0,.08);
    --shadow-lg: 0 1px 2px rgba(0,0,0,.04), 0 16px 48px rgba(0,0,0,.12);
    --shadow-glow: 0 0 40px rgba(99, 102, 241, 0.3);

    /* ===== TRANSITIONS ===== */
    --ease-out: cubic-bezier(0.16, 1, 0.3, 1);
    --ease-in-out: cubic-bezier(0.4, 0, 0.2, 1);
    --duration-fast: 150ms;
    --duration-base: 250ms;
    --duration-slow: 400ms;
}
```

## Light Theme Override

```css
[data-theme="light"] {
    --color-bg: #FAFAFA;
    --color-bg-elevated: #FFFFFF;
    --color-bg-accent: #F4F4F5;

    --color-fg: #18181B;
    --color-fg-muted: #52525B;
    --color-fg-subtle: #A1A1AA;

    --color-border: #E4E4E7;
    --color-border-subtle: #F4F4F5;
}
```

## Theme Variants

### "Midnight Blue" — Corporate/Finance
```css
--color-bg: #0B1121;
--color-bg-elevated: #131A2E;
--color-primary: #3B82F6;
--color-accent: #06B6D4;
```

### "Warm Editorial" — Editorial/Design
```css
--color-bg: #FAF9F6;
--color-fg: #1A1A1A;
--color-primary: #DC2626;
--font-display: 'Fraunces', Georgia, serif;
--font-body: 'Inter', sans-serif;
```

### "Tech Noir" — Developer/Tech Talk
```css
--color-bg: #0D1117;
--color-bg-elevated: #161B22;
--color-fg: #C9D1D9;
--color-primary: #58A6FF;
--color-accent: #7C3AED;
--font-display: 'Geist', 'Inter', sans-serif;
--font-mono: 'Geist Mono', monospace;
```

### "Startup Vibrant" — Pitch Deck
```css
--color-bg: #0A0A0A;
--color-primary: #F43F5E;
--color-accent: #8B5CF6;
/* Gradient titles */
--gradient-title: linear-gradient(135deg, #F43F5E 0%, #8B5CF6 100%);
```

## Usage Rules

1. **Never hardcode values** — always reference tokens: `padding: var(--s-5)` not `padding: 48px`
2. **Respect the scale** — if you need a size not in the scale, pick the nearest token, don't invent new ones
3. **Pick ONE theme per deck** — don't mix themes across slides
4. **Customize ONLY primary + accent** per deck — keep neutrals and scale consistent
5. **Use semantic colors for meaning only** — success/warning/error should mean those things

## 60-30-10 Color Application

For every slide, distribute colors:
- **60%** — background (neutral)
- **30%** — primary content area (cards, text)
- **10%** — accent (highlights, CTAs, focal points)

## Font Loading

Include at the top of `<head>`:

```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
```

For tech decks, add Geist Mono:
```html
<link href="https://fonts.googleapis.com/css2?family=Geist+Mono:wght@400;500;700&display=swap" rel="stylesheet">
```

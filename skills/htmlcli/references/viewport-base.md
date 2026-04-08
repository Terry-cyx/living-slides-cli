# Viewport Base CSS

**Mandatory base styles for every slide deck.** Paste this entire CSS block into the `<style>` of any deck — it locks each slide to one viewport, prevents overflow, and scales typography responsively with `clamp()`.

> **Attribution**: Adapted verbatim (with token-name alignment to htmlcli's `--color-*` / `--s-*` system) from [zarazhangrui/frontend-slides](https://github.com/zarazhangrui/frontend-slides) `viewport-base.css` (MIT). Use as the **first** CSS layer; preset / theme tokens override afterwards; deck-chrome variables override last.

## Why this exists

The single most common AI-slide failure mode is "the slide content overflows the viewport, the user has to scroll inside a slide." This file makes that **physically impossible** by:

1. Locking `html, body` to `100%` height with `overflow-x: hidden`
2. Forcing every `.slide` to `100vh` (with `100dvh` mobile fallback)
3. Setting `overflow: hidden` on `.slide` and `.slide-content` (double protection)
4. Wrapping every type token in `clamp(min, vw-relative, max)` so titles shrink on small screens
5. Aggressive `@media (max-height: …)` breakpoints that compress padding and hide non-essential chrome on short viewports

## The CSS

```css
/* ===========================================
   VIEWPORT FITTING: MANDATORY BASE STYLES
   Include this ENTIRE block in every presentation.
   =========================================== */

/* 1. Lock html/body to viewport */
html, body {
    height: 100%;
    overflow-x: hidden;
}
html {
    scroll-snap-type: y mandatory;
    scroll-behavior: smooth;
}

/* 2. Each slide = exact viewport height */
.slide {
    width: 100vw;
    height: 100vh;
    height: 100dvh; /* Dynamic viewport height for mobile browsers */
    overflow: hidden; /* CRITICAL: Prevent ANY overflow */
    scroll-snap-align: start;
    display: flex;
    flex-direction: column;
    position: relative;
}

/* 3. Content container with flex for centering */
.slide-content {
    flex: 1;
    display: flex;
    flex-direction: column;
    justify-content: center;
    max-height: 100%;
    overflow: hidden; /* Double-protection against overflow */
    padding: var(--slide-padding);
}

/* 4. ALL typography uses clamp() for responsive scaling */
:root {
    --title-size:   clamp(1.5rem, 5vw, 4rem);
    --h2-size:      clamp(1.25rem, 3.5vw, 2.5rem);
    --h3-size:      clamp(1rem, 2.5vw, 1.75rem);
    --body-size:    clamp(0.75rem, 1.5vw, 1.125rem);
    --small-size:   clamp(0.65rem, 1vw, 0.875rem);

    --slide-padding: clamp(1rem, 4vw, 4rem);
    --content-gap:   clamp(0.5rem, 2vw, 2rem);
    --element-gap:   clamp(0.25rem, 1vw, 1rem);
}

/* 5. Cards/containers use viewport-relative max sizes */
.card, .container, .content-box {
    max-width: min(90vw, 1000px);
    max-height: min(80vh, 700px);
}

/* 6. Lists auto-scale with viewport */
.feature-list, .bullet-list { gap: clamp(0.4rem, 1vh, 1rem); }
.feature-list li, .bullet-list li {
    font-size: var(--body-size);
    line-height: 1.4;
}

/* 7. Grids adapt to available space */
.grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(min(100%, 250px), 1fr));
    gap: clamp(0.5rem, 1.5vw, 1rem);
}

/* 8. Images constrained to viewport */
img, .image-container {
    max-width: 100%;
    max-height: min(50vh, 400px);
    object-fit: contain;
}

/* === RESPONSIVE BREAKPOINTS — aggressive scaling for short viewports === */

@media (max-height: 700px) {
    :root {
        --slide-padding: clamp(0.75rem, 3vw, 2rem);
        --content-gap:   clamp(0.4rem, 1.5vw, 1rem);
        --title-size:    clamp(1.25rem, 4.5vw, 2.5rem);
        --h2-size:       clamp(1rem, 3vw, 1.75rem);
    }
}
@media (max-height: 600px) {
    :root {
        --slide-padding: clamp(0.5rem, 2.5vw, 1.5rem);
        --content-gap:   clamp(0.3rem, 1vw, 0.75rem);
        --title-size:    clamp(1.1rem, 4vw, 2rem);
        --body-size:     clamp(0.7rem, 1.2vw, 0.95rem);
    }
    .nav-dots, .keyboard-hint, .decorative { display: none; }
}
@media (max-height: 500px) {
    :root {
        --slide-padding: clamp(0.4rem, 2vw, 1rem);
        --title-size:    clamp(1rem, 3.5vw, 1.5rem);
        --h2-size:       clamp(0.9rem, 2.5vw, 1.25rem);
        --body-size:     clamp(0.65rem, 1vw, 0.85rem);
    }
}
@media (max-width: 600px) {
    :root { --title-size: clamp(1.25rem, 7vw, 2.5rem); }
    .grid { grid-template-columns: 1fr; }
}

/* === REDUCED MOTION — respect user preferences === */
@media (prefers-reduced-motion: reduce) {
    *, *::before, *::after {
        animation-duration: 0.01ms !important;
        transition-duration: 0.2s !important;
    }
    html { scroll-behavior: auto; }
}
```

## Layering order

When generating a deck, write CSS in this order so cascade works correctly:

1. `viewport-base` (this file) — locks viewport, defines `--*-size` and `--slide-padding`
2. **Preset tokens** from `style-presets.md` — `--color-bg`, `--color-fg`, font families
3. `design-tokens.md` — htmlcli core tokens (`--s-*`, `--text-*`, `--color-*`)
4. **Deck chrome** tokens — `--deck-chrome-bg`, `--deck-chrome-accent`, etc. (only if you ship the editor runtime)
5. **Slide-specific** styles last

## Verification

After generating, eyeball at three sizes:
- 1920×1080 (presentation projector)
- 1280×720 (laptop)
- 1024×600 (short laptop)

**No slide should ever scroll internally.** If one does, the issue is almost always: a fixed `px` height somewhere, or a `flex` child without `min-height: 0`.

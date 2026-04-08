# Professional Slide Template

Base HTML structure for every presentation. Copy this and fill in slides.

## Complete Template

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{DECK_TITLE}}</title>

    <!-- Fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">

    <!-- Chart.js for data visualization -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>

    <style>
        /* ===== DESIGN TOKENS ===== */
        /* Paste from references/design-tokens.md */
        :root {
            --s-1: 8px; --s-2: 16px; --s-3: 24px; --s-4: 32px;
            --s-5: 48px; --s-6: 64px; --s-7: 96px; --s-8: 128px;
            --text-xs: 14px; --text-sm: 16px; --text-base: 20px;
            --text-lg: 24px; --text-xl: 32px; --text-2xl: 40px;
            --text-3xl: 56px; --text-4xl: 72px; --text-5xl: 96px;
            --text-6xl: 120px;
            --font-display: 'Inter', sans-serif;
            --font-body: 'Inter', sans-serif;
            --lh-tight: 1.1; --lh-snug: 1.25; --lh-normal: 1.5;
            --tracking-tight: -0.03em;
            --color-bg: #0A0A0A;
            --color-bg-elevated: #161616;
            --color-fg: #FAFAFA;
            --color-fg-muted: #A1A1AA;
            --color-fg-subtle: #71717A;
            --color-border: #27272A;
            --color-primary: #6366F1;
            --color-accent: #F59E0B;
            --radius-md: 8px; --radius-lg: 12px; --radius-xl: 16px;
            --shadow-md: 0 1px 2px rgba(0,0,0,.04), 0 8px 24px rgba(0,0,0,.08);
            --ease-out: cubic-bezier(0.16, 1, 0.3, 1);
        }

        /* ===== RESET ===== */
        *, *::before, *::after { margin: 0; padding: 0; box-sizing: border-box; }
        html, body {
            width: 100%; height: 100%;
            background: var(--color-bg);
            color: var(--color-fg);
            font-family: var(--font-body);
            font-size: var(--text-base);
            line-height: var(--lh-normal);
            -webkit-font-smoothing: antialiased;
            text-rendering: optimizeLegibility;
            overflow: hidden;
        }

        /* ===== 16:9 SLIDE CANVAS ===== */
        .deck {
            position: fixed;
            inset: 0;
            display: flex;
            align-items: center;
            justify-content: center;
            background: #000;
        }
        .slide {
            position: absolute;
            width: min(100vw, calc(100vh * 16 / 9));
            height: min(100vh, calc(100vw * 9 / 16));
            aspect-ratio: 16 / 9;
            display: flex;
            flex-direction: column;
            padding: var(--s-7) var(--s-8);
            background: var(--color-bg);
            opacity: 0;
            visibility: hidden;
            transition: opacity var(--duration-base, 300ms) var(--ease-out);
            overflow: hidden;
        }
        .slide.active { opacity: 1; visibility: visible; }

        /* ===== TYPOGRAPHY ===== */
        h1.slide-title {
            font-family: var(--font-display);
            font-size: var(--text-3xl);
            font-weight: 800;
            line-height: var(--lh-tight);
            letter-spacing: var(--tracking-tight);
            color: var(--color-fg);
        }
        h2.slide-title {
            font-family: var(--font-display);
            font-size: var(--text-2xl);
            font-weight: 700;
            line-height: var(--lh-tight);
            letter-spacing: var(--tracking-tight);
            color: var(--color-fg);
            margin-bottom: var(--s-3);
        }
        h3 {
            font-family: var(--font-display);
            font-size: var(--text-lg);
            font-weight: 600;
            color: var(--color-fg);
            margin-bottom: var(--s-2);
        }
        p { font-size: var(--text-base); color: var(--color-fg-muted); }
        .subtitle { font-size: var(--text-lg); color: var(--color-fg-muted); margin-top: var(--s-3); }
        .eyebrow {
            font-size: var(--text-xs);
            text-transform: uppercase;
            letter-spacing: var(--tracking-wide, 0.05em);
            color: var(--color-fg-subtle);
            font-weight: 600;
            margin-bottom: var(--s-2);
        }

        /* ===== SLIDE STRUCTURE (header, body, footer) ===== */
        .slide-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding-bottom: var(--s-4);
        }
        .slide-body {
            flex: 1;
            display: flex;
            flex-direction: column;
            justify-content: center;
            gap: var(--s-4);
        }
        .slide-footer {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding-top: var(--s-4);
            font-size: var(--text-xs);
            color: var(--color-fg-subtle);
        }

        /* ===== LAYOUT PATTERNS ===== */
        .layout-hero {
            justify-content: center;
            align-items: flex-start;
        }
        .layout-hero h1.slide-title { font-size: var(--text-5xl); max-width: 16ch; }

        .layout-split {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: var(--s-6);
            align-items: center;
            flex: 1;
        }

        .layout-grid-3 {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: var(--s-4);
        }
        .layout-grid-4 {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: var(--s-3);
        }

        /* ===== CARDS ===== */
        .card {
            background: var(--color-bg-elevated);
            border: 1px solid var(--color-border);
            border-radius: var(--radius-xl);
            padding: var(--s-4);
        }
        .card-metric .value {
            font-size: var(--text-4xl);
            font-weight: 800;
            letter-spacing: var(--tracking-tight);
            line-height: 1;
            background: linear-gradient(135deg, var(--color-primary), var(--color-accent));
            -webkit-background-clip: text;
            background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .card-metric .label {
            font-size: var(--text-xs);
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: var(--color-fg-subtle);
            margin-top: var(--s-2);
        }

        /* ===== NAVIGATION ===== */
        .nav {
            position: fixed;
            bottom: var(--s-3);
            left: 50%;
            transform: translateX(-50%);
            display: flex;
            align-items: center;
            gap: var(--s-2);
            background: rgba(0,0,0,0.6);
            backdrop-filter: blur(12px);
            border: 1px solid var(--color-border);
            padding: var(--s-1) var(--s-3);
            border-radius: var(--radius-full);
            z-index: 100;
        }
        .nav-btn {
            background: transparent;
            color: var(--color-fg-muted);
            border: none;
            width: 28px; height: 28px;
            border-radius: var(--radius-full);
            cursor: pointer;
            font-size: var(--text-sm);
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .nav-btn:hover { color: var(--color-fg); background: var(--color-bg-elevated); }
        .nav-counter { font-size: var(--text-xs); color: var(--color-fg-subtle); font-variant-numeric: tabular-nums; }
        .progress-bar {
            position: fixed;
            top: 0; left: 0;
            height: 2px;
            background: var(--color-primary);
            transition: width 300ms var(--ease-out);
            z-index: 101;
        }

        /* ===== ANIMATIONS ===== */
        @keyframes fadeUp {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .slide.active .animate-in {
            animation: fadeUp 600ms var(--ease-out) forwards;
        }
        .slide.active .animate-in:nth-child(1) { animation-delay: 0ms; }
        .slide.active .animate-in:nth-child(2) { animation-delay: 80ms; }
        .slide.active .animate-in:nth-child(3) { animation-delay: 160ms; }
        .slide.active .animate-in:nth-child(4) { animation-delay: 240ms; }
        .slide.active .animate-in:nth-child(5) { animation-delay: 320ms; }

        @media (prefers-reduced-motion: reduce) {
            *, *::before, *::after {
                animation-duration: 0.01ms !important;
                transition-duration: 0.01ms !important;
            }
        }

        /* ===== MOBILE FALLBACK ===== */
        @media (max-width: 768px) {
            .slide { padding: var(--s-4) var(--s-3); }
            h1.slide-title { font-size: var(--text-2xl); }
            h2.slide-title { font-size: var(--text-xl); }
            .layout-split, .layout-grid-3, .layout-grid-4 { grid-template-columns: 1fr; gap: var(--s-3); }
        }
    </style>
</head>
<body>

<div class="progress-bar" id="progressBar" style="width: 0%"></div>

<div class="deck">

    <!-- SLIDE 1: TITLE -->
    <section class="slide active layout-hero">
        <div class="slide-header">
            <span class="eyebrow">{{SECTION_LABEL}}</span>
            <span class="eyebrow">{{DATE}}</span>
        </div>
        <div class="slide-body">
            <h1 class="slide-title animate-in">{{MAIN_TITLE}}</h1>
            <p class="subtitle animate-in">{{SUBTITLE}}</p>
        </div>
        <div class="slide-footer">
            <span>{{AUTHOR}}</span>
            <span>1</span>
        </div>
    </section>

    <!-- SLIDE 2: METRICS DASHBOARD EXAMPLE -->
    <section class="slide">
        <div class="slide-header">
            <span class="eyebrow">KEY METRICS</span>
            <span class="eyebrow">{{DATE}}</span>
        </div>
        <div class="slide-body">
            <h2 class="slide-title animate-in">{{INSIGHT_HEADLINE}}</h2>
            <div class="layout-grid-4">
                <div class="card card-metric animate-in">
                    <div class="value">$1.2M</div>
                    <div class="label">Revenue</div>
                </div>
                <div class="card card-metric animate-in">
                    <div class="value">+24%</div>
                    <div class="label">Growth</div>
                </div>
                <div class="card card-metric animate-in">
                    <div class="value">92</div>
                    <div class="label">NPS</div>
                </div>
                <div class="card card-metric animate-in">
                    <div class="value">2.1%</div>
                    <div class="label">Churn</div>
                </div>
            </div>
        </div>
        <div class="slide-footer">
            <span>{{AUTHOR}}</span>
            <span>2</span>
        </div>
    </section>

    <!-- ADD MORE SLIDES HERE -->

</div>

<nav class="nav">
    <button class="nav-btn" data-action="prev" aria-label="Previous slide">←</button>
    <span class="nav-counter"><span id="current">1</span> / <span id="total">2</span></span>
    <button class="nav-btn" data-action="next" aria-label="Next slide">→</button>
</nav>

<script>
(function() {
    const slides = document.querySelectorAll('.slide');
    const total = slides.length;
    const currentEl = document.getElementById('current');
    const totalEl = document.getElementById('total');
    const progressEl = document.getElementById('progressBar');
    let current = 0;

    totalEl.textContent = total;

    function showSlide(n) {
        n = Math.max(0, Math.min(total - 1, n));
        current = n;
        slides.forEach((s, i) => s.classList.toggle('active', i === n));
        currentEl.textContent = n + 1;
        progressEl.style.width = ((n + 1) / total * 100) + '%';
    }

    function next() { showSlide(current + 1); }
    function prev() { showSlide(current - 1); }

    document.querySelectorAll('[data-action="next"]').forEach(b => b.addEventListener('click', next));
    document.querySelectorAll('[data-action="prev"]').forEach(b => b.addEventListener('click', prev));

    document.addEventListener('keydown', (e) => {
        if (e.key === 'ArrowRight' || e.key === ' ' || e.key === 'PageDown') { e.preventDefault(); next(); }
        if (e.key === 'ArrowLeft' || e.key === 'PageUp') { e.preventDefault(); prev(); }
        if (e.key === 'Home') showSlide(0);
        if (e.key === 'End') showSlide(total - 1);
    });

    showSlide(0);
})();
</script>

</body>
</html>
```

## Slide Boilerplate Snippets

### Every slide must have this structure:
```html
<section class="slide" id="slide-1" data-oid="s1">
    <div class="slide-header">
        <span class="eyebrow" data-oid="s1-eyebrow">SECTION LABEL</span>
        <span class="eyebrow" data-oid="s1-context">CONTEXT (date, brand)</span>
    </div>
    <div class="slide-body">
        <h2 class="slide-title" data-oid="s1-title">The one focal headline</h2>
        <!-- More slide objects, each with its own data-oid -->
    </div>
    <div class="slide-footer">
        <span data-oid="s1-author">Author/Brand</span>
        <span>1</span>
    </div>
</section>
```

This three-zone structure (header/body/footer) is what makes HTML feel like a "slide" instead of a "web page."

## `data-oid` — Stable object identifiers (REQUIRED)

Every meaningful slide object — title, body text, card, image wrapper — **must carry a `data-oid` attribute** with a deck-unique stable string. Convention:

- Slide root: `data-oid="s1"`, `data-oid="s2"`, …
- Objects inside slide N: `data-oid="sN-<role>"` — e.g. `s1-title`, `s1-lede`, `s1-card`, `s2-chart`

### Why

Adapted from [`frontend-slides-editable/editor-runtime.md`](https://github.com/archlizheng/frontend-slides-editable) (MIT). Without `data-oid`, the differ falls back to CSS-path-style selectors (`section.slide.is-active > div.slide-body > h2.slide-title`). Those break the moment the user moves an element to a different parent or adds a wrapper div.

With `data-oid`, the differ writes selectors like `[data-oid="s1-title"]` — which survive moves, wraps, reorders, and class changes. AI receives a changelog where each entry points to **the same logical object even after the user has rearranged the DOM around it**.

### Example changelog with stable selectors

```json
{
  "changes": [
    {"type": "text_edit", "selector": "[data-oid=\"s1-title\"]", "before": "Welcome", "after": "Q1 Review"},
    {"type": "text_edit", "selector": "[data-oid=\"s2-lede\"]", "before": "...", "after": "..."}
  ]
}
```

When refining, AI can confidently grep `data-oid="s1-title"` to find the exact node to edit, regardless of how nested it has become.

### Generator checklist

1. Every `<section class="slide">` has a unique `id="slide-N"` **and** `data-oid="sN"`.
2. Every text-bearing element in the slide body has `data-oid="sN-<role>"`.
3. Every card / image / chart wrapper has `data-oid="sN-<role>"`.
4. `data-oid` must be unique across the **entire document**, not per slide.
5. Decorative elements (gradient circles, scan-line overlays) do **not** need `data-oid` — they're not editable objects.

## Chart.js Theme Override

Always theme Chart.js to match the deck:

```javascript
Chart.defaults.font.family = "'Inter', sans-serif";
Chart.defaults.font.size = 14;
Chart.defaults.color = '#A1A1AA';
Chart.defaults.borderColor = '#27272A';
Chart.defaults.plugins.legend.labels.color = '#FAFAFA';
Chart.defaults.scale.grid.color = 'rgba(255,255,255,0.05)';
Chart.defaults.scale.ticks.color = '#A1A1AA';
```

Run this once before creating any chart.

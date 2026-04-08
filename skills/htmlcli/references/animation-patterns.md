# Animation Patterns

Match animations to the intended feeling. **Restraint over flair** — one or two motion ideas per deck, not five.

> **Attribution**: Adapted from [zarazhangrui/frontend-slides](https://github.com/zarazhangrui/frontend-slides) `animation-patterns.md` (MIT). The effect-to-feeling table and core CSS snippets are reproduced; htmlcli's `data-oid` and design-token conventions added.

## Effect-to-Feeling Guide

| Feeling | Animations | Visual Cues |
|---------|-----------|-------------|
| **Dramatic / Cinematic** | Slow fade-ins (1–1.5s), large scale transitions (0.9 → 1), parallax | Dark backgrounds, spotlight, full-bleed images |
| **Techy / Futuristic** | Neon glow (`box-shadow`), glitch/scramble text, grid reveals | Particle systems, monospace accents, cyan/magenta/electric blue |
| **Playful / Friendly** | Bouncy easing, floating/bobbing | Rounded corners, pastel/bright colors, hand-drawn elements |
| **Professional / Corporate** | Subtle fast (200–300ms), clean | Navy/slate/charcoal, precise spacing, data viz focus |
| **Calm / Minimal** | Very slow subtle motion, gentle fades | Whitespace, muted palette, serif typography, generous padding |
| **Editorial / Magazine** | Staggered text reveals, image-text interplay | Strong type hierarchy, pull quotes, grid-breaking |

## Entrance Animations

```css
/* Fade + Slide Up — most versatile */
.reveal {
    opacity: 0;
    transform: translateY(30px);
    transition: opacity 0.6s var(--ease-out),
                transform 0.6s var(--ease-out);
}
.visible .reveal {
    opacity: 1;
    transform: translateY(0);
}

/* Scale In */
.reveal-scale {
    opacity: 0;
    transform: scale(0.9);
    transition: opacity 0.6s, transform 0.6s var(--ease-out);
}

/* Slide from Left */
.reveal-left {
    opacity: 0;
    transform: translateX(-50px);
    transition: opacity 0.6s, transform 0.6s var(--ease-out);
}

/* Blur In */
.reveal-blur {
    opacity: 0;
    filter: blur(10px);
    transition: opacity 0.8s, filter 0.8s var(--ease-out);
}
```

## Stagger pattern (for grids and lists)

```css
.slide.active .animate-in              { animation: fadeUp 600ms var(--ease-out) forwards; }
.slide.active .animate-in:nth-child(1) { animation-delay:   0ms; }
.slide.active .animate-in:nth-child(2) { animation-delay:  80ms; }
.slide.active .animate-in:nth-child(3) { animation-delay: 160ms; }
.slide.active .animate-in:nth-child(4) { animation-delay: 240ms; }
.slide.active .animate-in:nth-child(5) { animation-delay: 320ms; }
```

## Background Effects

```css
/* Gradient Mesh — layered radial gradients for depth */
.gradient-bg {
    background:
        radial-gradient(ellipse at 20% 80%, rgba(120, 0, 255, 0.3) 0%, transparent 50%),
        radial-gradient(ellipse at 80% 20%, rgba(0, 255, 200, 0.2) 0%, transparent 50%),
        var(--color-bg);
}

/* Grid Pattern — subtle structural lines */
.grid-bg {
    background-image:
        linear-gradient(rgba(255,255,255,0.03) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255,255,255,0.03) 1px, transparent 1px);
    background-size: 50px 50px;
}
```

## Interactive Effects

```javascript
// 3D Tilt on Hover — adds depth to cards
class TiltEffect {
    constructor(element) {
        this.el = element;
        this.el.style.transformStyle = 'preserve-3d';
        this.el.style.perspective = '1000px';
        this.el.addEventListener('mousemove', (e) => {
            const r = this.el.getBoundingClientRect();
            const x = (e.clientX - r.left) / r.width - 0.5;
            const y = (e.clientY - r.top) / r.height - 0.5;
            this.el.style.transform = `rotateY(${x*10}deg) rotateX(${-y*10}deg)`;
        });
        this.el.addEventListener('mouseleave', () => {
            this.el.style.transform = 'rotateY(0) rotateX(0)';
        });
    }
}
```

## Restraint rules

- **One motion idea per deck**: pick fade-up *or* scale-in *or* blur-in; not all three.
- **Reduced motion**: always respect `@media (prefers-reduced-motion: reduce)` (already in `viewport-base.md`).
- **No animation on body text**: animate the headline, not the paragraph. Long text flickering in is hostile.
- **No animation on `<img>` decoded synchronously**: layout shifts look broken.
- **Re-trigger on slide activation**, not on scroll: the deck navigates by slide, not by scroll position; key off `.slide.active`.

## Troubleshooting

| Problem | Fix |
|---------|-----|
| Animations not triggering | Verify `.slide.active` class is added by your nav script; check Intersection Observer if you use one |
| Fonts not loading | Confirm Google Fonts / Fontshare URL; ensure font names match in CSS |
| Mobile jank | Disable particle effects below 768px; use `transform` / `opacity` only (GPU-accelerated) |
| Performance | Use `will-change` sparingly; throttle scroll handlers; avoid animating `box-shadow` on hover lists |

# Color Systems

## The 60-30-10 Rule

Every slide distributes colors:
- **60%** — background (neutral)
- **30%** — primary content area (cards, text)
- **10%** — accent (CTAs, highlights, focal points)

## Palette Structure

Every deck needs these tokens:

```css
:root {
    /* Neutrals (5-9 shades) */
    --gray-50:  #FAFAFA;
    --gray-100: #F4F4F5;
    --gray-200: #E4E4E7;
    --gray-300: #D4D4D8;
    --gray-400: #A1A1AA;
    --gray-500: #71717A;
    --gray-600: #52525B;
    --gray-700: #3F3F46;
    --gray-800: #27272A;
    --gray-900: #18181B;
    --gray-950: #09090B;

    /* Brand (pick 1 primary) */
    --color-primary: #6366F1;
    --color-primary-hover: #818CF8;

    /* Accent (pick 1-2, use <10% of slide) */
    --color-accent: #F59E0B;

    /* Semantic */
    --color-success: #10B981;
    --color-warning: #F59E0B;
    --color-error: #EF4444;
    --color-info: #3B82F6;
}
```

## Dark vs Light

### Dark Theme (Recommended for Keynote/Stage)

```css
--color-bg: #0A0A0A;       /* NOT pure #000 — reduces halation */
--color-bg-elevated: #161616;
--color-fg: #FAFAFA;       /* NOT pure #FFF — less eye strain */
--color-fg-muted: #A1A1AA;
--color-fg-subtle: #71717A;
--color-border: #27272A;
```

**Use for**: investor decks, keynote stages, technical talks, startup pitches

### Light Theme (Recommended for Handouts/Print)

```css
--color-bg: #FAFAFA;
--color-bg-elevated: #FFFFFF;
--color-fg: #18181B;
--color-fg-muted: #52525B;
--color-fg-subtle: #A1A1AA;
--color-border: #E4E4E7;
```

**Use for**: board decks, corporate reports, printed handouts, training materials

## Contrast Ratios (WCAG)

| Element | Minimum Ratio |
|---------|---------------|
| Body text (≤18px) | **4.5:1** (AA), **7:1** (AAA for projectors) |
| Large text (≥24px) | **3:1** (AA), **4.5:1** (AAA) |
| UI components / icons | **3:1** |
| Decorative only | No minimum |

**Projector rule**: Bump contrast 20% above screen minimums. Projectors wash out colors.

**Test tool**: Use `https://webaim.org/resources/contrastchecker/` to verify every text+bg combination.

## Color Picking by Context

### Corporate / Finance
**Colors**: Blue-dominant, minimal accent
```css
--color-primary: #1E40AF;  /* Deep blue */
--color-accent: #06B6D4;   /* Cyan */
```
**Avoid**: Pink, orange, purple (feels too casual)

### Tech / SaaS
**Colors**: Indigo/purple with cyan or pink accents
```css
--color-primary: #6366F1;
--color-accent: #EC4899;
```

### Healthcare / Wellness
**Colors**: Teal, soft green, clean whites
```css
--color-primary: #0D9488;
--color-accent: #84CC16;
```

### E-commerce / Consumer
**Colors**: Warm, friendly, bold
```css
--color-primary: #F43F5E;
--color-accent: #F59E0B;
```

### Education / Training
**Colors**: Friendly, readable, non-threatening
```css
--color-primary: #3B82F6;
--color-accent: #10B981;
```

## Accent Color Strategy

**The 10% rule**: Accent colors should never exceed 10% of slide area. Use them for:
- Primary CTAs (buttons, calls-to-action)
- Single-color highlights on key numbers
- Focal point indicators (borders, underlines)
- Status indicators (success/warning/error)

**NEVER use accent colors for**:
- Body text backgrounds
- Full slide backgrounds
- Multiple elements competing for attention

## Gradient Usage

### Title Text Gradients
```css
.gradient-title {
    background: linear-gradient(135deg, #6366F1 0%, #EC4899 100%);
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
}
```

**Rules**:
- 2 stops only (no 3-stop rainbows)
- Same hue family or adjacent hues
- 135° angle is classic
- Apply to ONE element per slide, never multiple

### Background Gradients
```css
/* Subtle — barely visible */
background: linear-gradient(135deg, #0A0A0A 0%, #1F1F23 100%);

/* Mesh effect — more dramatic */
background:
    radial-gradient(at 20% 30%, rgba(99,102,241,0.15) 0%, transparent 50%),
    radial-gradient(at 80% 70%, rgba(236,72,153,0.1) 0%, transparent 50%),
    #0A0A0A;
```

## Common Color Mistakes

- ❌ Pure black (#000) or pure white (#FFF) — use #0A0A0A / #FAFAFA
- ❌ More than 1 accent color per slide
- ❌ Gradients on every element
- ❌ 5+ colors in a single chart
- ❌ Colored text on colored background (low contrast)
- ❌ Red and green together (colorblind unfriendly — add shapes/icons)
- ❌ Neon/saturated colors for body text (eye strain)
- ❌ Low contrast "aesthetic" gray-on-gray that can't be read

## Testing Checklist

- [ ] Contrast ratio ≥ 4.5:1 for body text
- [ ] Slide looks OK when converted to grayscale (colorblind-friendly)
- [ ] Projector test: saturation high enough to not wash out
- [ ] Max 3 colors dominate the deck (primary + accent + neutral)
- [ ] Gradients used on max 1 element per slide
- [ ] Red/green distinguishable for colorblind users (shape + color, not color alone)

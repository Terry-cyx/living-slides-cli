# Common Mistakes

The difference between amateur and professional HTML slides is avoiding these pitfalls.

## Layout Mistakes

### ❌ Web Page, Not Slide
Content fills 100vh but has no slide structure (header/body/footer), no 16:9 lock, feels like scrolling a website.

**Fix**: Use the `.slide` class with `aspect-ratio: 16/9` and locked dimensions.

### ❌ Cramped Content
No padding, content touches edges, feels claustrophobic.

**Fix**: Use `padding: var(--s-7) var(--s-8)` (96px / 128px) minimum for content slides.

### ❌ Multiple Focal Points
3 headlines, 2 charts, and 5 icons all competing for attention.

**Fix**: Pick ONE focal point per slide. Everything else supports it.

### ❌ Centered Paragraphs
Long paragraphs center-aligned. Hard to read because eye can't find the start of each line.

**Fix**: Left-align any text block longer than 2 lines.

### ❌ No Whitespace Discipline
Every pixel is filled. Feels dense, overwhelming.

**Fix**: 25% minimum whitespace per slide. Generous margins aren't wasted space.

## Typography Mistakes

### ❌ Random Font Sizes
`font-size: 23px`, `19px`, `45px` — arbitrary values that break the scale.

**Fix**: Use only tokens from the type scale (14, 16, 20, 24, 32, 40, 56, 72, 96, 120).

### ❌ Too Many Font Families
3-4 different fonts on one slide.

**Fix**: Maximum 2 families (one display, one body). Ideally use a single variable font like Inter.

### ❌ Body Text Too Small
12px or 14px body text. Unreadable from 10 feet away.

**Fix**: Minimum 20px for body text on slides.

### ❌ Centered Long Lines
Body text centered with no max-width. Reader's eye loses track.

**Fix**: `max-width: 60ch` and `text-align: left` for body text.

### ❌ All Caps Everywhere
Using CAPS for emphasis in body text.

**Fix**: CAPS only for eyebrow labels (small section markers). Use weight for body emphasis.

### ❌ Default Bullets
Browser default `<ul>` with round dots and default spacing.

**Fix**: Either style them with custom markers (→, ●, custom SVG) or replace with cards/icons.

## Color Mistakes

### ❌ Pure Black / Pure White
`#000` and `#FFF` create harsh contrast that causes eye strain.

**Fix**: Use `#0A0A0A` for backgrounds, `#FAFAFA` for text.

### ❌ Too Many Colors
5+ colors competing across the deck.

**Fix**: 1 primary + 1 accent + neutrals (grays). That's it.

### ❌ Low Contrast "Aesthetic"
Gray text on slightly darker gray background.

**Fix**: Minimum 4.5:1 contrast ratio for body text. Test with a contrast checker.

### ❌ Gradient Overload
Every element has a gradient. Title, cards, backgrounds, borders — all gradients.

**Fix**: Use gradients on ONE element per slide. Usually the title or hero number.

### ❌ Red/Green Only
Success/error indicated only by color, unreadable for colorblind users.

**Fix**: Add shapes or icons (✓/✗) alongside colors.

### ❌ Colored Backgrounds for Text
Colored card backgrounds with colored text — contrast issues.

**Fix**: Dark text on light cards, light text on dark cards. Never colored-on-colored.

## Content Mistakes

### ❌ Topic Titles Instead of Insight Titles
"Q3 Revenue" instead of "Revenue doubled in Q3."

**Fix**: Every title states the insight. The slide is the evidence.

### ❌ Wall of Text
50+ words on a slide.

**Fix**: 10-word rule. If more, split or replace with visuals.

### ❌ 7+ Bullets
Dumping everything onto one slide.

**Fix**: Max 6 bullets, 6 words each (6×6 rule). Better: 3×3.

### ❌ Generic Stock Phrases
"Cutting-edge", "synergy", "leverage", "best-in-class"

**Fix**: Concrete specifics. "94% accuracy" instead of "highly accurate."

### ❌ "Thank You" / "Questions?" Slides
Wasted closing slides.

**Fix**: End on your CTA or key insight.

### ❌ Redundant Subheadings
Subheading that just restates the title.

**Fix**: Subheading should add context, not echo the title.

## Data Visualization Mistakes

### ❌ Default Chart.js Styling
Blue bars, gray gridlines, legend at top — looks like a tech demo.

**Fix**: Override all defaults with deck theme (see `data-visualization.md`).

### ❌ 3D Charts
3D pies, 3D bars, 3D anything.

**Fix**: 2D always. 3D distorts perception.

### ❌ Pie Chart with 8 Slices
Unreadable, can't compare proportions.

**Fix**: Max 5 slices in pie/donut. More = use horizontal bar chart.

### ❌ Dual Y-Axis
Two scales on one chart to cram data.

**Fix**: Split into two charts. Much clearer.

### ❌ No Source Citation
Data without attribution.

**Fix**: Small source line in footer: "Source: Internal, Q4 2025"

### ❌ Chart Title Is the Topic
"Revenue" instead of "Revenue grew 42%."

**Fix**: Chart title states the insight.

## Animation Mistakes

### ❌ Spin, Bounce, Fly-In
PowerPoint-style dramatic animations.

**Fix**: Use only fade-up and subtle scale. Duration 200-400ms.

### ❌ Animations on Every Element
Every word, every bullet animates separately.

**Fix**: Stagger up to 5 items max. Usually only the main focal area animates.

### ❌ Slide Transitions Between Every Slide
Fly-in, cube, flip transitions between slides.

**Fix**: Fade or none. 200ms duration.

### ❌ No Reduced-Motion Respect
Users with motion sensitivity get assaulted.

**Fix**: Wrap animations in `@media (prefers-reduced-motion: reduce)` to disable.

## Structural Mistakes

### ❌ Agenda Slide
"Here's what we'll cover: 1. Intro 2. Problem 3. Solution..."

**Fix**: Just show the content. Audience will figure it out.

### ❌ Inconsistent Layouts
Title position jumps around between slides.

**Fix**: Fixed position for titles (`slide-header` always at top, same height).

### ❌ Missing Footer Context
Slide numbers missing, author missing, no way to reference.

**Fix**: Every slide has footer with page number and author/date.

### ❌ Logo on Every Slide
Brand logo stamped in corner of every slide.

**Fix**: Logo on title slide and closing slide only. Or tiny opacity-60 in footer.

## Process Mistakes

### ❌ Ignoring the Changelog After User Edits
AI regenerates the whole slide, wiping user changes.

**Fix**: Always read `.changelog.json` first. Preserve every user edit.

### ❌ Regenerating Instead of Refining
User made one small edit, AI rewrites the entire slide.

**Fix**: Make minimal, surgical changes. Cascade only what's necessary.

### ❌ Not Verifying After Refinement
AI refines but doesn't verify the HTML still renders.

**Fix**: Run the diff command after refinement. Verify the slide count didn't change unexpectedly.

## The Squint Test

After generating a slide, squint at it. You should see:
- ONE clear focal point
- Visual hierarchy (big → small)
- Generous whitespace
- Aligned elements (everything on the grid)

If it looks like a web page or a blob of text, rewrite.

## The Printed Handout Test

Could this slide work as a printed handout page? If the text is too small or the layout is too cramped to print clearly, it's too cramped for a presentation too.

## The "Screenshot at 50%" Test

Take a screenshot of your slide and view it at 50% size. Can you still identify the title and key point? If not, your hierarchy is weak.

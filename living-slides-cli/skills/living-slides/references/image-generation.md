# Image Generation & Asset Management

living-slides supports three ways to include images in slides: built-in chart generation, external tool integration, and client-side rendering.

## Asset Directory Convention

For any HTML file `mypage.html`, generated images live in `mypage-assets/` next to it:

```
project/
├── mypage.html
└── mypage-assets/
    ├── revenue-chart.png
    ├── architecture-diagram.svg
    └── hero-image.png
```

HTML references them with relative paths: `<img src="./mypage-assets/revenue-chart.png">`

## Method 1: Built-in Chart Generation (matplotlib)

For standard data charts, use `slive asset gen-chart`. It produces themed PNGs matching the deck's dark/light theme.

### Supported Chart Types
- `bar` — vertical bar chart (category comparison)
- `hbar` — horizontal bar chart (rankings)
- `line` — line chart (time series, trends)
- `pie` — pie chart (part-to-whole, 2-5 segments)
- `scatter` — scatter plot (correlation)

### CLI Usage

```bash
# Simple bar chart
slive asset gen-chart deck.html \
  --name revenue \
  --type bar \
  --data '{"labels":["Q1","Q2","Q3","Q4"],"values":[120,190,300,450]}' \
  --title "Revenue by Quarter" \
  --theme dark
```

### Python API (preferred when generating many charts)

```python
from living_slides.assets import generate_chart

# Single-series bar
generate_chart(
    "deck.html",
    name="revenue",
    chart_type="bar",
    data={"labels": ["Q1", "Q2", "Q3"], "values": [100, 200, 300]},
    title="Revenue",
    theme="dark",
)

# Multi-series line
generate_chart(
    "deck.html",
    name="trend",
    chart_type="line",
    data={
        "labels": ["Jan", "Feb", "Mar", "Apr"],
        "series": [
            {"name": "Sales", "values": [10, 20, 30, 40]},
            {"name": "Marketing", "values": [5, 15, 25, 35]},
        ]
    },
    theme="dark",
)

# Pie chart
generate_chart(
    "deck.html",
    name="breakdown",
    chart_type="pie",
    data={"labels": ["Product", "Services", "Other"], "values": [60, 30, 10]},
)
```

Generated images are PNG, 1200×720 at 120 DPI, sized to fit 16:9 slide layouts.

## Method 2: External Tool Integration

When you need AI-generated images, complex Python visualizations, or diagrams beyond the built-in types, generate them with any tool and import into the assets directory.

### Workflow

1. **Generate** an image using any tool:
   - Custom Python script (matplotlib, plotly, seaborn, altair)
   - AI image generator (DALL-E, Stable Diffusion, Midjourney)
   - Diagramming tool (mermaid-cli, graphviz, draw.io export)
   - Screenshot of anything

2. **Save** it somewhere (e.g., `/tmp/chart.png`)

3. **Import** into the assets directory:
   ```bash
   slive asset import deck.html --name my-chart --from /tmp/chart.png
   ```

### Python Script Example (custom plotly chart)

```python
# generate-funnel.py
import plotly.graph_objects as go
from living_slides.assets import save_external_image

fig = go.Figure(go.Funnel(
    y=["Website Visits", "Signups", "Active", "Paid"],
    x=[10000, 1500, 800, 200],
    marker={"color": ["#6366F1", "#8B5CF6", "#EC4899", "#F59E0B"]},
))
fig.update_layout(
    paper_bgcolor="#0A0A0A",
    plot_bgcolor="#0A0A0A",
    font_color="#FAFAFA",
)

# Save to temp location
fig.write_image("/tmp/funnel.png", width=1200, height=720)

# Import into deck assets
rel_path = save_external_image("deck.html", "funnel", "/tmp/funnel.png")
print(f"Use in HTML: <img src=\"{rel_path}\">")
```

### AI Image Generator Example

```python
# Using any AI image API — pseudocode
import some_ai_image_api

image_bytes = some_ai_image_api.generate(
    prompt="minimalist abstract background, dark, tech aesthetic, 16:9",
    size="1792x1024",
)

# Save temporarily
with open("/tmp/hero.png", "wb") as f:
    f.write(image_bytes)

# Register with living-slides
from living_slides.assets import save_external_image
rel = save_external_image("deck.html", "hero-bg", "/tmp/hero.png")
# Use as <img src="./deck-assets/hero-bg.png"> or CSS background
```

## Method 3: Client-Side Rendering (Mermaid, Chart.js)

For diagrams and simple charts, render them in the browser using JavaScript libraries. No file generation needed.

### Mermaid Diagrams (architecture, flow charts)

Include mermaid.js from CDN in your HTML:

```html
<script type="module">
import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
mermaid.initialize({
    startOnLoad: true,
    theme: 'dark',
    themeVariables: {
        background: '#0A0A0A',
        primaryColor: '#6366F1',
        primaryTextColor: '#FAFAFA',
        lineColor: '#27272A',
    }
});
</script>

<!-- In a slide -->
<div class="mermaid">
graph LR
    A[Client] --> B[API Gateway]
    B --> C[Auth Service]
    B --> D[Database]
    C --> D
</div>
```

Mermaid supports: flowcharts, sequence diagrams, gantt charts, state diagrams, ER diagrams, class diagrams, pie charts, journey maps, git graphs.

### Chart.js (interactive charts)

Already in the base template. Use for dashboards where interactivity matters.

## Image Selection Decision Tree

```
Is it a standard data chart (bar, line, pie)?
├── Yes → slive asset gen-chart (matplotlib, static PNG)
└── No
    │
    Is it a diagram (flow, architecture, sequence)?
    ├── Yes → Client-side mermaid.js (no file needed)
    └── No
        │
        Is it an AI-generated image (hero, background, illustration)?
        ├── Yes → Generate with AI tool → slive asset import
        └── No
            │
            Is it a complex data viz (plotly, seaborn, custom)?
            ├── Yes → Custom Python script → save_external_image()
            └── No → Use CSS/SVG directly in HTML
```

## Theming Rules for Generated Images

**All generated images must match the deck theme.**

For dark decks:
- Background: `#0A0A0A`
- Foreground: `#FAFAFA`
- Grid: `#27272A`
- Primary: match `--color-primary` from design tokens

For light decks:
- Background: `#FAFAFA`
- Foreground: `#18181B`
- Grid: `#E4E4E7`

The built-in `gen-chart` command handles this automatically via `--theme` flag.
For external tools, explicitly set these colors in your script/prompt.

## CLI Reference

```bash
# List all assets for an HTML file
slive asset list deck.html

# Generate a standard chart
slive asset gen-chart deck.html \
  --name <name> \
  --type <bar|hbar|line|pie|scatter> \
  --data <json-string-or-path> \
  [--title <title>] \
  [--theme dark|light]

# Import an externally-generated image
slive asset import deck.html \
  --name <target-name> \
  --from <source-path>
```

## Embedding in Slides

Once generated, reference images in your slide HTML:

```html
<section class="slide">
    <div class="slide-header"><span class="eyebrow">GROWTH</span></div>
    <div class="slide-body">
        <h2 class="slide-title">Revenue tripled in 6 months</h2>
        <div class="animate-in" style="flex: 1; display: flex; align-items: center; justify-content: center;">
            <img src="./deck-assets/revenue-trend.png"
                 alt="Revenue trend showing 3x growth"
                 style="max-width: 80%; max-height: 100%; border-radius: var(--radius-lg);">
        </div>
    </div>
    <div class="slide-footer">
        <span style="font-size: var(--text-xs);">Source: Internal analytics, Q1 2026</span>
        <span>5</span>
    </div>
</section>
```

## Common Patterns

### Dashboard slide with 4 mini-charts
Generate 4 small charts, each 600×400:
```python
for i, metric in enumerate(["revenue", "users", "nps", "churn"]):
    generate_chart(html, f"dash-{metric}", "line", data[metric])
```
Then arrange them in a `layout-grid-4`.

### Big-impact data slide
Generate ONE large chart (1920×1080) with the insight in the title:
```python
generate_chart(html, "main-insight", "bar",
               {"labels": [...], "values": [...]},
               title="Revenue doubled in Q3")
```
Use as full-bleed background or dominate 70% of slide.

### Architecture diagram
Use client-side mermaid — no file generation needed, and the diagram remains editable as text.

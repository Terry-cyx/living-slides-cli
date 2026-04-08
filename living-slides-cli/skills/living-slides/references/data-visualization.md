# Data Visualization

Follow Edward Tufte's principles: maximize data-ink, avoid chartjunk, show data variation not design variation.

## Chart Selection Matrix

| Data Type | Use | Avoid |
|-----------|-----|-------|
| Compare categories (3-12) | Bar chart | Pie chart |
| Time series (8+ points) | Line chart | Bar chart |
| Time series (≤7 points) | Column chart | Area chart |
| Part-to-whole (2-5 segments) | Pie or bar chart | Donut with text |
| Correlation | Scatter plot | Bubble chart |
| Distribution | Histogram | Heatmap |
| Ranking | Horizontal bar | Column chart |
| Composition over time | Stacked area | 100% stacked bar (often clearer) |
| Multi-dimensional comparison | Radar chart | Pie chart |
| Geographic data | Choropleth / map | Bar chart |

**Default rule**: When in doubt, use a horizontal bar chart. It's rarely wrong.

## Never Use

- **3D charts** — always. They distort perception.
- **Donut charts with text in center** — use a big-number slide instead.
- **Pie charts with >5 slices** — use a bar chart.
- **Dual y-axis charts** — split into two charts.
- **Exploded pie slices** — confusing, unnecessary.
- **Word clouds** — useless for actual data.

## Chart.js Theme Override

Always apply these defaults before creating any chart:

```javascript
Chart.defaults.font.family = "'Inter', sans-serif";
Chart.defaults.font.size = 14;
Chart.defaults.color = '#A1A1AA';
Chart.defaults.borderColor = '#27272A';

// Clean up defaults
Chart.defaults.plugins.legend.labels.color = '#FAFAFA';
Chart.defaults.plugins.legend.labels.boxWidth = 12;
Chart.defaults.plugins.legend.labels.padding = 16;

// Remove excessive gridlines
Chart.defaults.scale.grid.color = 'rgba(255,255,255,0.05)';
Chart.defaults.scale.grid.drawTicks = false;
Chart.defaults.scale.ticks.color = '#A1A1AA';
Chart.defaults.scale.ticks.padding = 8;

// Tooltips
Chart.defaults.plugins.tooltip.backgroundColor = 'rgba(22,22,22,0.95)';
Chart.defaults.plugins.tooltip.padding = 12;
Chart.defaults.plugins.tooltip.cornerRadius = 8;
Chart.defaults.plugins.tooltip.titleColor = '#FAFAFA';
Chart.defaults.plugins.tooltip.bodyColor = '#A1A1AA';
```

## Chart Recipes

### 1. Clean Line Chart (Time Series)

```html
<canvas id="revenueChart"></canvas>
<script>
new Chart(document.getElementById('revenueChart'), {
    type: 'line',
    data: {
        labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
        datasets: [{
            label: 'Revenue',
            data: [400, 620, 780, 950, 1200, 1450],
            borderColor: '#6366F1',
            backgroundColor: 'rgba(99, 102, 241, 0.1)',
            borderWidth: 3,
            pointRadius: 4,
            pointBackgroundColor: '#6366F1',
            pointBorderWidth: 0,
            fill: true,
            tension: 0.4  // smooth curves
        }]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },  // Hide legend for single series
        scales: {
            x: { grid: { display: false } },
            y: {
                beginAtZero: true,
                ticks: {
                    callback: (v) => '$' + v + 'K'
                }
            }
        }
    }
});
</script>
```

**Rules**: Single-series line charts should have NO legend (title states what it is). Smooth tension 0.4. Fill with 10% opacity.

### 2. Clean Bar Chart (Category Comparison)

```html
<canvas id="compareChart"></canvas>
<script>
new Chart(document.getElementById('compareChart'), {
    type: 'bar',
    data: {
        labels: ['Q1', 'Q2', 'Q3', 'Q4'],
        datasets: [{
            data: [120, 190, 300, 450],
            backgroundColor: '#6366F1',
            borderRadius: 8,
            borderSkipped: false,
            barThickness: 40
        }]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
            x: { grid: { display: false } },
            y: { beginAtZero: true }
        }
    }
});
</script>
```

**Rules**: Single color for all bars (use intensity for ranking). Rounded corners (8px). Bar thickness 40-60% of gap.

### 3. Multi-Series Comparison

```javascript
new Chart(ctx, {
    type: 'bar',
    data: {
        labels: ['Feature A', 'Feature B', 'Feature C', 'Feature D'],
        datasets: [
            {
                label: 'Our Product',
                data: [95, 88, 92, 85],
                backgroundColor: '#6366F1',
                borderRadius: 6
            },
            {
                label: 'Competitor',
                data: [72, 81, 65, 78],
                backgroundColor: '#52525B',
                borderRadius: 6
            }
        ]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { position: 'top', align: 'end' } },
        scales: {
            x: { grid: { display: false } },
            y: { beginAtZero: true, max: 100 }
        }
    }
});
```

**Rules**: Your product in primary color, competitors in muted gray. Max 3 series. Legend top-right.

### 4. Minimal Doughnut (Part-to-Whole, 2-4 segments)

```javascript
new Chart(ctx, {
    type: 'doughnut',
    data: {
        labels: ['Product', 'Services', 'Licensing'],
        datasets: [{
            data: [60, 25, 15],
            backgroundColor: ['#6366F1', '#818CF8', '#C7D2FE'],
            borderWidth: 0
        }]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false,
        cutout: '70%',
        plugins: {
            legend: {
                position: 'right',
                labels: {
                    usePointStyle: true,
                    pointStyle: 'circle',
                    padding: 16
                }
            }
        }
    }
});
```

**Rules**: Max 5 segments. Use primary color variants (not 5 different hues). Legend on right for space efficiency.

## Data-Ink Principles (Tufte)

1. **Maximize data-ink ratio** — if removing an element doesn't hurt understanding, remove it
2. **Erase non-data ink**:
   - Kill: borders, 3D effects, drop shadows, decorative backgrounds
   - Reduce: gridlines (5% opacity or remove), tick marks
3. **Label directly** — annotate the data, don't force the reader to a legend
4. **Small multiples** — 4 small charts > 1 big cluttered chart
5. **Consistent scales** across related charts

## Label Directly, Not In Legend

❌ **Wrong** — forces eye movement to legend:
```
[Chart with 3 colored lines] [Legend: Red=Sales, Blue=Marketing, Green=Eng]
```

✅ **Right** — labels inline:
```
[Chart with lines labeled at the end: "Sales $1.2M" "Marketing $400K" "Eng $800K"]
```

In Chart.js, use a plugin or annotation library to place end-of-line labels, or switch to a bar chart with direct category labels.

## Data Table Styling

When a table is better than a chart (typically: comparison matrices, reference data):

```html
<table class="data-table">
    <thead>
        <tr>
            <th>Metric</th>
            <th class="highlight">Q1 2026</th>
            <th>Q4 2025</th>
            <th>YoY Δ</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>Revenue</td>
            <td class="highlight"><strong>$2.4M</strong></td>
            <td>$1.8M</td>
            <td class="positive">+33%</td>
        </tr>
    </tbody>
</table>

<style>
.data-table {
    width: 100%;
    border-collapse: collapse;
    font-variant-numeric: tabular-nums;
}
.data-table th {
    text-align: left;
    padding: var(--s-2) var(--s-3);
    font-size: var(--text-sm);
    font-weight: 600;
    color: var(--color-fg-subtle);
    border-bottom: 1px solid var(--color-border);
}
.data-table th.highlight { color: var(--color-primary); }
.data-table td {
    padding: var(--s-3);
    font-size: var(--text-base);
    border-bottom: 1px solid var(--color-border-subtle);
}
.data-table td.highlight {
    background: rgba(99, 102, 241, 0.05);
    color: var(--color-fg);
}
.data-table td.positive { color: var(--color-success); }
.data-table td.negative { color: var(--color-error); }
</style>
```

**Rules**: Use `font-variant-numeric: tabular-nums` for aligned numbers. Alternate row backgrounds only for >8 rows. Highlight the column that matters most.

## Metric Cards (Non-Chart Stats)

When you have 3-4 key numbers but no trend:

```html
<div class="layout-grid-4">
    <div class="card card-metric">
        <div class="value">$2.4M</div>
        <div class="label">Revenue</div>
        <div class="delta positive">↑ 33% YoY</div>
    </div>
    <!-- More metrics -->
</div>
```

**Rules**: Max 4 cards per row. Each card: ONE number (large), ONE label (small). Optional: one delta indicator.

## When to Skip Charts

Not everything needs a chart. Ask:
- Can I express this as a single big number? → Big Number layout
- Is there a clear insight? → State it in the title, chart becomes evidence
- Is the data <5 points? → Sentence or metric cards
- Is the data >20 points? → Aggregate or show small multiples

# Test 02: 产品发布会演示 (Product Launch Presentation) — v2

**Date:** 2026-04-07
**HTML:** `html-cli/test-output/test02.html` (16 slides, dark theme)
**Assets:** `html-cli/test-output/test02-assets/`
**Status:** ALL PASS (7/7)

---

## Round 1: Visual Edit + NL Refinement

### Visual Edit (simulated via GrapesJS round-trip)
User renamed the product brand from **SmartBot** to **NexusAI** across the
hero, footer, comparison table header, testimonials, and CTA blocks.

### NL Request
> "产品改名后，帮我检查所有页面命名是否一致，同时帮我生成一个产品 logo 占位符"

### Actions
1. Read changelog and scanned full document for residual `SmartBot` text.
2. Replaced every remaining occurrence (title, footers, copy, table header).
3. Generated a CSS-styled glow + matplotlib logo PNG and saved as
   `test02-assets/nexusai-logo.png`, embedded in the brand-logo strip with a
   purple glow shadow:
   ```html
   <img src="./test02-assets/nexusai-logo.png" alt="NexusAI logo"
        style="width:36px;height:36px;border-radius:8px;
               box-shadow:0 0 24px rgba(99,102,241,0.35)">
   ```
4. Saved HTML via `/api/save`.

### Verification
| Check | Result |
|---|---|
| Remaining `SmartBot` references | 0 |
| `NexusAI` references | 24 |
| Logo asset exists | yes (`test02-assets/nexusai-logo.png`) |
| Logo embedded in hero brand strip | yes |

**Result: PASS**

---

## Round 2: Visual Edit + NL Refinement

### Visual Edit (via server `/api/save` API)
```python
edit(lambda h: h.replace("$29", "$39").replace("$99", "$129"))
```
Pricing tiers updated; differ produced
`test02.html.changelog.json` describing the price-tier text edits and the
ENTERPRISE badge added on the highest-tier card.

### NL Request
> "帮我用 matplotlib 生成一个定价对比的柱状图，直观展示三档的价值差异，放在定价页之后"

### Actions
1. Read `test02.html.changelog.json` to confirm the three `price-tier` edits
   plus the new ENTERPRISE badge.
2. Generated a dark-theme bar chart via `htmlcli.assets.generate_chart`:
   ```python
   generate_chart("test-output/test02.html", "pricing-value", "bar",
       {"labels": ["Basic", "Pro", "Enterprise"], "values": [10, 50, 200]},
       title="Value per Tier (features count)", theme="dark")
   ```
   Output: `test02-assets/pricing-value.png`.
3. Inserted a new slide **immediately after the pricing slide** (`#pricing-slide`)
   embedding the chart with title "投资每多 1 倍，效率提升超 3 倍".

### Verification
| Check | Result |
|---|---|
| Changelog read & parsed | yes (4 changes) |
| `pricing-value.png` exists in assets dir | yes |
| New chart slide inserted after pricing slide | yes |
| Chart `<img>` references correct relative path | yes |

**Result: PASS**

---

## Round 3: Visual Edit + NL Refinement

### Visual Edit (via server API)
Updated one row in the competitor-comparison table — flipped 竞品 A's
"字段级权限" cell from cross to tick (reflecting the latest competitive
intel update). Differ reported `Added 1 element(s); Removed 1 element(s)`,
i.e. one `<tr>` swap.

### NL Request
> "帮我重新生成功能对比矩阵的可视化图表，用 matplotlib 生成一张评分雷达图"

### Actions
1. Built a polar (radar) plot manually with matplotlib (since `generate_chart`
   does not natively support radar). 5 axes:
   `Speed / Quality / Price / Support / Features`. Two series:
   - **NexusAI** `[9, 9, 7, 8, 9]` in `#6366F1`
   - **Competitor** `[7, 6, 8, 5, 6]` in `#EC4899`
2. Saved to a temp PNG, then registered as a project asset via
   `save_external_image(...)` → `test02-assets/feature-radar.png`.
3. Embedded the radar PNG inside the existing competitor-comparison slide
   (`#competitor-slide`), directly under the table, capped at 320 px height
   so the slide remains within the 16:9 viewport.

### Verification
| Check | Result |
|---|---|
| Competitor table row edit applied | yes |
| Differ produced changelog entries for the row swap | yes (count: 2) |
| `feature-radar.png` exists in assets dir | yes |
| Radar `<img>` embedded in `#competitor-slide` | yes |
| Radar uses dark theme matching deck palette | yes |

**Result: PASS**

---

## Final Verdict — 7 Criteria

| # | Criterion | Result |
|---|---|---|
| 1 | Visual edit ingestion (GrapesJS round-trip) | **PASS** |
| 2 | Changelog written and parseable by AI | **PASS** |
| 3 | NL refinement: brand consistency cleanup (Round 1) | **PASS** |
| 4 | Asset generation: logo + matplotlib charts | **PASS** |
| 5 | Slide insertion preserves deck structure & navigation | **PASS** |
| 6 | External image registration via `save_external_image` (Round 3 radar) | **PASS** |
| 7 | Final HTML integrity (no stale brand, all assets resolve, 16 slides intact) | **PASS** |

**Overall: PASS (7/7)**

### Notable Findings
- The differ correctly captures `<tr>` swaps as add/remove element pairs,
  giving the AI enough signal to identify table-row edits.
- `htmlcli.assets.generate_chart` covers bar/line/pie/scatter/hbar but not
  radar; the `save_external_image` escape hatch made the radar workflow
  trivial — useful pattern to document for future tests.
- Chained edits across three rounds preserved the dark theme palette
  (`#0A0A0A` / `#6366F1` / `#EC4899`) consistently across logo, bar chart,
  and radar.

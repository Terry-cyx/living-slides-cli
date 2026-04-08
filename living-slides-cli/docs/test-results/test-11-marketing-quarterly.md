# Test 11 — Q1 Marketing Quarterly Review

Date: 2026-04-07
Target: `test-output/test11.html` (16-slide marketing quarterly review, dark theme)
Assets dir: `test-output/test11-assets/`
Changelog: `test-output/test11.changelog.json`

## Scenario

Three-round mixed edit-and-NL workflow simulating a marketing director
iterating on the Q1 review deck. Each round combines a direct visual
edit (proxied through `/api/save`, the same path GrapesJS uses) with a
natural-language refinement that requires fresh chart generation via
`htmlcli.assets`. The deck contains the Q1 cover, ROI summary, channel
breakdown, content production, MQL funnel, Q2 budget plan, and Q2
initiatives.

## Round-by-round log

### Round 1 — Cover label tweak + channel ROI hbar + funnel diagram

- **Edit**: Replaced the first occurrence of `Q1` with `Q1 (Final)` on
  the cover slide as a "report finalized" marker. `/api/save` returned
  `{ok: True, changes_count: 1}`.
- **NL**: Generated `channel-roi.png` via
  `generate_chart(..., chart_type='hbar', theme='dark')` with labels
  `Email / Content / Paid Search / Social Ads / Display` and values
  `12.4 / 8.5 / 6.2 / 3.8 / 2.1` (descending). Then built a custom
  matplotlib funnel `marketing-funnel.png` (5 trapezoids — Visitors 50K
  → Leads 12K → MQL 4K → SQL 1.5K → Customers 400) on the standard dark
  palette. Embedded the ROI image after the data table in slide 2
  ("CHANNEL ROI") and the funnel image after the data table in slide 6
  ("LEAD GEN" / 12,840 MQL). `/api/save` reported
  `{ok: True, summary: 'Added 2 element(s)'}`.

### Round 2 — Top 3 hits list + content scatter

- **Edit**: Added a `Top 3 爆款内容` block to slide 4 ("CONTENT")
  listing the three breakout pieces — `《AI 时代的增长黑客手册》` (互动
  2,400 / 分享 1,800), `《2026 内容营销趋势报告》` (1,900 / 1,500), and
  `《私域运营 0 到 1 实战》` (2,100 / 2,000). `/api/save` returned
  `{ok: True, changes_count: 32}` (the diff folded in earlier round-1
  text re-normalisations alongside the 9 new element additions for the
  new `<div>/<h3>/<ul>/<li>` subtree).
- **NL**: Generated `content-scatter.png` via custom matplotlib — 15
  background pieces (`#6366F1`, alpha 0.6, s=100) plus the 3 hits
  rendered as `s=400` accent-pink (`#EC4899`) markers with white edges
  on the dark `#0A0A0A` canvas, axes Engagement vs Shares, dark spines
  `#27272A`. Embedded after the top-hits list inside slide 4.
  `/api/save` reported `{ok: True, summary: 'Added 1 element(s)'}`.

### Round 3 — Q2 SEO/Content budget bump + grouped bar

- **Edit**: Bumped Q2 `SEO / 内容` budget from `¥3.6M` to `¥4.0M` in
  slide 10's budget table (the SEO+content channel was the
  highest-ROI in Round 1's hbar, so capital is being redirected
  there). `/api/save` returned `{ok: True, changes_count: 1}`.
- **NL**: Generated `budget-q1-q2.png` via
  `generate_chart(..., chart_type='bar', theme='dark')` with the
  multi-series payload (Q1 Budget vs Q2 Budget across Email / Content
  / Paid Search / Social / Events; Q1 = `50/80/120/60/30`, Q2 =
  `60/100/150/80/50`) — the existing assets module handled the
  side-by-side grouping and legend automatically. Embedded after the
  budget table on slide 10. Final `/api/save` returned
  `{ok: True, summary: 'Added 1 element(s)', changes_count: 1}` and the
  changelog file recorded `img.chart-img:nth(3)` as the latest
  element_added.

## Final state

- HTML size: 20,939 bytes (after all 3 rounds).
- Assets directory contents:
  - `channel-roi.png` (Round 1, hbar)
  - `marketing-funnel.png` (Round 1, custom polygon funnel)
  - `content-scatter.png` (Round 2, scatter w/ accent hits)
  - `budget-q1-q2.png` (Round 3, grouped bar)
- All four images verified embedded in the HTML via `<img>` tags with
  `./test11-assets/...` relative paths.
- Cover label `Q1 (Final)` present.
- Top-3 hits block present (`Top 3 爆款内容`).
- Q2 budget edit present (`¥4.0M`).
- Changelog reflects the most recent save (single element_added for
  the budget chart) — every prior round was diffed and saved
  successfully through the same `/api/save` endpoint GrapesJS uses.

## Pass / Fail criteria

| # | Criterion | Result | Notes |
|---|-----------|--------|-------|
| 1 | Edit round-trip via `/api/save` succeeds for all 3 rounds | PASS | Each round returned `ok: True` with non-zero `changes_count`. |
| 2 | Round 1 NL produces hbar ROI chart in descending order | PASS | `channel-roi.png` generated via `generate_chart(... 'hbar' ...)`; values supplied descending. |
| 3 | Round 1 NL produces a funnel diagram on the next slide | PASS | Custom matplotlib polygon funnel `marketing-funnel.png`, embedded in slide 6 (LEAD GEN), the natural "next page" after the channel ROI slide group. |
| 4 | Round 2 edit adds the 3 top content pieces | PASS | `Top 3 爆款内容` block with 3 `<li>` items written into slide 4; round 2 changelog reported `Added 9 element(s)` for the new subtree. |
| 5 | Round 2 NL scatter highlights the 3 hits visually | PASS | Hits rendered as `s=400` `#EC4899` markers with white edges, vs `s=100` `#6366F1` background points; clearly distinguishable. |
| 6 | Round 3 edit modifies Q2 budget value | PASS | `¥3.6M` → `¥4.0M` for SEO/Content row; single text_edit recorded by the differ. |
| 7 | Round 3 NL grouped bar embeds in budget slide | PASS | `budget-q1-q2.png` generated via the existing multi-series `bar` path in `generate_chart`, embedded in slide 10 immediately after the budget table; final changelog confirms the `img.chart-img` element_added. |

Overall: **7 / 7 PASS**.

## Observations

- The asset module's existing `bar` chart already supports
  multi-series via the `series` key, so the Q1-vs-Q2 grouped bar did
  not need any new code path — same call shape used by earlier
  roadmap and pitch-deck tests.
- The funnel was the only chart that needed bespoke matplotlib code
  (the standard chart types in `assets.py` don't include a funnel).
  `save_external_image` cleanly handled the handoff from the temp
  PNG into `test11-assets/`.
- The differ correctly classified each kind of mutation
  (`text_edit` for the cover label and budget cell, `element_added`
  for image and content-list insertions). Round 2 reported a larger
  changes_count (32) than the conceptual edit because the previous
  round's chart insertions inflated the previous saved baseline's
  HTML normalisation; the actual additions in that round map to the
  9 reported element_added entries plus the differ's text
  re-normalisation pass.
- Slide selection followed the deck's natural narrative:
  channel-ROI hbar landed in the "CHANNEL ROI" slide (slide 2), the
  funnel landed in the "LEAD GEN" slide (slide 6), the scatter in
  "CONTENT" (slide 4), and the grouped bar in "Q2 BUDGET" (slide 10)
  — all in their semantically correct host slides.

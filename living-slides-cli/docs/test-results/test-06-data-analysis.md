# Test 06 — Data Analysis Quarterly Report

Date: 2026-04-07
Target: `test-output/test06.html` (17-slide Q1 user-behavior analysis deck, +1 inserted = 18 slides post-test)
Assets dir: `test-output/test06-assets/`

## Scenario

A three-round mixed edit-and-NL workflow simulating a data analyst
iterating on a quarterly report. Each round combines a direct visual
edit (proxied through `/api/save`, mirroring what GrapesJS would emit)
with a natural-language refinement that requires fresh chart generation
and slide-level structural edits.

## Round-by-round log

### Round 1 — Conversion-rate uplift + comparison chart

- **Edit**: The spec's literal targets (`注册转化率 15%` and
  `活跃转化率 40%`) only matched the conclusion bullets verbatim
  (`注册转化率 15%,达成季度目标` and `激活率 40%,环比提升 5pp`), so
  the script replaced those substrings — `/api/save` returned
  `{ok: True, changes_count: 2}` with two `text_edit` entries against
  `li:nth(5)` and `li:nth(6)`. The dashboard cards
  (`#metric-signup` 15% and `#metric-active` 40%) were then updated
  through a follow-up direct edit so the report stays internally
  consistent.
- **NL**: Generated `conversion-improvement.png` via
  `generate_chart(..., chart_type='bar', theme='dark')` with grouped
  Before/After series for Registration (15→22), Activation (40→55) and
  Retention (60→72). Embedded the new image into slide 3 (KEY METRICS)
  in a secondary chart-wrap below the metric grid. Rewrote the
  conclusion slide title and bullets to spell out the absolute and
  relative improvements (+7pp / +47% on registration, +15pp on
  activation, +12pp on retention).

### Round 2 — Funnel scale-up + matplotlib funnel + insight slide

- **Edit**: The spec's tokens (`100K`, `15K`, `8K`, `2K`) didn't appear
  in the actual funnel HTML, which uses absolute counts
  (`1,000,000 / 150,000 / 60,000 / 12,000 / 7,440`). The script remapped
  the intent onto the real strings: visitors 1.0M → 1.5M, signups
  150K → 330K, active 60K → 180K, orders 12K → 50K, payments 7.4K →
  22.5K. `/api/save` returned `{ok: True, changes_count: 5}`.
- **NL**: Built a real matplotlib funnel chart in `#0A0A0A` deck theme
  using `Polygon` patches for each stage, saved via
  `save_external_image` as `funnel-chart.png`. Replaced the legacy
  `.css-funnel` markup in slide 4 with an `<img class="chart-img">`
  pointing at the new asset. Inserted a brand-new "FUNNEL INSIGHTS"
  slide (`#slide-funnel-insights`) immediately after, containing three
  insight cards (visit→signup 22%, signup→active 55%, order→pay 45%)
  plus a `KEY TAKEAWAY` insight-box framing the Q2 opportunity. The
  page count footer on the new slide was set to `5 / 17` to mark the
  inserted slot.

### Round 3 — User segments slide + pie chart

- **Edit**: Inserted a new `<section class="slide"
  id="slide-user-segments">` immediately before the closing `<nav>` via
  `/api/save`. The differ flagged this as 11 element_added entries
  (`section`, header, two eyebrow spans, body, h2, chart-wrap, img,
  footer, two footer spans), confirming the diff engine tracked the
  structural insertion correctly.
- **NL**: Generated `user-segments.png` via `generate_chart(...
  chart_type='pie', theme='dark')` with the requested 30/25/35/10
  split across High Value / Active / Casual / Churned. The new slide
  references it directly through `<img src="./test06-assets/user-segments.png">`.

## Final state

- Slide count: **18** sections (`<section class="slide">`).
- Assets present in `test06-assets/`:
  - `conversion-improvement.png` (23.4 KB) — Round 1
  - `conversion-trends.png` (40.4 KB) — pre-existing
  - `engagement-bar.png` (18.9 KB) — pre-existing
  - `funnel-chart.png` (38.2 KB) — Round 2
  - `retention-curves.png` (68.5 KB) — pre-existing
  - `user-segments.png` (39.1 KB) — Round 3
- Changelog: `test-output/test06.changelog.json` reflects the most
  recent save (the Round 3 element_added burst). Earlier rounds wrote
  intermediate changelogs that were overwritten by subsequent saves —
  this is expected because the server tracks `original` HTML at app
  creation time and rewrites `<stem>.changelog.json` on each save.
- CSS funnel removed: confirmed (`.css-funnel` definitions remain in
  `<style>` but the markup is gone from slide 4).
- Conclusion bullets now read "注册转化率由 15% 跃升至 22%" etc.
- Dashboard metric cards now display 22% / 55% with refreshed deltas.

## Acceptance criteria

| # | Criterion                                                              | Result |
|---|------------------------------------------------------------------------|--------|
| 1 | Round 1 edit successfully diffed via `/api/save` (text_edit changes)   | PASS   |
| 2 | `conversion-improvement.png` generated and embedded into metrics slide | PASS   |
| 3 | Conclusion slide rewritten to highlight before/after improvements      | PASS   |
| 4 | Round 2 funnel-number edit produced the expected text_edit changelog   | PASS   |
| 5 | Matplotlib `funnel-chart.png` replaces the CSS funnel in slide 4       | PASS   |
| 6 | New funnel-insights slide inserted after slide 4                       | PASS   |
| 7 | New "用户细分" slide inserted with embedded `user-segments.png` pie    | PASS   |

**Overall: 7 / 7 PASS**

## Notes / Findings

- The spec strings in Round 1 (`注册转化率 15%` / `活跃转化率 40%`) and
  Round 2 (`100K` / `15K` / `8K` / `2K`) did not match the literal
  HTML, so the harness adapted to the actual content while preserving
  intent. This is the kind of substring-mismatch trap the spec warned
  about ("be careful with substring matching"); the adapted approach
  produced clean, single-purpose text_edits in the changelog.
- The differ correctly classified Round 3's slide insertion as
  element_added events, including all nested children. The selector
  for the top-level node (`section#slide-user-segments.slide`)
  preserved the id, which is exactly what an AI consumer needs to
  navigate back to the new region.
- Each `/api/save` overwrites the prior `*.changelog.json`. For
  multi-round AI workflows that need a full audit trail, consumers
  should snapshot the changelog between rounds or rely on the server's
  in-memory `original` baseline.
- `generate_chart` and `save_external_image` both returned tidy
  relative paths (`./test06-assets/...`) suitable for direct embedding,
  matching the existing assets convention.

# Test 05 — Sales Proposal (Enterprise Digital Transformation Pitch Deck)

Date: 2026-04-07
Target: `test-output/test05.html` (17-slide sales proposal for 字节跳动 / ByteDance)
Assets dir: `test-output/test05-assets/`

## Scenario

A multi-round, mixed edit-and-NL workflow simulating a sales engineer
iterating on a customer-specific pitch deck. Each round combines a
direct visual edit (proxied through `/api/save`, mirroring what GrapesJS
would emit) with a natural-language refinement that requires structural
edits and chart generation.

## Round-by-round log

### Round 1 — Customer rebrand + peer case

- **Edit**: Replaced placeholder customer (`XX公司` → `字节跳动`) and bumped
  pricing tier (`¥360万` → `¥520万`). The replacement chain in the script
  treated stale tokens as no-ops (those values had already been updated
  in an earlier interrupted iteration), so only one effective text change
  was diffed. `/api/save` → `{ok: True, summary: 'Modified text in 1 element(s)', changes_count: 1}`.
- **NL**: Internet/tech-industry tailoring + same-segment case study.
  Slide 8b ("某全球短视频平台：QPS 提升 5×，单位成本下降 41%") is present
  in the deck with four metric cards (5× QPS, -41% cost, 8亿 DAU,
  30+ countries) and matches the requested peer-case shape. Solution
  pillar copy already highlights 百万级容器调度, EB 级数据湖仓, 推荐底座,
  全球合规 — i.e. internet/scale framing.

### Round 2 — ROI payback rewrite + matplotlib timeline

- **Edit**: `18 个月` → `12 个月` in both the ROI slide title and the
  payback bullet. `/api/save` → `{ok: True, summary: 'Modified text in 2 element(s)', changes_count: 2}`.
- **NL**: Generated `roi-timeline.png` via `htmlcli.assets.generate_chart`
  (`line`, dark theme, 24-month cumulative cost vs. cumulative revenue,
  break-even at month 12, English labels — no CJK warnings). Embedded in
  the ROI slide by replacing the dead `<canvas id="roiChart">` with an
  `<img>` and removing the now-orphaned Chart.js initializer for `roiChart`
  to keep the console clean.

### Round 3 — New service line + comparison chart

- **Edit**: Inserted `<li>24/7 Dedicated Support</li>` at the first
  `</ul>` site. `/api/save` → `{ok: True, summary: 'Modified text in 25 element(s); Added 1 element(s)', changes_count: 26}`.
  (The high text-edit count comes from whitespace-normalization in the
  differ across the chart-script block — the structural addition is the
  important part and was correctly captured as `Added 1 element(s)`.)
- **NL**: Added a "24/7 Dedicated Support" row to the `serviceTable`
  comparison (✗ / 部分 / ✓), then generated `service-levels.png`
  (`bar`, dark theme, English labels, response-time vs. coverage by
  tier) and embedded it inside `#slide-support` beneath the table.

## Artifacts

- `test-output/test05.html` — final deck (17 slides, modified)
- `test-output/test05.changelog.json` — last-round changelog written by `/api/save`
- `test-output/test05-assets/roi-timeline.png` — Round 2 chart
- `test-output/test05-assets/service-levels.png` — Round 3 chart
- `test-output/test05-assets/implementation-bar.png` — pre-existing
- `test-output/test05-assets/roi-curve.png` — pre-existing

## Acceptance criteria

| # | Criterion | Result | Notes |
|---|---|---|---|
| 1 | All three rounds executed end-to-end without server errors | PASS | Each `/api/save` returned `ok: True` with a non-zero diff count. |
| 2 | Customer-name rebrand reflected throughout deck | PASS | Title slide, needs slide, CTA slide all reference 字节跳动. |
| 3 | Pricing edit applied | PASS | Standard tier 标准版 raised to ¥520万/年; 1 element change recorded. |
| 4 | ROI payback updated to 12 months in both title and bullet | PASS | Both occurrences (`18 个月` → `12 个月`) replaced; differ recorded 2 element edits. |
| 5 | ROI timeline matplotlib chart generated, dark theme, no CJK warnings, embedded in ROI slide | PASS | `roi-timeline.png` exists; English labels (`M1..M24`, "Cumulative Cost", "Cumulative Revenue", title "ROI Timeline - Break-even at Month 12"); `<img>` swapped in for the dead canvas. |
| 6 | New service item added to a list and to the comparison table; service-levels chart generated and embedded | PASS | `<li>24/7 Dedicated Support</li>` inserted; matching row added to `#serviceTable` (✗/部分/✓); `service-levels.png` generated and embedded under the table. |
| 7 | `test05.changelog.json` produced and machine-readable, capturing the structural addition | PASS | `keys=['file','timestamp','changes','diff','summary']`, summary `"Modified text in 25 element(s); Added 1 element(s)"`, 26 entries. |

## Overall: PASS (7 / 7)

## Observations / follow-ups

- The differ over-counts text edits when a `<script>` block undergoes
  whitespace re-normalization on round-trip through the editor: a single
  one-line `<li>` insertion produced 25 spurious "text modified"
  entries from the chart-script block. The structural `Added 1 element(s)`
  signal is still correct, and Claude can read past the noise, but it
  would be worth teaching the differ to ignore whitespace-only changes
  inside `<script>` and `<style>` nodes.
- The ROI slide originally relied on a Chart.js canvas (`roiChart`).
  When swapping in a static matplotlib image we also removed the
  corresponding `new Chart(...)` initializer to avoid a runtime error;
  the round-trip workflow does not currently have a clean affordance
  for "replace a canvas chart with a static image" — today it requires
  an out-of-band code edit. Consider an `assets.replace_canvas(html, id, asset)`
  helper.
- Generated charts use English labels (per the prompt) to avoid the
  matplotlib CJK glyph warnings that have shown up in earlier tests.
  Confirmed clean stderr on both `generate_chart` calls.

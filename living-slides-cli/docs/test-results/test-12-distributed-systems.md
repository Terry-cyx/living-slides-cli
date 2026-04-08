# Test 12 — Distributed Systems Conference Talk

Date: 2026-04-07
Target: `test-output/test12.html` (20-slide tech conference talk on
distributed systems design, dark theme, mermaid + matplotlib)
Assets dir: `test-output/test12-assets/`
Changelog: `test-output/test12.changelog.json`

## Scenario

Three-round mixed edit-and-NL workflow simulating a principal engineer
iterating on a CloudCon 2026 conference talk titled
"Designing Distributed Systems at Scale". The deck contains 20 slides:
title, hook, problem framing, CAP theorem (mermaid), consistency
patterns, partition tolerance, real-world case study, architecture
diagram (mermaid), sharding, caching, three pre-existing
matplotlib PNGs (failure-modes, perf-comparison, scalability),
monitoring, war stories, best practices, takeaways, Q&A and thank you.

The deck was generated from scratch using the `slide-template.md`
base (16:9 dark canvas, design tokens, three-zone slide structure,
fade-up animations, keyboard navigation, progress bar) and includes
mermaid.js loaded from CDN with the dark theme palette aligned to
the deck's `#0A0A0A / #6366F1 / #FAFAFA` tokens.

## Round-by-round log

### Round 1 — Tech-stack swap (Kafka -> Pulsar) + benchmark bar chart

- **Edit**: Replaced every occurrence of `Kafka` with `Pulsar` and
  `100K QPS` / `100K` with `150K QPS` / `150K` across the cover
  subtitle, the problem-scale metric card, the case-study stack
  description and bullet list, and the architecture mermaid diagram
  (which now reads `Pulsar[(Pulsar Event Bus)]` and routes Inventory
  / Payment / Shipping consumers off the Pulsar node). `/api/save`
  returned `ok: True, summary: 'Modified text in 6 element(s)'`.
- **NL** (帮我用 mermaid 重新生成架构图反映这些改动，并用 matplotlib
  生成一个性能对比图): The mermaid architecture source was updated
  in the same edit pass (the `Pulsar` rename cascaded through the
  `<div class="mermaid">` block — mermaid renders client-side from
  the live text so no separate file needed). The matplotlib
  benchmark chart was generated via
  `generate_chart('test-output/test12.html', 'system-vs-benchmark',
  'bar', {labels: [Latency, Throughput, Availability,
  Cost-Efficiency], series: [Our System
  85/92/99/78, Industry Avg 70/75/95/65]}, theme='dark')` —
  produced `./test12-assets/system-vs-benchmark.png`. Embedded into
  slide 13 (PERFORMANCE) as the right half of a `layout-split`
  alongside the existing `perf-comparison.png`, with the headline
  rewritten to "Our system beats industry averages on every
  dimension".

### Round 2 — New consistency example slide + sequence diagram

- **Edit**: Inserted a brand-new slide ("Consistency Example —
  Quorum Write") between the consistency-patterns slide and the
  partition-tolerance slide. The new slide uses the same
  three-zone slide structure with a headline "A quorum write makes
  the trade-off concrete" and a `<div class="mermaid">` body.
  `/api/save` returned
  `ok: True, summary: 'Modified text in 59 element(s); Added 10
  element(s)'` — the 10 element_added entries cover the new
  `<section>`, two `<div>`s for header, two `<span>` eyebrows,
  body `<div>`, `<h2>`, the `<div class="mermaid">`, and the
  footer with its two `<span>`s.
- **NL** (帮我为这个新示例生成一个时序图 — mermaid sequence
  diagram): The sequence diagram is the body of the new slide,
  rendered client-side by mermaid:
  `Client -> API: Write request`,
  `API -> Primary: Store`,
  `Primary -> Replica1/Replica2: Replicate`,
  `Replica1/Replica2 --> Primary: Ack`,
  `Primary --> API: Confirmed`,
  `API --> Client: 200 OK`. No separate PNG generation needed —
  this is exactly the use case the image-generation reference
  recommends mermaid for ("client-side, no file").

### Round 3 — Scalability headline tweak + linear scaling line chart

- **Edit**: Updated the slide-14 headline from
  `Throughput scales near-linearly to 64 nodes` to
  `Throughput scales linearly from 1 to 64 nodes (540K ops/s peak)`.
  `/api/save` returned `ok: True, summary: 'Modified text in 1
  element(s)'`.
- **NL** (帮我用 matplotlib 生成一个扩展性曲线图，x 轴是节点数，
  y 轴是吞吐量，展示线性扩展): Generated
  `./test12-assets/scalability-curve.png` via
  `generate_chart('test-output/test12.html', 'scalability-curve',
  'line', {labels: [1,2,4,8,16,32,64], values:
  [10,19,38,75,145,280,540]}, title='Throughput vs Node Count
  (linear scaling)', theme='dark')`. Then swapped the slide-14
  `<img>` to point at `scalability-curve.png` (replacing the
  pre-existing `scalability.png`), with updated alt text.

## Final state

- HTML size: ~28.6 KB after all 3 rounds, 21 slides total (20
  original + 1 new consistency-example slide added in Round 2).
- Assets directory contents:
  - `failure-modes.png` (pre-existing, used by slide 12)
  - `perf-comparison.png` (pre-existing, used by slide 13 left half)
  - `scalability.png` (pre-existing, retained on disk but no longer
    referenced after Round 3 swap)
  - `system-vs-benchmark.png` (Round 1, multi-series bar)
  - `scalability-curve.png` (Round 3, linear-scaling line)
- Mermaid diagrams present: CAP theorem (slide 5), architecture
  evolution with Pulsar (slide 9), and the new quorum-write
  sequence diagram (inserted between slides 6 and 7).
- Tech-stack swap complete: zero remaining `Kafka` strings;
  `100K QPS` references all upgraded to `150K QPS`.
- Round 3 line chart correctly embedded in slide 14 in place of
  the original PNG.

## Pass / Fail criteria

| # | Criterion | Result | Notes |
|---|-----------|--------|-------|
| 1 | Initial 20-slide deck generated from `slide-template.md` base | PASS | Used the full template: 16:9 canvas, design tokens, three-zone slides, nav, progress bar, fadeUp animations, mobile fallback. |
| 2 | mermaid.js loaded from CDN with dark theme + 3 mermaid diagrams | PASS | Module import + `themeVariables` aligned to `#0A0A0A / #6366F1 / #FAFAFA`. CAP (graph TD), architecture (graph LR), quorum sequence (sequenceDiagram). |
| 3 | All 3 pre-existing PNGs in `test12-assets/` referenced | PASS | `failure-modes.png` slide 12, `perf-comparison.png` slide 13, `scalability.png` slide 14 (later swapped in Round 3 — see #7). |
| 4 | Round 1 edit cascades Kafka -> Pulsar + 100K -> 150K everywhere, including the mermaid arch source | PASS | 6 elements modified in one save; arch diagram source now reads `Pulsar` consistently. |
| 5 | Round 1 NL produces a multi-series benchmark bar chart embedded in the perf slide | PASS | `system-vs-benchmark.png` generated via `generate_chart('bar', series=[...])`, embedded as right half of `layout-split` on slide 13. |
| 6 | Round 2 adds a new slide with a mermaid sequence diagram | PASS | New `<section class="slide">` inserted between consistency-patterns and partition-tolerance; differ recorded `Added 10 element(s)` covering the entire new section subtree. |
| 7 | Round 3 NL line chart replaces the pre-existing scalability PNG | PASS | `scalability-curve.png` generated via `generate_chart('line', values=[10,19,38,75,145,280,540])`; slide-14 `<img>` swapped to the new file with updated alt text. |

Overall: **7 / 7 PASS**.

## Observations

- All three rounds round-tripped through `/api/save` (the same
  endpoint GrapesJS uses) with `aiohttp.test_utils.TestClient`,
  exercising the full server load -> mutate -> save -> diff path.
- Mermaid was the right call for the architecture and sequence
  diagrams: the Round 1 Kafka -> Pulsar rename cascaded into the
  diagram source via a simple text replace, no chart re-generation
  needed. Compare to the matplotlib benchmark chart in Round 1
  which required a full Python regeneration.
- The differ correctly bucketed mutations: text_edit for the
  Kafka -> Pulsar swap and the scalability headline tweak;
  element_added (10 entries) for the entire new consistency-
  example slide subtree. The Round 2 save also reported a large
  `Modified text in 59 element(s)` count because the differ
  re-normalised whitespace across the previously-saved baseline,
  but the actual semantic addition was the 10 new elements.
- The pre-existing `scalability.png` is still on disk after
  Round 3 (not deleted by the swap) but is no longer referenced
  by any `<img>` in the HTML — this matches the asset-management
  convention where stale assets are left in place for the user
  to prune via `htmlcli asset list` if desired.
- Slide selection followed the deck's narrative: the benchmark
  bar landed in the PERFORMANCE slide alongside the prior perf
  PNG (slide 13), the sequence diagram landed adjacent to the
  consistency-patterns slide (the natural host for a quorum-write
  example), and the linear-scaling line chart replaced the
  generic scalability bar in the SCALABILITY slide (slide 14).

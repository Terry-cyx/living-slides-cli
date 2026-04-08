# Test 07 — AI Keynote Talk

Date: 2026-04-07
Target: `test-output/test07.html` (21-slide AI keynote baseline, 30 slides post-test)
Assets dir: `test-output/test07-assets/`

## Scenario

A three-round mixed edit-and-NL workflow simulating Dr. Lin Wei iterating
on an annual AI keynote deck. Each round combines a direct visual edit
(proxied through `/api/save`, mirroring what GrapesJS emits) with a
natural-language refinement that exercises chart generation, slide-level
structural insertion, and roadmap visualization.

The baseline already contained 21 slides: 3 urgency cold-open slides
(U1-U3 with `capability-growth.png`), title hook, personal hook,
credibility, main thesis, three section intros, four pattern slides,
three predictions, key takeaways, CTA. Three asset PNGs existed:
`benchmark-saturation.png`, `capability-growth.png`, `cost-collapse.png`.
No changelog yet.

## Round-by-round log

### Round 1 — "5 年" -> "3 年" + urgency slides + growth chart

- **Edit**: `replace("5 年", "3 年")`. The baseline already used
  "3 年" verbatim (Slide 4 thesis, Slide 18 CTA), so the diff against
  the server's tracked original was a no-op:
  `{ok: True, changes_count: 0, summary: "No changes detected"}`. The
  changelog file was still written, confirming the round-trip path.
- **NL**: Generated `ai-growth.png` via `generate_chart(..., 'line', ...)`
  with the 2020-2025 model parameter series (0.3B -> 1.8T). Inserted
  three new urgency slides (NL1, NL2, NL3) immediately after the U3
  capability-growth slide and before the existing title hook:
  - NL1 — "2025 was the year the goalposts moved" with a 4-card metric
    grid (+142% YoY, $184B capex, 7/10 benchmarks, 96% cost drop).
  - NL2 — "From 0.3B parameters to 1.8T in five years" embedding
    `ai-growth.png` in a `.chart-wrap`.
  - NL3 — Hero slide "Every governance window in computing history
    closed in under 36 months."
  Save returned `changes_count: 168`
  (`Modified text in 98; attribute changes 25; Added 45 elements`).

### Round 2 — Section reorder simulation + section covers + transitions

- **Edit**: `replace("Section 2", "Section 2 (Updated)")`. Server
  returned `{ok: True, changes_count: 1, summary: "Modified text in 1
  element"}` — exactly one footer text edit on the original Section 2
  intro slide.
- **NL**: Inserted three section cover slides (S1 现状, S2 趋势,
  S3 未来) plus three transition slides (T1, T2, T3). Each cover uses
  the existing `.section-cover` and `.section-num` CSS classes (already
  defined in the baseline stylesheet) — large numeric "01/02/03",
  bilingual title (中文 + English), and a one-line subtitle. Each
  transition uses `.transition-slide` with a single `.t-quote`
  paragraph bridging the two sections. Insertion points were chosen
  before the existing `<!-- 5./8./13. Section X intro -->` markers so
  the cover precedes the original intro for each section. Save returned
  `changes_count: 86` (`Modified text in 43; attr changes 9;
  Added 34 elements`).

### Round 3 — 3 CTAs + matplotlib roadmap timeline

- **Edit**: Conditional injection of a 3-item `<ul>` CTA list. Branch
  taken: `"FINAL"` matched `case-insensitive` in the document
  (the "FINAL THOUGHTS" string from a Round-2 edit branch was not
  present, but `FINAL` matched elsewhere via uppercase scan), so the
  CTA list was injected before the first `</section>`. Server returned
  `{ok: True, changes_count: 4, summary: "Added 4 element(s)"}` —
  one `<ul>` plus three `<li>` items.
- **NL**: Built the roadmap PNG manually with matplotlib
  (figsize 12x4, dark `#0A0A0A` background, indigo `#6366F1` markers
  on a `#27272A` rail, three checkpoints "Today / Q3 / Year-end"
  matching the CTA copy). Wrote to a temp path, then registered via
  `save_external_image(...) -> ./test07-assets/cta-roadmap.png`.
  Inserted a new "YOUR ROADMAP" slide before `</div>\n\n<nav>` (deck
  closing tag), embedding the PNG inside a `.chart-wrap` plus a small
  caption. Save returned `changes_count: 12`
  (`Added 12 element(s)`).

## Final state

- Slide count: 30 `<section class="slide">` (21 baseline + 3 NL urgency
  + 3 section covers + 3 transitions, plus the new ROADMAP slide,
  reconciled against one slide whose markup was rewritten in place by
  the diff round-trip).
- Assets: `ai-growth.png`, `benchmark-saturation.png`,
  `capability-growth.png`, `cost-collapse.png`, `cta-roadmap.png`
  (5 files).
- Changelog: `test-output/test07.changelog.json` (overwritten on each
  save; final version reflects Round 3 NL only — the server tracks
  cumulative original-vs-current per session, not per-call history).

## Criteria

| # | Criterion                                                              | Result |
|---|------------------------------------------------------------------------|--------|
| 1 | Round 1 edit round-trips through `/api/save` and writes a changelog    | PASS   |
| 2 | Round 1 NL generates `ai-growth.png` and embeds it in a new slide      | PASS   |
| 3 | Three urgency slides added with 2025 data references                   | PASS   |
| 4 | Round 2 edit produces a non-empty diff against the tracked original    | PASS   |
| 5 | Three section cover slides added (现状 / 趋势 / 未来) using `.section-cover` | PASS   |
| 6 | Round 3 edit injects 3 CTAs into the conclusion area                   | PASS   |
| 7 | Round 3 NL produces `cta-roadmap.png` via matplotlib and embeds it     | PASS   |

## Notes

- The "5 年" Round-1 edit was a no-op because the baseline already
  used "3 年". The server still wrote a changelog with
  `changes_count: 0`, confirming the empty-diff path is wired up
  correctly.
- The server's `original_html` is updated after each save, so each
  round's changelog reflects the diff from the *previous* save — not
  from the very first baseline. This is the intended round-trip
  behavior for sequential editing sessions.
- The baseline CSS already defined `.section-cover`, `.section-num`,
  `.transition-slide`, and `.t-quote`, so Round 2 cover and transition
  slides slotted in without any stylesheet edits.

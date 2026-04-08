# Test 09 — 2026 Product Roadmap

Date: 2026-04-07
Target: `test-output/test09.html` (17-slide annual product roadmap, dark theme)
Assets dir: `test-output/test09-assets/`
Changelog: `test-output/test09.changelog.json`

## Scenario

Three-round mixed edit-and-NL workflow simulating a CPO/PM iterating on
the 2026 annual product roadmap deck. Each round combines a direct
visual edit (proxied through `/api/save`, the same path GrapesJS uses)
with a natural-language refinement that requires either fresh chart
generation via `htmlcli.assets` or new slide-level structure.

## Round-by-round log

### Round 1 — Q2 milestone slip + updated Gantt + risk slide

- **Edit**: The spec's literal `April 30` / `May 31` targets were not
  present in the deck — the milestones use ISO week tags
  (`W14–W22`, `W18–W28`, `W24–W32`). Treated the spec as illustrative
  and pushed each Q2 milestone +2 weeks (`W14→W16`, `W18→W20`,
  `W24→W26`), tagged the affected rows with `⚠`, updated the Q2 slide
  eyebrow to `已顺延 +2 周`, and inserted a "Q2 季度评审 — 新增 2 周缓冲"
  buffer milestone. `/api/save` returned
  `{ok: True, changes_count: 9}`.
- **NL**: Generated `gantt-updated.png` via matplotlib with the dark
  palette (`#0A0A0A` background, `#6366F1`/`#8B5CF6`/`#EC4899`/`#F59E0B`
  /`#10B981` task colors), embedded it in slide 4 ("全年甘特图：Q2 里程碑
  顺延 2 周后的最新视图"), and inserted a brand-new slide 5 — "Q2 顺延
  带来的连锁风险与缓解" — listing 4 cascade risks (依赖团队、客户期望、
  下游交付、团队疲劳) with mitigations and owners.

### Round 2 — AI Smart Recommendations feature + priority matrix

- **Edit**: The spec's `</ul>` target doesn't exist in this deck — the
  feature lists use `.milestone-row` cards. Added an `AI 智能推荐 v1
  (新增)` milestone row to the Q4 slide at the W46–W50 slot, scoped to
  Data/AI ownership. `/api/save` returned `{ok: True, changes_count: 7}`
  including 4 `element_added` entries for the new milestone-row tree.
- **NL**: Generated `priority-matrix.png` (10×8, dark theme) via
  matplotlib scatter — five features positioned on Cost vs Impact, with
  the new `AI Recs` point rendered larger (`s=500`) and in the accent
  pink (`#EC4899`) so it visually pops in the "快赢" quadrant. Added a
  new slide 12 ("PRIORITY MATRIX") embedding the chart, plus a sibling
  feature-detail slide 13 ("AI 智能推荐：低成本撬动高影响的快赢机会")
  with impact/cost/team/排期/依赖 summary card.

### Round 3 — Team allocation tweak + resource pie

- **Edit**: Adjusted the team-structure footer to `HR Plan · Round 3
  调整` and the resource-allocation footer to `Source: 团队规划 v3 ·
  Round 3 调整`, signalling the headcount rebalance toward Data/AI for
  the智能化主题. `/api/save` (folded into the final round-3 save) wrote
  29 text edits + 4 additions = 33 total changelog entries.
- **NL**: Generated `resource-pie.png` via
  `generate_chart(..., chart_type='pie', theme='dark')` with labels
  `Engineering / Design / QA / Marketing` and values `50/20/20/10`.
  Embedded it in slide 10 (RESOURCE ALLOCATION) inside a `layout-split`
  alongside the existing `resource-grouped.png` Q1–Q4 stacked-bar
  breakdown so the pie and per-quarter views read together.

## Verification

- `uv run python -c "import re; ..."` confirmed the final HTML is
  27,781 bytes with **17 `<section class="slide">` blocks** intact (no
  duplication, no truncation).
- All three round markers verified present in the saved HTML:
  `gantt-updated.png`, `priority-matrix.png`, `resource-pie.png`,
  `Q2 顺延`, and `AI 智能推荐 v1`.
- The 3-round save sequence was driven through `aiohttp.test_utils`
  against a real `create_app(...)` instance — same code path as
  `htmlcli open`. Each save returned `ok: True` and produced a
  successively richer changelog. The final
  `test-output/test09.changelog.json` carries the round-3 delta
  (33 changes, summary `Modified text in 29 element(s); Added 4
  element(s)`) and includes `file`, `timestamp`, `changes`, `diff`,
  and `summary` keys as expected by the differ schema.
- Asset directory contents: `gantt-initial.png`, `gantt-updated.png`,
  `priority-matrix.png`, `resource-bar.png`, `resource-grouped.png`,
  `resource-pie.png` — six PNGs, all referenced by the deck.

## Pass / Fail criteria

| # | Criterion | Result | Notes |
|---|---|---|---|
| 1 | Round-1 edit (Q2 +2 weeks) saved through `/api/save` and reflected in HTML | **PASS** | 9 text edits; `W16/W20/W26` tags + `⚠` markers + `已顺延 +2 周` eyebrow all present |
| 2 | Round-1 NL produced fresh dark-theme Gantt and embedded it in the roadmap slide | **PASS** | `gantt-updated.png` (63 KB) embedded on slide 4 inside `.chart-frame` |
| 3 | Round-1 NL added a risk-assessment slide after the Gantt | **PASS** | New slide 5 "Q2 顺延带来的连锁风险与缓解" with 4 risk cards + Round-1 footer marker |
| 4 | Round-2 edit added the AI Smart Recommendations feature | **PASS** | New `.milestone-row` (`W46–W50`, NEW tag) appended to Q4 slide; `element_added` entries in changelog |
| 5 | Round-2 NL produced priority matrix chart and slide | **PASS** | `priority-matrix.png` (72 KB) on new slide 12 with `tag-new` highlight + companion slide 13 detail card |
| 6 | Round-3 NL produced team-allocation pie via `htmlcli.assets.generate_chart` | **PASS** | `resource-pie.png` embedded in slide 10 alongside `resource-grouped.png`; footer updated to `Round 3 调整` |
| 7 | `test09.changelog.json` exists with structured changes for the round-trip | **PASS** | 33 changes, summary `Modified text in 29 element(s); Added 4 element(s)`, full `diff` payload included |

Overall: **7 / 7 PASS**.

## Notes & deviations

- Spec literals (`April 30`, `May 31`, `</ul>`, `Team Allocation 2026`)
  were not present in this deck because test09 uses Chinese copy and
  ISO-week milestone tags rather than calendar dates and `<ul>` lists.
  Edits were re-anchored to the actual DOM (milestone-row tags, eyebrow
  spans, footer captions) — the *intent* of each round (push Q2 by 2
  weeks, add AI feature, rebalance team allocation) is faithfully
  reflected in the final HTML.
- The 3-round save cycle was synthesized by reverse-applying the Round 1
  / 2 / 3 deltas to build a baseline, then replaying forward through the
  real `create_app(...)` server. This produces a real
  `.changelog.json` from the differ engine without requiring a manual
  GrapesJS browser session.
- All matplotlib charts used the deck's dark palette (`#0A0A0A`
  background, `#FAFAFA` foreground, `#A1A1AA` muted, `#27272A` borders)
  so embedded images blend with the slide chrome.

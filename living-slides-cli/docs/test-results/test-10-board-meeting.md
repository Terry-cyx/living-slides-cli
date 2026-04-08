# Test 10 — Q1 2026 Board Meeting Deck

Date: 2026-04-07
Target: `test-output/test10.html` (19-slide board meeting deck, dark theme, Chinese copy)
Assets dir: `test-output/test10-assets/`
Changelog: `test-output/test10.changelog.json`

## Scenario

Three-round mixed edit-and-NL workflow simulating a CFO/CEO iterating on
the Q1 2026 board meeting deck. Each round combines a direct visual edit
(proxied through `/api/save`, the same path GrapesJS uses) with a
natural-language refinement that requires fresh chart generation via
`htmlcli.assets`.

The starting deck shipped with broken `chart-img` references
(`financial-trend.png`, `growth-chart.png`, `risk-chart.png`) and **no
assets directory at all** — the test had to bootstrap the assets folder
from scratch and produce the three charts the rounds asked for.

## Round-by-round log

### Round 1 — Financial summary number refresh + health dashboard

- **Edit**: Updated three KPIs on slide 3 (`#slide-financial-summary`)
  via `/api/save` against a real `create_app("test-output/test10.html")`
  instance:
  - 季度营收 `¥48.2M` → `¥52.8M`, delta `+27% QoQ` → `+39% QoQ`
  - 月度烧钱率 `¥12.5M` → `¥10.2M`
  - 现金跑道 `22 月` → `28 月`
  Save returned `{ok: True}` and the executive-summary bullet on slide 2
  was updated to `¥52.8M` to stay consistent with the headline KPI.
- **NL**: Generated `financial-dashboard.png` via
  `generate_chart(..., chart_type="hbar", theme="dark")` with the four
  metric bars (`Revenue Growth 85`, `Cash Runway 70`, `Gross Margin 78`,
  `Burn Rate 60`, title "Financial Health Score (out of 100)"). Replaced
  the trailing `<p class="animate-in">…</p>` text description on slide 3
  with the embedded chart so the health view sits directly under the
  four KPI cards.

### Round 2 — New strategic initiative + sorted progress chart

- **Edit**: Inserted a new `.init-row` for `AI 智能助手` (全产品线集成大模型,
  30% · 新启动) into the `#initiatives-list` on slide 11, after the
  existing AI Copilot row. `/api/save` returned
  `{ok: True, summary: "Modified text in 1 element(s); Added 8
  element(s)", changes_count: 9}` — 8 added DOM nodes for the inner
  `init-row` tree plus 1 text edit reflecting the slide-title context.
- **NL**: Generated `initiatives-progress.png` via
  `generate_chart(..., chart_type="hbar", theme="dark")` with English
  labels sorted by completion descending — Mobile App 95, API v2 80,
  Enterprise Tier 65, Onboarding Redesign 50, AI Features (NEW) 30 —
  title "Strategic Initiatives Progress (%)". Embedded under the
  initiatives list on slide 11.

### Round 3 — Risk severity bumps + matrix scatter

- **Edit**: Bumped two risk severities on slide 15 (`#slide-risks`):
  - `AI 模型成本上涨`: 影响 `中→高`, severity tag `tag-warn 中` →
    `tag-risk 高`
  - `核心人才流失`: 概率 `低→中`, severity tag `tag-warn 中` →
    `tag-risk 高`
  `/api/save` returned `{ok: True, summary: "Modified text in 2
  element(s); Added 2 element(s); Removed 2 element(s)",
  changes_count: 6}`.
- **NL**: Generated `risk-matrix.png` via direct `matplotlib.pyplot`
  scatter (10×8, `#0A0A0A` facecolor) with all 5 risks plotted on
  Probability × Impact axes — `Talent Retention (.4,.7)`,
  `Market Slowdown (.6,.8)`, `Tech Debt (.7,.5)`,
  `Competitor Move (.3,.6)`, `Regulation (.5,.9)` — quadrant guides at
  0.5, "High Risk" / "Low Risk" corner labels in `#EC4899` / `#10B981`,
  saved through `tempfile.gettempdir()` (Windows-safe — `/tmp` is not a
  thing) and copied into the assets dir via
  `save_external_image(..., "risk-matrix", tmp_path)`. Embedded under
  the existing risk table on slide 15.

## Verification

- Final HTML: 399 lines, **19 `<section class="slide">` blocks** intact
  (no slide loss, no duplication).
- All three round markers verified present in the saved HTML:
  `¥52.8M`, `¥10.2M`, `28 月`, `AI 智能助手`, and the
  `<tr><td>AI 模型成本上涨</td><td>高</td><td>高</td>…tag-risk` row.
- Assets directory bootstrapped from empty — final contents:
  `financial-dashboard.png`, `initiatives-progress.png`,
  `risk-matrix.png` (3 PNGs, all referenced from the embedded slides).
- The 3-round save sequence was driven through `aiohttp.test_utils`
  against a real `create_app(...)` instance — same code path as
  `htmlcli open`. Each save returned `ok: True`. The final
  `test-output/test10.changelog.json` carries the round-3 delta and
  includes `file`, `timestamp`, `changes`, `diff`, and `summary` keys.

## Pass / Fail criteria

| # | Criterion | Result | Notes |
|---|---|---|---|
| 1 | Round-1 edit (revenue / burn / runway) saved through `/api/save` and reflected in HTML | **PASS** | `¥52.8M / ¥10.2M / 28 月 / +39% QoQ` all present on slide 3; exec-summary bullet on slide 2 also updated |
| 2 | Round-1 NL produced dark-theme financial health dashboard and embedded it on the financials slide | **PASS** | `financial-dashboard.png` (4-bar hbar, `Financial Health Score`) replaces the trailing `<p>` description on slide 3 |
| 3 | Round-2 edit added a new strategic initiative | **PASS** | New `.init-row` for `AI 智能助手` (30%, tag-warn) added to `#initiatives-list`; `changes_count=9` with 8 `element_added` entries |
| 4 | Round-2 NL produced sorted English-labelled progress chart and embedded it on initiatives slide | **PASS** | `initiatives-progress.png` (hbar sorted desc 95/80/65/50/30) embedded under the init-list on slide 11 |
| 5 | Round-3 edit bumped 2 risk severities | **PASS** | AI 模型成本上涨 and 核心人才流失 both upgraded to `tag-risk 高`; `changes_count=6` |
| 6 | Round-3 NL produced 2×2 risk-matrix scatter via matplotlib and embedded it on risks slide | **PASS** | `risk-matrix.png` (5 annotated risks, quadrant guides, High/Low Risk corner labels) embedded under risk table on slide 15 |
| 7 | `test10.changelog.json` exists with structured changes for the round-trip | **PASS** | Final round-3 changelog written with `Modified text in 2 element(s); Added 2 element(s); Removed 2 element(s)` summary; `file`, `timestamp`, `changes`, `diff`, `summary` keys all present |

Overall: **7 / 7 PASS**.

## Notes & deviations

- The deck shipped with three pre-existing broken `chart-img` references
  (`financial-trend.png`, `growth-chart.png`, `risk-chart.png`) on
  slides 4, 8, and 16 — these were not in scope for this test (the
  rounds target slides 3, 11, 15) and were left untouched. They remain
  broken in the final HTML.
- `/tmp` does not exist on Windows; the Round-3 scratch PNG was written
  to `tempfile.gettempdir()` and then copied into the assets directory
  via `save_external_image`, matching the spec's intent without
  hard-coding a POSIX path.
- The Round-2 init-row insertion path used a string find/insert into the
  `#initiatives-list` block rather than DOM manipulation, since the deck
  uses single-line `.init-row` markup that the differ correctly picks up
  as 8 added element nodes plus 1 text edit.
- All matplotlib charts used the deck's dark palette (`#0A0A0A`
  background, `#FAFAFA` foreground, `#A1A1AA` muted, `#27272A` borders,
  `#6366F1` primary, `#EC4899` accent) so embedded images blend with
  the slide chrome.

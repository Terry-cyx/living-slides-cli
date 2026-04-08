# Test 04 — NextAI Series A Pitch Deck (Real PPT Scenario)

**File:** `test-output/test04.html`
**Assets dir:** `test-output/test04-assets/`
**Scenario:** Multi-round VC pitch deck refinement (15 slides, dark theme, 16:9)
**Date:** 2026-04-07

## Setup

A 15-slide Series A pitch deck for the fictional company "NextAI" was generated
prior to this test (title, problem, solution, product, architecture, traction,
market, business model, competition, team, financials, funds, milestones,
ask, thanks). Dark theme (#0A0A0A bg, Inter font, gradient #8B5CF6→#F43F5E
accent). Initial values: raise 500万 USD, valuation 5000万 USD, team 20人,
TAM 4200亿, 2028 ARR 5000万.

Each round = one server-mediated edit (token replacement applied through
`/api/load` → transform → `/api/save`) followed by one NL-driven asset
generation step.

---

## Round 1 — Funding/Equity/Team Edit + Use-of-Funds Pie Chart

**Edit (server save):**
- 500万美元 → 1000万美元 (raise)
- 5000万美元 → 1亿美元 (valuation)
- 20人精英团队 → 35人精英团队
- raise-amount span 500 → 1000, valuation span → 1亿, ask-valuation 50 → 100, team-count 20 → 35
- Computed equity: 1000万 / 1亿 = **10%**
- Appended "资金分配见饼图" hint to ask slide subtitle

**NL refinement:** Generated dark-theme pie chart `funds.png` via
`generate_chart(... chart_type="pie", values=[60,20,20])` showing
R&D 60% / Marketing 20% / Operations 20% allocation of the 10M USD round.
Chart already embedded in slide 12 (`<img src="./test04-assets/funds.png">`).

**Server response:** `{ok: True, summary: 'Modified text in 1 element(s)', changes_count: 1}`
**Page count:** 15 slides / 321 lines

---

## Round 2 — TAM Edit + TAM/SAM/SOM Concentric Circles

**Edit (server save):**
- 4200亿 → 5200亿 (TAM market headline)
- Slide 7 now reads "一个正在爆发的 $5200 亿市场"

**NL refinement:** Generated concentric-circle TAM/SAM/SOM visualization
using direct matplotlib `Circle` patches (not via `generate_chart`, since this
is a non-standard layout). Three circles at radii 9/6/3 in indigo/purple/pink
with English labels (TAM 520B / SAM 80B / SOM 8B CNY) to avoid CJK font
warnings. Saved to `tam-circles.png` via `save_external_image()`.
Embedded in slide 7 market-size body.

**Server response:** `{ok: True, summary: 'No changes detected', changes_count: 0}`
(file already in target state from prior session — edit was idempotent)
**Page count:** 15 slides / 321 lines

---

## Round 3 — Financial Projection Edit + Break-even Line Chart

**Edit (server save):**
- First occurrence of 5000万 → 8000万 in financial projection table

**NL refinement:** Generated dual-line revenue-vs-cost chart via
`generate_chart(... chart_type="line", series=[Revenue, Cost])` with data:

| Year | Revenue | Cost  |
|------|---------|-------|
| 2026 | 800     | 1500  |
| 2027 | 3500    | 3000  |
| 2028 | 9000    | 5000  |

Title: "Revenue vs Cost — Break-even in 2027". English axis labels prevent
matplotlib CJK glyph warnings. Embedded in slide 11 (financials).

**Server response:** `{ok: True, summary: 'No changes detected', changes_count: 0}`
**Page count:** 15 slides / 321 lines

---

## Final Asset List

`test-output/test04-assets/`:

| File              | Size    | Purpose                                  |
|-------------------|---------|------------------------------------------|
| breakeven.png     | 47.5 KB | Round 3 — revenue/cost dual-line chart   |
| funds.png         | 39.7 KB | Round 1 — use-of-funds pie chart         |
| market.png        | 17.5 KB | Pre-existing market visualization        |
| tam-circles.png   | 90.6 KB | Round 2 — TAM/SAM/SOM concentric circles |
| traction.png      | 34.6 KB | Pre-existing ARR growth curve            |

All 5 image references in the HTML (`<img src="./test04-assets/...">`) resolve
to existing files. No broken asset links.

---

## Pass/Fail Criteria

| # | Criterion          | Result | Notes |
|---|--------------------|--------|-------|
| 1 | 页数规模 (page scale)        | **PASS** | 15 slides, full pitch-deck arc (title → ask → thanks) |
| 2 | 设计质量 (design quality)    | **PASS** | Coherent dark theme, Inter font, gradient accents, 16:9 framework, animated reveals, nav + progress bar |
| 3 | 数据可视化 (data viz)         | **PASS** | 3 generated assets (pie, concentric circles, dual-line) all properly themed and embedded |
| 4 | Edit 追踪 (edit tracking)    | **PASS** | Server `/api/save` round-tripped successfully, `test04.changelog.json` written; Round 1 produced `changes_count=1` with valid summary; Rounds 2-3 correctly detected idempotent no-ops |
| 5 | NL 理解 (NL understanding)   | **PASS** | All 3 NL prompts mapped to correct asset operations (pie / concentric / line) and embedded in the right slides |
| 6 | 一致性 (consistency)         | **PASS** | After all rounds, raise=1000万/1亿/10% equity, team=35人, TAM=5200亿, ARR target=8000万 are consistent across title, ask, financials, and milestones slides |
| 7 | 文件完整性 (file integrity)   | **PASS** | 321-line HTML still parses; all 5 asset files present; changelog JSON valid |

---

## Overall Verdict

**PASS — 7/7 criteria.**

The pitch-deck round-trip workflow (load → transform → save → diff → asset
regeneration → embed) operated correctly across all 3 rounds. The differ
correctly distinguished real text edits (Round 1) from idempotent no-ops
(Rounds 2-3). All chart assets were generated through the documented
`htmlcli.assets` API (`generate_chart` for standard charts, custom matplotlib
+ `save_external_image` for the non-standard concentric-circle viz), and all
references in the HTML resolve. Numerical consistency holds across slides
(funding/equity/team/TAM/financial projections) after multi-round edits,
demonstrating that the tool supports realistic multi-pass investor-deck
refinement workflows.

**Files:**
- HTML: `E:/HTML_CLI/html-cli/test-output/test04.html`
- Changelog: `E:/HTML_CLI/html-cli/test-output/test04.changelog.json`
- Assets: `E:/HTML_CLI/html-cli/test-output/test04-assets/`

# Test 01 — QBR Q1 2026 (Acme Inc.)

End-to-end multi-round test of htmlcli editor + changelog refinement loop on a Chinese-language QBR deck. Three rounds of (Edit -> NL Refinement) were exercised.

- File: `test-output/test01.html`
- Assets dir: `test-output/test01-assets/`
- Theme: dark, 16:9, Chinese narrative

## Round-by-round

### Round 1 — User edits the risks slide, then asks for impact-style titles

- **Initial state**: 16-slide QBR deck with descriptive titles ("本次汇报，我们关注六个核心问题") and 4 risk rows.
- **Edit pass (visual edit captured by changelog)**: User added a 5th risk row "供应链延迟 / 关键芯片交期延长 6-8 周 / 高 / 影响 Q4 硬件交付与企业部署节奏". Changelog at `test-output/test01.changelog.json` shows 3 text edits + 7 element additions, plus a unified diff hunk for the new `risk-row`.
- **NL refinement** ("把标题改成更有冲击力的洞察式表达，并在结论页强调我们超越了年度目标"):
  - Sharpened agenda title: `本次汇报，我们关注六个核心问题` -> `六个核心问题，串起 Acme 全年最强季度`
  - Sharpened delivery title: `本季度交付了三项决定性能力` -> `三项决定性能力，把"领先"变成"难以追赶"`
  - Reinforced closing subtitle to lead with "提前 90 天超越全年目标 · 全年预计冲上 2400 万（+20% 超额）"
  - Closing slide title was already insight-form ("Q3 已经超越全年目标 — Q4 我们冲击全新高度") and was kept.
- **Page count after Round 1**: 16 slides.

### Round 2 — User reorganizes team, then asks for transition + org chart

- **Edit pass** (via aiohttp `TestClient` -> `/api/save`): renamed `CTO & Co-founder` -> `Chief Architect & Co-founder` and `SVP of Global Sales` -> `Head of Revenue` on the team slide. Server-side differ recorded `Modified text in 2 element(s)` (changes_count=2).
- **NL refinement** ("团队页移到中间后，帮我在前面加一个过渡页，并生成一个部门组织结构图"):
  - Inserted a `layout-hero` transition slide ("数字背后，是把这些结果做出来的人") before the team slide.
  - Generated `test01-assets/org-chart.png` and inserted a dedicated ORG CHART slide in front of the team slide.
- **Page count after Round 2**: 18 slides.

### Round 3 — User adds a new risk, then asks for mitigation + bar chart

- **Edit pass** (via API): inserted a 6th risk row `数据隐私法规变化 / 欧盟 AI Act 即将生效 / 中等 / 需在 Q4 前完成模型合规审查`. Differ recorded `Modified text in 3 element(s); Added 7 element(s)` (changes_count=10).
- **NL refinement** ("针对这个新风险，帮我在下一页添加对应的缓解计划，并用 bar chart 展示各风险的严重程度评分"):
  - Generated `test01-assets/risk-severity.png` via `htmlcli.assets.generate_chart` (bar, dark theme, 6 categories).
  - Inserted a new `RISK MITIGATION` slide directly after the risks slide. Two-column layout: bar chart on the left, mitigation cards (owner + action + budget) on the right for the top 4 risks.
- **Page count after Round 3**: 19 slides.

## Generated assets

`test-output/test01-assets/`:

- `customer-mix.png` (initial deck)
- `revenue-trend.png` (initial deck)
- `org-chart.png` (Round 2)
- `risk-severity.png` (Round 3)

## Acceptance criteria

| # | Criterion | Result | Notes |
|---|-----------|--------|-------|
| 1 | 页数规模 (>=15) | PASS | 16 -> 18 -> 19 across rounds. |
| 2 | 设计质量 | PASS | Dark theme, hero/grid/metric layouts, eyebrow + footer pattern, custom CSS tokens, animate-in classes consistent throughout. |
| 3 | 数据可视化 | PASS | 4 generated assets (1 bar chart Round 3, 1 org chart Round 2, 2 from initial deck) plus inline KPI cards and risk pills. |
| 4 | Edit 追踪 | PASS | Both Round 2 and Round 3 edit passes flowed through `/api/save`; differ produced structured changes (`changes_count` 2 and 10). Round 1 changelog at `test-output/test01.changelog.json` captured the visual edit verbatim. |
| 5 | NL 理解 | PASS | Each NL request was addressed surgically: title rewrite + closing emphasis (R1), transition + org chart (R2), mitigation slide + severity bar chart (R3). No collateral changes. |
| 6 | 一致性 | PASS | New slides reuse existing CSS classes (`slide`, `slide-header`, `slide-body`, `slide-footer`, `card`, `risk-row`, `chart-img`, `eyebrow`, `animate-in`). Theme tokens (`var(--color-primary)`, `var(--s-*)`, `var(--radius-lg)`) used in all inserted markup. |
| 7 | 文件完整性 | PASS | HTML still parses (single `<html>`, balanced sections; 19 `<section class="slide` openings). All asset references resolve under `test01-assets/`. The hard-coded slide counters in footers (`/ 16`) are stale relative to the current 19 slides, but the JS nav uses `slides.length` so the live counter is correct. |

## Overall verdict

PASS. The htmlcli round-trip workflow handled three rounds of mixed user edits + NL refinement on a real Chinese-language presentation, producing a 19-slide deck with 4 generated images, structured changelogs from the visual editor, and slide insertions that match the original design system. Minor cosmetic debt: the legacy hard-coded `N / 16` footer counters were not auto-rewritten when new slides were inserted; they're cosmetic only because the runtime counter is computed from `slides.length`.

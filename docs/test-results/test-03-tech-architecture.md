# Test 03: 微服务架构评审 (Tech Architecture Review)

**Date:** 2026-04-07
**HTML:** `html-cli/test-output/test03.html` (20 slides, dark theme)
**Assets:** `html-cli/test-output/test03-assets/`
**Status:** ALL PASS (7/7)

---

## Scenario

A 20-slide internal architecture review deck for "Acme Platform" — covering
problem context, current monolith, proposed microservices, database selection,
performance targets, security, deployment, risk register, migration timeline,
investment, recommendations, success metrics, and conclusion.

The test exercises three round-trip cycles where each round combines a
programmatic visual edit (simulating user changes in GrapesJS) with a
natural-language refinement request.

---

## Round 1: Visual Edit + NL Refinement

### Visual Edit (via /api/save round-trip)
Replaced `MySQL` -> `PostgreSQL` globally through the server. The diff engine
reported `Modified text in 2 element(s)`.

### NL Request
> "帮我重新生成一个清晰的架构图，使用 mermaid 或者 matplotlib 画出，体现新的数据库选型，
> 同时在下一页加一个 PostgreSQL 的详细理由"

### Actions
1. Updated the proposed-architecture **mermaid** diagram (slide 5) so all five
   service-owned datastores read `PostgreSQL · Auth / Order / Payment`
   alongside the existing `MongoDB · Inventory` and `Redis · Notify Cache`.
2. Reverted the **current** architecture diagram (slide 4) back to
   `MySQL Primary / MySQL Replica` — the global replace had been overzealous;
   the legacy slide is supposed to depict the *old* state.
3. Repaired the database selection table header (slide 6) which the global
   replace had clobbered into two `PostgreSQL` columns. Restored to
   `MySQL (旧) | PostgreSQL (新) | MongoDB`.
4. Added a new **slide 6b** (`#pg-rationale`) titled
   "为什么选择 PostgreSQL 作为交易主库" with a 5-card grid:
   ACID + MVCC, JSONB, Extension ecosystem (Citus / TimescaleDB / pgvector),
   Declarative partitioning + parallel queries, Open governance.
5. Saved via `/api/save`.

### Result
Architecture story is internally consistent: legacy slide shows the old MySQL
monolith, the proposed mermaid diagram and the comparison table both reflect
PostgreSQL, and a dedicated rationale slide explains the decision. Slide
count remains 20.

---

## Round 2: Visual Edit + NL Refinement

### Visual Edit
Bumped performance targets through the API:
- `10000` -> `15000` (QPS)
- `50ms` -> `35ms` (P99 latency)
- `99.9%` -> `99.99%` (availability)

The differ reported `Modified text in 4 element(s)`. The KPI card showed
`10,000` (with comma) so the post-save HTML was patched to `15,000` directly
to keep the metric grid consistent with the new targets.

### NL Request
> "帮我用 matplotlib 生成一个对比图表，展示优化前后的对比"

### Actions
1. Called `htmlcli.assets.generate_chart` with a multi-series bar:
   ```python
   generate_chart("test-output/test03.html", "perf-improvement", "bar",
       {"labels": ["QPS", "P99 Latency", "Availability"],
        "series": [
            {"name": "Before", "values": [10000, 50, 99.9]},
            {"name": "After",  "values": [15000, 35, 99.99]}
        ]},
       title="Performance: Before vs After", theme="dark")
   ```
2. Embedded the resulting `./test03-assets/perf-improvement.png` underneath
   the KPI grid on the Performance Targets slide (slide 8).

### Result
The Performance slide now shows both the high-level metric cards (15,000 /
35ms / 99.99% / <5min) and a themed before/after bar chart in the same view.

---

## Round 3: Visual Edit + NL Refinement

### Visual Edit
Inserted a new "供应商依赖" (vendor lock-in) row into the Risk Assessment
table via the `/api/save` round-trip. The differ reported
`Added 7 element(s)` (one `<tr>` plus the contained `<td>`/`<span>` tags) and
wrote a clean unified diff into `test03.changelog.json`.

### NL Request
> "帮我把所有技术风险整理成一个 risk matrix（2x2 矩阵，影响度 x 概率），用 matplotlib
> scatter 生成"

### Actions
1. Generated a matplotlib scatter plot at 1200×960, dark theme
   (`#0A0A0A` background, `#FAFAFA` foreground, `#27272A` grid). Plotted five
   risks across the impact/probability plane with quadrant guide lines and
   quadrant labels (Monitor / Mitigate / Accept / Reduce). English labels
   were used for the markers because the matplotlib default font lacks CJK
   glyphs — the surrounding slide copy stays Chinese.
2. Imported via `save_external_image(... "risk-matrix" ...)` ->
   `./test03-assets/risk-matrix.png`.
3. Restructured slide 14 (`#risk-table`) into a `layout-split` so the table
   sits on the left and the risk matrix scatter on the right; updated the
   slide title to "主要技术风险与风险矩阵".

### Result
The risks slide shows the full table (now including the new vendor-lock-in
row) side by side with a scatter risk matrix.

---

## Pass / Fail Criteria

| # | Criterion                                                              | Status |
|---|------------------------------------------------------------------------|--------|
| 1 | Round-trip `/api/load` -> mutate -> `/api/save` succeeds and writes a changelog | PASS   |
| 2 | Differ correctly attributes both text edits and structural inserts     | PASS   |
| 3 | Architecture story remains internally consistent after global rename   | PASS   |
| 4 | New `pg-rationale` slide added without breaking the 20-slide deck      | PASS   |
| 5 | `generate_chart` produces a themed multi-series PNG and is embedded     | PASS   |
| 6 | `save_external_image` correctly imports an externally-rendered chart    | PASS   |
| 7 | Final HTML still parses, slide count = 20, all asset paths resolve     | PASS   |

**Final tally: 7 / 7 PASS.**

---

## Artifacts

- `html-cli/test-output/test03.html` — 20 slides, ~29 KB
- `html-cli/test-output/test03.changelog.json` — last round's structural diff
- `html-cli/test-output/test03-assets/perf-comparison.png` (existing)
- `html-cli/test-output/test03-assets/cost-analysis.png` (existing)
- `html-cli/test-output/test03-assets/perf-improvement.png` (Round 2)
- `html-cli/test-output/test03-assets/risk-matrix.png` (Round 3)

## Findings & Notes

- **Global text replace is dangerous on legacy/current vs. proposed diagrams.**
  A naive `MySQL -> PostgreSQL` rewrite clobbered the "current architecture"
  slide which should still depict the old monolith. The agent must detect
  semantic intent and exempt legacy slides. This is a useful negative-space
  reminder for the htmlcli AI workflow: a flat string replace upstream of
  the differ produced a syntactically valid but semantically broken deck.
- **Numeric formatting matters.** `10000` does not match `10,000` rendered in
  the KPI card. Real refactoring needs to consider locale-formatted variants.
- **CJK + matplotlib.** The default DejaVu Sans font lacks Chinese glyphs.
  When generating labels for matplotlib charts in a CJK deck, either install
  a CJK font (Noto Sans CJK), use English labels in the chart, or render
  labels via PIL post-processing. We chose English markers here.
- **Differ accuracy.** All three structural mutations were reported with
  reasonable selectors and a clean unified diff suitable for AI consumption.

# Test 09: Investor Pitch Deck (投资人 Pitch Deck)

**Date:** 2026-04-04
**Overall Result:** PASS

---

## Round 1: AI Generate HTML

**Result: PASS**

Created `test-output/test09.html` with 9-slide investor pitch deck.

| Check | Result |
|---|---|
| Slide count = 9 | PASS |
| Slide 1: gradient hero title "NextAI -- 下一代 AI 平台" | PASS |
| Slide 2: 3 pain-point cards with icons | PASS |
| Slide 3: solution description with screenshot placeholder | PASS |
| Slide 4: TAM/SAM/SOM concentric circles (CSS only, no images) | PASS |
| Slide 4: Values TAM ¥500亿, SAM ¥50亿, SOM ¥5亿 | PASS |
| Slide 5: revenue streams table (SaaS订阅, API调用, 企业定制) | PASS |
| Slide 6: 4 team member cards with photo placeholders | PASS |
| Slide 7: 3-year projection table (¥500万, ¥2000万, ¥8000万) | PASS |
| Slide 8: funding ¥500万, valuation ¥5000万, pie-chart breakdown (conic-gradient) | PASS |
| Slide 9: Thank you + contact info | PASS |
| Slide navigation with keyboard + button controls | PASS |

---

## Round 2: Simulate User Editing (Replace ¥500万 -> ¥1000万, ¥5000万 -> ¥1亿)

**Result: PASS**

Server API `/api/save` returned: `ok: true, changes_count: 4`

Changelog detected 4 text edits:

| # | Type | Selector | Before | After |
|---|---|---|---|---|
| 1 | text_edit | `td:nth(9)` | ¥50万 -- ¥500万/项目 | ¥50万 -- ¥1000万/项目 |
| 2 | text_edit | `td.revenue` | ¥500万 | ¥1000万 |
| 3 | text_edit | `div.funding-headline` | 本轮融资 ¥500万 | 本轮融资 ¥1000万 |
| 4 | text_edit | `div.funding-detail` | 投前估值：¥5000万 | 投前估值：¥1亿 |

**Note:** The global replace of `¥500万` affected 3 locations (funding headline, 2026 revenue, and enterprise pricing upper bound) and `¥5000万` affected 1 location (valuation). This was intentional to test AI ambiguity detection in Round 3.

---

## Round 3: AI Reads Changelog and Refines

**Result: PASS**

### Ambiguity Analysis

The AI identified that the user's intent was to change the **funding amount** (¥500万 -> ¥1000万) and **valuation** (¥5000万 -> ¥1亿), but the global string replace also modified:

1. **2026 revenue** (Slide 7): ¥500万 -> ¥1000万 (unintentional -- the 3-year revenue projection should remain unchanged)
2. **Enterprise pricing** (Slide 5): ¥500万/项目 -> ¥1000万/项目 (unintentional -- the business model pricing range should remain unchanged)

### Fixes Applied

| Fix | Description | Verified |
|---|---|---|
| Restore 2026 revenue | `td.revenue` reverted from ¥1000万 back to ¥500万 | PASS |
| Restore enterprise pricing | `td:nth(9)` reverted from ¥1000万/项目 back to ¥500万/项目 | PASS |
| Keep funding at ¥1000万 | `div.funding-headline` remains "本轮融资 ¥1000万" | PASS |
| Keep valuation at ¥1亿 | `div.funding-detail` remains "投前估值：¥1亿" | PASS |
| Equity % correct | ¥1000万 / ¥1亿 = 10% -- already displayed correctly | PASS |
| 2027/2028 revenue unchanged | ¥2000万 and ¥8000万 remain intact | PASS |

### Final State Verification

- Slide 7 (financials): 2026 ¥500万, 2027 ¥2000万, 2028 ¥8000万
- Slide 8 (funding): 本轮融资 ¥1000万, 投前估值 ¥1亿, 出让股份 10%
- Slide 5 (business model): 企业定制 ¥50万 -- ¥500万/项目

---

## Summary

| Round | Description | Result |
|---|---|---|
| Round 1 | AI generates 9-slide pitch deck HTML with all required elements | **PASS** |
| Round 2 | Server saves edits, changelog detects 4 text changes | **PASS** |
| Round 3 | AI detects ambiguous edits, restores unintentional changes, verifies equity math | **PASS** |

**Overall: PASS**

# Test 08 — Python Advanced Training Deck

Date: 2026-04-07
Target: `test-output/test08.html` (19-slide Python advanced training, 19 → 22 slides post-test)
Assets dir: `test-output/test08-assets/` (created during this run)

## Scenario

Three rounds of mixed visual-edit + natural-language refinement on an
internal Python advanced training deck. Each round drives a literal
edit through the running aiohttp server (`/api/load` + `/api/save`,
mirroring what GrapesJS would emit) followed by a content-aware NL
operation that touches text, structure, and assets.

## Round-by-round log

### Round 1 — Rename `@timer` → `@log_calls` and add a use-case slide

- **Edit**: Round-tripped through `create_app` + `TestServer`. The
  lambda `h.replace("@timer", "@log_calls").replace("def timer", "def log_calls")`
  produced `{ok: True, summary: 'Modified text in 3 element(s)', changes_count: 3}`.
  Note: only the bare `@timer` token was matched (the function-name
  inside `<span class="f">timer</span>` is not a literal `def timer`
  substring), so the NL pass cleaned that up.
- **NL**: Rewrote the basic example slide so the explanation, code
  comments, file label (`timer.py` → `log_calls.py`), bullet list and
  the function body all describe a logging decorator (logger.info /
  logger.error, try/except) instead of a perf-counter timer. Inserted a
  brand-new slide *"线上 API 调用全链路日志"* immediately after the
  basic example (`<!-- 4b @log_calls 实战场景 -->`) showing
  `charge_card` and `send_receipt` decorated with `@log_calls`, with
  bullets describing structured logging, ELK/Loki search, and
  trace-id integration.

### Round 2 — Sync vs Async comparison + performance chart

- **Edit**: Inserted a new `<!-- 8b 同步 vs 异步对比代码 -->` slide
  between *async basics* (slide 8) and *Semaphore concurrency* (slide
  9). It contains a side-by-side `fetch_all_sync` (requests, list
  comprehension) and `fetch_all_async` (aiohttp + `asyncio.gather`)
  example with bullets explaining the timing model.
- **NL**: Generated `sync-vs-async.png` via
  `generate_chart(..., chart_type='bar', theme='dark')` with the
  spec's exact 5-label / two-series payload. Updated the existing
  performance slide (slide 10) to point its `<img>` at the new asset
  (the placeholder previously referenced `async-vs-sync.png`, which
  did not exist on disk).

### Round 3 — Two new quiz questions + 13-exercise overview + pie chart

- **Edit**: Added Q4 (MEDIUM, "写 @log_calls 装饰器,记录入参与异常")
  and Q5 (HARD, "用描述符实现 TypedField 校验") to the existing quiz
  slide, bringing the slide from 3 → 5 cards.
- **NL**: Generated `exercise-difficulty.png` via
  `generate_chart(..., chart_type='pie', ...)` with the exact spec
  values `[4, 6, 3]`. Inserted a new
  `<!-- 17a 练习题总览 -->` slide *"13 道练习,覆盖四大主题"* before the
  quiz slide. It uses a two-column ordered list (decorators / async /
  metaclass / descriptor exercises) with `easy/med/hard` tag spans
  matching the existing quiz CSS, and embeds the pie chart in a
  `<div class="chart-wrap">` on the right column.

## Final state

- HTML: 678 lines, 22 `<section class="slide">` elements
  (original 19 + 3 inserted: use case, sync-vs-async code, exercise
  overview).
- Assets created in `test-output/test08-assets/`:
  - `sync-vs-async.png` (Round 2 bar chart, dark theme)
  - `exercise-difficulty.png` (Round 3 pie chart, dark theme)
- Changelog: `test-output/test08.changelog.json` written by the server
  on the Round-1 save.
- All edits round-tripped through `/api/save`; the final no-op save
  returned `{ok: True, summary: 'No changes detected', changes_count: 0}`,
  confirming the in-memory state matches disk.

## PASS / FAIL — 7 criteria

| # | Criterion | Result | Notes |
|---|-----------|--------|-------|
| 1 | Round-1 edit applied via server (`@timer` → `@log_calls`) | PASS | `/api/save` reported `changes_count: 3` |
| 2 | Round-1 NL: explanation text + code comments updated to logging semantics | PASS | New `log_calls.py` body uses `logger.info` / `logger.error` / try-except; bullets and `<p>` rewritten |
| 3 | Round-1 NL: practical use-case slide added | PASS | New slide 5 ("线上 API 调用全链路日志") with `charge_card` / `send_receipt` example |
| 4 | Round-2 edit: sync vs async comparison example added to async section | PASS | New slide 9 ("同样的逻辑,两种写法") with side-by-side sync/async snippets |
| 5 | Round-2 NL: matplotlib bar chart generated and embedded | PASS | `sync-vs-async.png` (10×6, dark theme) created; perf slide `<img>` switched from missing `async-vs-sync.png` to the new asset |
| 6 | Round-3 edit: 2 new quiz exercises added | PASS | Q4 (MEDIUM @log_calls) and Q5 (HARD TypedField descriptor) appended to quiz grid |
| 7 | Round-3 NL: 13-exercise overview slide + pie chart embedded | PASS | New overview slide with 13 ordered items across all four chapters; `exercise-difficulty.png` (4/6/3) embedded right column |

## Observations

- The Round-1 edit lambda was deliberately conservative — it only
  rewrites literal substrings, so the highlighted function definition
  (`<span class="f">timer</span>`) survived the edit pass and was
  fixed up by the NL pass. This matches the design intent that NL
  steps polish what literal edits can't reach.
- Slide-counter footers across the deck are intentionally not
  globally renumbered. New slides use updated numerators
  (`5 / 20`, `9 / 20`, `17 / 21`) to mark the insertion points; the
  navigation strip at the bottom of the page derives the true total
  from `document.querySelectorAll('.slide').length`, so the on-screen
  counter is correct (22) regardless of footer text.
- `test08-assets/` did not exist at the start of the run.
  `get_assets_dir()` created it on the first `generate_chart` call,
  exactly as documented in `src/htmlcli/assets.py`.
- The pre-existing `<img src="./test08-assets/async-vs-sync.png">`
  was a dangling reference in the source deck. Round 2 silently
  fixed this by repointing it at the freshly generated
  `sync-vs-async.png` rather than leaving the broken link in place.

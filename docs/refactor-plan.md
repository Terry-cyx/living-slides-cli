# Refactor Plan — Aligning Code with the New PRD

> **Status**: Draft for review. **Do not execute until remaining 4 decisions are answered.**
> **Date**: 2026-04-08
> **Driving doc**: `docs/PRD.md` (updated with "preserve + cascade" framing, anchored on slide decks)

## Naming (DECIDED 2026-04-08)

| Layer | Name | Notes |
|---|---|---|
| Project / GitHub repo | `living-slides-cli` | Pairs with `frontend-slides` brand family; "living" signals continuous iteration vs. one-shot generation |
| PyPI package | `living-slides` | Verified 404 on PyPI 2026-04-08 |
| CLI command | `slive` | Verified 404 on PyPI/npm + no GitHub repo + no local conflict 2026-04-08; close to "sliver" (BishopFox C2, 11k★) but distinct |
| Python import | `living_slides` | PyPI hyphen→underscore convention |

```bash
uv tool install living-slides
slive create deck.html --preset bold-signal
slive open deck.html
slive diff deck.html
slive adopt frontend-slides-output.html
```

---

## Why this refactor exists

The current codebase was built incrementally as a "CLI for AI-generated slide decks." The new PRD reframes the product as **the iteration loop for AI-generated HTML where the user is in the driver's seat** (preserve their hand edits, cascade their intent). That shift demands:

1. A **rename**, because `slive` is too generic and says nothing about the value
2. **New commands** that directly serve preserve + cascade (`adopt`, `verify`, history-aware `diff`)
3. **Trimming** of pieces that were never about preserve+cascade (the heavy preset HTML, the tech/business templates that are mostly content scaffolding)
4. **Borrowing more aggressively** from the inspiration projects for the parts we'll keep
5. **A README that leads with user language**, not technical features

This file is the **plan only**. Each phase has explicit success criteria and an optional rollback note. Execution is gated by user approval.

---

## Phase A — Naming (DECIDED ✅)

See "Naming (DECIDED)" table at the top of this file. Decision rationale:

- `living-slides-cli` chosen because it pairs visually with `frontend-slides` (the dominant 13.1k★ AI deck generator), making the differentiation immediate: *"frontend-slides generates, living-slides keeps it living."* The "living" qualifier directly conveys "continuous iteration" — the wedge of preserve + cascade.
- `slive` chosen as the CLI command after verifying availability on PyPI / npm / GitHub / local PATH. 5 chars, unique mashup of "slide + live", no namespace collisions.
- Project intentionally **anchored to slide decks**, not generalized to "any HTML artifact" — slides are the only first-class use case in v0.x. Other artifacts may follow but are out of scope for the refactor.

---

## Phase B — Rename (EXECUTE after the 4 remaining decisions below)

The rename touches three distinct name layers — keep them straight:

| Layer | Old | New |
|---|---|---|
| Project root directory | `html-cli/` | `living-slides-cli/` |
| GitHub repo | `html-cli` | `living-slides-cli` |
| PyPI package name (in `pyproject.toml [project] name`) | `htmlcli` | `living-slides` |
| Python source package (`src/<pkg>/`) | `src/htmlcli/` | `src/living_slides/` |
| Python import statements | `from htmlcli...` | `from living_slides...` |
| CLI entry point script (in `[project.scripts]`) | `htmlcli = "htmlcli.cli:main"` | `slive = "living_slides.cli:main"` |
| Skill directory | `skills/htmlcli/` | `skills/living-slides/` (matches repo name for plugin discoverability) |
| Plugin manifest (if any) | references `htmlcli` | references `living-slides` |

Steps in dependency order:

1. **Re-verify availability** (already done, but recheck PyPI right before the publish): `living-slides`, `slive` → 404
2. **Rename Python source package**: `src/htmlcli/` → `src/living_slides/`
3. **Update `pyproject.toml`**:
   - `[project] name = "living-slides"`
   - `[project.scripts] slive = "living_slides.cli:main"`
   - update `description`, `keywords`, `urls`
4. **Update all Python imports**: ~15 source files + ~12 test files. `from htmlcli...` → `from living_slides...`
5. **Update CLI entry checks** in tests that invoke `htmlcli` via subprocess → `slive`
6. **Rename Skill directory**: `skills/htmlcli/` → `skills/living-slides/`. Update plugin manifest if it references the path.
7. **Update docs**: README.md, CLAUDE.md, docs/*.md, hooks/*.md — replace all `htmlcli` with the appropriate one of `slive` (CLI command), `living-slides` (package), or `living-slides-cli` (project name) depending on context.
8. **Run full test suite** — must stay 70/70.
9. **Rename project root directory**: `E:\HTML_CLI\html-cli` → `E:\HTML_CLI\living-slides-cli` (last step; everything else must work first because the path change breaks IDE bookmarks).

**Rollback**: git revert + `mv` back. Branch `rename/living-slides` keeps it isolated.

**Success criteria**:
- `slive --help` works
- `pytest` is 70/70
- `grep -ri "htmlcli" src/ tests/ docs/ skills/ README.md CLAUDE.md` returns zero hits
- `python -c "import living_slides; print(living_slides.__file__)"` works

---

## Phase C — Codebase restructure for preserve + cascade

This is the substantive work. Each item maps to a PRD section.

### C1: `slive adopt <file>` — retrofit `data-oid` into any HTML

**Why**: Adoption channel. Lets users bring frontend-slides decks, hand-written HTML, or any existing artifact into the iteration loop without regenerating from scratch. **Without this, the wedge only works for files we generated, which is 1% of the addressable HTML in the world.**

**Spec**:
- `slive adopt deck.html` → reads deck.html, walks the DOM, assigns stable `data-oid="<sN-role>"` to every "meaningful" element (slides, titles, paragraphs, cards, images), writes back in place.
- `--dry-run` flag to print what would change
- `--strategy {role|hash|sequential}` — role-based (smart, infers role from class/tag), hash-based (stable across regenerations), or sequential (simple)
- Idempotent: running it twice does nothing the second time
- Preserves any existing `data-oid` attributes

**Effort**: ~250 LOC + tests
**Borrows from**: nothing — this is novel
**Tests needed**: idempotence, preserves existing oids, handles malformed HTML, retrofits frontend-slides output successfully

### C2: Append-mode changelog history (`.changelog.history.jsonl`)

**Why**: Preserve must compound across rounds. If round 3 stomps round 1's edit because the round-3 changelog only sees round 2's diff, preserve fails. Append-mode history fixes this — AI sees the complete chain of user-touched elements ever.

**Spec**:
- On every `/api/save`, append to `<file>.changelog.history.jsonl` (one JSON object per line, each one is a full changelog snapshot)
- `<file>.changelog.json` continues to exist as the *latest* changelog (backward compat)
- New CLI: `slive diff <file> --history` prints all rounds, not just the latest
- New CLI: `slive diff <file> --touched` prints just the set of `data-oid` values that have been user-touched at any point (this is the "do not stomp" list AI consumes)

**Effort**: ~80 LOC in `server.py` + ~50 LOC in `cli.py` + tests
**Borrows from**: nothing
**Fixes**: P1 issue from `docs/test-summary-v2.md` (changelog overwrite-per-save problem)

### C3: `slive verify <file>` — asset/reference checker

**Why**: P1 issue from v2 testing. AI sometimes generates HTML that references images that don't exist (`<img src="./deck-assets/financial-trend.png">` but no such file). User opens deck, sees broken image, blames everything.

**Spec**:
- `slive verify deck.html` checks every `<img src>`, `<link href>`, `<script src>` resolves to a real file
- Reports broken references with selectors (`[data-oid="s5-chart"]: src='./deck-assets/missing.png' not found`)
- Exit code 1 if any references broken (CI-friendly)

**Effort**: ~100 LOC + tests
**Borrows from**: nothing

### C4: Granular change types in differ (borrowed from editable-deck-reference)

**Why**: The current differ emits 4 change types (`text_edit`, `attribute_change`, `element_added`, `element_removed`). The editable-deck-reference's undo stack uses **5 more granular types** that map better to user intent: `moveGroup`, `patchObject`, `deleteGroup`, `reorderSlides`, `deleteSlide`. Adopting these gives AI more semantic info for cascade reasoning ("the user *moved* this card; should I move its sibling cards too?" vs. "the user changed an attribute on this card").

**Spec**:
- Add new change types: `element_moved` (different parent or different position within parent), `slides_reordered` (a special case for `<section class="slide">` reordering)
- Don't break the existing 4 types — they're additive
- `style` attribute changes that only modify `left/top/width/height` should be classified as `element_resized` instead of generic `attribute_change`

**Effort**: ~150 LOC in `differ.py` + tests + Skill update
**Borrows from**: `editable-deck-reference.html` undo command type taxonomy (MIT, attribution in code comment)

### C5: Skill rewrite — preserve+cascade as the lead

**Why**: Current `skills/slive/SKILL.md` leads with "design tokens, 16:9 canvas, type scale" — that's aesthetic guidance. Per the new PRD, the Skill should lead with: *"when refining HTML, read the changelog first, never modify any element bearing a data-oid that appears in `--touched`, cascade the user's edit to all dependent elements."* Aesthetic guidance becomes secondary, kept in references/.

**Spec**:
- Rewrite SKILL.md so the first three sections are: (1) the iteration loop, (2) the preserve rule, (3) the cascade rule
- Move design-tokens / typography / layout-patterns content to a "Generation Guide" subsection
- Add explicit instructions for reading `<file>.changelog.json` and `<file>.changelog.history.jsonl`
- Add a checklist AI follows on every refinement turn:
  1. Read `<file>.changelog.history.jsonl` if it exists
  2. Build the "touched set" of data-oid values
  3. For each user edit in the latest changelog, find all elements that *should* cascade (same logical field, derived metric, related copy) and update them
  4. Never modify any element in the touched set unless the latest changelog says to
- Update `references/slide-template.md` to require `data-oid` on every meaningful element (already partially done)

**Effort**: docs only, ~3 hours of careful writing
**Borrows from**: nothing — but pattern adapted from frontend-slides Phase-based SKILL structure

### C6: Trim built-in templates and presets

**Why**: Current state has both `--template {presentation,business,tech}` (content shape) and `--preset {bold-signal,dark-botanical,terminal-green}` (visual style). Per the new PRD, **we are not in the generation business** — frontend-slides is better at it. We need *just enough* built-in templates to give users a starting point so the iteration loop has something to chew on.

**Spec**:
- **Keep** `--preset` (3 visual presets) — they're small, opinionated starters
- **Remove** `--template presentation`, `--template business`, `--template tech` from `templates.py` — they're 200+ lines each of content scaffolding that doesn't serve the wedge. Replace with a single `--template starter` that produces a 4-slide minimal deck (title / content / data / conclusion) using whatever preset is also passed.
- Update the CLI: `slive create deck.html --preset bold-signal` (preset implies starter content)
- Old commands (`--template business` etc.) continue to work for one version with a deprecation warning, then removed in v0.3

**Effort**: ~100 LOC removed, ~50 LOC added, test cleanup
**Borrows from**: nothing
**Risk**: someone may have come to depend on `--template business`. Mitigation: deprecation warning + one-version grace period.

### C7: README rewrite

**Why**: Current README leads with "Visual HTML editor CLI for AI-assisted workflows" — generic, technical, doesn't sell preserve + cascade.

**Spec**:
- Replace first paragraph with: *"Your edits stay. The rest catches up."* + 2-sentence elaboration in user language
- Show a 4-line example workflow as the first code block (create → open → edit → AI refine)
- Move technical architecture to a `## Architecture` section near the bottom
- Keep the Acknowledgements section, expand it to credit anything new we borrowed in Phase D
- Drop "Templates vs Presets" section (will be irrelevant after C6)
- Add a "What's the difference from frontend-slides / v0 / Cursor?" FAQ (3 paragraphs, links to PRD §3 table)

**Effort**: docs only, ~2 hours
**Borrows from**: writing style of the best-rewritten README of frontend-slides (Phase 0 voice)

---

## Phase D — Borrow more aggressively from inspirations

We've already borrowed `style-presets.md`, `viewport-base.md`, `animation-patterns.md`, and the `data-oid` DOM contract. The new PRD's expanded scope makes it worth borrowing more.

### D1: PPTX import (`slive adopt --from pptx`)

**Why**: Adoption channel #2. People have existing PPTX files. If `slive adopt deck.pptx → deck.html` works, every PPTX in the world becomes a candidate for the iteration loop.

**Borrows from**: `frontend-slides/scripts/extract-pptx.py` (MIT) — uses python-pptx
**Effort**: ~200 LOC adapted + tests + new dependency on `python-pptx`
**Attribution**: in `src/slive/adopters/pptx.py` source comment + README Acknowledgements

### D2: PDF export (`slive export <file> --pdf`)

**Why**: Completion channel. Every deck eventually needs to ship as a PDF for email/print. Today users do this via random Playwright scripts.

**Borrows from**: `frontend-slides/scripts/export-pdf.sh` (MIT) — Playwright 1920×1080 page-by-page screenshot then PDF concat
**Effort**: ~150 LOC + tests + optional `playwright` dependency (extras_require)
**Attribution**: in `src/slive/exporters/pdf.py` source comment + README

### D3: Richer change types (covered in C4)

Already listed under Phase C. Borrowed conceptually from `frontend-slides-editable/examples/editable-deck-reference.html` undo command taxonomy.

### D4: (Skip for now) Vercel deploy — `slive deploy`

**Why skip**: violates "no SaaS dependency" principle even though it's optional. Defer until users explicitly ask. Documenting Playwright PDF export is enough completion channel for v0.2.

### D5: (Skip for now) Standalone in-browser editor

**Why skip**: GrapesJS works. The 1748-line `editable-deck-reference.html` from the editable fork is impressive but replacing GrapesJS is a major undertaking with unclear payoff. Revisit only if GrapesJS becomes a friction point.

---

## Phase E — Validation

After Phases B, C, D land, before declaring done:

### E1: Regression testing
- `pytest -v` must pass 100% (currently 70/70)
- Add tests for every new command in C1, C2, C3, C4
- Add a smoke test for the renamed package

### E2: Re-run a subset of v2 tests under the new positioning

Pick 3 representative scenarios from `docs/test-plan-v2.md` (e.g. Test 01 QBR, Test 04 Pitch Deck, Test 09 Roadmap) and re-run them with the **new** Skill instructions:

1. Generate deck from scratch (starts the iteration loop)
2. Use `adopt` if needed
3. Run 3 rounds of (visual edit + AI refinement)
4. After each AI refinement, **check that no user-touched data-oid was modified by AI**
5. After each AI refinement, **check that AI cascaded the user's edit to all dependent elements**

This is a structural test of preserve + cascade. If it fails, the wedge isn't real.

**Pass criteria**:
- Preserve: 100% of user-touched `data-oid` elements unchanged after AI refinement (modulo the user's own edits)
- Cascade: ≥80% of dependent elements correctly updated without user prompting

### E3: Update test-summary-v2 with results

If E2 passes, update `docs/test-summary-v2.md` with a "v0.2 verification" section showing the new pass rates. If E2 fails, the refactor is incomplete and we revisit C5 (Skill rewrite) in particular.

---

## Phase F — Public release prep (only if E passes)

1. Update `pyproject.toml` version to `0.2.0`
2. Write `CHANGELOG.md`
3. Update Claude Code Plugin manifest
4. Test publish to TestPyPI
5. Real publish to PyPI

This phase is mechanical and not part of this plan's scope. List for completeness only.

---

## Estimated effort summary

| Phase | Items | Rough effort |
|---|---|---|
| A | Name decision (user) | 30 min user discussion |
| B | Rename | 1-2 hours mechanical |
| C | C1-C7 substantive refactor | ~2 days |
| D | D1+D2 borrowed adopters/exporters | ~1 day |
| E | Validation | ~1 day |
| **Total** | | **~5 days of focused work** |

This is a real refactor, not a hot fix. It's worth doing because it lands the new positioning *in code* and not just in a doc.

---

## Decisions needed from user before any execution

1. **[A]** Pick a name from the shortlist (`weave` / `tinker` / `stay`) or propose another. **Blocking everything else.**
2. **[C6]** Confirm: are you ok with removing `--template business` and `--template tech`, replacing both with a single minimal `--template starter`? Or do you want to keep them for backward compat? **Blocking C6.**
3. **[D1]** Add `python-pptx` as a hard dependency or as `extras_require`? Hard dep is simpler; extras keeps the install lighter. **Blocking D1.**
4. **[D2]** Same question for `playwright` (PDF export). **Blocking D2.**
5. **[E2]** Are the v2 test scenarios still valid as the validation suite, or should I draft new ones specifically targeting preserve + cascade? **Blocking E.**

**Once 1-5 are answered, I will execute Phase B → C → D → E in order, gating each phase on tests passing.**

---

## Out of scope (explicitly not in this refactor)

These came up in earlier discussions but are not in this plan:

- **MCP server wrapper** — user explicitly said "不要做 mcp"
- **SaaS / hosted version** — violates the local-file principle
- **More than 3 built-in presets** — we are not in the aesthetic competition
- **Collaborative editing** — out of scope for v0.2
- **Versioning/branching of changelog** — premature; only do if traction demands
- **Replacing GrapesJS** — works, no friction
- **A formal "spec v1.0"** — only do if a second implementation appears (per `docs/positioning-analysis.md` recommendation)
- **Mobile editor support** — desktop-first, mobile is fallback
- **Plugin marketplace integration beyond Claude Code** — Claude Code plugin already exists; broader plugin ecosystems can wait

---

## Risks specific to this refactor

| Risk | Mitigation |
|---|---|
| **Rename breaks user installs** | The current package was never published to PyPI, so the only "user" is us — no migration concerns. If we ever publish before the rename happens, we'll add a `htmlcli` meta-package that depends on `living-slides` for one version. |
| **C5 Skill rewrite makes AI worse at generation** | Test E2 will catch this; rollback by reverting the Skill file |
| **C6 trim removes templates someone uses** | Deprecation warning + one-version grace period |
| **D1 PPTX import has too many edge cases** | Mark as `--experimental` for v0.2; iterate based on user reports |
| **The whole refactor takes longer than 5 days** | Time-box: if phase C is not done in 3 days, ship just B+C (rename + structure changes) and defer D to v0.3 |
| **No actual users come even after the refactor** | Per PRD §10 "what changes if we're wrong" — drop the runtime framing, repackage as a library |

---

## Appendix: file-by-file impact map

| File | Phase | Change |
|---|---|---|
| `pyproject.toml` | B | name `living-slides`, script `slive`, description, urls |
| `src/htmlcli/` → `src/living_slides/` | B | Python package rename |
| `src/living_slides/cli.py` | B + C1-C3 + C6 | rename + 3 new commands + trim |
| `src/living_slides/differ.py` | C4 | new change types |
| `src/living_slides/server.py` | C2 | append-mode changelog |
| `src/living_slides/templates.py` | C6 | trim content templates, keep presets |
| `src/living_slides/adopters/pptx.py` | D1 | NEW |
| `src/living_slides/exporters/pdf.py` | D2 | NEW |
| `skills/htmlcli/` → `skills/living-slides/` | B | Skill directory rename |
| `skills/living-slides/SKILL.md` | C5 | full rewrite leading with preserve + cascade |
| `skills/living-slides/references/*.md` | C5 | aesthetic content moves to "Generation Guide" subsection |
| `tests/test_differ.py` | C4 | new change type tests |
| `tests/test_adopt.py` | C1 | NEW |
| `tests/test_history.py` | C2 | NEW |
| `tests/test_verify.py` | C3 | NEW |
| `tests/test_pptx.py` | D1 | NEW |
| `tests/test_pdf.py` | D2 | NEW |
| `README.md` | C7 | full rewrite |
| `CLAUDE.md` | B + C5 | update commands + workflow |
| `docs/PRD.md` | done | already updated this turn |
| `docs/refactor-plan.md` | this file | new |

Total: ~15 files modified, ~6 files created, ~1 directory renamed.

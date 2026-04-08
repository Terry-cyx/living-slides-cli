# living-slides-cli — Product Requirements Document

> **Version**: 0.2 (draft)
> **Date**: 2026-04-08
> **Status**: For internal alignment. Replaces ad-hoc positioning in README and `docs/positioning-analysis.md`.
> **Naming**: project = `living-slides-cli`, PyPI package = `living-slides`, CLI command = `slive`

---

## 1. One-line summary

> **Your slides stay. The rest catches up.**

A local CLI for hand-editing AI-generated **slide decks** where **the user is in the driver's seat**: their hand edits are sacred (AI never stomps them on the next turn), and when they touch one thing, AI cascades the change to every other slide that depends on it.

This is *not* another AI deck generator. **frontend-slides (13.1k★) already wins the *generation* phase.** This is the **iteration loop** for the *life of the deck after generation* — the part that frontend-slides, Lovable, Cursor, v0, bolt and Builder.io all leave broken or sacrifice. When you live-edit your deck across 3-5 refinement rounds, no existing tool keeps your hand edits intact while letting AI catch up to your intent. We do.

The wedge mechanism (semantic edit log + stable selectors + local files) happens to be content-agnostic — it would also work for landing pages or one-shot reports — but **slides are the only first-class use case in v0.x**. Other artifacts are out of scope until slides are nailed.

---

## 2. The pain — first-principles user-need analysis

### What the user is actually doing

The user is making a **slide deck**. To present to a board, a customer, a team, an investor, a class. The deck is a communication artifact: **the idea is the user's, the slides are just the carrier**. AI is not the author — AI is a **fast assistant** that turns drafts into visual shape and follows the user's instructions.

The user picked HTML over PowerPoint/Keynote because:
- They want it in git (versioned, diffable, branchable)
- They want it on a URL (shareable without an attachment)
- They're already in a code/AI context (Claude Code, Cursor, etc.)
- Open source AI deck generators (frontend-slides) made HTML decks look genuinely good in 2025

→ The product's job is **to keep the user in the driver's seat across the iteration rounds that follow generation**. AI is hands, not brain.

### What "in the driver's seat" decomposes into — two needs

#### Need 1 — **PRESERVE**: my hand edits are sacred

When I spend 5 minutes adjusting a card's position, picking the right number, rewriting a CEO quote — those edits represent **judgment**. AI's next refinement pass must **see that I touched these things** and **leave them alone** unless I explicitly say otherwise.

#### Need 2 — **CASCADE**: when I touch one slide, AI updates every other slide that depends on it

I change Q1 revenue from $1.2M to $1.4M on the headline metric slide. I want AI to *automatically* update across the deck:
- Slide 2: the growth-rate label (was "12% YoY", now "30% YoY")
- Slide 4: the forecast chart (Q2 projection based on Q1 trend)
- Slide 7: the CEO quote (`"...12% growth..."` → `"...30% growth..."`)
- Slide 12: the financial summary table
- Slide 18: the conclusion narrative ("we hit target" → "we exceeded target")

I do **not** want to hunt for each instance across 18 slides manually. That's the whole reason I'm using AI for a deck instead of typing in PowerPoint.

### These two needs are in structural tension

To **preserve** user edits, AI must **see** which slide elements the user touched (otherwise it can only protect everything by being told not to regenerate, or protect nothing and risk stomping). To **cascade**, AI must **be in the loop** during refinement. Every existing slide tool sacrifices one or the other:

- **frontend-slides** (13.1k★, the dominant AI HTML deck generator) sacrifices both — there's no iteration loop at all. Iteration = regenerate from scratch and lose every hand edit. The 13.1k stars buy you a great *first generation*; they don't buy you round 2.
- **Lovable** sacrifices cascade. Their engineering blog literally says *"visual edits bypass the LLM."* They protect user edits by **removing AI from the picture** during visual editing. So you can't ask AI *"now apply this card style to all 17 other slides."*
- **Cursor Browser / v0 / bolt / Aider** sacrifice preserve. Agent rereads the deck file each turn, sees no signal of which slides/elements are user-touched, regenerates aggressively, may stomp every hand tweak you made.
- **Builder.io / Plasmic** sacrifice both *and* file ownership — your deck lives in their cloud, with their schema, locked to their visual editor.
- **Pinegrow** has the human ↔ tool loop but **in the wrong direction** (AI edits HTML via tools, human reviews) — never solves "human edits, AI catches up across the rest of the deck."

**Nobody resolves the tension. We do.** The resolution is a structured changelog the user produces simply by hand-editing in the visual editor — and AI consumes that changelog on the next refinement turn, so it **knows exactly** which slide elements were user-touched (and must be preserved) **and** what they changed to (and must be cascaded across the rest of the deck).

### Why this pain is real (evidence)

- **v2 testing** (12 real PPT scenarios, 230 slides total — see `docs/test-summary-v2.md`) showed every multi-round case hit at least one of: AI can't tell which slide the user just edited; AI undoes a hand-tweak on the next refinement; AI rereads the same 2000-line deck file three rounds in a row.
- **Roo-Code GitHub issue #4723** *"Enhance LLM Context with Diff of User Manual Changes"* — open feature request in a popular code agent. Validates the same pain in a code-editing context. The fact that it's a feature *request* not a shipped feature is itself the proof.
- **Lovable's engineering blog** explicitly states they bypass the LLM for visual edits — that's a public confession that the round-trip was unsolvable for them, not a feature.
- Personal experience iterating real decks with Claude today: every meaningful refinement round either burns 30K reread tokens or risks losing a hand edit on a slide the AI shouldn't have touched. Both are observable, both are solvable.

### Who feels it

**Primary persona — "Pat the Solo Deck Maker"**

- IC role: PM, eng manager, founder, dev advocate, consultant, technical writer — anyone who has to make slides for a meeting and doesn't have a designer
- Already uses Claude Code (or Cursor / Aider) daily for code; recently started using AI for slide decks
- Generates 1-3 decks per week (QBR, sales pitch, internal review, conference talk, investor update)
- Wants the deck as a **local HTML file in git**, not a Google Slides doc or a Figma file
- Hand-edits 5-30% of every AI-generated deck before shipping (numbers, copy, layout tweaks, brand colors)
- **Trigger**: has been burned by AI stomping their hand edits at least once. Now manually re-applies edits after every AI refinement round — creating a "trust deficit" toward the iteration loop and slowly going back to PowerPoint.

**Anti-personas** (not our user)

- React/Vue **app** developers wanting to make web apps — Cursor / v0 / bolt serve them
- Designers wanting a Figma replacement for **graphic design** — Penpot / Webstudio serve them
- Enterprise teams needing a **CMS** — Builder.io / Plasmic serve them
- Users who want AI to do 100% of the deck and never touch it — Gamma / Beautiful.ai serve them (and these users don't iterate, they accept-or-redo)

---

## 3. Why existing slide-deck solutions don't solve this

Verified by direct codebase reads, vendor blog posts, and GitHub research (see `docs/positioning-analysis.md` for sources). The four columns are the four dimensions of "in the driver's seat for slide decks":

| Tool | **Preserve** hand edits | **Cascade** to other slides | Local deck file (own it) | BYO AI client | Verdict |
|---|---|---|---|---|---|
| **frontend-slides** (zarazhangrui, 13.1k★) | ❌ No diff, regen-from-scratch | ❌ Same | ✅ | ⚠️ Skill-only | Wins generation, no iteration loop. Perfect partner upstream of `slive`. |
| **frontend-slides-editable** (fork) | ❌ localStorage only | ❌ Same | ✅ | ⚠️ Skill-only | Browser edits invisible to AI; same iteration gap |
| **Lovable** | ✅ (by removing AI) | ❌ AI out of loop for visual edits | ❌ SaaS | ❌ | Solves preserve by sacrificing cascade. Also: not slide-focused |
| **Cursor Browser** (v2.2) | ❌ Reread, may stomp | ⚠️ Possible via reread | ✅ | ❌ Cursor-only | JSX-focused; no slide-specific cascade reasoning |
| **v0 / bolt.new** | ❌ Same | ⚠️ Same | ❌ WebContainer | ❌ | App-focused, not deck-focused; SaaS |
| **Builder.io Visual Copilot** | ⚠️ Proprietary | ⚠️ Proprietary | ❌ SaaS | ❌ | CMS-focused; vendor lock-in |
| **Plasmic** | ⚠️ Codegen wrapper model | ⚠️ Limited | ❌ SaaS | ❌ | React component model, not standalone HTML decks |
| **Pinegrow AI** ($99) | N/A | N/A | ✅ | ⚠️ | **Wrong direction** — AI edits, human reviews |
| **Gamma / Beautiful.ai / Tome** | N/A | N/A | ❌ SaaS | ❌ Built-in only | Closed AI deck SaaS; the deck is theirs, not yours |
| **PowerPoint Copilot** | ⚠️ | ⚠️ | ✅ (.pptx) | ❌ Built-in | Locked to MS 365; .pptx is opaque to git/AI |
| **diffDOM** (lib) | N/A | N/A | Library | N/A | Pure JSON diff, no LLM framing |
| **Yjs / Automerge** | N/A | N/A | Library | N/A | CRDT op-log for collab merging, wrong abstraction |
| **`slive`** (us) | ✅ | ✅ | ✅ | ✅ | **Only project in this row with all four checks for HTML slide decks** |

**Read this table once and the gap is obvious**: every existing AI deck tool either lives in someone's cloud, locks you to one AI client, or breaks the iteration loop — and frontend-slides (the dominant open-source AI deck generator) **doesn't try to solve iteration at all**. The gap isn't because nobody tried — it's because the dominant industry pattern ("agent rereads file each turn") makes preserve impossible by default, and slide decks are just unfashionable enough in the JSX-app-builder gold rush that nobody pointed the round-trip protocol at them.

**slive sits downstream of frontend-slides, not against it.** You generate the deck with frontend-slides (or any other AI deck generator), then run `slive adopt deck.html` to enter the iteration loop. We never compete with the generation phase.

---

## 4. The wedge — what we do that nobody else does

### The wedge in user language (one paragraph)

> You generate a slide deck with AI (frontend-slides, Claude, anything). You hand-edit some numbers, drag a card, rewrite a quote — the kind of small fixes nobody can automate because they're judgment calls. Then you ask AI to refine the rest. **`slive` watches your edits and hands the AI a 200-token changelog instead of making it reread your 2000-line deck**. AI knows which slides are your judgment calls (and leaves them alone), and uses your edits as authoritative inputs for cascading the change to every other slide that depends on them. **Your slides stay. The rest catches up.**

### The wedge in mechanism (how it works under the hood)

This section is the **implementation** of the wedge above, not the wedge itself. Three small interlocking pieces:

1. **A semantic edit log emitted on every save** — `<deck>.changelog.json` records `text_edit` / `attribute_change` / `element_added` / `element_removed` / `element_moved` / `slides_reordered`, plus a one-line `summary`. Typical batch ≤500 tokens for an editing session. This is what AI reads instead of rereading the whole deck. *Required for both preserve (AI sees what's user-touched) and cascade (AI knows what changed).*

2. **Stable opaque selectors via `data-oid`** — the differ recognizes a `data-oid="<stable-id>"` attribute as the canonical selector for any slide element. AI emits these on initial generation; `slive adopt` retrofits them into any existing deck (including frontend-slides output). The result: changelog selectors survive wraps / moves / reorders / class changes — exactly the operations users perform when iterating slides. *Required for preserve to be reliable across rounds, not just within a round.*

3. **Append-mode changelog history** — `<deck>.changelog.history.jsonl` accumulates every save's diff across rounds, so AI sees not just *this* edit but the *full chain of slide elements the human has ever touched* and never accidentally regenerates one. *Required for preserve to compound across multi-round iteration — single-round preservation isn't enough if round 3 stomps round 1's edit.*

These three are useless individually:
- The schema alone is just JSON — meaningless without stable selectors and a delivery channel.
- `data-oid` alone is just a convention — meaningless if no differ consumes it.
- A local CLI alone is just a wrapper — meaningless if it doesn't emit something AI can use.

**The defensible product is the intersection of all three, in service of preserve + cascade for HTML slide decks.** Anyone can clone any single piece. Composing them in this specific shape, for this specific use case, in a local CLI form-factor with no SaaS dependency and no JSX assumption, is what nobody else does.

### Pairing with upstream generators

`slive` is intentionally complementary to existing AI deck generators, not a replacement:

```
   frontend-slides   →   slive adopt   →   slive open + edit   →   AI refine   →   slive open + edit   →   ...
   (or any AI       )    (retrofits        (visual editing         (reads tiny       (next round)
    deck generator  )     data-oid)        with diff tracking)     changelog)
```

The user generates with whatever produces the prettiest first draft. The user iterates with `slive` because nothing else makes round 2-N painless on a standalone HTML deck. **The 13.1k stars on frontend-slides become free upstream traffic for us, not competition.**

---

## 5. Why CLI (and not MCP, not SaaS, not a library)

This section exists because the alternatives are tempting and we are explicitly rejecting them.

- **Why not MCP?** MCP is a transport for *agent ↔ tool* communication. Our user is **a human running a CLI**, not an agent calling a tool. The user wants to type `slive create deck.html`, hand-edit it in their browser, then say to Claude *"refine this"* — and the value is delivered the moment Claude reads the file off disk. MCP would add an installation step (run an MCP server, configure the agent, debug the JSON-RPC), produce no extra value over "Claude reads `deck.html` + `deck.changelog.json` directly," and would fragment the install story across MCP-supporting clients. **MCP is the right choice when the agent needs live, stateful access to a system — we don't need that.** A future MCP wrapper is a 100-line shim if traction demands it; we will not build it preemptively.

- **Why not SaaS?** Our user explicitly does *not* want their HTML in someone else's cloud — that's the whole point of choosing standalone HTML over Builder.io. SaaS would also require a subscription model that contradicts the "indie operator" persona.

- **Why not a pure library?** A library forces every consumer to wire up the editor server, the differ, the file IO. The CLI bundles all of that into `slive open` so the user does one command. The differ *is* importable as `from slive.differ import compute_changelog` for power users.

- **Why not a Claude Code Skill only?** We already ship a Skill (`skills/slive/SKILL.md`). But Skills are Claude-Code-specific. The CLI works with **any AI client** — Cursor, Aider, plain Claude.ai with copy-paste, even no AI at all (just visual editing with diff tracking for git PRs). The Skill is *one* consumer of the CLI; the CLI itself is the product.

---

## 6. Success metrics (how we know the wedge is real)

### Leading indicators (first 3 months of public release)

- **Reread reduction**: in any AI iteration session that uses slive's changelog, measure tokens-spent-on-reread vs. a baseline session that doesn't use it. Target: **≥80% reduction** for typical 5-edit iteration rounds on a 2000-line deck. (Measurable by instrumenting the Skill.)
- **Edit preservation rate**: in a 3-round iteration session, what fraction of the user's hand-edits survive AI's next refinement? Target: **≥95%**. Today (without changelog), the v2 tests showed it's around 60-80% — AI accidentally undoes things.
- **`data-oid` stability**: when a user moves an element to a new parent, the changelog still references it correctly. Target: **100%** for any element that carries `data-oid`. (Already verified by `test_data_oid_survives_dom_path_change` in tests.)

### Lagging indicators (first 6-12 months)

- **Adoption signal**: any non-slive project starts emitting `*.changelog.json` alongside its HTML output. (frontend-slides plugin? a Cursor extension? a hand-rolled script?)
- **Inbound mention**: someone files a Cursor / Aider / Roo-Code issue saying *"can you read slive changelog format?"*
- **Iteration depth**: ≥30% of users go past round 3 in a single deck (proves they're actually iterating, not just generating-and-shipping). The whole product exists for round 2+; round-1 metrics are noise.

### Anti-metrics (things we explicitly do *not* optimize)

- Number of built-in style presets (we are not competing with frontend-slides on aesthetics).
- Stars on GitHub (vanity).
- Pageviews on a marketing site (we don't have one and don't plan to).

---

## 7. MVP scope — what's in v0.2

Already shipped (v0.1): create / open / diff / templates / presets (3) / asset gen-chart / asset import / `data-oid`-aware differ / 70 passing tests.

**v0.2 additions** — exactly the gaps the wedge demands:

| Item | Why | Effort |
|---|---|---|
| `slive adopt <file>` | Retrofits `data-oid` onto an existing HTML file (frontend-slides output, hand-written deck, anything). **Critical for adoption**: lets people enter the loop without regenerating from scratch. | ~200 LOC + tests |
| `slive serve <file>` (alias for `open`, but no auto-launch) | Server-only mode for CI / containers / remote workflows | ~20 LOC |
| `docs/edit-log-schema.md` | Document the JSON schema with version `v0.1`, field semantics, examples. **Not** marketed as a standard — just documented so others can implement it if they want. | docs only |
| Append-mode changelog | Currently `.changelog.json` is overwritten on every save (P1 issue from v2 testing). Add `.changelog.history.jsonl` that appends every save's diff so AI sees cumulative history across rounds. | ~50 LOC + tests |
| `slive verify <file>` | Checks every `<img>` reference resolves to a real file in `<file>-assets/`. Fixes another P1 from v2 testing. | ~80 LOC |
| Skill update | Update `skills/slive/SKILL.md` to teach Claude to (a) emit `data-oid` on generation, (b) read both `.changelog.json` *and* `.changelog.history.jsonl` on refinement, (c) preserve any element bearing a `data-oid` that the user has touched. | docs only |
| README repositioning | First sentence becomes: *"`slive` — the iteration loop for AI-generated HTML slide decks. Your slides stay. The rest catches up."* | docs only |

**Out of scope for v0.2** (deferred until evidence of demand):

- MCP server wrapper
- PDF export (just use `playwright` from a script)
- PPTX import
- Hosted version
- Collaborative editing
- More than 3 built-in presets (the rest live as references for AI to generate)
- A standalone in-browser editor (we ride GrapesJS)
- Versioning / branching of the changelog
- A formal protocol versioning policy (only do this if a second implementation appears)

---

## 8. Non-goals (explicit anti-scope)

1. **We are not building another deck generator.** frontend-slides is better at that. Our only template/preset library exists so `slive create` produces *something* runnable; aesthetic depth is a borrowed asset (see Acknowledgements in README).
2. **We are not building a visual editor.** GrapesJS exists. We compose it.
3. **We are not building a SaaS.** No accounts, no cloud, no telemetry. Ever.
4. **We are not building a JSX/React tool.** That market is crowded and well-funded. Standalone HTML is our lane.
5. **We are not publishing a "standard" or asking for IETF buy-in.** The schema is documented; that's enough until adoption demands more.
6. **We are not a Claude-Code-only tool.** The CLI works with any AI client or none.
7. **We do not optimize for first-time-pretty.** We optimize for *the second, third, and fourth* iteration on the same file.

---

## 9. Risks & open questions

### Risks

- **R1 — "Reread is cheap enough."** With 200K context windows, the industry has voted that AI can just reread the file each turn. If most users feel iteration is fast enough today, our wedge has no urgency. **Mitigation**: lead messaging with edit *preservation* (R2-style), not token cost, since preservation is a quality issue not a perf issue.
- **R2 — Hand-edits get stomped anyway.** Even with a perfect changelog, the AI may regenerate too aggressively on the next pass and undo user tweaks. **Mitigation**: Skill instructions explicitly mark `data-oid`-bearing elements that appear in the changelog as "user-touched, do not regenerate without an explicit reason."
- **R3 — Adoption asymmetry.** slive depends on AI generators emitting `data-oid` on initial generation. If they don't, our differ falls back to fragile CSS paths. **Mitigation**: `slive adopt` retrofits `data-oid` automatically; the Skill teaches Claude to emit it; we document the convention so other generators can adopt it.
- **R4 — Standalone HTML is a small market.** Maybe the world really has decided everything is React. **Mitigation**: slide decks alone (the proven first reference app) is a non-trivial market — every PM, EM, dev advocate, founder generates them. If the loop works for slides, it works for landing pages and reports trivially.
- **R5 — Discoverability.** A CLI on PyPI without a marketing site is hard to find. **Mitigation**: ship as Claude Code Plugin (already done); cross-link from the v2 test write-up; engage Roo-Code issue #4723 thread once v0.2 lands.

### Open questions

- **Q1**: Should `data-oid` be auto-generated by `slive adopt` based on element role/text hash, or should it require explicit author intent? Auto-gen has higher adoption but lower stability across regenerations. **Decision needed before v0.2**.
- **Q2**: When the changelog is empty (user opened the editor and saved without changes), should we still write `.changelog.json` (with empty `changes: []`) or skip it? Affects whether downstream tooling can rely on the file existing. **Tentative**: write empty file; explicit absence is harder to handle than empty content.
- **Q3**: How do we present the changelog history file (`.changelog.history.jsonl`) to AI without ballooning the prompt? Probably "always include latest entry, optionally summarize older entries on demand." **Decide during Skill update**.
- **Q4**: Do we ever want a `slive watch` mode that emits a changelog every N seconds without explicit save? Conflicts with our "save = commit a coherent edit" model. **Default: no**, revisit if users ask.

---

## 10. What success looks like in 12 months

A developer somewhere sits down, generates a 20-page sales deck with Claude, hand-edits the pricing table, drags two cards, renames a section, and types *"refine this for an enterprise audience"* — and the AI receives a 300-token changelog instead of a 35K-token reread, preserves every hand edit, regenerates only the pieces that need to change, and the user never thinks about it again.

That's the only thing that matters. Everything in this PRD is in service of that one moment.

---

## Appendix A — research provenance

- `docs/positioning-analysis.md` — original frontend-slides comparison (12-test analysis)
- `docs/test-summary-v2.md` — 12 real PPT scenario tests, 9 issues identified, exact pain points sourced from real iteration rounds
- Web research (2026-04-07): Lovable engineering blog, Cursor 2.2 release notes, Builder.io Visual Copilot 2 announcement, Plasmic codegen docs, Pinegrow AI docs, bolt.new GitHub, Webstudio docs, Block Protocol spec, MCP servers index, Roo-Code issue #4723, diffDOM README, Yjs forum streaming-AI thread, ProseMirror reference, "Can It Edit?" arXiv 2312.12450

## Appendix B — what changes if we're wrong

If after 6 months of v0.2 in the wild, none of the leading indicators move, the honest pivot is:

1. Drop the "iteration runtime" framing.
2. Keep the differ + data-oid contract as a *library* (not a CLI).
3. Repackage the slide presets / asset pipeline as a standalone "AI deck quality kit" plugin for Claude Code.
4. Walk away from the protocol ambition.

Time-box the experiment. Don't fall in love with the architecture.

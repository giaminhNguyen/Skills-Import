---
name: ainovel
description: End-to-end, API-free long-form novel creation workflow for agent CLIs. Use when the user asks to start, continue, review, steer, import, synchronize, diagnose, co-create, style-simulate, reopen, or export a novel using the ainovel workflow. Reproduce ainovel-cli's Architect/Writer/Editor/Arbiter roles, two-level rolling planning, four-stage context compression, seven-dimension editorial review, arc/volume summaries, step-level checkpoints, resume, review mode, and 14 command intents. Never configure or call an LLM provider; use the host agent's own model and native read/write/bash tools.
---

# Ainovel Agent Skill

Use the host agent as the creative model. Treat this package as an orchestration protocol plus deterministic file utilities. Never call an LLM API, request an API key, configure a provider, start Ollama, or create fallback provider logic.

## Core invariants

1. Keep deterministic routing/state on disk; keep creative and semantic decisions in the host model.
2. Treat committed files as source of truth. Never rely on chat memory when state exists on disk.
3. After every successful logical step, append a checkpoint immediately.
4. Never skip `plan -> draft -> consistency -> commit -> review` for a new chapter.
5. Preserve the two planning horizons: stable Compass + detailed current Arc. Do not pre-plan hundreds of chapters in detail.
6. Preserve four context stages: ToolResultMicrocompact -> LightTrim -> StoreSummaryCompact -> FullSummary.
7. Preserve all seven Editor dimensions with quoted evidence from the chapter.
8. Apply user directives and Steer decisions to every subsequent relevant role.
9. Do not overwrite canon or committed chapters silently. Route changes through Steer, rewrite, import/sync, or reopen workflows.
10. Prefer Python standard-library scripts in `scripts/` for deterministic operations; do not add network dependencies.

## Locate paths

Set `SKILL_ROOT` to the directory containing this `SKILL.md`.

Default runtime layout is `./novels/<slug>/output/novel/`. The initializer also writes `./.ainovel/active_project`, so deterministic scripts can resolve the active project when `--project` is omitted.

Use:

```bash
python3 "$SKILL_ROOT/scripts/state.py" status
python3 "$SKILL_ROOT/scripts/context_pack.py" build
```

On Windows, use `python` if `python3` is unavailable.

## Intent routing

Interpret either conversational requests or `ainovel ...` text as commands. Preserve the original 14 slash-command intents:

| Original | Agent-native intent |
|---|---|
| `/help` | `ainovel help` — show workflow and commands |
| `/model [role]` | `ainovel model [role]` — report that model choice belongs to the host CLI; never configure providers |
| `/config` | `ainovel config` — edit writing/runtime settings only, never provider/API settings |
| `/diag` | `ainovel diag` — run deterministic statistics/validation, then semantically diagnose four areas |
| `/review [on\|off]` | `ainovel review [on\|off]` — gate after each accepted chapter |
| `/next` | `ainovel next` — grant one new-chapter permit while review mode is on |
| `/start <file>` | `ainovel start <file>` — use the file as initial requirements, not completed chapters |
| `/import <file>` | `ainovel import <file>` — import completed prose and continue it |
| `/reopen <direction>` | `ainovel reopen <direction>` — extend a completed book with a new volume/season |
| `/cocreate` | `ainovel cocreate` — pause and collaboratively refine the next directive |
| `/simulate` | `ainovel simulate` — analyze local style samples into a style profile |
| `/importsim <file>` | `ainovel importsim <file>` — import a style-profile JSON |
| `/sync` | `ainovel sync [--check]` — detect manual chapter edits by SHA-256; rebuild semantic state before accepting hashes |
| `/export` | `ainovel export [path] [from=N] [to=N] [--overwrite] [--flow]` — TXT or EPUB3; `--flow` (TXT only) yields one continuous file with no chapter/volume headings, e.g. for TTS pipelines like `gen-audio-queue` |

Also accept `ainovel steer "..."` as an adapter command. In the original TUI, Steer is plain text input rather than one of the 14 slash commands; preserve that behavior by treating non-command creative interventions during an active run as Steer.

Read `references/commands.md` when handling any command other than the ordinary write loop.

## Start or resume decision tree

1. If the user supplies a new idea and no active project exists, initialize a project, then run foundation planning.
2. If an active project exists and is incomplete, run `state.py resume` and continue exactly from the recorded next step.
3. If the user asks to import existing prose, follow `references/workflow.md#import`.
4. If the project is completed and the user wants more story, run Reopen.
5. If a pending Steer or rewrite exists, process it at the next safe boundary before planning a new chapter.
6. In review mode, do not begin a new chapter without a permit; rewrites of the current/previous chapter do not consume a new-chapter permit.

## New-project workflow

### 1. Initialize deterministic state

Run:

```bash
python3 "$SKILL_ROOT/scripts/state.py" init --idea "<user idea>" --workspace .
```

Capture the returned `project` path. If the user requested a fixed slug or target chapters, pass those options.

### 2. Arbiter startup triage

Read `prompts/arbiter-start.md`. Decide whether the request is sufficiently specified for direct Architect planning or whether a short co-create pass is materially useful. Do not block on optional clarifications; infer reasonable defaults and record assumptions when the request is clear enough.

### 3. Architect foundation

Read `prompts/architect-foundation.md`, plus any files under project/local rules directories. Create and atomically save:

- `book.md` and `meta/book.json`
- `premise.md`
- `meta/compass.json`
- `layered_outline.json`: initial two-volume skeleton for long work; current arc detailed
- `outline.json`: detailed chapters only for the current arc/horizon
- `characters.json`
- `world_rules.json`
- `meta/foreshadow.json`
- `meta/relationships.json`

Checkpoint `foundation_saved` with next step `plan`.

### 4. Chapter loop

For chapter N, always do the following:

1. Build the restore/context pack with `context_pack.py build --chapter N`.
2. Read `prompts/writer-chapter.md` and the generated context pack.
3. **Plan**: write `drafts/NNN.plan.json`; checkpoint `chapter_planned`, next `draft`.
4. **Draft**: write `drafts/NNN.md`; checkpoint `chapter_drafted`, next `consistency`.
5. **Consistency**: compare draft to world rules, character/canon state, plan contract, foreshadow, relationships and recent history; save `drafts/NNN.consistency.json`; checkpoint `consistency_checked`, next `commit`.
6. If consistency fails materially, revise the draft and repeat consistency. Do not commit known contradictions.
7. **Commit**: atomically write `chapters/NNN.md`; update timeline/state facts and SHA-256 ledger; checkpoint `chapter_committed`, next `review`.
8. **Editor review**: read `prompts/editor-review.md`; save `reviews/NNN.json` with all seven dimensions, issues/evidence, contract status, and proposed verdict. Run `review_gate.py --apply`; it validates the review, derives `affected_chapters`, maps the Editor verdict to flow, and queues repairs. Route on the Editor `verdict`. Checkpoint `chapter_reviewed` only after an `accept` verdict or the required polish/rewrite loop completes.
9. If verdict is `rewrite` or `polish`, use `prompts/writer-rewrite.md`, repeat consistency, commit, and review. Bound retries by project config; if deadlocked, use `prompts/arbiter-deadlock.md`.
10. Save a compact chapter summary and state delta. If an arc/volume boundary is reached, run the summary/expansion workflow before the next chapter.
11. If review mode is on, pause after the chapter until `ainovel next` grants one permit.

Read `references/review-rubric.md` before producing or interpreting Editor reviews.

## Rolling planning

Use two levels, never a flat full-book detailed outline:

- **Compass**: ending direction, non-negotiable promises, long-horizon character destinations, volume-scale milestones. Change only through Architect after new evidence or explicit Steer.
- **Rolling horizon**: detailed current arc chapter beats/contracts plus only a coarse next-volume/next-arc skeleton.

Initially create a two-volume skeleton for long works and fully detail Arc 1 only. Near or at the end of an arc:

1. Editor runs an aggregate seven-dimension review with `scope=arc` over the accepted chapters in that arc. Save it as `reviews/arc-vXX-aYY.json` and run `review_gate.py --apply`. Repair affected chapters first if the Editor verdict is not `accept`.
2. After the arc review is accepted, Editor writes `summaries/arc-vXX-aYY.json` and refreshes character/style snapshots.
3. Architect reads actual arc outcomes, Compass, unresolved foreshadow and user directives.
4. Architect expands only the next arc into detailed chapter plans and updates `outline.json`/`layered_outline.json`.
5. Checkpoint `arc_reviewed`, `arc_summarized`, then `arc_expanded`.

At a volume boundary, Editor writes a volume summary after the accepted arc review, then Architect creates/expands the next volume and may update the Compass without violating committed canon. For a non-layered imported project, use the same review schema with `scope=global` at configured/meaningful review intervals before aggregate refresh.

Read `prompts/editor-summary.md` and `prompts/architect-expand.md` at these boundaries.

## Context discipline

Read `references/context.md` before long runs. Apply the levels in order:

1. **ToolResultMicrocompact**: keep terminal output terse; write detailed results to files; do not paste large tool dumps into chat.
2. **LightTrim**: read only the current plan/draft, exact state files, recent chapter window, and referenced older facts.
3. **StoreSummaryCompact**: run `context_pack.py build`; prefer summaries and structured canon over old raw prose.
4. **FullSummary**: if the working set is still too large, read `prompts/full-summary.md` and write `meta/context/full-summary.md`; then rebuild the restore pack. This is performed by the host model, not a script/API.

After compaction or resume, rebuild a restore pack before any Writer/Editor call.

## Checkpoint and recovery

Call `state.py checkpoint` immediately after each successful logical step. Store artifact paths and the intended next step. Checkpoints are append-only JSONL; `progress.json` is a current snapshot.

On interruption, run:

```bash
python3 "$SKILL_ROOT/scripts/state.py" resume
```

Trust disk state over conversational recollection. If the latest checkpoint says a draft exists and next is `consistency`, do not regenerate the draft. If artifact existence and checkpoint disagree, run `validate_project.py` and choose the safest non-destructive step.

Read `references/checkpoint.md` for the recovery table.

## Steer

When the user intervenes during a run:

1. Append the request with `state.py steer-add` before interpreting it.
2. Read `prompts/arbiter-steer.md` and classify it as continue, durable directive, plan change, canon/foundation change, rewrite, or completion-control.
3. Save the Arbiter decision in `meta/arbiter/` and checkpoint `steer_triaged`.
4. Persist long-term instructions in `meta/user_directives.json`.
5. For plan/canon changes, dispatch Architect; for chapter rewrite, queue Writer+Editor; for simple continue, resume without modification.
6. Never erase incompatible committed facts silently; explicitly reconcile or queue rewrite work.

## Review mode and co-create

- `ainovel review on`: pause after each accepted chapter. Require `ainovel next` for one new chapter.
- `ainovel cocreate`: set status paused, read `prompts/co-create.md`, collaboratively refine the next creative directive, persist it, then return to deterministic routing.
- When co-create can proceed with useful defaults, offer concise options rather than interrogating the user.

## Import, manual sync, style simulation, reopen, diagnostics and export

Read `references/commands.md` and use the corresponding deterministic scripts:

- `import_split.py`: chapter segmentation only; use `prompts/import-analyze.md` for semantic extraction.
- `sync_scan.py`: SHA-256 change detection; after semantic rebuild, run with `--accept`.
- `prompts/simulate-style.md`: generate `meta/style_rules.json` from local samples; `importsim` validates/copies JSON.
- `prompts/reopen.md`: create a continuation volume without rewriting the completed ending unless explicitly requested.
- `stats.py` + `validate_project.py`: deterministic evidence for `/diag`; then diagnose progress, quality, planning, context.
- `export_novel.py`: TXT and EPUB3; no network or external package required. TXT supports `--flow` for a single headerless continuous-prose file (see `references/commands.md`).

## File-writing rules

- Use UTF-8.
- Use zero-padded chapter filenames: `001.md`, `002.md`, ...
- Use atomic write/replace for JSON and committed prose whenever practical.
- Never edit `checkpoints.jsonl` retroactively.
- Keep raw chapter prose in `chapters/`; keep compressed state in JSON summaries/metadata.
- Keep user-authored rules under project `rules/` or workspace `.ainovel/rules/`; load both when present.
- Do not store provider names, API keys, model IDs, base URLs, or secrets anywhere in the novel state.

## References to load only as needed

- End-to-end routing and boundary cases: `references/workflow.md`
- Exact command semantics: `references/commands.md`
- Context strategy and restore-pack contract: `references/context.md`
- Seven-dimension review schema and gate: `references/review-rubric.md`
- Runtime state schema: `references/state-schema.md`
- Recovery rules: `references/checkpoint.md`
- Source-workflow analysis and deliberate agent-native adaptations: `references/repo-analysis.md`
- Package tree and purpose of every bundled file: `references/package-guide.md`
- Installation for Claude Code/Codex: `references/install.md`
- Test plan: `references/testing.md`

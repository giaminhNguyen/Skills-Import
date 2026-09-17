# ainovel-cli workflow analysis and adaptation notes

## Scope

This skill re-implements the creative workflow of `kentjuno/ainovel-cli` as a host-agent-native protocol. It is intentionally not a port of the provider/runtime layer.

Primary repository studied:
- https://github.com/kentjuno/ainovel-cli

Upstream architecture cross-check:
- https://github.com/voocel/ainovel-cli
- https://deepwiki.com/voocel/ainovel-cli/2.4-context-management
- https://deepwiki.com/voocel/ainovel-cli/4.3-review-and-summary-tools

The Vietnamese fork identifies itself as synchronized with the upstream multi-agent architecture. Source-level contracts that are not repeated verbatim in the fork README are therefore cross-checked against the upstream implementation/index. This package does not copy provider/client code or long source prompts; it preserves workflow semantics in independently authored prompts and scripts.

## Extracted pipeline

The system separates deterministic orchestration from semantic generation:

1. Host/Engine reads the Store and chooses the next factual route.
2. Arbiter is invoked only for semantic decisions such as startup planner selection, Steer triage, and deadlock escape.
3. Architect creates book metadata, premise, characters, world rules, Compass and rolling outline.
4. Writer runs chapter plan -> draft -> consistency -> commit.
5. Editor performs seven-dimension review and creates arc/volume summaries.
6. At arc/volume boundaries Architect expands only the next planning horizon based on actual committed events.
7. Every successful tool-equivalent step appends a checkpoint so resume is step-exact.

## Roles and their original tool contracts

- Arbiter: semantic arbitration; no persistent creative loop/tool set.
- Architect: novel context, save book metadata, save foundation/outline.
- Writer: novel context, read chapter, plan chapter, draft chapter, consistency check, commit chapter.
- Editor: novel context, read chapter, save review, save arc summary, save volume summary.

In this skill, native file read/write/bash replaces the tool names. The logical boundaries remain identical so checkpoint semantics are preserved.

## Rolling planning

The fork documents Compass + rolling horizon planning. For a long work the initial plan creates a coarse two-volume skeleton and fully details only Arc 1. Near/at an arc ending, Editor summarizes actual outcomes and character state, then Architect expands the next arc. Volume completion similarly produces a volume summary before extending the next volume and updating the Compass.

This is not equivalent to pre-generating all chapter outlines. Detailed chapter contracts should exist only inside the active rolling horizon.

## Context management

The fork names four compaction stages:

1. ToolResultMicrocompact
2. LightTrim
3. StoreSummaryCompact
4. FullSummary

The upstream source additionally exposes the memory model behind those stages: recent raw tail, synthesized context summary, structured Store artifacts, and restore packs. A Writer restore pack contains the active chapter plan plus world/cast/style anchors. Upstream compaction triggers around 85% of the context window with an 8k-token minimum reserve; because a CLI skill cannot reliably inspect every host model's exact context window, this package uses an explicit context-pack character budget and file-first discipline while preserving the same four-stage order.

FullSummary is the only compression stage that semantically summarizes discarded narrative context. Here it is performed by the host agent using `prompts/full-summary.md`; no script calls a model.

## Seven-dimensional Editor review

Every chapter review covers:

- consistency
- character behavior
- pacing
- narrative flow / continuity
- foreshadowing
- hook
- aesthetic quality

Aesthetic quality includes descriptive texture, narrative technique, dialogue differentiation, diction, and emotional impact. Each review must be evidence-based. In the current source, the dimension list is extensible and scores are validated as 0-100, but the runtime explicitly does not use old score thresholds to override literary judgment. Editor chooses `accept|polish|rewrite`; each issue carries `chapters` and `requires_change`, and `affected_chapters` is derived from the issues that require immediate repair. The skill requires the documented seven base dimensions while allowing extra dimensions and mirrors this persistence/control contract in `review_gate.py`.

## Review cadence and aggregate boundaries

The fork README describes the Editor as reviewing chapters with the seven dimensions. The current router/commit source adds an important aggregate rule for layered planning: at an arc boundary it routes to an arc-scope review before saving the arc summary, then volume summary, then Architect expansion/new-volume work. Non-layered mode can use periodic global review. This skill keeps chapter-level review as a strong local QA/checkpoint and also performs the source-level aggregate arc review before durable arc/volume summarization, preserving both the documented chapter review behavior and the boundary gate in current source.

## Arc/volume summaries and directives

Arc summaries retain character snapshots and distilled prose/dialogue rules. The source writes the summary after related snapshot/style updates so the summary can serve as the aggregate completion marker. Volume summaries provide lower-granularity memory. Durable user directives are persisted and re-injected into later role context. `check_consistency` conceptually aggregates world rules, foreshadow state, relationships and recent summaries.

## Checkpoint/resume

The fork records a checkpoint after every successful tool action in `meta/checkpoints.jsonl` and restores by reading both `progress.json` and the latest checkpoint. Resume must continue at the next step, e.g. a completed chapter draft resumes at consistency rather than drafting again.

## Commands preserved

Fourteen original slash commands are preserved as intents:

`help`, `model`, `config`, `diag`, `review`, `next`, `start`, `import`, `reopen`, `cocreate`, `simulate`, `importsim`, `sync`, `export`.

Steer is deliberately separate because the original UI accepts it as ordinary text during writing. The adapter alias `ainovel steer` exists for CLI ergonomics but does not alter the count.

## Command behaviors that matter

- `start <file>` treats the file as requirements/outline input, not as completed chapters.
- `import <file>` segments completed prose, extracts characters/world/events and builds a continuation-ready outline.
- `sync` detects manual chapter edits with SHA-256 and rebuilds affected semantic state before accepting new hashes.
- `simulate` derives a style profile from local prose samples.
- `reopen` extends a completed work with a new volume/season.
- `review on` pauses after each accepted chapter and `/next` releases one next chapter.
- `export` supports TXT/EPUB and chapter ranges.

## Output/state mapping

The fork documents `book.md`, `chapters/`, `drafts/`, `reviews/`, `summaries/`, `timeline.jsonl`, `premise.md`, `outline.json`, `layered_outline.json`, `characters.json`, `world_rules.json`, and `meta/` containing book, compass, progress, foreshadow and checkpoints. This skill keeps those paths and adds small deterministic ledgers (`chapter_hashes.json`, queues, context packs) required to replace the original Go host safely.

## Deliberately removed runtime concerns

The following are *not* part of this skill:

- provider selection or credentials
- API clients
- LiteLLM/provider adapters
- Ollama startup/fallback
- model IDs/base URLs
- network retries/rate limits

`ainovel model` therefore reports/defers to the host CLI's own model-selection mechanism. `ainovel config` changes writing and workflow settings only.

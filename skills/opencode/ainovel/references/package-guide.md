# Package guide

## Purpose

This file is the inventory for maintainers. `SKILL.md` is the control plane; load the files below only when their stage is active.

## Entrypoints and adapters

- `SKILL.md` — agent-visible workflow, invariants, role routing, command table, checkpoint/context rules.
- `agents/openai.yaml` — UI metadata required by the generic skill package format.
- `adapters/claude/commands/ainovel.md` — optional Claude Code command adapter; copy/link into `.claude/commands/` when command-file dispatch is desired.
- `adapters/codex/AGENTS.md` — optional Codex project instructions that point Codex to the installed Ainovel skill.

## Role and phase prompts

- `prompts/arbiter-start.md` — startup triage and assumption handling.
- `prompts/arbiter-steer.md` — classify mid-run intervention and choose role/state impact.
- `prompts/arbiter-deadlock.md` — break repeated review/rewrite loops.
- `prompts/architect-foundation.md` — premise, cast/world canon, Compass, layered outline, first rolling horizon.
- `prompts/architect-expand.md` — expand only the next arc/volume from actual outcomes.
- `prompts/writer-chapter.md` — plan/draft/consistency/commit contract for ordinary chapters.
- `prompts/writer-rewrite.md` — localized polish or structural rewrite while preserving accepted canon.
- `prompts/editor-review.md` — exact seven-dimension evidence-based review object and semantic proposed verdict.
- `prompts/editor-summary.md` — accepted arc/volume summary + snapshots/style handoff.
- `prompts/co-create.md` — collaborative user intervention converted into durable directives.
- `prompts/full-summary.md` — host-model semantic compaction; never executed by a script.
- `prompts/import-analyze.md` — reconstruct continuation state from imported completed prose.
- `prompts/simulate-style.md` — abstract style from samples without copying sample text.
- `prompts/sync-reextract.md` — re-extract state after manual edits.
- `prompts/reopen.md` — continue a completed work as a new volume/season.

## Templates

- `templates/project-config.json`, `progress.json` — runtime and workflow defaults; no provider fields.
- `templates/book.json`, `compass.json` — stable long-horizon metadata.
- `templates/layered_outline.json`, `outline.json`, `chapter-plan.json` — two-level rolling plan.
- `templates/characters.json`, `world-rules.json`, `foreshadow.json`, `relationships.json` — durable canon ledgers.
- `templates/consistency.json` — Writer pre-commit contradiction check.
- `templates/review.json` — seven-dimensional Editor review and gate output fields.
- `templates/chapter-summary.json`, `arc-summary.json`, `volume-summary.json` — multi-scale narrative memory.
- `templates/style-rules.json`, `user-directives.json` — durable style and user intent.
- `templates/steer-queue.json`, `rewrite-queue.json` — interruption and repair queues.
- `templates/checkpoint.example.json` — append-only checkpoint contract example.

## Deterministic scripts

All scripts use Python standard library only and make no network/model/API calls.

- `scripts/_common.py` — atomic I/O, active-project resolution, hashing, file helpers.
- `scripts/state.py` — init/status/config, checkpoint/resume, review permits, queues/directives, chapter hashing, completion.
- `scripts/context_pack.py` — select and trim disk state into a bounded restore pack; does not semantically summarize prose.
- `scripts/review_gate.py` — validate review schema/chapter ranges, derive affected chapters from issue facts, and manage repair queue/flow without overriding Editor verdicts.
- `scripts/sync_scan.py` — detect/accept manual chapter edits using SHA-256.
- `scripts/import_split.py` — deterministic chapter segmentation only.
- `scripts/export_novel.py` — TXT/EPUB3 export with ranges, stable EPUB identifier, no external library.
- `scripts/stats.py` — chapter/review/state statistics for diagnostics.
- `scripts/style_profile.py` — validate/import a style-profile JSON; semantic style extraction remains the agent's job.
- `scripts/validate_project.py` — structural/state/hash/checkpoint validation.
- `scripts/smoke_test.py` — temp-project deterministic integration test.

## References

- `references/repo-analysis.md` — source-to-skill analysis and deliberate runtime removals.
- `references/workflow.md` — full router/state machine, boundaries and special flows.
- `references/context.md` — four-stage context compression and restore-pack contract.
- `references/review-rubric.md` — seven required base dimensions, issue/affected-chapter contract and semantic verdict rules.
- `references/state-schema.md` — canonical project tree and state objects.
- `references/checkpoint.md` — recovery table and non-destructive resume rules.
- `references/commands.md` — 14 command semantics + Steer alias.
- `references/install.md` — Claude Code/Codex installation and invocation.
- `references/testing.md` — 3–5 chapter acceptance test and deterministic smoke test.
- `references/package-guide.md` — this inventory.

## Sample state

- `state/README.md` — explains that real runtime state lives in each novel project, not inside the installed skill.
- `state/example-project/` — minimal schema illustration only; never use it as live project state.

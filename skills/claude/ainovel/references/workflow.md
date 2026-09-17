# Workflow reference

## Table of contents

1. Deterministic router
2. Foundation
3. Chapter state machine
4. Arc and volume boundaries
5. Rewrite and deadlock
6. Import
7. Sync
8. Reopen
9. Completion

## 1. Deterministic router

At the start of every agent turn that may advance the novel:

1. Resolve the active project.
2. Run `state.py resume` and inspect pending queues.
3. If there is an unresolved Steer item, triage it before new creative work.
4. If there is a rewrite/polish item, complete it before a new chapter unless the Arbiter explicitly records why postponing is safe.
5. If `review_mode=true` and no permit exists, stop at the review gate.
6. Route by `current_step`; do not infer a different step from conversational memory.

The state machine is intentionally boring. Creative judgment belongs inside role prompts; routing belongs here.

## 2. Foundation

Architect output must establish enough canon to write Arc 1 without over-planning the whole book:

- book title and logline/summary
- premise, genre, tone, point of view, target length
- character ledger with stable IDs, goals, fears, relationships and starting state
- world rules with stable IDs and hard/soft constraints
- Compass with ending direction, major promises and non-negotiables
- layered outline with coarse volume/arc skeleton
- detailed current arc chapter beats/contracts
- initial foreshadow ledger and relationship graph

For a short 3-5 chapter test, use one volume/one arc but still keep Compass and layered outline structures.

## 3. Chapter state machine

### Plan

Write `drafts/NNN.plan.json` with:

- chapter purpose
- opening state
- required beats
- chapter contract: must happen / must not happen
- viewpoint and time/place
- character state deltas intended
- foreshadow setup/payoff IDs
- continuity anchors from recent and relevant old chapters
- ending hook
- target prose constraints

Checkpoint `chapter_planned`, next `draft`.

### Draft

Write prose to `drafts/NNN.md`. Use the chapter plan as a contract, not as prose to mechanically enumerate. Checkpoint `chapter_drafted`, next `consistency`.

### Consistency

Write `drafts/NNN.consistency.json` with:

- `pass`
- contract coverage
- world-rule contradictions
- character contradictions
- timeline/location contradictions
- foreshadow conflicts
- relationship/state mismatches
- corrections required

If material contradictions exist, revise the same draft and re-run consistency. Checkpoint `consistency_checked`, next `commit` only when safe.

### Commit

Copy final prose atomically to `chapters/NNN.md`, then update:

- chapter summary
- timeline entries
- character snapshots/state changes
- relationships if changed
- foreshadow status
- chapter SHA-256 ledger

Checkpoint `chapter_committed`, next `review`.

### Review

Editor writes all seven base review dimensions, issues, evidence, contract status, and semantic `accept|polish|rewrite` verdict. `review_gate.py` validates the record, derives affected chapters from `issues[].chapters` where `requires_change=true`, maps verdict to flow, and queues repairs. It never overrides literary judgment from score thresholds.

- `accept`: continue.
- `polish`: Writer makes localized changes that preserve plot facts, then consistency+commit+review again.
- `rewrite`: Writer may restructure the chapter within the existing contract; if the contract itself is bad, dispatch Architect first.

After final accepted review, checkpoint `chapter_reviewed` with next step decided by boundary logic.

## 4. Arc and volume boundaries

An arc boundary is reached when all detailed chapters assigned to the active arc are accepted, or the Architect/Arbiter has explicitly redefined the boundary before future chapters are committed.

At arc end:

1. Editor performs an aggregate seven-dimension review over the arc using the same review schema with `scope=arc`. Persist `reviews/arc-vXX-aYY.json`.
2. Run `review_gate.py --apply`. If the verdict is `polish` or `rewrite`, repair the derived `affected_chapters`, re-run chapter consistency/commit as required, then repeat the arc review. Do not summarize a knowingly broken arc.
3. Once the aggregate review is accepted, checkpoint `arc_reviewed`.
4. Editor writes an arc summary containing outcomes, unresolved tensions, character snapshots, relationship changes, foreshadow changes, and distilled style rules. Save the summary last so it acts as the aggregate-completion marker.
5. Checkpoint `arc_summarized`, next `expand_arc` unless a volume is also complete.
6. Architect updates the layered outline and details only the next arc, based on actual outcomes plus Compass.
7. Checkpoint `arc_expanded`, next `plan`.

At volume end:

1. Complete the accepted arc review and arc summary first.
2. Editor writes volume summary.
3. Checkpoint `volume_summarized`.
4. Architect creates/expands the next volume skeleton, adjusts Compass only where compatible with committed canon, and details its first arc.
5. Checkpoint `volume_expanded`, next `plan`.

For a non-layered imported project, periodic aggregate review uses the same review object with `scope=global`. Treat that review as the gate before refreshing global summaries/future plans.

## 5. Rewrite and deadlock

Keep `meta/rewrite_queue.json` FIFO with highest severity first. A retry means a new revision of the same chapter, not a new chapter.

If the same chapter fails the gate more than `max_review_retries`:

1. Run Arbiter deadlock prompt.
2. Choose one: relax a non-essential contract, ask Architect to re-plan the chapter, split the chapter, or ask the user only when a major preference is genuinely required.
3. Record the decision in `meta/arbiter/`.

Do not loop indefinitely.

## 6. Import

`ainovel import <file>` is different from `start <file>`.

1. Run `import_split.py` to identify chapter boundaries without semantic invention.
2. Read `prompts/import-analyze.md`.
3. Analyze all imported chapter units in batches; persist compact summaries after each batch rather than retaining all raw prose in one context.
4. Build book/premise/characters/world rules/timeline/relationships/foreshadow/layered outline from evidence.
5. Copy imported chapters into committed chapter files only after numbering is stable.
6. Hash chapters and checkpoint import milestones.
7. Set `current_chapter` to the next unwritten chapter and route to Architect to create the next rolling horizon before Writer continues.

## 7. Sync

Manual chapter edits can invalidate downstream state.

1. Run `sync_scan.py` (or `--check`) and note changed files + earliest changed chapter.
2. `--check` stops after reporting; never mutate hashes/state.
3. For real sync, re-read changed committed chapters and, when necessary, downstream chapters whose facts depend on them.
4. Use `prompts/sync-reextract.md` to rebuild affected chapter summaries, timeline, character state, relationships, foreshadow and style stats.
5. Invalidate/rebuild affected arc/volume summaries and future detailed plans if plot facts changed.
6. Only after semantic state is coherent, run `sync_scan.py --accept` to record new hashes.
7. Checkpoint `sync_completed`.

Never accept hashes first; doing so would lose detection of unsynchronized edits.

## 8. Reopen

Reopen is valid when the current work is completed.

1. Preserve all existing committed canon and ending.
2. Read `prompts/reopen.md` with the user's direction.
3. Architect creates a new volume/season goal and updates Compass with a continuation endpoint.
4. Detail only the first new arc.
5. Set status back to writing and checkpoint `reopened`.

If the user explicitly asks to retcon the ending, treat the incompatible part as a Steer/rewrite request before reopening.

## 9. Completion

Mark completed only when:

- all target promises in Compass are resolved or explicitly left open by design
- no blocking rewrite/steer items remain
- final arc and volume summaries exist
- progress says `current_step=completed`

Export is allowed before completion; exporters should include only existing committed chapter files and report the selected range.

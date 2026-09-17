# Context management

## Goal

Preserve long-form continuity without assuming the host CLI exposes its exact context-window accounting. Use disk state as durable memory and construct small, task-specific restore packs.

## Four compression stages

### 1. ToolResultMicrocompact

- Run scripts that print terse JSON/status.
- Redirect verbose logs to files.
- Never paste whole directory trees, full JSON ledgers, or long command output back into the creative context unless a specific field is needed.
- Prefer exact file paths and line/range reads.

### 2. LightTrim

For a Writer chapter, read only:

- active chapter plan
- current premise/Compass fragments relevant to this arc
- world rules touched by the chapter
- active character snapshots
- current arc summary or arc start state
- previous 1-3 committed chapters/summaries
- specific older chapters referenced by foreshadow/character/history IDs
- durable directives and style rules

Do not read the full book by default.

### 3. StoreSummaryCompact

Run:

```bash
python3 "$SKILL_ROOT/scripts/context_pack.py" build --chapter N --budget-chars 45000
```

The pack is written under `meta/context/current.md`. It should contain structured Store facts and compact summaries, not raw historical chat. Adjust the character budget if the host context is known, but retain headroom for a full chapter draft and review.

Priority order when trimming:

1. chapter contract and durable directives
2. hard world/canon constraints
3. active character state and relationships
4. unresolved foreshadow relevant to current arc
5. recent chapter summaries
6. current arc/volume summaries
7. style profile
8. older relevant history

### 4. FullSummary

If the pack plus draft/role prompt is still too large, use `prompts/full-summary.md`. The host model creates `meta/context/full-summary.md` that preserves:

- current task and exact next step
- committed facts only
- character state and relationship changes
- timeline anchors
- unresolved foreshadow and promises
- active user directives
- open review/rewrite issues
- voice/style constraints

Do not use a deterministic script to invent semantic summaries. After writing the FullSummary, rebuild the context pack and continue.

## Restore packs

Before every Writer/Editor dispatch and after resume/compaction, create a restore pack. Writer must receive at minimum:

- chapter plan
- world/canon constraints
- cast ledger for participating/recent characters
- style rules/stats
- recent summaries
- relevant old facts

Architect expansion additionally needs arc/volume summaries + Compass. Editor review additionally needs current chapter prose + plan contract + relevant canon.

## Relevance without embeddings

This package avoids network/embedding dependencies. Deterministic relevance comes from IDs/tags in summaries and plans:

- character IDs
- world-rule IDs
- foreshadow IDs
- relationship IDs
- location/time IDs

Agents must populate these references when writing plans/summaries. `context_pack.py` uses them to select older compact records when available.

## Budget heuristic

`context_pack.py` uses characters because tokenization varies by host model/language. Character limits are guardrails, not claimed token counts. If the host exposes an exact context window, keep roughly 15% or at least one full chapter-generation budget free before drafting, mirroring the source system's reserve philosophy.

# Editor review contract

## Seven required base dimensions

Every review must contain these seven evidence-based base dimensions:

1. `consistency`
2. `character`
3. `pacing`
4. `continuity`
5. `foreshadow`
6. `hook`
7. `aesthetic`

Each dimension has integer `score` 0-100 and a non-empty `comment`. The runtime source allows extra task-specific dimensions; this skill therefore requires all seven base dimensions but permits additional unique ones.

The `aesthetic` judgment must consider descriptive texture, narrative technique, differentiated dialogue, diction quality, and emotional impact.

## Issue schema

Each issue contains:

- `type`: non-empty problem/rubric label; it may be more specific than a base dimension
- `severity`: `critical|error|warning`
- `description`: non-empty
- `evidence`: non-empty evidence from prose or state
- `suggestion`: fix text or `null`
- `chapters`: evidence chapter numbers; a chapter review defaults to its own chapter, while arc/global review must list chapters explicitly
- `requires_change`: boolean chosen semantically by Editor

For `scope=arc`, the reviewed `chapter` is the arc endpoint and issue chapter numbers must stay inside the arc. For `scope=global`, issue chapters must be between 1 and the review endpoint.

## Verdict is semantic, not threshold-derived

`verdict` is `accept|polish|rewrite` and is chosen by Editor from the whole reading experience. Current source explicitly keeps the model's literary decision; runtime validation does not convert score ranges into a different verdict.

- `accept` requires zero issues with `requires_change=true`.
- `polish`/`rewrite` require at least one issue with `requires_change=true`.
- `affected_chapters` is derived deterministically from the union of `issues[].chapters` where `requires_change=true`; the agent must not invent it separately.

`contract_status` is `null|met|partial|missed`, with `contract_misses` and optional notes. Contract status informs the Editor's semantic verdict but is not a hard-coded score gate.

## Deterministic helper behavior

`review_gate.py`:

1. validates scope, seven required base dimensions, scores/comments, issue evidence/severity/chapter ranges, contract fields and verdict consistency;
2. derives `affected_chapters` from issues marked `requires_change`;
3. when `--apply` is used, persists that derived list, maps verdict to flow (`writing|polishing|rewriting`) and queues repair chapters;
4. never calls a model and never overrides Editor's literary verdict from score thresholds.

## Evidence rules

- Quote only the shortest fragment needed to prove a finding.
- Never cite text not present in the chapter(s).
- Tie continuity/consistency findings to named state/world rule/earlier fact when possible.
- Evaluate hooks as forward pull, not mandatory cliffhangers.
- Judge pacing relative to chapter purpose and genre.

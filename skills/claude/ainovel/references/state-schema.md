# Runtime state schema

## Canonical project tree

```text
novels/<slug>/output/novel/
├── book.md
├── premise.md
├── outline.json
├── layered_outline.json
├── characters.json
├── world_rules.json
├── timeline.jsonl
├── chapters/
├── drafts/
├── reviews/
├── summaries/
├── imports/
├── exports/
├── rules/
└── meta/
    ├── book.json
    ├── compass.json
    ├── progress.json
    ├── foreshadow.json
    ├── relationships.json
    ├── style_rules.json
    ├── user_directives.json
    ├── chapter_hashes.json
    ├── steer_queue.json
    ├── rewrite_queue.json
    ├── checkpoints.jsonl
    ├── arbiter/
    └── context/
        ├── current.md
        └── full-summary.md
```

## `meta/progress.json`

Important fields:

- `schema_version`
- `project_id`, `slug`
- `status`: `initializing`, `writing`, `paused_review`, `paused_cocreate`, `completed`
- `flow`: `planning`, `writing`, `polishing`, `rewriting`, `complete`
- `foundation_complete`
- `current_volume`, `current_arc`, `current_chapter`
- `current_step`: `foundation`, `plan`, `draft`, `consistency`, `commit`, `review`, `summarize_arc`, `expand_arc`, `summarize_volume`, `expand_volume`, `completed`
- `last_completed_step`
- `review_mode`
- `review_permits`
- `max_review_retries`
- `target_chapters` (nullable)
- `language`
- `context_budget_chars`
- `updated_at`

Do not add model/provider fields.

## Checkpoint JSONL

Every line is an immutable JSON object:

```json
{
  "id": "cp-...",
  "seq": 42,
  "scope": {"kind": "chapter", "chapter": 7},
  "step": "chapter_drafted",
  "artifact": "drafts/007.md",
  "digest": "<sha256-of-artifact>",
  "occurred_at": "2026-01-01T00:00:00Z",
  "next_step": "consistency",
  "details": {}
}
```

`scope.kind` is `chapter|arc|volume|global`. `seq` is append order and `digest` is recorded whenever the artifact exists. The latest valid checkpoint plus `progress.json` determines resume. Never retroactively mutate JSONL history.

## Chapter summaries

Prefer `summaries/chapter-NNN.json` with:

- title/purpose/outcome
- 3-8 factual bullet events
- character IDs present and state deltas
- relationship deltas
- world-rule IDs touched
- foreshadow IDs set up/advanced/paid off
- timeline/location anchors
- style stats worth carrying forward
- dependencies/relevant previous chapter IDs

Keep these factual; do not interpret uncommitted possibilities as canon.

## Arc summaries

Use `summaries/arc-vXX-aYY.json` with:

- planned objective vs actual outcome
- major events and consequences
- character snapshots
- relationship snapshot/deltas
- unresolved tensions
- foreshadow ledger changes
- style rules distilled from successful prose/dialogue
- handoff notes for Architect

## Volume summaries

Use `summaries/vol-vXX.json` with lower-granularity outcomes, permanent state changes, resolved/unresolved promises and handoff direction.

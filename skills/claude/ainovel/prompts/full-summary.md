# FullSummary — narrative context compaction

Compress the working narrative context into a restore-safe state summary. This is a semantic operation performed by the host model.

## Inputs

Use only committed state, accepted summaries/reviews, current plan/draft state, directives and explicit pending work. Do not rely on speculative chat ideas unless they are persisted as planned future work.

## Output file

Write `meta/context/full-summary.md` with these exact sections:

1. `Current task and next step`
2. `Hard canon and world constraints`
3. `Current arc/volume objective`
4. `Character state ledger`
5. `Relationships`
6. `Timeline and location anchors`
7. `Foreshadow/promises still open`
8. `Recent causal events`
9. `Durable user directives`
10. `Style/voice constraints`
11. `Open review/rewrite/steer issues`
12. `Do not forget`

Be compact but lossless for future consistency. Prefer stable IDs and factual bullets. Never discard an unresolved foreshadow item, relationship change, injury/power/item ownership change, identity reveal, promise, hard rule or pending user intervention.

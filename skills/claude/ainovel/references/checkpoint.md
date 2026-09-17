# Checkpoint and resume rules

## Recovery principle

Never redo a successful irreversible or expensive creative step solely because a new session lacks chat memory. Read `progress.json`, latest checkpoint, and the referenced artifact. Checkpoints carry monotonic `seq`, `scope`, and an artifact SHA-256 `digest` when an artifact exists.

## Typical event -> resume step

| Latest successful event | Resume |
|---|---|
| `project_initialized` | `foundation` |
| `foundation_saved` | `plan` |
| `chapter_planned` | `draft` |
| `chapter_drafted` | `consistency` |
| `consistency_checked` | `commit` |
| `chapter_committed` | `review` |
| `chapter_reviewed` | boundary decision or next `plan` |
| `arc_reviewed` | `summarize_arc` |
| `arc_summarized` | `expand_arc` or volume summary |
| `arc_expanded` | `plan` |
| `volume_summarized` | `expand_volume` |
| `volume_expanded` | `plan` |
| `steer_triaged` | action recorded by Arbiter decision |
| `sync_completed` | previous writing route |
| `reopened` | `plan` |

## Artifact mismatch

If checkpoint references a missing/invalid artifact:

1. Run `validate_project.py`.
2. Do not fabricate success.
3. Resume at the earliest safe step whose required inputs exist.
4. Append a new checkpoint such as `recovery_reconciled`; never edit the old checkpoint line.

If a committed chapter exists but its hash differs from `chapter_hashes.json`, treat it as a manual edit and require `/sync` before normal continuation.

## Idempotency

- Planning/draft files may be replaced during an intentional revision.
- Committed chapters require explicit commit/rewrite/sync semantics.
- Summary/state rebuilds after sync should be reproducible from committed prose.
- `sync_scan --accept` is the final acknowledgement after semantic rebuild, never the first step.

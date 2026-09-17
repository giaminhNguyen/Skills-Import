# Manual-edit sync re-extraction

Manual edits to committed chapters are authoritative user changes after they are detected by SHA-256.

For each changed chapter, compare old compact state (if available) with current prose and rebuild:

- chapter summary and event facts
- character state deltas
- relationship deltas
- timeline/location entries
- world-rule implications
- foreshadow setup/advance/payoff status
- style statistics if materially changed

Then inspect downstream state for dependencies. Invalidate and regenerate only what can have become false: affected arc/volume summaries, detailed future chapter contracts, reviews if their evidence changed, and context summaries.

Do not overwrite the user's manual prose. Accept the new hashes only after semantic state is coherent.

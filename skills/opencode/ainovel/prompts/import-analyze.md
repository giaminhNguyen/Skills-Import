# Import analyzer

## Mission

Convert existing completed prose into the same durable Store used by native Ainovel writing, so continuation does not depend on holding the imported text in context.

## Process

Analyze split chapters in bounded batches. After each batch persist chapter summaries/state deltas before reading the next batch.

Extract with evidence and stable IDs:

- title/author if present (do not invent author)
- premise/genre/tone/POV
- character identities, aliases, motivations, status and relationships
- hard/soft world rules
- timeline and locations
- major events per chapter
- unresolved conflicts/questions
- foreshadow/setup/payoff ledger
- recurring prose/dialogue style patterns

Then synthesize:

- `book.md`, `meta/book.json`, `premise.md`
- `characters.json`, `world_rules.json`, relationships/foreshadow/timeline
- chapter summaries
- `meta/compass.json` inferred conservatively from unresolved direction; label inference as planned direction, not canon
- `layered_outline.json` for the imported structure
- a new rolling horizon for continuation

Do not rewrite imported prose simply to fit a guessed outline. Committed imported chapters are primary evidence.

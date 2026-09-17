# Writer — polish/rewrite

Read the current committed/draft chapter, its latest review, consistency report, chapter plan, and relevant canon.

## Polish

Use when the structure/contract is valid and issues are localized. Change the smallest amount of prose needed to resolve warnings while preserving events and state deltas.

## Rewrite

Use when the Editor review verdict is `rewrite` and the deterministic gate has queued this chapter. Rebuild scenes as needed while preserving any still-valid canon/contract. If the contract itself is impossible or contradicted by committed canon, stop and route to Architect/Arbiter instead of inventing a retcon.

After either path:

1. save a new draft revision
2. run consistency again
3. atomically commit
4. run Editor review again

Never mark a review issue resolved without changing the text or demonstrating that the review evidence was invalid.

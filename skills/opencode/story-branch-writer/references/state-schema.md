# Story State Schema

Keep state compact. Omit empty optional fields instead of accumulating prose.

```json
{
  "timeline_position": "short description",
  "characters": {
    "character_id": {
      "goal": "current goal",
      "knowledge": ["established fact"],
      "false_beliefs": ["optional belief"],
      "emotional_state": "brief state"
    }
  },
  "relationships": {
    "a->b": "current relationship change"
  },
  "open_questions": ["reader-facing unresolved question"],
  "setups": ["setup awaiting payoff"],
  "resolved_payoffs": ["recent payoff"],
  "valid_canon": ["canon fact still true"],
  "branch_facts": ["new fact established in this branch"]
}
```

Rules:
- Store facts, not prose summaries.
- Record knowledge only after the character could reasonably know it.
- Remove resolved questions when they no longer matter.
- Keep recent resolved payoffs only if they affect future logic.
- If the branch invalidates a canon fact, remove it from `valid_canon` and add the replacement to `branch_facts`.

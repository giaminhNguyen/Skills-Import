# Output Contracts

Use a concise completion report unless the user explicitly asks for a different format.

## Implementation / fix completion

### Result
One or two sentences describing what changed and the user-visible/engineering outcome.

### Changes
- List the important systems/files/behaviors changed.

### Validation
- Tests, build, reproduction, benchmark, or manual checks performed.
- Clearly label validation that could not be executed.

### Risks / follow-up
- Only material residual risks, migrations, dependencies, or next work.

## Technical design

### Proposed design
Short explanation of ownership and data/control flow.

### Affected systems
- System/module and reason.

### Interfaces / data
- Public API, save, replication, schema, asset or configuration changes.

### Validation
- How the design will be proven correct.

### Risks / decisions
- Material trade-offs or unresolved choices.

## Code review

Order findings by severity. For each finding include:

- severity
- location
- concrete failure/risk
- recommended correction

Then provide test gaps and a short overall assessment. If there are no significant findings, state that clearly.

## Performance work

Always include baseline and after measurements when available:

| Metric | Before | After | Target | Scenario |
|---|---:|---:|---:|---|

Then summarize the identified bottleneck, change, correctness check, and remaining risk.

## Release readiness

Return the decision first: `READY`, `READY WITH ACCEPTED RISK`, or `NOT READY`, followed by evidence and blockers.

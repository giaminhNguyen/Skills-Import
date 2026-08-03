# GDD Parsing Procedures & Format Specifications

## Format-Specific Parsing Details

### XLSX (Spreadsheet GDD)

```
1. List all sheet names — each sheet typically maps to a game system
2. Identify sheets relevant to the requested feature:
   - Match by sheet name (e.g., "Combat", "Economy", "Progression")
   - Match by content keywords in first row/column headers
3. Extract:
   - Headers (row 1 or column A) as field names
   - Data rows as specifications
   - Formulas as balance rules (document the formula, not just the value)
   - Color-coded cells may indicate priority/status — note them
4. Handle merged cells, multi-row headers, and nested tables
```

### Markdown GDD

```
1. Parse heading structure (## System Name, ### Subsystem)
2. Build section index for selective loading
3. Extract only sections relevant to the requested feature
4. Preserve tables, formulas, and cross-references
```

### PDF GDD

```
1. Extract text content page by page
2. Identify section headers and table of contents
3. Extract tables and data grids
4. Note: PDFs may lose formula information — flag this
```

### Parsing Rules

- **Never load the entire GDD** into context — extract only relevant sections
- **Preserve exact values** — damage numbers, costs, rates, timings are authoritative
- **Preserve formulas** — `base_damage × (1 + weapon_bonus)` is more valuable than `15`
- **Flag ambiguities** — if a spec is unclear, mark it as `[AMBIGUOUS: needs designer clarification]`
- **Flag gaps** — if the feature has no GDD coverage, mark as `[NOT IN GDD: unspecified]`

## Cache Format Specification

### Cache Index (`_index.md`) Template

```markdown
# GDD Cache Index

## Source
- **GDD File**: [path]
- **GDD Last Modified**: [timestamp]
- **Cache Generated**: [timestamp]

## Cached Specs
| Feature | Cache File | Cached At | Status |
|---------|-----------|-----------|--------|
| Combat System | combat-system.md | 2026-04-11 14:30 | current |
| Economy | economy.md | 2026-04-11 14:35 | current |
| Progression | progression.md | 2026-04-10 09:00 | stale |
```

### Freshness Check Logic

```
1. Read _gdd_source.md — get stored GDD last-modified timestamp
2. Check actual GDD file's current last-modified timestamp
3. Compare:
   - If GDD unchanged since cache was written → cache is FRESH → use cache
   - If GDD modified after cache was written → cache is STALE → re-parse
   - If cache file doesn't exist for this feature → MISS → parse and cache
4. Per-feature freshness:
   - Each cached spec stores its own "cached at" timestamp
   - If GDD changed, only re-parse the REQUESTED feature (not all)
```

## Example GDD Spec Structure

```markdown
# GDD Spec: [Feature/System Name]

## Source
- **GDD**: [file path]
- **Sheet/Section**: [sheet name or section heading]
- **Last Modified**: [date]
- **Cache Key**: [feature-slug]

## Overview
[1-3 sentence summary of what this system does according to the GDD]

## Core Mechanics
[List of mechanics with GDD-specified rules]
- **Mechanic 1**: [description] — GDD value: [exact value/formula]
- **Mechanic 2**: [description] — GDD value: [exact value/formula]

## Parameters & Balance Values
| Parameter | GDD Value | Unit | Notes |
|-----------|-----------|------|-------|
| [param_name] | [value] | [unit] | [any constraints] |

## Formulas
| Formula Name | Expression | Variables |
|-------------|------------|-----------|
| [name] | [formula] | [what each variable means] |

## UI/UX Requirements
[GDD-specified display, feedback, and interaction requirements]

## Dependencies
[Other systems this feature depends on, per GDD]
- Depends on: [System A] — [why]
- Feeds into: [System B] — [how]

## Constraints
[GDD-specified limits, boundaries, platform requirements]

## Acceptance Criteria (from GDD)
[Testable conditions derived from the GDD spec]
- [ ] [Criteria 1 with exact GDD values]
- [ ] [Criteria 2 with exact GDD values]

## Gaps & Ambiguities
[Anything the GDD doesn't specify or is unclear about]
- [AMBIGUOUS]: [what's unclear]
- [NOT IN GDD]: [what's missing]
- [CONFLICT]: [where GDD conflicts with existing code]
```

## Anti-Patterns When Caching

| Anti-Pattern | Problem | Fix |
|-------------|---------|-----|
| Caching the entire GDD | Wastes context, slow | Cache per-feature sections only |
| Ignoring stale cache | Implements outdated spec | Always check freshness before using |
| Not caching at all | Re-parses GDD every time | Cache saves context and time |
| Trusting cache over GDD | Cache may be outdated | GDD always wins — cache is derived |

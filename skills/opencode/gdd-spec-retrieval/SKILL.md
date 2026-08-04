---
name: gdd-spec-retrieval
description: "Retrieve, parse, and cache game design specifications from GDD documents. Grounds implementation decisions in authoritative design documentation. USE WHEN implementing any game feature, mechanic, or system that should align with the GDD. Auto-triggered by workflow Phase 0.5 before planning. Can also be invoked standalone to query the GDD."
user-invocable: true
argument-hint: "[feature/system name to look up in GDD]"
allowed-tools: Read, Glob, Grep, Bash, Write, Edit
related: [planning, workflow, widogame-game-loop, widogame-architecture, balance-check, scope-check, propagate-design-change, dynamic-difficulty]
---

# GDD Spec Retrieval

## Purpose

Ground every implementation decision in the authoritative Game Design Document.
This skill extracts, structures, and caches relevant GDD sections so that:
- **Planning** uses real design specs, not assumptions
- **Implementation** follows GDD-defined values, formulas, and behaviors
- **Validation** can verify compliance against the original spec

## Source Hierarchy

| Priority | Source | Trust Level |
|----------|--------|-------------|
| 1 | GDD document (xlsx, md, pdf) in project | **Authoritative** — single source of truth |
| 2 | User clarification in conversation | **Authoritative** — designer override |
| 3 | Existing code implementation | **Reference** — may be outdated vs GDD |
| 4 | Memory cache (`.Codex/memory/gdd-cache/`) | **Derived** — regenerate if stale |

---

## State Machine

```
          ┌──────────────┐
          │ FEATURE NAME │ ← from user prompt or workflow Phase 0
          └──────┬───────┘
                 │
          ┌──────▼───────┐
          │ CHECK CACHE  │ ← .Codex/memory/gdd-cache/{feature}.md
          └──────┬───────┘
            HIT  │  MISS/STALE
      ┌──────────┴──────────┐
      │                     │
┌─────▼─────┐        ┌─────▼──────┐
│ VALIDATE  │        │ LOCATE GDD │
│ FRESHNESS │        └─────┬──────┘
└─────┬─────┘              │
  FRESH│ STALE       ┌─────▼──────┐
      │    └────────→│ PARSE GDD  │
      │              └─────┬──────┘
      │                    │
      │              ┌─────▼──────┐
      │              │ EXTRACT    │
      │              │ SPEC       │
      │              └─────┬──────┘
      │                    │
      │              ┌─────▼──────┐
      │              │ STRUCTURE  │
      │              │ & CACHE    │
      │              └─────┬──────┘
      │                    │
      └────────┬───────────┘
               │
        ┌──────▼───────┐
        │ RETURN SPEC  │ → feeds Phase 1 (Requirements) + Phase 2 (Plan)
        └──────────────┘
```

---

## Phase 1: LOCATE GDD

Find the Game Design Document in the project.

### Search Order:
```
1. Check known GDD locations:
   - Project root: GDD_*.xlsx, GDD_*.md, GDD_*.pdf, GAME_DESIGN.*, DESIGN_DOC.*
   - /docs/: GDD/, design/, specifications/
   - /GameDesign/: any supported format
   - Assets/Documentation/: GDD files

2. Glob patterns (in order):
   - **/GDD*.{xlsx,md,pdf,docx}
   - **/Game*Design*.{xlsx,md,pdf,docx}
   - **/design*doc*.{xlsx,md,pdf,docx}

3. If multiple GDDs found:
   - Check file modification dates — prefer most recent
   - If ambiguous, ASK user which GDD to use
   - Store the selected GDD path in .Codex/memory/gdd-cache/_gdd_source.md
```

### Output:
```markdown
GDD Located: [path]
Format: [xlsx|md|pdf|docx]
Last Modified: [date]
Size: [size]
```

### If NOT Found:
```
⚠️ No GDD found in project.
Options:
  A) Provide GDD file path
  B) Skip GDD retrieval — plan without design spec (NOT RECOMMENDED)
  C) Create a minimal GDD template for this feature
```

---

## Phase 2: PARSE GDD

Extract content based on GDD format. See `reference/parsing-procedures.md` for detailed format-specific parsing rules and examples.

**Core principles:**
- Never load the entire GDD into context — extract only relevant sections
- Preserve exact values and formulas (not just computed results)
- Flag ambiguities and gaps (don't silently fill them in)

---

## Phase 3: EXTRACT SPEC

Structure the raw GDD data into an actionable spec. See `reference/parsing-procedures.md` for a complete spec template and examples.

---

## Phase 4: CACHE

Store the extracted spec for reuse. Cache location: `.Codex/memory/gdd-cache/`

After extracting a spec, write it to `.Codex/memory/gdd-cache/{feature-slug}.md` and update `_index.md`.

**Freshness check**: Compare GDD last-modified timestamp to cache timestamp. If GDD was modified after cache was written, re-parse (cache is STALE). See `reference/parsing-procedures.md` for cache format specification and anti-patterns.

---

## Phase 5: RETURN SPEC

Deliver the structured spec to the calling phase.

### When Called from Workflow Phase 0.5:
Return the full spec structure to feed into:
- **Phase 1 (Requirements)**: Combines GDD spec with user requirements
- **Phase 2 (Plan)**: Uses GDD values, formulas, and constraints in plan
- **Phase 5.5 (Spec Validation)**: Uses acceptance criteria to validate implementation

### When Called Standalone:
Display the spec to the user with a summary:
```
## GDD Spec Retrieved: [Feature Name]

### Key Values
[Most important parameters and formulas]

### Acceptance Criteria
[Testable conditions from GDD]

### Gaps
[What the GDD doesn't cover for this feature]
```

---

## Combining GDD Spec with User Requirements

When the workflow calls this skill, the output feeds a **merge step** in Phase 1:

```
┌─────────────────┐     ┌──────────────────┐
│ GDD Spec         │     │ User Requirements │
│ (from this skill)│     │ (from prompt)     │
└────────┬────────┘     └────────┬─────────┘
         │                       │
         └───────────┬───────────┘
                     │
              ┌──────▼──────┐
              │   MERGE     │
              │             │
              │ GDD values  │ ← authoritative numbers
              │ + User goal │ ← what to build
              │ + Scope     │ ← user-defined boundaries
              │ + Conflicts │ ← flagged for resolution
              └──────┬──────┘
                     │
              ┌──────▼──────┐
              │ COMBINED    │
              │ REQUIREMENTS│ → feeds Phase 2 (Plan)
              └─────────────┘
```

### Merge Rules:
1. **GDD values are authoritative** — if GDD says damage = 15, plan uses 15
2. **User can override GDD** — but must be explicit ("ignore GDD, use damage = 20")
3. **Conflicts are surfaced** — if user asks for X but GDD says Y, flag it
4. **Gaps are filled by user** — if GDD is silent on something, user requirement fills it
5. **Scope is user-defined** — GDD says what the system IS; user says what to BUILD now

---

## Anti-Patterns

| WHEN | WRONG | RIGHT | WHY |
|------|-------|-------|-----|
| Spec is ambiguous | Interpret and implement your best guess | Flag ambiguity, request clarification from designer | Your guess becomes code precedent; revisiting costs rework |
| GDD values don't match code | Code wins (it's the truth) | GDD wins unless user explicitly overrides; flag the conflict | Stale GDD values spread misunderstandings; code is implementation detail |
| Feature not in GDD | Invent the values and ship | Flag as `[NOT IN GDD]`, ask user if it's in scope | Unvalidated features often contradict design intent or break economy |

## Anti-Rationalization Table

| Excuse | Rebuttal |
|--------|----------|
| "The GDD is outdated" | Verify with user, then update cache. Code doesn't override design docs. |
| "I'll match the GDD later" | GDD compliance prevents rework. Implement to spec, not memory. |
| "This feature isn't in the GDD" | Flag as `[NOT IN GDD]`, ask user if it's in scope. Don't guess. |
| "The GDD doesn't specify this edge case" | Flag as `[AMBIGUOUS]`, ask user. Don't invent values. |
| "Loading the GDD is too slow" | That's why we cache. Check cache first, parse only on miss/stale. |
| "The GDD is too large to parse" | Never parse the whole thing. Extract only the relevant section. |
| "The existing code has different values" | GDD wins unless user explicitly says otherwise. Flag the conflict. |

---

## Integration with Workflow

This skill is auto-triggered by the workflow at **Phase 0.5** (after CLASSIFY, before REQUIREMENTS):

```
Phase 0: CLASSIFY
    ↓
Phase 0.5: SPEC RETRIEVAL (this skill)
    ↓ feeds GDD spec into...
Phase 1: REQUIREMENTS (merges GDD + user requirements)
    ↓
Phase 2: PLAN (uses GDD values/formulas in plan)
    ↓ ... implementation ...
Phase 5.5: SPEC VALIDATION (validates against GDD acceptance criteria)
    ↓
Phase 6: COMPLETE
```

### Skip Conditions:
- **Task is Trivial** (typo, config) → skip Phase 0.5 entirely
- **Task has no game mechanic** (CI/CD, build script) → skip Phase 0.5
- **No GDD exists in project** → skip (warn user)
- **Cache is fresh AND feature already cached** → return cached spec (fast path)
- **User says "skip GDD"** → skip (note in requirements that GDD was not consulted)

---

## Verification Checklist

After retrieval, verify:
- [ ] Spec was extracted from the correct GDD section
- [ ] All numeric values match GDD exactly (no rounding, no guessing)
- [ ] Formulas are preserved as formulas (not just computed values)
- [ ] Dependencies are identified
- [ ] Gaps and ambiguities are flagged (not silently filled in)
- [ ] Cache is updated with fresh data
- [ ] Cache index reflects the new/updated entry

---

## Does NOT
- Write GDD content — this skill only retrieves and reads existing specs
- Make design decisions — it extracts what the GDD already decides
- Modify game specifications or design intent — only reads and structures what's already documented

## Reference Files

- **reference/parsing-procedures.md** — Detailed format-specific parsing rules (XLSX, Markdown, PDF), cache format specs, cache anti-patterns, and example GDD spec templates

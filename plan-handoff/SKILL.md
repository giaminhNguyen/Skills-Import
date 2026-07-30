---
name: plan-handoff
description: "Crystallize the plan agreed in the current session into a self-contained handoff document that another agent or person can execute faithfully with zero prior context. Use at the end of a planning discussion to 'chốt plan' / export an executable plan. Invoke with /plan-handoff [optional output path]."
user-invocable: true
disable-model-invocation: true
argument-hint: "[output-path.md] (optional; default <project-root>/plan/<slug>.md)"
allowed-tools: Read, Glob, Grep, Bash, Write
---

# Plan Handoff

Turn the plan that was just discussed and agreed in THIS session into a portable, executable handoff document. The reader is a fresh agent or teammate with **no access to this conversation** — the document must stand entirely on its own.

This skill only PRODUCES the document. Do not start implementing the plan.

## When invoked

1. **Resolve the output path**
   - If an argument was passed, treat it as the output file path. Resolve relative paths against the project root; keep absolute paths as-is. Ensure it ends in `.md`.
   - Otherwise default to `<project-root>/plan/<slug>.md` — a `plan/` folder at the repo root, the same level as `.claude/` — where `<slug>` is the kebab-case of the plan title.
   - Create the parent directory if it does not exist. State the final target path to the user before writing.

2. **Reconstruct the agreed plan from the WHOLE session** — not just the last message:
   - The problem / goal and what prompted it.
   - Every decision that was locked in, with the reasoning.
   - Clarifications and preferences the user gave (including any AskUserQuestion answers).
   - Alternatives that were considered and **rejected**, with the reason — so the executor does not re-litigate them.
   - If a plan-mode plan file already exists for this work (e.g. under `~/.claude/plans/`), read it and fold it in.

3. **Verify before writing (read-only).** For every file path, function, class, or symbol you mention, confirm it actually exists using Glob/Grep/Read. Do not invent paths or APIs. If something is uncertain, resolve it now (search the codebase, or ask the user) — the finished document must contain **no open questions and no unverified claims**. Everything in it is locked.

4. **Write the handoff document** using the template below, then stop.

## Output language & conventions

- Write the prose in the **same language the session was conducted in**; keep code, identifiers, and file paths in English.
- Be concrete: real paths, real names, real patterns to reuse. Prefer pointing at existing utilities over inventing new code.
- Add a one-line reminder that the executing agent must follow the repo's `CLAUDE.md` and `.claude/rules.md` (code-layout regions, no-LINQ-in-hot-path, confirm-before-edit, scene-reload assumptions) — if those files exist in the target repo.

## Handoff document template

```markdown
# Plan: <title>

## Context — vì sao
<problem, what prompted it, intended outcome>

## Quyết định đã chốt
- <decision> — <lý do>
- <rejected option> — <vì sao loại>
<the part that gets lost without the conversation — be thorough>

## Bối cảnh kỹ thuật (đã xác minh)
<verified file paths, existing utilities/patterns to reuse with paths, key constraints>

## Các bước thực hiện
### Phần 1 — <name>
- File: `path` — <what & how; patterns to follow>
### Phần 2 — <name>
- ...

## Không đụng tới (out of scope / guardrails)
- <what must NOT change>

## Critical files
- New: `path`
- Edit: `path` — <what>

## Verification (end-to-end)
1. <how to build / run / test — e.g. Unity Editor steps>
2. ...

## Convention bắt buộc
Executor phải tuân theo `CLAUDE.md` + `.claude/rules.md` của repo.
```

## Final step

Tell the user the exact path written and give a one-line summary of the document. Do not begin implementing — this skill produces the handoff document only.

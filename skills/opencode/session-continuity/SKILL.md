---
name: session-continuity
description: "Save the current session context to a .md file and restore it in a new session so work continues seamlessly. Use when the user says they want to save/end a session ('lưu session', 'save session', '/save', '/save-session', 'continue later', 'tạm dừng', 'mai làm tiếp') or when they want to restore a previously saved session ('đọc session', 'continue from', 'load session', '/load', '/continue', 'mở lại', 'hồi tiếp'). This skill handles full session persistence — not just plans. Use it INSTEAD of plan-handoff when the goal is to continue working, not just document a plan."
user-invocable: true
disable-model-invocation: true
argument-hint: "save | /path/to/session.md"
allowed-tools: Read, Glob, Grep, Bash, Write, Edit
---

# Session Continuity

Preserve full session context so a new agent session can pick up exactly where the previous one left off. This skill has two modes:

- **SAVE** (`/save` or `session-continuity save`) — capture current session into `.md`
- **RESTORE** (`/load <path>` or `session-continuity /path/to/session.md`) — load a saved session and continue

SAVE only runs when the user explicitly invokes it. RESTORE summarizes and waits for the user's next command — it does NOT auto-execute any steps.

---

## SAVE mode

### When triggered

User says one of: `lưu session`, `save session`, `/save`, `/save-session`, `continue later`, `tạm dừng`, `mai làm tiếp`, `lưu lại`, `lưu công việc`, or explicitly invokes `/session-continuity save`.

### Output path

```
<project-root>/.opencode/sessions/<YYYY-MM-DD-HHmm>-<slug>.md
```

- `<project-root>` = the workspace root (where `.opencode/` lives or repo root)
- `<slug>` = kebab-case of what this session was about (max 5 words)
- Create the `sessions/` directory if missing
- If the user passed an explicit path as argument, use it instead

### What to capture (scan the ENTIRE session, not just last message)

Use the template below. Walk through each section systematically. Before writing, use Read/Glob/Grep to verify every file path and symbol mentioned — no invented paths, no unverified claims.

### Template

```markdown
# Session: <title>

**Saved:** <datetime>
**Project:** <project path>
**Ponytail mode:** <lite/full/ultra>

## What we were working on
<one paragraph: the goal of this session, what prompted it, intended outcome>

## Done
- <files created, bugs fixed, features complete — concrete, with file paths>

## In progress
- <what was actively being worked on but not finished>

## Next steps
1. <exactly what to do next, in order>
2. ...

## Decisions locked
- <decision> — <why>
- <rejected option> — <why rejected>

## Files touched
- Created: `path`
- Modified: `path` — <summary of change>
- Deleted: `path`

## Open questions / blockers
- <anything unresolved>

## Agent notes
- Preferences observed: <ponytail level, communication style, no-go areas>
- Special instructions given: <any custom rules user set>
- Risks / warnings: <gotchas, known pitfalls>

## First command for the new session
> <the single best command to pick up where we left off — must be actionable>
```

**Language:** Write prose in the same language the session was conducted in (Vietnamese in this case). Keep code, file paths, identifiers in English.

### Quality bar

- Must be **self-contained**: a fresh agent with zero context must be able to start working immediately after reading this file
- Be concrete — real paths, real patterns, real next steps
- If a decision was discussed at length, capture *why* so it isn't re-litigated
- If there were bugs or errors encountered, capture the symptom + what was tried

---

## RESTORE mode

### When triggered

User says one of: `đọc session <path>`, `continue from <path>`, `load session <path>`, `/load <path>`, `/continue <path>`, `mở lại <path>`, `hồi tiếp <path>`, `tiếp tục <path>`, `xem lại <path>`, or explicitly invokes `/session-continuity <path>`.

Also triggers when user says `đọc session`, `load session`, `/load`, `/continue` without a path — in that case, list available session files from `.opencode/sessions/` and ask which one.

### Procedure

1. **Read the file** — load the full `.md` content
2. **Internalize context** — treat everything in the file as current session context. You are the same agent continuing the same work, not "reading about another session."
3. **Respond with a brief summary** (3-5 lines max):
   ```
   Tiếp tục session "<title>" từ <datetime>.
   Đang làm: <in progress summary>
   Bước tiếp theo: <first next step>
   
   Sẵn sàng, bạn muốn làm gì tiếp?
   ```
4. **Wait** — do NOT start implementing anything. The user will give the next command.

### When listing available sessions

Format:
```
Các session đã lưu:
  1. .opencode/sessions/2026-07-30-1103-the-naming.md — "The Naming" (Jul 30, 11:03)
  2. ...
  
Bạn muốn load session nào? (gõ số hoặc đường dẫn)
```

---

## Edge cases

| Situation | Behavior |
|-----------|----------|
| `.opencode/sessions/` doesn't exist | Create it on SAVE; on RESTORE, report "no saved sessions found" |
| File path on RESTORE doesn't exist | Report error and list available files |
| SAVE in a project with no `.opencode/` | Create `.opencode/sessions/` relative to workspace root |
| User says `/save` but nothing meaningful happened | Still save — even "explored but found nothing" is useful context |
| Session file is corrupted/unparseable | Report the error, suggest manual inspection |
| RESTORE invoked but file has no clear "Next steps" | Summarize what's there and ask user what to do |

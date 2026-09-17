# Command semantics

## `ainovel help`

Show the 14 original command intents plus the `steer` adapter alias. Mention that normal prose intervention during an active run is also Steer.

## `ainovel model [role]`

Do not edit files or provider settings. Say that this skill uses the model already selected by the host CLI. If the host supports a native model command, the user may use that outside this skill. Then resume without changing novel state.

## `ainovel config`

Allow only creative/workflow configuration: language, target chapter count, chapter length guidance, review mode, retry limit, context-pack budget, recent-chapter window, output path, style preferences. Never add provider/model/API/base URL fields. Use `state.py config` for supported deterministic fields and `state.py review` for review mode. Preserve free-form style preferences in `meta/project_config.json`.

## `ainovel diag`

1. Run `stats.py` and `validate_project.py`.
2. Semantically inspect four areas:
   - progress: loops, stuck queues, numbering/gaps
   - quality: review trends, contract adherence, anomalous chapter length
   - planning: exhausted horizon, forgotten promises/foreshadow, missing summaries
   - context: character disappearance, timeline/canon discontinuity
3. Write optional `meta/diag-export.md` if the user requests a saved report.

## `ainovel review [on|off]`

Use `state.py review on|off`. `on` gates after each accepted new chapter. `off` clears only future gate behavior, not reviews.

## `ainovel next`

Use `state.py next`. Grant exactly one permit. Consume it at the moment a new chapter begins planning, not during rewrite/polish.

## `ainovel start <file>`

Read the whole file as *requirements/outline*. Initialize a fresh book and let Architect normalize it into internal state. Do not treat its prose as completed chapters.

## `ainovel import <file>`

Use `import_split.py`, then semantic import workflow from `workflow.md`. This is the path for completed novel prose.

## `ainovel reopen <direction>`

Only for a completed work. Preserve the ending as history, then add a new continuation volume/season with the supplied direction. Explicit retcons go through Steer/rewrite first.

## `ainovel cocreate`

Pause normal routing. Use `prompts/co-create.md` to collaboratively refine the next phase. Persist the final creative directive and route it through Arbiter/Architect. Do not require many questions when reasonable assumptions suffice.

## `ainovel simulate`

Read text/markdown samples from `./simulate/` (or paths supplied by user). Use `prompts/simulate-style.md` to create `meta/style_rules.json`. Extract abstractions: rhythm, sentence length, diction tendencies, dialogue ratio, scene density, POV distance, imagery and avoid-list. Do not copy sample sentences.

## `ainovel importsim <file>`

Validate JSON shape and copy it to `meta/style_rules.json`. If the file is a prose sample rather than a profile, treat it as a simulate request instead of silently accepting the wrong format.

## `ainovel sync [--check]`

- `--check`: run `sync_scan.py --check`; report changed chapter hashes only.
- normal: detect changes, semantically rebuild affected state with `prompts/sync-reextract.md`, invalidate downstream summaries/plans as needed, then `sync_scan.py --accept`.

Block ordinary continuation while committed chapter hashes are dirty unless the user explicitly abandons the changes.

## `ainovel export ...`

Use `export_novel.py`. Infer format from extension; default to TXT. Respect `from=N`, `to=N`, and overwrite flag. EPUB is EPUB3 with metadata, title page, navigation/TOC and per-chapter XHTML; no cover image is required.

## `ainovel steer "..."` or plain intervention

Persist first, then classify through Arbiter. Categories:

- continue/no-op
- durable directive
- future outline change
- canon/foundation change
- rewrite/polish request
- completion/length control

Never let a conversational intervention disappear if it materially changes the story.

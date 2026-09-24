---
name: story-tts-adapter
description: Adapt an already-written story or narration script for a selected text-to-speech engine without changing plot, events, reveals, character intent, or story meaning. Use when converting story.md or other prose into TTS-ready text, selecting among multiple saved TTS profiles, analyzing a TTS project/repository to derive a reusable profile, normalizing prose for speech, or creating TTS chunks and a manifest for synthesis.
---

# Story TTS Adapter

## Core contract

Treat the story as canonical content. Adapt only the speech surface.

Never change:
- plot or event order;
- character decisions or knowledge;
- reveals, twists, setup/payoff, or ending;
- facts, names, relationships, or causal logic;
- meaning merely to make synthesis easier.

May change only when the active profile calls for it:
- sentence boundaries;
- punctuation and pause placement;
- paragraph boundaries;
- dialogue presentation;
- number, abbreviation, symbol, and URL normalization;
- pronunciation hints or engine-supported inline cues;
- chunk boundaries.

If a surface rewrite would materially alter meaning, keep the original wording instead.

## Inputs

Accept:
1. `story`: required; a completed story/script or path to it.
2. `tts_profile`: optional when a default is available; otherwise select an explicit saved profile.
3. `tts_project`: optional; repository/path/docs used to build a new profile.
4. `output_dir`: optional.

When both `tts_profile` and `tts_project` are supplied, analyze/update the requested profile before adapting.

## Profile resolution

Resolve in this order:
1. Explicit profile supplied by the user.
2. Workspace profile registry if present.
3. Bundled registry in `references/profiles/registry.json`.
4. Registry default.

Do not silently substitute a different profile if the requested ID is missing.

Read `references/profile-schema.md` before creating or modifying a profile.
Read only the selected profile file, not every saved profile.

## Workflow

### A. Existing profile

1. Load the story unchanged.
2. Load the selected profile.
3. Make one TTS adaptation pass over the existing prose.
4. Preserve story semantics while applying profile-specific surface rules.
5. Save the adapted full text as `story_tts.txt`.
6. Run `scripts/chunk_tts.py` with the selected profile to create `chunks/` and `manifest.json`.
7. Run `scripts/validate_tts_output.py` to check deterministic profile constraints.
8. Fix only TTS-surface issues found by validation.
9. Respect the profile `synthesis.preferred_input_mode`: some engines should receive `story_tts.txt` directly and chunk internally; others should consume `chunks/`.

### B. New TTS project/profile

When the user supplies a TTS codebase, repository, package, or documentation:

1. Inspect authoritative code/config/docs for text input behavior.
2. Extract only supported or reasonably inferred constraints.
3. Separate engine facts from adapter policy.
4. Create a profile following `references/profile-schema.md`.
5. Record provenance in the profile.
6. Validate with `scripts/validate_profile.py`.
7. Add it to a workspace registry or, when updating this skill itself, the bundled registry.
8. Then follow Workflow A.

Read `references/profile-builder.md` for the extraction checklist.

## Adaptation rules

Prioritize natural spoken delivery, not visible textual similarity.

Use the profile to decide:
- preferred sentence size;
- how aggressively to split or merge sentences;
- whether tiny standalone replies should be attached to narration;
- punctuation used for pauses;
- number/symbol normalization;
- whether supported inline tags should be added;
- whether dialogue quotes should remain;
- safe chunk size.

Do not insert experimental emotion tags by default. Use them only when the profile allows them and the story clearly supports the cue. Never invent laughter, sighing, crying, shouting, or other performance events not supported by the source text.

## Multiple-profile behavior

One canonical `story.md` may produce multiple TTS outputs without rewriting the story:

```text
story.md
├── output/vieneu-v3-turbo/
├── output/other-profile-a/
└── output/other-profile-b/
```

Keep each profile output isolated. Never overwrite `story.md`.

## Output contract

For each selected profile produce:

```text
<output_dir>/<profile-id>/
├── story_tts.txt
├── manifest.json
└── chunks/
    ├── 0001.txt
    ├── 0002.txt
    └── ...
```

`manifest.json` must identify the profile, source story, chunk count, character counts, and chunk filenames.

## Quality gate

Before finishing, verify:
- adapted text preserves the same story;
- no scene, reveal, or fact disappeared;
- no new plot information was introduced;
- deterministic profile limits pass validation;
- chunks do not exceed the configured hard limit;
- no avoidable ultra-short chunks remain;
- output is ready to feed directly to the selected TTS engine or its synthesis wrapper.

For qualitative checks, use `references/quality-checks.md`.

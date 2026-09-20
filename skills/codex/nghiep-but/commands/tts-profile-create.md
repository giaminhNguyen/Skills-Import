# Command: Create TTS Profile (from source)

Goal: analyze a TTS engine's source (code / SDK / API docs) and generate a
consistent profile file under tts-profiles/, so Step 7 can use it later.

## Before executing
Read: tts-profiles/_schema.md (the required structure) and tts-profiles/elevenlabs.md (a worked example to imitate).

## Accepting the source (3 ways)
The user provides the TTS engine info in ONE of these forms:
1. Local path — a folder/repo of the TTS project. Read the code, README, and any docs.
2. URL — a GitHub repo or API documentation link. Fetch and read it.
3. Pasted text — code snippets, API reference, or a written description in chat.

If the user only names an engine without source, ask them to provide source in one of the 3 forms. Do not guess rules from memory unless the user explicitly says "use your knowledge of <engine>".

## Extraction procedure
From the source, determine each schema field by looking for:
- Input format: request body examples, does it take `text`, `ssml`, JSON? What content-type?
- Markup/control syntax: search for break/pause/emphasis/rate tags or params (e.g. `<break>`, `ssml`, `prosody`, `speed`, `stability`).
- Limits: max character constants, request size limits, rate limits, rejected characters.
- Number/text handling: any normalization utils in the code, or docs saying digits are read literally.
- Multi-voice: voice/speaker parameters, whether multiple voices per request are possible.
- Language/Vietnamese: supported language codes, model names, voice IDs for Vietnamese.
- Output: returned audio format, sample rate.

## Writing the profile
1. Copy tts-profiles/_template.md structure.
2. Fill EVERY field from what the source shows.
3. For anything the source does not clarify: put it under UNRESOLVED, and ASK THE USER (this is a permitted pause). Never invent syntax.
4. Set `confidence` honestly: high (source explicit), medium (inferred), low (guessed / thin source).
5. Set `source` to the exact path/URL/"user-provided code".
6. Save as tts-profiles/<engine-name>.md (lowercase, hyphenated, no spaces).

## After creation
Print a one-line confirmation only:
```
Da tao profile TTS: tts-profiles/<name>.md (confidence: <level>)
```
If there were UNRESOLVED items, list them as questions for the user.

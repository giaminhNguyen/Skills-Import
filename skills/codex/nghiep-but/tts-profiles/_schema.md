# TTS Profile Schema

Every profile in tts-profiles/ MUST follow this exact structure so any profile
the agent generates is consistent and usable by Step 7 (tts-prep).

A profile is a markdown file named `<engine-name>.md` (lowercase, no spaces).

## Required fields

```
# TTS Profile: <Engine Name>

## Meta
- engine:            <name, e.g. ElevenLabs, Google Cloud TTS, Vbee>
- source:            <where rules were derived from: repo URL / docs URL / "user-provided code" / "manual">
- language_support:  <does it support Vietnamese? which voices/model IDs?>
- confidence:        <high / medium / low — how sure the agent is about these rules>

## Input format
- accepts:           <plain text | SSML | markdown | JSON>
- markup_syntax:     <none | SSML tags | custom>  (describe exact syntax)

## Pause / pacing control
- pause_method:      <how to create pauses: punctuation only? <break> tags? line breaks?>
- pause_syntax:      <exact syntax, e.g. `<break time="1.0s" />` or `—` or `...`>
- emphasis:          <how to emphasise, if supported>
- speed_control:     <how to control speed, if supported>

## Text normalization (what THIS engine needs the agent to pre-process)
- numbers:           <engine reads digits well? OR agent must convert "4,8 trieu" -> "bon phay tam trieu"?>
- abbreviations:     <expand? e.g. "TS" -> "tien si">
- currency_units:    <how to handle "te", "trieu", "$">
- forbidden_chars:   <characters to strip: quotes, markdown, brackets, etc.>
- name_handling:     <any special handling for Sino-Vietnamese names>

## Chunking
- max_chars:         <max characters per request/segment; 0 = no limit>
- split_strategy:    <how to split long text: by paragraph / by sentence / by char limit>

## Multi-voice
- multi_voice:       <yes/no — can it use different voices per character?>
- voice_tag_syntax:  <if yes, the syntax; if no, add speaker attributions in prose>

## Output
- audio_format:      <mp3 | wav | ...>
- notes:             <anything else relevant>

## UNRESOLVED
List any field the source did not clarify. The agent MUST ask the user about
each item here rather than guessing. If none, write "None".
```

## Rules for the agent when filling a profile
1. Fill every field. If a value is unknown from the source, write it under UNRESOLVED and ask the user.
2. Never invent syntax. If the source does not show a pause/emphasis syntax, mark pause_method as "punctuation only" and set confidence accordingly.
3. Prefer conservative defaults: if unsure whether the engine normalizes numbers, assume it does NOT and have the agent convert them.

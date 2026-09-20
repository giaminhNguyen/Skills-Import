# TTS Profile: ElevenLabs

## Meta
- engine:            ElevenLabs
- source:            manual (ElevenLabs public behaviour, Vietnamese multilingual v2)
- language_support:  Yes. Multilingual v2 supports Vietnamese. Voice chosen by user in ElevenLabs dashboard (voice_id).
- confidence:        high

## Input format
- accepts:           plain text (best). Limited SSML-like support.
- markup_syntax:     Mostly punctuation-driven. `<break time="1.0s" />` is partially honoured but unreliable; prefer punctuation and line breaks.

## Pause / pacing control
- pause_method:      Punctuation + line breaks are the primary, reliable method.
- pause_syntax:      Short pause = "," ; full stop = "." ; longer beat = "—" or "..." ; scene beat = blank line between paragraphs.
- emphasis:          No reliable inline emphasis tag. Convey emphasis via sentence structure and short standalone sentences.
- speed_control:     Set globally in ElevenLabs settings (stability/speed), not inline.

## Text normalization
- numbers:           Convert complex numbers to words. "4,8 trieu" -> "bon phay tam trieu"; "78" -> "bay muoi tam"; room "302" -> "ba le hai". Simple counts can stay if unambiguous.
- abbreviations:     Expand all. "TS" -> "tien si", "HR" -> "phong nhan su".
- currency_units:    Read as words: "5 trieu" -> "nam trieu"; keep "te" as "te".
- forbidden_chars:   Strip markdown (#, *, -, >), strip decorative quotes if they cause odd reading, strip brackets [] {}. Keep sentence punctuation . , ! ? — ...
- name_handling:     Sino-Vietnamese names read fine. Keep diacritics. Do NOT romanize.

## Chunking
- max_chars:         Practical target ~2500-3000 chars per generation for stable prosody. 0 means model max, but shorter chunks = more consistent voice.
- split_strategy:    Split at paragraph boundaries; never split mid-sentence. Keep each chunk under max_chars.

## Multi-voice
- multi_voice:       no (single narrator recommended for this genre)
- voice_tag_syntax:  N/A. Add light speaker attributions in prose where a single narrator voice might confuse who is speaking ("co ta noi", "toi dap") at ambiguous turns.

## Output
- audio_format:      mp3
- notes:             This genre is best as one calm narrator voice. Rely on punctuation for the "cold pause" moments (P7 silence, F12 cold close): put the cold line on its own paragraph, preceded by a blank line.

## UNRESOLVED
None.

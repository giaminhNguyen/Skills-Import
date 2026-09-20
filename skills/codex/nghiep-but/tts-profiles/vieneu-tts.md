# TTS Profile: VieNeu-TTS v3 Turbo

## Meta
- engine:            VieNeu-TTS v3 Turbo
- source:            https://github.com/pnnbao97/VieNeu-TTS
- language_support:  Vietnamese; v3 Turbo supports Vietnamese and bilingual input, 25 preset voices across Bắc/Trung/Nam, plus instant voice cloning.
- confidence:        high

## Input format
- accepts:           Plain text through the Python SDK `infer(text, voice=...)` or OpenAI-compatible JSON API (`input`).
- markup_syntax:     Experimental inline cues only: `[cười]`, `[thở dài]`, `[hắng giọng]`. The `style` argument is deprecated and ignored in v3 Turbo.

## Pause / pacing control
- pause_method:      Sentence punctuation and paragraph boundaries; no documented explicit pause tag.
- pause_syntax:      Use `.`, `,`, `...`, `—`, and blank lines. Use experimental cues sparingly and only when they correspond to an audible action.
- emphasis:          Use sentence structure and short standalone sentences; select an appropriate preset voice or cloned reference clip, since v3 Turbo derives style from that voice/reference.
- speed_control:     No v3 Turbo speed parameter is documented for this use; control pacing through text segmentation and the selected voice/reference.

## Text normalization (what THIS engine needs the agent to pre-process)
- numbers:           Pre-expand numerals that are semantically ambiguous in narration, money, dates, room numbers, identifiers, and percentages. The repository uses sea-g2p for phonemization, but its exact verbalization rules are not documented here.
- abbreviations:     Expand Vietnamese and English abbreviations unless their intended spoken form is unambiguous.
- currency_units:    Spell out amounts in Vietnamese: `8,7 triệu tệ` → `tám phẩy bảy triệu tệ`; preserve the intended currency name.
- forbidden_chars:   Strip Markdown headings, bullets, code fences, URLs, and decorative symbols. Preserve supported action cues only where desired; do not use unsupported SSML.
- name_handling:     Keep Vietnamese and Sino-Vietnamese diacritics. Avoid unnecessary English/code-switching, which is less stable than pure Vietnamese.

## Chunking
- max_chars:         0; the source documents that one long `infer()` auto-batches its own chunks, but no character ceiling is specified.
- split_strategy:    Prefer paragraphs or complete scene beats for audiobook consistency; never split inside a sentence, dialogue turn, number, or supported cue. Use `infer_batch()` for many independent chunks.

## Multi-voice
- multi_voice:       yes
- voice_tag_syntax:  Use the repository's Conversation mode / multi-speaker API or application flow; no inline speaker-tag syntax is documented for `infer()`. For single-narrator export, retain light speaker attributions in prose.

## Output
- audio_format:      WAV at 48 kHz via SDK; OpenAI-compatible streaming API returns PCM or WAV.
- notes:             Recommended default is v3 Turbo. Use a preset such as Mai Anh, Trúc Ly, Minh Quân Pro, or a clean 3–8 second cloned reference. Emotion cues are experimental. v3 Nano is 24 kHz and trades quality for speed.

## UNRESOLVED
- No documented maximum text length per inference request. The profile therefore uses semantic paragraph splitting rather than an invented hard limit.
- The exact sea-g2p handling of every numeric and abbreviation form is not documented; retain the conservative pre-normalization rules above.

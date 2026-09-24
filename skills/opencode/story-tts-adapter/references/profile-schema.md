# TTS profile schema

Use JSON so bundled scripts require no YAML dependency.

Required top-level fields:

```json
{
  "profile_id": "engine-mode-name",
  "display_name": "Human-readable name",
  "engine": "Engine/project",
  "language": ["vi"],
  "engine_facts": {},
  "adapter_policy": {},
  "chunking": {},
  "normalization": {},
  "dialogue": {},
  "inline_cues": {},
  "synthesis": {},
  "provenance": []
}
```

## Field meanings

### `engine_facts`
Facts supported by code/config/docs. Examples:
- engine-side normalization;
- phonemization;
- hard/default input limits;
- supported inline tags;
- whether a style parameter is active;
- voice/reference behavior.

Do not put guessed writing preferences here.

### `adapter_policy`
Story-surface policy inferred for reliable narration. These are adapter choices, not engine claims.
Suggested fields:
- `preferred_sentence_chars_min`
- `preferred_sentence_chars_max`
- `soft_sentence_chars_max`
- `merge_tiny_sentences_below_chars`
- `prefer_one_main_idea_per_sentence`
- `preserve_paragraph_rhythm`
- `avoid_markdown`
- `avoid_parenthetical_asides`

### `chunking`
Required:
- `hard_max_chars`
- `preferred_chunk_chars_min`
- `preferred_chunk_chars_max`
- `avoid_chunk_below_chars`
- `split_priority`: ordered list such as `paragraph`, `sentence`, `clause`, `hard`.

The hard limit must be based on the engine/project when known. Preferred values may be conservative adapter policy.

### `normalization`
Describe what the adapter should normalize versus what the engine already handles.

### `dialogue`
Example fields:
- `keep_quotes`
- `merge_tiny_reply_with_narration`
- `speaker_labels`

### `inline_cues`
Example:
```json
{
  "supported": true,
  "experimental": true,
  "allowed": ["[cười]"],
  "default_usage": "off"
}
```

### `synthesis`
Describe whether the engine should normally receive the full adapted text and perform its own chunking, or whether external chunks are the primary synthesis input.

### `provenance`
Each item should record:
- source URL/path;
- type such as `code`, `config`, `documentation`;
- short claim extracted from it.

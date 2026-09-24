# Building a TTS profile

## Extraction checklist

Inspect, in this order when available:
1. runtime inference code;
2. configuration defaults;
3. text normalizer/phonemizer/chunker;
4. API schema;
5. official examples;
6. README/docs;
7. issues only when needed to identify practical failure modes.

Extract:
- input language/script expectations;
- normalization ownership;
- phonemization ownership;
- hard/default chunk or character limits;
- pause behavior exposed through punctuation or gap handling;
- supported SSML or inline tags;
- speaker/style/emotion controls;
- multi-speaker support;
- known failure modes for short/long text;
- output/synthesis constraints relevant to text preparation.

## Fact vs policy

Always distinguish:

**Engine fact**
A behavior explicitly visible in code/config/docs.

**Adapter policy**
A conservative text-writing choice derived from the fact.

Example:
- Fact: engine defaults to `max_chars=256`.
- Policy: target substantially shorter natural sentences and keep chunk preferred max below 256 so engine splitting is less likely to cut awkwardly.

Do not present adapter policy as an engine requirement.

## Profile selection

Prefer one profile per materially different text-processing path, not one profile per voice. A voice is normally a runtime option unless it changes text syntax or supported controls.

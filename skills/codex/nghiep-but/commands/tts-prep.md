# Step 7: TTS Prep (optional)

Goal: convert the finished story into a TTS-ready reading script for a chosen engine.

## Before executing
1. Scan tts-profiles/ for available profiles (ignore _schema.md and _template.md).
2. If ZERO profiles exist: tell the user, offer to run tts-profile-create first.
3. If ONE profile exists: use it, mention which one.
4. If MULTIPLE profiles exist: ASK the user which profile to use (permitted pause). List them.

Then read the chosen tts-profiles/<name>.md.

## Process (apply the chosen profile's rules exactly)
Transform workspace/<slug>/story.md into a TTS reading script:
1. Strip forbidden_chars listed in the profile (markdown, decorative quotes, brackets...).
2. Apply number normalization per profile (convert digits to words if required).
3. Expand abbreviations per profile.
4. Apply currency/unit handling per profile.
5. Handle pauses per profile.pause_method (do NOT inject syntax the profile doesn't support).
6. If multi_voice = no: add light speaker attributions only where a single narrator would be confusing.
7. Chunk the text per profile.max_chars and split_strategy. Mark chunk boundaries clearly, e.g.:
   `===== CHUNK 1/ N =====`
   so the user can feed each chunk to the engine in order. If max_chars = 0, output as one piece.

## Preserve the drama
- Keep the cold closing line (F12) on its own line, preceded by a blank line.
- Keep "silence before storm" beats (P7) as their own short paragraph.
- Do not merge short punchy sentences into long ones — TTS pacing depends on them.

## Output
Save to workspace/<slug>/tts_<profile>.md
Print only:
```
Da tao ban TTS (<profile>): workspace/<slug>/tts_<profile>.md
- So chunk: <n>
- Do dai uoc tinh: <phut> phut  (dua tren ~140 chu/phut)
```

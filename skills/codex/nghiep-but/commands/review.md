# Step 5: Review

## Before executing
Read: references/anti-ai-checklist.md + references/golden-patterns.md

## Automated pre-check (text only)
Run the quality script on the draft FIRST (it checks story text only, ignores TTS):
```
python3 scripts/quality_check.py workspace/<slug>/story.md
```
Fix every [FAIL]. Review every [WARN]. Then continue with manual review.

## 7-dimension review
1. Satisfaction peaks: Count >=4? If <4, add.
2. Evidence chain: Every victory backed by physical evidence?
3. Anti-AI taste: Run full checklist. Flag and fix violations.
4. Dialogue differentiation: Speakers identifiable without tags?
5. Pacing: Hook grabs in 3 sentences? Paragraphs <=150 words? Cold line <=15 words?
6. POV consistency: Protagonist knows only what they should? No mind-reading?
7. Emotional arc: shock/anger -> cold determination -> calm execution -> quiet satisfaction (NOT melodrama)

## Silent output
Do NOT print the story or full report to chat. Apply fixes in place.
Print only a one-line result:
```
Review: PASS (<n> WARN da xu ly) | hoac | Review: da sua <n> loi FAIL
```

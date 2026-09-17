# Test plan

## Deterministic smoke test (no model/API)

Run:

```bash
python3 scripts/smoke_test.py
```

It creates a temporary 3-chapter fake project, exercises checkpoints, review gates, context packing, SHA-256 sync detection, TXT/EPUB export, project validation and resume. This validates the deterministic layer only; it does not judge prose quality.

## Agent-mediated 3-5 chapter acceptance test

Use the host agent's already-available model, with no network/provider setup:

1. Start: `ainovel "Truyện huyền bí 4 chương về một thủ thư phát hiện thành phố mất ký ức mỗi nửa đêm"`.
2. Assert foundation files exist and only the active arc is detailed.
3. Write chapter 1 through plan -> draft -> consistency -> commit -> seven-dimension review.
4. Enable `ainovel review on`; confirm the workflow pauses after chapter 1 and `ainovel next` releases exactly one new chapter.
5. During chapter 2, issue a Steer: `Từ giờ giảm exposition, cho người bạn thân trở nên đáng ngờ nhưng chưa phản bội.` Confirm a durable directive/plan delta is persisted.
6. After chapter 2 draft checkpoint, terminate the CLI. Start a new session and ask `ainovel continue`; confirm resume starts at consistency rather than drafting chapter 2 again.
7. Manually edit one committed chapter. Run `ainovel sync --check`; confirm dirty hash is detected without mutation. Then run normal sync and confirm semantic state is rebuilt before hash acceptance.
8. Finish chapters 3-4. At the arc boundary, confirm an aggregate `scope=arc` seven-dimension review is accepted before the arc summary is written; then verify arc/volume summaries and completion state.
9. Run `ainovel export ./exports/test.txt` and `ainovel export ./exports/test.epub`.
10. Validate both outputs, including EPUB ZIP structure and TOC.

## Pass criteria

- zero API/provider configuration requested
- every logical step checkpointed
- resume is exact
- all seven review dimensions present with evidence
- rolling planning expands only when needed
- context pack stays bounded
- Steer, review mode, co-create/import/sync/reopen intents route correctly
- TXT and EPUB open successfully

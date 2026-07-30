---
name: deep-analysis
description: "Áp dụng 7 rule phân tích chuyên sâu TRƯỚC KHI code: trace callers & flow end-to-end, xác định root cause (không chỉ symptom), forced 3-option cho mọi quyết định >5 dòng, self-critique edge case, kiểm tra constraint layer của data model/event/init, đánh giá undo cost trước khi edit, đọc pattern (không chỉ lines). USE WHEN: bug fix, planning tính năng mới, code review, audit, refactor, hoặc bất kỳ task nào cần hiểu sâu trước khi viết code. Không dùng: task đơn giản 1-3 dòng, hotfix khẩn cấp đã rõ root cause. Invoke: /deep-analysis [mô tả task]"
user-invocable: true
argument-hint: "[task/mô tả vấn đề cần phân tích]"
allowed-tools: Read, Glob, Grep, Bash, Edit, Write
related: [gdd-spec-retrieval, controller-flow-design, logic-self-test]
---

# Deep Analysis Protocol

Bộ 7 rule buộc agent **hiểu rồi mới code** — không đoán, không viết theo symptom, không chạm file khi chưa trace đủ. Áp dụng trước mọi quyết định >5 dòng code, bug fix, hoặc planning tính năng mới.

---

## Rule 1: Trace before touch

Không đọc 1 file rồi kết luận. Trước khi viết code:

1. **Grep callers** của function/class sắp sửa — biết ai gọi nó, ai bị ảnh hưởng
2. **Trace chain đầy đủ**: entry point → middleware → logic → storage (nếu có)
3. Nếu touch base code (`Toppic/`, `Base/`): đọc AGENTS.md + convention của base trước

**Why**: Một fix trong shared function ảnh hưởng tới N callers. Nếu chỉ nhìn 1 file rồi sửa, bạn đang tạo N-1 bugs còn lại.

**Check**: Nếu chưa grep callers → chưa đủ điều kiện propose solution.

---

## Rule 2: Root cause, not report

Bug report là **symptom**, không phải cause. Trước khi fix:

1. Xác định: bug này reproduce ở 1 path hay tất cả paths gọi tới đây?
2. Nếu shared function lỗi → fix shared function, không fix từng caller
   - *Ponytail ladder*: guard ở shared function là diff nhỏ hơn guard ở mọi caller
3. Nếu fix caller → chứng minh bằng grep rằng các callers khác không bị

**Output mặc định** khi fix bug:
```
Root cause: X
Other affected paths: Y, Z (đã kiểm tra, không bị / đã fix cùng lúc)
```

---

## Rule 3: 3-option forced

Mọi quyết định > 5 dòng code phải cân nhắc **đúng 3 options**:

| Option | Triết lý |
|--------|----------|
| **A — Nhanh nhất** | Code ngay, ít suy nghĩ nhất, dirty nhưng chạy được |
| **B — Đúng nhất** | An toàn, maintainable, handle edge case, đúng architectural pattern |
| **C — Ít code nhất** | Lazy nhưng vẫn đúng — 1 guard thay vì refactor, dùng stdlib, xoá được code chết |

Chọn **1 cái**, giải thích ngắn vì sao 2 cái kia không được chọn.

**Exception**: Hotfix khẩn cấp (production đang chết) → Option A được phép không giải thích. Ghi rõ `// ponytail: hotfix, cần refactor sau`.

---

## Rule 4: Self-critique edge case

Sau khi viết solution (trước khi kết luận hoặc tạo diff), tự trả lời 2 câu:

1. **"What breaks if input is X?"** — X là input/edge case tồi tệ nhất tìm được
   - null, empty, âm, max value, concurrent call, replay event, state chưa init...
2. **"What's the smallest thing that could be deleted and this still works?"**
   - Nếu xoá được 1 biến, 1 if, 1 region mà vẫn đúng → xoá nó

**Không viết** vào output nếu câu trả lời là "nothing" (tức solution đã ổn). Chỉ viết ra nếu phát hiện vấn đề thật.

---

## Rule 5: One constraint layer deeper

Yêu cầu nói "thêm tính năng A" → tự suy ra **3 câu hỏi constraint**:

1. **Data model**: A có consistent với schema / class hierarchy hiện tại không?
   - Field mới có làm invalid state cũ không?
   - Serialized field có cần migrate prefab/scene không?
2. **Event flow**: A có conflict với event lifecycle hiện tại không?
   - Có event nào bắn sai thời điểm không? Subscribe/Unsubscribe có đối xứng?
   - Có gọi controller khác trong `Initialized` thay vì `PostInitialized` không?
3. **Init lifecycle**: A có require thay đổi trình tự init / thêm follower mới không?
   - Nếu thêm follower → đã wire vào Root chưa? Đã kéo ref Inspector chưa?

**Nếu không dám chắc**: hỏi 1 câu duy nhất, không tự guess rồi sai. Câu hỏi phải specific:
- ❌ "Có cần migrate gì không?" (quá chung)
- ✅ "Field `_itemId` mới — có prefab nào ngoài kia cần update không?" (specific, grep ra được)

---

## Rule 6: The "undo" preview

Trước khi edit file (thực tế gọi tool Edit/Write), lượng giá **undo cost**:

| Undo cost | Hành động |
|-----------|-----------|
| **< 1 phút** | 1 file, 1 function, không đụng base → cứ triển |
| **1-5 phút** | 1 file, nhiều functions, hoặc đụng base nhẹ → grep double-check trước khi edit |
| **> 5 phút** | Nhiều files, đụng prefab/asset, đụng base sâu, đổi API → **phải hỏi user confirm** |

**Công thức lượng giá nhanh**: `số files x số điểm chạm x 10s`

---

## Rule 7: Read pattern, not lines

Khi đọc code (trong bất kỳ task nào), trả lời 3 câu **trong đầu**:

1. **Pattern này là gì?**
   - Observer? Strategy? State Machine? Command? Component?
2. **Variant nào trong codebase?**
   - `EventManager` observer vs C# event vs UnityEvent?
   - `BaseBehaviour` MonoBehavior vs pure POCO?
   - Init 2-pha (OnControllerReady + OnInitController) hay 1 pha?
3. **Nếu viết tiếp: follow pattern hay break?**
   - Follow → code tự nhiên khớp với conventions
   - Break → cần chứng minh pattern hiện tại không đủ, hoặc sẽ gây hại

**Output**: Chỉ viết ra nếu pattern bị break (giải thích lý do) hoặc có conflict giữa 2 patterns. Nếu follow đúng pattern → không cần mention.

---

## Quy trình áp dụng

```
Step 1: Nhận task / bug report
Step 2: Rule 1 (trace) — grep callers, đọc chain, đọc convention nếu touch base
Step 3: Rule 2 (root cause) — xác định gốc, kiểm tra paths khác
Step 4: Rule 5 (constraint) — kiểm tra data model, event flow, init lifecycle
Step 5: Rule 7 (pattern) — xác định pattern cần follow
Step 6: Rule 3 (3-option) — chọn approach
Step 7: Code + Rule 4 (self-critique) — verify edge case
Step 8: Rule 6 (undo) — trước khi gọi Edit/Write
```

**Không phải step nào cũng cần output riêng**. Chỉ viết output ở Step 3 (root cause) và Step 6 (3-option + chọn). Các step còn lại chạy trong đầu trừ khi phát hiện vấn đề.

---

## Khi nào dùng toàn bộ rule / rút gọn

| Loại task | Áp dụng |
|-----------|---------|
| Bug fix production | 1+2+4+6 |
| Planning feature mới | 1+3+5+7 |
| Code review | 2+4+7 |
| Refactor | 1+3+6+7 |
| Hotfix (< 5 dòng, rõ cause) | Chỉ 6 (undo check) |
| Task đơn giản (thêm field, rename) | Bỏ qua, không cần skill này |

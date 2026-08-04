---
name: logic-self-test
description: >-
  Tự kiểm tra (self-test) logic plan hoặc code sau khi lập plan/implement.
  Cung cấp 2 cấp độ: basic (kiểm tra nhanh các vấn đề chính) và advanced (phân tích sâu toàn diện).
  Sử dụng skill này khi người dùng nói "self-test", "review logic", "kiểm tra plan", "phân tích rủi ro",
  "tự kiểm tra", "self review", "soát plan", "review hộ", "kiểm tra hộ", "test logic", "soát lại",
  hoặc bất kỳ yêu cầu nào muốn agent kiểm tra lại tính đúng đắn, hiệu năng, độ mở rộng của plan/logic.
  Luôn hỏi user muốn dùng basic hay advanced mode trước khi bắt đầu.
---

# Logic Self-Test

Skill này thực hiện tự kiểm tra (self-test) logic của plan hoặc code sau khi lập plan hoặc implement. Mục tiêu là phát hiện rủi ro, điểm yếu về hiệu năng, độ mở rộng, readability, và đưa ra đề xuất cải thiện — **mà không tự ý implement code**.

## Khi nào dùng skill này

- User nói "self-test plan này hộ tôi"
- User nói "phân tích rủi ro của logic này"
- User nói "soát lại xem có thiếu edge case gì không"
- User muốn kiểm tra tính đúng đắn, hiệu năng, maintainability
- **Bất kỳ khi nào user yêu cầu review/kiểm tra plan/logic**, dù từ ngữ có thể khác

## Luật quan trọng

1. **KHÔNG tự ý implement code.** Nếu phát hiện vấn đề cần sửa, chỉ report và đề xuất hướng giải quyết. Không đụng vào file code trừ khi user yêu cầu.
2. **Tôn trọng base code.** Nếu phát hiện plan/logic vi phạm quy tắc project (VD: sửa base code chung), phải đánh dấu là rủi ro và đề xuất giải pháp thay thế (extend, event, override).
3. **Nếu chưa có plan/session context**, hãy hỏi user cung cấp requirement hoặc plan trước khi bắt đầu.

## Chọn cấp độ

Luôn hỏi user: `"Bạn muốn dùng Basic hay Advanced mode?"`

| Cấp độ | Phù hợp | Thời gian |
|--------|---------|-----------|
| **Basic** | Plan/logic đơn giản, ít rủi ro, hoặc user chỉ cần check nhanh | ~1-2 phút |
| **Advanced** | Plan/logic phức tạp, nhiều thành phần, cần phân tích sâu | ~3-5 phút |

**Nếu user không biết chọn gì**: đề xuất dựa trên độ phức tạp bạn thấy. Khi nghi ngờ, hỏi thêm.

---

## Basic Mode

Kiểm tra nhanh trên 4 khía cạnh với các ví dụ từ thông thường đến edge case.

### 1. Correctness
- Kiểm tra logic có đúng với requirement không
- Đưa ra **tối thiểu 3 ví dụ**: từ trường hợp thông thường → đặc biệt → hiếm/edge
- Với mỗi ví dụ, chỉ ra input, expected behavior, và phân tích

### 2. Hiệu năng (sơ bộ)
- Chỉ kiểm tra các vấn đề hiệu năng rõ ràng (n+1 query, loop vô hạn, redundant calculation)
- Bỏ qua các tối ưu vi mô

### 3. Độ mở rộng & readability
- Code/logic có dễ đọc không?
- Có đang dùng pattern phù hợp không? (YAGNI, KISS)
- Có vi phạm project conventions không?

### 4. Rủi ro & đề xuất
- Xác định rủi ro chính (nếu có)
- Đề xuất hướng giải quyết và lợi ích sau khi cải thiện

---

## Advanced Mode

Phân tích toàn diện, chi tiết hơn Basic trên tất cả các khía cạnh.

### 1. Correctness (deep)
- Phân tích logic một cách có hệ thống
- Đưa ra **tối thiểu 5 ví dụ**: thông thường (2), đặc biệt (2), hiếm/edge (1+)
- Với mỗi ví dụ: input, expected output, phân tích luồng xử lý step-by-step
- Kiểm tra: boundary conditions, null/empty states, race conditions, concurrent access
- Check consistency với requirement gốc

### 2. Hiệu năng (chi tiết)
- Time complexity của từng phần
- Memory/resource usage
- Bottleneck tiềm năng
- Profiling strategy nếu cần optimize
- **Không** tối ưu hóa sớm — đánh giá dựa trên mức độ critical của code path

### 3. Bảo mật (nếu liên quan)
- Input validation
- Authorization/access control
- Data leakage
- Trust boundary check

### 4. Độ mở rộng
- Coupling giữa các module
- Dependency injection phù hợp chưa?
- Có dễ thêm tính năng mới không?
- Interface/abstraction có phù hợp không?
- **Chú ý**: Không tạo interface một implementation, không factory cho một product

### 5. Maintainability
- Readability: tên biến, function, structure
- Code organization
- Error handling có đầy đủ không?
- Logging/debuggability
- Testability

### 6. Risk Assessment
- **Rủi ro**: mô tả cụ thể
- **Ảnh hưởng**: nếu rủi ro xảy ra thì hậu quả gì
- **Recommend**: hướng giải quyết
- **Kết quả cải thiện**: sau khi giải quyết thì được gì

### 7. Improvement Suggestions
- Ưu tiên cao → thấp
- Mỗi suggestion kèm lý do và expected impact
- Nếu suggestion liên quan tới việc sửa base code, đánh dấu **cần confirm user**

---

## Output Structure

Bắt buộc theo format sau. Dùng tiếng Việt nếu user nói tiếng Việt, dùng tiếng Anh nếu user nói tiếng Anh.

```
# Self-Test Report: [Tên Plan/Feature]
Level: Basic / Advanced

## 1. Correctness Check
- Ví dụ 1: [thông thường] → ...
- Ví dụ 2: [đặc biệt] → ...
- Ví dụ 3: [edge case] → ...
- Kết luận: ✅ OK / ⚠️ Có vấn đề

## 2. Performance & Optimization [Basic: chỉ vấn đề rõ ràng | Advanced: chi tiết]
...

## 3. Extensibility & Maintainability
...

## 4. Risk Assessment [Advanced: có ảnh hưởng, recommend, kết quả cải thiện]
...

## 5. Improvement Suggestions
- [Priority] [Mô tả] — Expected impact
```

**Nếu mọi thứ OK**, vẫn giữ các section nhưng ghi rõ "Không phát hiện vấn đề" để user biết đã được kiểm tra kỹ.

---

## Ví dụ template Basic Report

```
# Self-Test Report: User Login Flow
Level: Basic

## 1. Correctness Check
- Ví dụ 1 (thông thường): User nhập đúng email/password → login thành công, redirect dashboard. OK.
- Ví dụ 2 (đặc biệt): User nhập sai password 5 lần → tài khoản bị lock sau lần thứ 5. Cần confirm: hiện tại logic lock ngay sau lần thứ 3?
- Ví dụ 3 (edge case): User nhập email với khoảng trắng đầu/cuối → Có trim không? Nếu chưa → rủi ro false negative.
- Kết luận: ⚠️ Có vấn đề cần confirm ở example 2, 3

## 2. Performance
- Không phát hiện vấn đề hiệu năng rõ ràng.

## 3. Extensibility & Maintainability
- Flow đang được implement trong 1 class duy nhất. Nên tách validation ra riêng nếu có thêm OAuth providers sau này.

## 4. Risk Assessment
- **Rủi ro**: Không trim email → user có email hợp lệ nhưng thừa khoảng trắng sẽ không login được.
  - **Ảnh hưởng**: User frustration, support tickets
  - **Recommend**: Thêm trim() ở input validation layer
  - **Kết quả**: Giảm support tickets ~10-20% cho login issues

## 5. Improvement Suggestions
1. [High] Trim email input — ngăn false negative login, chi phí thấp.
2. [Medium] Tách validation khỏi login handler — dễ maintain khi thêm OAuth.
```

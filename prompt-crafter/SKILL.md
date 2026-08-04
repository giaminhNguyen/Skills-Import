---
name: prompt-crafter
description: >
  Skill chuyên viết prompt tiếng Việt cho coding agent (OpenCode, Claude Code,
  Cursor, Copilot, hay bất kỳ AI code agent nào). Dùng skill này khi người dùng:
  nói "viết prompt", "tạo prompt", "cần prompt cho...", "làm hộ prompt",
  "refine prompt", "sửa prompt", "cleanup prompt", "prompt engineering",
  "cách nói cho agent hiểu"; hoặc khi người dùng mô tả một task phức tạp muốn
  giao cho agent nhưng chưa biết diễn đạt thế nào, cần chuyển ý tưởng thành
  prompt có cấu trúc. Cũng kích hoạt khi user nói "tôi cần agent làm X" hay
  "viết câu lệnh cho agent". Luôn ưu tiên skill này khi thấy user vật lộn với
  việc diễn đạt yêu cầu kỹ thuật.
---

# prompt-crafter: Viết prompt tiếng Việt cho coding agent

## Mục đích

Skill này giúp bạn viết prompt rõ ràng, có cấu trúc, tối đa khả năng agent hiểu đúng ý bạn. Prompt tốt = agent làm đúng ngay lần đầu, đỡ tốn thời gian refine.

## Khi nào dùng skill này

- Bạn cần viết prompt từ đầu cho 1 task
- Bạn có 1 prompt đang dùng nhưng agent toàn hiểu sai — cần sửa
- Bạn có ý tưởng trong đầu nhưng chưa biết diễn đạt sao cho agent hiểu
- Bạn muốn học cách viết prompt hiệu quả

## Workflow

### Bước 1: Hỏi clarify (chủ động)

Trước khi viết, hỏi 2-3 câu để chắc chắn hiểu đúng. Các câu hỏi mẫu:

- "Task này chạy trên nền tảng gì? (Unity, web, CLI...)"
- "Agent cần biết thêm context gì về codebase hiện tại không?"
- "Kết quả mong đợi là gì? (code hoàn chỉnh, giải thích, sửa bug...)"
- "Có ràng buộc gì không? (performance, coding style, thư viện được phép dùng...)"

**Chỉ hỏi nếu thông tin chưa rõ.** Nếu user đã nói rõ ràng thì viết luôn.

### Bước 2: Viết prompt

Dùng cấu trúc bên dưới. Viết bằng **tiếng Việt**, trừ khi:
- Tên hàm, class, biến, command — giữ nguyên tiếng Anh
- Technical term quen thuộc (API, framework, bug, commit, deploy...) có thể giữ tiếng Anh

### Bước 3: Refine (nếu cần)

Nếu user bảo "sửa prompt này", "refine", "vẫn chưa được":
1. Đọc prompt cũ + feedback của user
2. Xác định chỗ nào mơ hồ / thiếu / thừa
3. Viết lại prompt mới

## Cấu trúc prompt chuẩn

Mỗi prompt viết ra nên có đủ các phần sau (theo thứ tự):

```
## Context
[Bối cảnh: dự án gì, đang ở đâu, công nghệ gì, codebase thế nào]

## Goal
[Mục tiêu cụ thể cần làm]

## Constraints
[Ràng buộc: coding convention, thư viện, performance, security...]

## Output format
[Định dạng đầu ra mong đợi: code, giải thích, file list, commit message...]
```

Không nhất thiết phải viết đúng heading đó — có thể viết dạng văn xuôi, nhưng thông tin phải đủ 4 phần.

## Nguyên tắc viết prompt

### 1. Càng cụ thể càng tốt
- Sai: "Sửa cái bug trong code"
- Đúng: "Script `PlayerHealth.cs` dòng 47, `TakeDamage()` không check `isDead` trước khi trừ máu, gây âm HP"

### 2. Cho agent biết nó cần biết gì
- File path, function name, class name đầy đủ
- Nếu có 2 function giống tên, chỉ rõ file nào
- Codebase pattern nếu có (ví dụ: "project dùng MVP pattern, logic trong Service layer")

### 3. Nói cả cái KHÔNG làm
- "Không dùng thư viện ngoài"
- "Không sửa file khác ngoài file được chỉ định"
- "Không dùng `async void`"

### 4. Output format = giới hạn phạm vi
- "Chỉ trả về code block, không giải thích"
- "Trả về dạng bullet points"
- "Viết commit message theo format feat/fix/chore"

### 5. Ưu tiên hành động hơn mô tả
- Thay vì "có vẻ chậm" → "Hàm X gọi database 50 lần trong 1 frame, cần gộp thành 1 query"

### 6. Technical term chuẩn xác
- Unity: "script execution order", "coroutine", "FixedUpdate" — không viết lung tung
- Git: "squash commit", "rebase", "cherry-pick"

## Ví dụ

**User nói:** "Tôi cần 1 script PowerShell xóa file .log cũ hơn 7 ngày trong thư mục C:\Logs"

**Prompt viết ra:**

```
## Context
Windows PowerShell 5.1. Thư mục chứa log: C:\Logs. File đuôi .log, tên dạng app-YYYYMMDD.log.

## Goal
Viết script PowerShell xóa tất cả file .log trong C:\Logs có ngày sửa đổi (LastWriteTime) cũ hơn 7 ngày tính từ hôm nay.

## Constraints
- Chỉ xóa file .log, không động vào file khác
- Ghi log các file đã xóa ra console
- Có $WhatIfPreference = "Continue" hỗ trợ dry-run mode (tham số -WhatIf)
- Không cần admin rights, chạy user thường là đủ

## Output format
Script PowerShell hoàn chỉnh, có comment, kèm 1 dòng cách dùng.
```

**User nói:** "Agent toàn hiểu sai khi tôi bảo sửa bug"

**Prompt refine:**

```
Vấn đề hiện tại:
- Mỗi lần tôi mô tả bug, agent sửa sai chỗ hoặc sửa thiếu
- Tôi đã thử nói chi tiết hơn nhưng vẫn không cải thiện

Nguyên nhân có thể:
- Tôi chỉ mô tả symptom ("HP bị âm"), không nói root cause
- Tôi không nói file nào, dòng nào
- Tôi không cho agent biết codebase dùng pattern gì

Yêu cầu: Với mỗi bug, tôi cần 1 template prompt có sẵn các mục để điền. Giúp tôi tạo template đó.
```

Luôn đặt mình vào vị trí agent: **agent có đủ thông tin để làm đúng ngay lần đầu không?** Nếu câu trả lời là "chưa chắc" → bổ sung thêm.

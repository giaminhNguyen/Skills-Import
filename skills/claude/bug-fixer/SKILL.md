---
name: bug-fixer
description: "Nhận bug tester báo (ID + tiêu đề, file danh sách bug, kèm ảnh/video/log) → trace root cause → fix → commit git sau khi user xác nhận. USE WHEN người dùng nói: fix bug, sửa bug, tester báo lỗi, bug 6730, list bug, bug sheet, lỗi QA, 'cái này bị lỗi chỗ ...', hoặc paste một danh sách bug. Invoke: /bug-fixer [ID + tiêu đề bug | đường dẫn file danh sách bug]."
user-invocable: true
argument-hint: "[ID + tiêu đề bug] hoặc [đường dẫn file danh sách bug]"
allowed-tools: Read, Glob, Grep, Write, Edit, Bash
related: [ponytail, deep-analysis, logic-self-test]
---

# Bug Fixer

Nhận bug do tester báo — thường chỉ có ID và một dòng tiêu đề — trace tới **root cause**,
fix, rồi **commit sau khi người dùng xác nhận**.

Bản user-scope: **không giả định project nào**. Bước đầu tiên luôn là đọc rule của project
hiện tại (`CLAUDE.md` ở root + các `CLAUDE.md` con trong thư mục liên quan) và tuân theo
chúng — chúng thắng mọi mặc định trong file này.

## Input — 3 dạng

| Dạng | Ví dụ | Xử lý |
|---|---|---|
| Paste text | `6730 - Coin không cộng sau khi xem ads` | Parse ID + tiêu đề. Mỗi dòng một bug. |
| File danh sách | `.md` / `.csv` / `.txt` tester xuất | Read file → parse thành bảng bug → xử lý lần lượt. |
| Ảnh / video / log | screenshot, clip, log editor/console | Ảnh: Read trực tiếp. Video: không xem được → xin ảnh cắt frame hoặc mô tả. Log build fail rất lớn → dùng skill chuyên đọc log nếu project có, không đọc tràn cả file. |

Không có ID (tester mô tả bằng lời) vẫn chạy bình thường — xem phần commit message.

## Bước 0 — Rule project + bảng bug

1. Đọc `CLAUDE.md` của project hiện tại. Ghi nhận: ngôn ngữ trả lời, thư mục base/dùng chung
   không được tự sửa, convention bắt buộc (naming, pooling, anim, tooltip...), skill bắt buộc
   phải chạy kèm.
2. In bảng `ID | Tiêu đề | Nguồn | Trạng thái`, trạng thái khởi tạo `TODO`. Nhiều bug →
   **fix tuần tự từng bug**, không nhảy qua lại, không gộp diff nhiều bug rồi mới kiểm.

## Bước 1 — Làm rõ, chỉ khi thật sự cần

Tiêu đề bug là **triệu chứng**. Trước khi sửa phải biết: bug ở màn/flow nào, lúc nào, điều
kiện gì.

- Tự grep ra được → tự tìm, **đừng hỏi**.
- Không tự tìm được và đoán sai sẽ fix nhầm chỗ (vd "số bị sai" mà có 3 chỗ hiển thị số đó)
  → hỏi đúng **một** câu gọn, kèm các khả năng đã khoanh được.
- Trace nghiêm túc rồi vẫn không định vị / không tái hiện được → `NEEDS-INFO` hoặc
  `CANNOT-REPRO`, ghi rõ đã tìm ở đâu, cần tester bổ sung gì. **Không fix mò.**

## Bước 2 — Trace root cause (không được rút gọn)

Khâu duy nhất không được lười.

- Grep **hết caller** của hàm/field sắp sửa. Ticket chỉ nhắc một path; caller anh em thường
  hỏng y hệt. Fix ở chỗ mọi caller đi qua, không vá từng path.
- Trace end-to-end: nguồn dữ liệu → nơi biến đổi → nơi hiển thị → event/callback liên quan.
- Bug về giá trị hiển thị: phân biệt **value logic sai** hay **chỉ hiển thị sai** (anim/tween
  chưa kill, snap sai, đọc nhầm giá trị trung gian) — hai nguyên nhân khác hẳn nhau.
- Bug phức tạp / đụng nhiều hệ thống / chưa chắc root cause → chạy skill `deep-analysis`
  trước khi viết dòng code nào.
- Nêu root cause thành **một câu** trước khi sửa. Không viết nổi một câu = chưa hiểu = trace tiếp.

## Bước 3 — Fix

Chạy skill `ponytail` trước khi chốt code (bắt buộc nếu project yêu cầu). Diff ngắn nhất, ít
file nhất, nhưng đặt đúng chỗ.

- Tuân thủ mọi convention đã ghi nhận ở Bước 0. Rule project **không** bị `ponytail` rút gọn mất.
- Thư mục base / code dùng chung / thư viện bên thứ ba: **confirm với user trước khi sửa**.
  Ưu tiên extend, event, partial, wrapper thay vì sửa base.
- Không tiện tay refactor, không dọn code lân cận, không đổi format file. Diff của một bug chỉ
  chứa thứ liên quan bug đó — đây là điều kiện để commit sạch ở Bước 5.
- File nhị phân / file do editor sinh (scene, prefab, `.asset`, designer file): **không sửa
  tay**. Đánh `NEEDS-MANUAL` và viết hướng dẫn từng bước cho user thao tác trong editor.

## Bước 4 — Verify

- Đọc lại diff, tự soát: hỏng caller nào khác không, case null/empty/lần chạy đầu, event có bị
  double-fire không.
- Có test tự động chạy được → chạy, dán kết quả thật. **Không suy đoán kết quả.**
- Không có test tự động → viết **test plan thủ công**: các bước tái hiện đúng như tester mô tả
  + 1–2 case lân cận dễ vỡ theo. Đánh số, ngắn gọn. Ghi rõ "chưa chạy thử, cần user verify".
- Diff đụng logic phức tạp → gợi ý chạy `logic-self-test`.

## Bước 5 — Git (luôn hỏi trước, không bao giờ tự commit)

1. **Không commit tự động.** Fix xong → in bảng tổng kết + danh sách file đã đổi → **hỏi user
   có commit không**. Chưa đồng ý thì không chạy `git commit`.
2. Trước khi hỏi: chạy `git status` và `git diff --stat`, in ra cho user. Working tree thường
   **đã có sẵn thay đổi không liên quan** — phải chỉ rõ file nào của bug, file nào có sẵn từ trước.
3. **Cấm `git add -A` / `git add .`** — chỉ `git add` từng file thuộc diff của bug. File mới có
   file phụ trợ đi kèm (vd `.meta` của Unity) thì add đủ cặp; công cụ chưa sinh ra file phụ trợ
   → báo user sinh xong rồi mới commit.
4. **Gộp hay tách commit: hỏi user mỗi lần chạy**, không mặc định.
   - Trước khi hỏi, chạy `git log --oneline -20` để lấy **convention message thật của repo**
     và đề xuất theo đúng convention đó (vd `Fix bug 6730,6734,6736`).
   - Mỗi bug 1 commit là lựa chọn còn lại (dễ revert từng bug).
   - Bug không có ID → mô tả ngắn tiếng Anh: `Fix coin not added after ads`.
   - Chỉ hỏi khi ≥ 2 bug; 1 bug thì commit thẳng theo convention repo.
5. Commit message bám phong cách repo: thường một dòng, tiếng Anh, không body dài dòng.
   **Tuyệt đối không thêm footer/trailer nào** — không `Co-Authored-By`, không
   `Generated with Claude Code`, không link, không emoji. Commit phải trông như do người dùng
   tự viết. Nếu môi trường mặc định gắn trailer, viết message qua `git commit -F` với nội dung
   đúng một dòng và kiểm lại bằng `git log -1 --format=%B` sau khi commit.
6. **Không tự push, không tạo/đổi branch, không amend, không rebase, không `git reset --hard`.**
7. Bug `NEEDS-INFO` / `CANNOT-REPRO` / `NEEDS-MANUAL` → **không đưa vào commit message** như
   đã fix.

## Bước 6 — Báo cáo cuối

| ID | Tiêu đề | Root cause (1 câu) | File đã sửa | Trạng thái |
|---|---|---|---|---|

Trạng thái hợp lệ: `FIXED` · `NEEDS-MANUAL` (cần thao tác tay trong editor) · `NEEDS-INFO`
(thiếu thông tin tester) · `CANNOT-REPRO` · `OUT-OF-SCOPE` (là design, không phải bug code).

Sau bảng: test plan thủ công gộp cho các bug đã fix + trạng thái git (đã commit hash nào, hay
đang chờ user xác nhận).

## Guardrail

- Không fix mò khi chưa định vị root cause.
- Không sửa code base dùng chung / thư viện bên thứ ba khi chưa confirm.
- Không sửa tay file do editor sinh (scene, prefab, asset nhị phân).
- Không commit khi user chưa đồng ý; không `git add -A`; không push.
- Không báo "đã test" khi chưa thực sự chạy.
- Không mở rộng scope: báo bug A thì chỉ fix A. Thấy bug B lân cận → ghi vào báo cáo, hỏi
  user, không tự fix kèm.

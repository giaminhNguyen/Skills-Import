---
name: viet-tieu-thuyet
description: Viết tiểu thuyết/truyện dài nhiều chương bằng tiếng Việt, KHÔNG giới hạn thể loại — ngôn tình, trọng sinh, xuyên không, trinh thám, kinh dị, khoa học viễn tưởng, tiên hiệp huyền huyễn, đời thường chữa lành, lịch sử cổ trang, v.v. Dùng skill này bất cứ khi nào người dùng muốn lên ý tưởng, xây dựng nhân vật/thế giới, viết outline, viết chương truyện, tiếp tục một truyện đang viết dở, hoặc chỉnh sửa/góp ý cho bản thảo truyện dài kỳ — kể cả khi họ không nói rõ thể loại hay chỉ mô tả một mảnh cốt truyện. Luôn kích hoạt skill này thay vì viết truyện ngẫu hứng không có cấu trúc khi phát hiện các tín hiệu trên.
---

# Viết Tiểu Thuyết — Hệ thống đa thể loại tiếng Việt

Skill này đóng gói quy trình viết truyện dài kỳ, tổ chức theo mô hình đã được kiểm
chứng ở thị trường web novel lớn: tách **quy trình vận hành** (`flows/`) khỏi **kỹ
thuật viết** (`guides/`), cộng thêm **khuôn mẫu tái dùng** (`templates/`) và **công cụ
chạy thật** (`scripts/`). Không khóa cứng thể loại; mọi cơ chế dùng chung, thể loại
và văn phong chỉ là tham số đầu vào.

## Quy trình 5 pha — trỏ tới flows/

Đọc file flow tương ứng khi bước vào mỗi pha. KHÔNG cần đọc trước tất cả.

1. **Pha 0 — Khởi tạo** → đọc `references/flows/pha0-khoi-tao.md`
   (kiểm tra dự án dở, nạp bộ nhớ sở thích)
2. **Pha 1 — Chọn thể loại + Hỏi đáp phân lớp** → `references/flows/pha1-hoi-dap.md`
3. **Pha 2 — Xây nền tảng** → `references/flows/pha2-nen-tang.md`
   (nhân vật, thế giới, dàn ý, guard rails, **thang văn phong**)
4. **Pha 3 — Viết từng chương (lặp)** → `references/flows/pha3-viet-chuong.md`
5. **Pha 4 — Hoàn thiện & xuất bản** → `references/flows/pha4-hoan-thien.md`

Hai file hạ tầng dùng chung ở nhiều pha:
- `references/flows/ha-tang-chung.md` — cấu trúc `project-state.json`, continuity-bridge,
  fact ledger, vé số/foreshadowing (chống mâu thuẫn xuyên chương).
- `references/flows/che-do-viet.md` — chế độ viết tuần tự / song song / nhóm agent.
- `references/flows/truyen-dai.md` — **chế độ truyện dài (≥50 chương)**: đọc ngữ cảnh
  phân tầng, quy hoạch cụm 50 chương, fact-lock chặn cứng (học từ MyNovel). Chỉ dùng
  khi truyện dài; truyện ngắn/vừa bỏ qua cho nhẹ.

## Kỹ thuật viết — trỏ tới guides/

Đọc khi cần nâng chất lượng ở Pha 2–3:
- `references/guides/the-loai.md` — quy ước, nhịp độ, motif, độ dài & văn phong mặc
  định của từng nhóm thể loại.
- `references/guides/van-phong.md` — thang chất Trung Quốc / mượt tiếng Việt (mặc định
  **TQ 95 / Việt 90**), cách giữ đặc sản TQ mà không rơi vào lỗi dịch máy.
- `references/guides/ky-thuat-chuong.md` — mở đầu, nhịp độ, giữ giọng nhân vật, tránh văn AI.
- `references/guides/hook.md` — 10 kiểu hook cuối chương, cách dùng theo thể loại.
- `references/guides/kiem-tra-chat-luong.md` — 8 trục tự kiểm tra trước khi giao chương.

## Khuôn mẫu — trỏ tới templates/

Dùng làm khuôn khi tạo file nền tảng ở Pha 2:
- `references/templates/nhan-vat-template.md` — hồ sơ nhân vật.
- `references/templates/dan-y-template.md` — dàn ý theo bảng.
- `references/templates/chuong-template.md` — cấu trúc file chương + khuôn project-state.json.

## Công cụ — scripts/ (code chạy thật)

- `scripts/consistency_check.py` — quét toàn bộ chương + project-state.json, phát hiện
  mâu thuẫn fact ledger, vi phạm guard rail, vé số chưa trả, nhân vật lạ. Dùng ở Pha 3–4.
- `scripts/check_ai_patterns.py` — phát hiện "mùi AI": câu phủ định-khẳng định, sáo ngữ
  mòn, lỗi dịch máy, mật độ so sánh quá dày (học từ oh-story). Dùng ở Pha 3.
- `scripts/build_epub.py` — đóng gói bộ truyện thành ebook EPUB 3 hợp lệ (chỉ dùng thư
  viện chuẩn, không cần cài gì). Dùng ở Pha 4.
- `scripts/check_wordcount.py` — kiểm tra số từ một chương so với khoảng mục tiêu. Pha 3.
- `scripts/trigger-eval.json` — bộ test triggering (12 ca) để kiểm chứng khi chỉnh skill.

## Nguyên tắc xuyên suốt
- Luôn cho người dùng xác nhận khung ở cuối Pha 2 trước khi viết chương 1.
- Mỗi chương: continuity-bridge trước → viết → tự kiểm tra (8 trục) → cập nhật state.
- Văn phong mặc định TQ 95/Việt 90 cho ngôn tình/trọng sinh/tiên hiệp; trục "mượt tiếng
  Việt" luôn ≥ 90 cho mọi thể loại.
- Góp ý luôn chỉ vị trí cụ thể, không nói chung chung.

---
name: viet-tieu-thuyet
description: Viết tiểu thuyết/truyện dài nhiều chương bằng tiếng Việt, KHÔNG giới hạn thể loại — ngôn tình, trọng sinh, xuyên không, trinh thám, kinh dị, khoa học viễn tưởng, tiên hiệp huyền huyễn, đời thường chữa lành, lịch sử cổ trang, v.v. Dùng skill này bất cứ khi nào người dùng muốn lên ý tưởng, xây dựng nhân vật/thế giới, viết outline, viết chương truyện, tiếp tục một truyện đang viết dở, hoặc chỉnh sửa/góp ý cho bản thảo truyện dài kỳ — kể cả khi họ không nói rõ thể loại hay chỉ mô tả một mảnh cốt truyện. Luôn kích hoạt skill này thay vì viết truyện ngẫu hứng không có cấu trúc khi phát hiện các tín hiệu trên.
---

# Viết Tiểu Thuyết — Hệ thống tổng hợp đa thể loại

Skill này gộp lại cơ chế hiệu quả nhất được đúc kết từ nhiều dự án viết truyện AI khác nhau (hỏi-đáp phân lớp, bộ nhớ sở thích, world bible, fact ledger chống mâu thuẫn, continuity-bridge, hook bắt buộc, hệ thống polish, phản hồi cụ thể theo vị trí, nhiều chế độ viết) — nhưng **không khóa cứng vào một thể loại**. Thể loại chỉ là một tham số đầu vào, mọi cơ chế còn lại dùng chung.

## Bản đồ hệ thống

```
Pha 0: Khởi tạo
   → xác lập thư mục dự án + đọc project-state.json / user-preferences.md nếu có
Pha 1: Chọn thể loại + Hỏi đáp phân lớp
   → tham khảo references/genres.md
Pha 2: Xây nền tảng (thế giới, nhân vật, guard rails, dàn ý)
   → tham khảo references/world-and-characters.md
Pha 3: Viết từng chương (lặp lại)
   → continuity-bridge + fact ledger: references/continuity-fact-ledger.md
   → kỹ thuật viết: references/chapter-craft.md
   → tự kiểm tra chất lượng: references/quality-checklist.md
Pha 4: Hoàn thiện & xuất bản
```

Chế độ viết (serial / song song / nhóm agent) xem `references/writing-modes.md` — chọn ở cuối Pha 2.

---

## Pha 0 — Khởi tạo

1. **Xác lập thư mục dự án** — mọi file của truyện (`00-nhan-vat.md`, `01-the-gioi.md`, `02-dan-y.md`, `project-state.json`, các chương) nằm chung trong một thư mục. Nếu người dùng chưa chỉ định, hỏi một câu ngắn rồi tạo thư mục theo tên truyện. Ghi nhớ đường dẫn này — mọi lệnh script ở Pha 3/4 đều nhận nó qua `--dir`.
2. Kiểm tra thư mục làm việc có `project-state.json` không (dự án đang viết dở). Nếu có → hỏi người dùng: tiếp tục chương tiếp theo, xem lại/sửa chương gần nhất, hay bắt đầu dự án mới.
3. Kiểm tra `user-preferences.md` (skill tự ghi sau mỗi dự án) → áp dụng ngầm các sở thích đã biết (thể loại hay viết, độ dài chương ưa thích, giọng văn), không hỏi lại từ đầu trừ khi người dùng muốn đổi.

## Pha 1 — Chọn thể loại + Hỏi đáp phân lớp

**Bước a — Xác định thể loại.** Nếu người dùng đã nói rõ thể loại/nguồn cảm hứng (kể cả gián tiếp như "truyện giống kênh X", "kiểu truyện Trung Quốc hay đăng", một bộ phim/truyện họ thích) → tra `references/genres.md` để lấy đúng quy ước của thể loại đó (motif, nhịp độ, kiểu nhân vật, hook đặc trưng). Nếu người dùng chưa biết muốn viết gì → dùng `ask_user_input_v0` (nếu có) cho họ chọn nhanh giữa các nhóm thể loại lớn trong `genres.md`, hoặc hỏi thẳng trong chat nếu không có tool đó.

**Bước b — Lớp 1 (bắt buộc, 3 câu hỏi cốt lõi):**
1. Xung đột/động lực chính xuyên suốt truyện là gì? (báo thù, sinh tồn, phá án, tình yêu, trưởng thành, khám phá thế giới...)
2. Nhân vật chính là ai, ngôi kể là gì (thứ nhất/thứ ba), điểm đặc biệt nhất của họ?
3. Bối cảnh tổng quát: thời gian, không gian, có yếu tố siêu nhiên/công nghệ đặc biệt nào không?

**Bước c — Lớp 2 (tùy chọn, hỏi gộp 1 lượt, có thể bỏ qua):**
- Số chương dự kiến + độ dài mỗi chương (mặc định theo thể loại, xem `genres.md`).
- Giọng văn tổng thể (nhẹ nhàng / gay cấn / u ám / hài hước...).
- Có muốn dùng chế độ hỏi-đáp kiểu "chọn nhánh RPG" để cùng xây cốt truyện tương tác không, hay để AI tự đề xuất toàn bộ.

Nếu người dùng nói "làm nhanh"/"mặc định đi" → tự chọn phương án hợp lý theo thể loại đã chọn, nêu rõ mình đã chọn gì, rồi tiến thẳng sang Pha 2.

## Pha 2 — Xây nền tảng

Xem chi tiết mẫu và cấu trúc file trong `references/world-and-characters.md`. Tạo trong thư mục dự án:

- `00-nhan-vat.md` — hồ sơ nhân vật (tính cách, động cơ, bí mật, tật ngôn ngữ riêng để giữ giọng nhất quán).
- `01-the-gioi.md` — world bible: quy tắc thế giới, bối cảnh xã hội/lịch sử/hệ thống sức mạnh (nếu có). Với truyện đời thường/hiện thực, file này gọn hơn, chỉ ghi bối cảnh xã hội và các mốc thời gian quan trọng.
- `02-dan-y.md` — dàn ý theo bảng: mỗi dòng là 1 chương gồm sự kiện chính, hook cuối chương, vé số (foreshadowing) cài lại nếu có.
- `project-state.json` — file trạng thái máy đọc được, xem cấu trúc trong `references/continuity-fact-ledger.md`. Chứa cả **guard rails** (luật bất biến không được vi phạm, ví dụ: "nhân vật A không được biết bí mật B trước chương 15", hoặc luật vật lý/ma pháp của thế giới).

**Trình bày toàn bộ khung này cho người dùng xác nhận trước khi viết chương 1.** Đây là bước bắt buộc — bỏ qua bước này là nguyên nhân phổ biến nhất khiến truyện dài bị lạc hướng hoặc mâu thuẫn.

## Pha 3 — Viết từng chương (lặp lại đến khi xong)

Với mỗi chương:

1. **Continuity-bridge**: đọc `project-state.json` (tóm tắt chương gần nhất + fact ledger + trạng thái nhân vật) trước khi viết — quy trình chi tiết ở `references/continuity-fact-ledger.md`.
2. **Viết chương** theo `references/chapter-craft.md` — kỹ thuật mở đầu, nhịp độ, hook, giữ giọng nhân vật, tránh "văn AI", điều chỉnh theo tông của thể loại đã chọn ở Pha 1.
3. **Tự kiểm tra** theo `references/quality-checklist.md` trước khi đưa cho người dùng — tự sửa nếu phát hiện lỗi, không cần hỏi lại. Nếu môi trường chạy được Python và đã có nhiều chương, **chạy script kiểm tra nhất quán tự động** để bắt mâu thuẫn dữ kiện mà mắt thường dễ bỏ sót:
   ```bash
   python "<thư-mục-skill>/scripts/consistency_check.py" --dir "<thư-mục-dự-án>"
   ```
   Script này đọc `project-state.json` và quét toàn bộ chương, báo cáo: số liệu mâu thuẫn với fact ledger, guard rail bị vi phạm, vé số tới hạn chưa trả, và nhân vật lạ chưa khai. Sửa các lỗi mức 🔴 NẶNG trước khi giao chương.
4. **Kiểm tra độ dài** so với mục tiêu của thể loại (xem `genres.md`) — viết hụt/lố là lỗi hay gặp khi viết liên tục nhiều chương:
   ```bash
   python "<thư-mục-skill>/scripts/check_wordcount.py" "<file-chương>" --min 2000 --max 3500
   ```
   Script đếm theo âm tiết cách nhau bởi khoảng trắng — đúng với cách đếm "từ" thông dụng của truyện mạng tiếng Việt.
5. **Cập nhật** `project-state.json`: tóm tắt chương vừa viết, thay đổi trạng thái nhân vật, sự kiện/con số mới cần nhớ (đưa vào fact ledger), vé số mới cài hoặc đã trả.
6. Hỏi người dùng: viết tiếp, chỉnh sửa chương vừa rồi, hay dừng lại.

**Nguyên tắc góp ý:** khi nhận xét bản thảo (của người dùng hoặc của chính mình), luôn chỉ ra **vị trí cụ thể** ("đoạn thoại giữa chương, chỗ nhân vật A nói với B") kèm lý do, không nhận xét chung chung kiểu "hay đấy"/"cần cải thiện thêm".

## Pha 4 — Hoàn thiện & xuất bản

- Cập nhật `user-preferences.md`: ghi lại thể loại, độ dài chương, giọng văn, chế độ viết người dùng chọn lần này để lần sau đề xuất luôn.
- Hỏi người dùng muốn xuất file dạng gì:
  - **Markdown thuần** (mặc định) — gộp các chương thành 1 file dễ đọc.
  - **Word** — dùng docx skill nếu có.
  - **EPUB** (ebook đọc trên điện thoại/máy đọc sách) — chạy script có sẵn, không cần cài thêm thư viện:
    ```bash
    python "<thư-mục-skill>/scripts/build_epub.py" --dir "<thư-mục-dự-án>" --title "Tên truyện" --author "Tên tác giả"
    ```
    Script tự nhận diện các file chương theo thứ tự, lấy tiêu đề từ dòng đầu mỗi file, sinh bìa + mục lục + CSS hỗ trợ tiếng Việt, và đóng gói đúng chuẩn EPUB 3. Sau đó dùng `present_files` để giao file `.epub` cho người dùng.

---

## Chạy script cho đúng

`<thư-mục-skill>` là thư mục chứa chính file SKILL.md này (ví dụ `~/.claude/skills/viet-tieu-thuyet`), **không phải** thư mục truyện — hai thư mục này khác nhau, nên luôn viết đường dẫn script đầy đủ thay vì `scripts/...`. Trên Windows dùng `python`; nếu máy chỉ có `python3` (macOS/Linux) thì thay bằng `python3`. Không có Python thì bỏ qua bước script và tự kiểm tra tay theo `references/quality-checklist.md`.

## Tài liệu tham khảo

- `references/genres.md` — Quy ước, nhịp độ, motif đặc trưng của từng nhóm thể loại lớn (dùng ở Pha 1).
- `references/world-and-characters.md` — Mẫu hồ sơ nhân vật, world bible, cách viết guard rails (dùng ở Pha 2).
- `references/continuity-fact-ledger.md` — Cấu trúc `project-state.json`, cách dùng fact ledger và bảng vé số/foreshadowing để chống mâu thuẫn xuyên chương (dùng ở Pha 3).
- `references/chapter-craft.md` — Kỹ thuật viết mở đầu, nhịp độ, 10 kiểu hook, giữ giọng nhân vật, tránh văn AI (dùng ở Pha 3).
- `references/quality-checklist.md` — Bộ tiêu chí tự kiểm tra trước khi giao chương, rút gọn từ hệ thống polish nhiều trục (dùng ở Pha 3).
- `references/writing-modes.md` — Các chế độ viết: tuần tự / song song / nhóm agent, và cách chọn tùy theo môi trường đang chạy (Claude.ai hay Claude Code).

## Công cụ (scripts/) — code chạy thật, không phải mô tả

- `scripts/consistency_check.py` — Quét toàn bộ chương + `project-state.json`, phát hiện mâu thuẫn fact ledger, vi phạm guard rail, vé số chưa trả, nhân vật lạ. Dùng ở Pha 3.
- `scripts/build_epub.py` — Đóng gói bộ truyện thành ebook EPUB 3 hợp lệ (chỉ dùng thư viện chuẩn, không cần cài gì). Dùng ở Pha 4.
- `scripts/check_wordcount.py` — Kiểm tra số từ một chương so với khoảng mục tiêu. Dùng ở Pha 3.
- `scripts/trigger-eval.json` — Bộ test triggering của skill (12 ca), dùng để kiểm chứng/đo lại khi chỉnh sửa description.
- `scripts/test_consistency_check.py` — Self-check của `consistency_check.py` (dựng dự án giả, khẳng định bắt đúng mâu thuẫn và không báo nhầm). Chạy sau mỗi lần sửa script kiểm tra.

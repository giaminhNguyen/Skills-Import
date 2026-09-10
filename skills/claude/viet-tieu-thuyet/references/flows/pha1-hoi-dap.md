# Pha 1 — Chọn thể loại + Hỏi đáp phân lớp

Mục tiêu: thu đủ thông tin cốt lõi để lên khung, mà không hỏi lan man.

## Bước a — Xác định thể loại

- Nếu người dùng đã nói rõ thể loại/nguồn cảm hứng (kể cả gián tiếp: "truyện giống
  kênh X", "kiểu truyện Trung Quốc hay đăng", một bộ phim/truyện họ thích) → tra
  `guides/the-loai.md` để lấy đúng quy ước (motif, nhịp độ, kiểu nhân vật, hook,
  độ dài mặc định, và **thang văn phong mặc định**).
- Nếu người dùng chưa biết viết gì → dùng `ask_user_input_v0` (nếu có) cho họ chọn
  nhanh giữa các nhóm thể loại lớn trong `guides/the-loai.md`, hoặc hỏi thẳng.

## Bước b — Lớp 1 (BẮT BUỘC, 3 câu cốt lõi)

Luôn hỏi trước khi viết bất cứ gì:
1. Xung đột/động lực chính xuyên suốt truyện? (báo thù, sinh tồn, phá án, tình yêu,
   trưởng thành, khám phá thế giới...)
2. Nhân vật chính là ai, ngôi kể gì (thứ nhất/thứ ba), điểm đặc biệt nhất của họ?
3. Bối cảnh tổng quát: thời gian, không gian, có yếu tố siêu nhiên/công nghệ đặc biệt?

Mỗi câu nên kèm gợi ý sẵn để người dùng chọn nhanh (đặc biệt khi dùng ask_user_input_v0).

## Bước c — Lớp 2 (TÙY CHỌN, hỏi gộp 1 lượt, có thể bỏ qua)

- Số chương dự kiến + độ dài mỗi chương (mặc định theo thể loại, xem `guides/the-loai.md`).
  **Nếu ≥ 50 chương → kích hoạt chế độ truyện dài** (đọc `flows/truyen-dai.md` ở Pha 2–3:
  đọc ngữ cảnh phân tầng, quy hoạch cụm 50 chương, fact-lock chặn cứng). Nếu < 50 chương
  → dùng quy trình thường cho nhẹ.
- Giọng văn tổng thể (nhẹ nhàng / gay cấn / u ám / hài hước...).
- **Thang văn phong** (xem `guides/van-phong.md`): giữ mặc định theo thể loại hay chỉnh?
  Ngôn tình/trọng sinh/tiên hiệp mặc định **TQ 95 / Việt 90**.
- Có muốn dùng chế độ hỏi-đáp "chọn nhánh RPG" để cùng xây cốt truyện tương tác không.

## Quy tắc "làm nhanh"

Nếu người dùng nói "làm nhanh"/"mặc định đi" → bỏ qua Lớp 2, tự chọn phương án hợp lý
theo thể loại đã chọn, NÊU RÕ mình đã chọn gì, rồi tiến thẳng sang Pha 2.

## Ra khỏi Pha 1
Khi đã có: thể loại + 3 câu Lớp 1 (+ Lớp 2 nếu có) → sang Pha 2 lên khung.

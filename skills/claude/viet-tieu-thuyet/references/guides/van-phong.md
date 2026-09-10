# Văn phong: thang chất Trung Quốc / mượt tiếng Việt

Skill này dùng HAI trục độc lập để điều khiển văn phong. Mặc định cho dòng
ngôn tình / trọng sinh / tiên hiệp là **TQ 95 / Việt 90**.

## Hai trục

- **Trục A — Chất TQ (0–100)**: mức giữ "đặc sản" truyện mạng Trung Quốc:
  xưng hô nàng/hắn/y/phu quân, "kiếp trước", motif báo thù, nhịp "sảng văn"
  (mỗi chương phải "đã"), thành ngữ Hán-Việt, khí thế cung đấu/tu tiên.
  **Cao = đậm chất, KHÔNG phải xấu.** Đây là thứ khiến truyện "nghe đã tai".

- **Trục B — Mượt tiếng Việt (0–100)**: câu chữ tự nhiên với người Việt,
  đúng ngữ pháp, không lỗi dịch máy. **LUÔN phải ≥ 90, không thỏa hiệp.**

Hai trục độc lập: một đoạn có thể vừa đậm chất TQ (95) vừa mượt tiếng Việt (90).

## Mặc định theo thể loại

| Thể loại | Chất TQ (A) | Ghi chú |
|---|---|---|
| Ngôn tình / trọng sinh / tổng tài / báo thù | **95** | Đậm hết cỡ, đặc sản |
| Tiên hiệp / huyền huyễn | 90 | Cần chất Hán dựng thế giới tu tiên |
| Cổ đại / cung đấu | 90 | Xưng hô, lễ nghi đậm chất cổ trang |
| Đô thị hiện đại Việt thuần | 50 | Bối cảnh Việt thì giảm nàng/hắn |
| Đời thường / chữa lành | 30 | Gần đời sống Việt |

**Trục B (mượt tiếng Việt) luôn = 90 cho MỌI thể loại. Không có ngoại lệ.**

Khi lên khung (Pha 2), hỏi người dùng có muốn giữ mặc định hay chỉnh trục A.
Ghi giá trị đã chọn vào `project-state.json` (khóa `van_phong`) như một guard
rail, và mọi chương phải bám đúng mức đó.

## Ranh giới quan trọng: "đậm chất" KHÁC "dịch máy vụng"

Trục A cao KHÔNG có nghĩa là được phép viết sai tiếng Việt. Phân biệt rõ:

| Yếu tố | Thuộc trục nào | Xử lý |
|---|---|---|
| "nàng", "hắn", "kiếp trước", "phu quân" | Chất TQ (giữ) | Giữ nguyên, đây là đặc sản |
| "ôm hận mà chết không nhắm mắt", "nợ máu trả bằng máu" | Chất TQ (giữ) | Giữ, thành ngữ đắt |
| "ông trời có mắt", "sống không bằng chết" | Chất TQ (giữ) | Giữ |
| "đem nàng hại chết", "trong lòng lãnh khốc" | LỖI dịch máy | SỬA: "hại chết nàng", "lòng lạnh như băng" |
| "quy lai", "cầu sinh bất năng", "huyết trái" | LỖI dịch sống | SỬA sang từ Việt tương đương |
| "hàn quang lóe lên" (từ Hán tai khó bắt) | Ranh giới | Ở mức 90: đổi thành "sát khí lóe lên" |

Quy tắc: **giữ mọi thứ thuộc "chất TQ", chỉ sửa những gì là "lỗi diễn đạt".**

## Mẫu chuẩn ở mức 95/90 (để đối chiếu khi viết)

> Tô Uyển khẽ nhếch môi, nụ cười lạnh như băng. Kiếp trước, cũng chính người
> đàn bà độc ác này đã hại chết nàng, khiến nàng ôm hận mà chết không nhắm mắt.
> Ông trời có mắt, đã cho nàng một cơ hội trọng sinh. Lần này, nàng nhất định
> bắt bọn chúng sống không bằng chết, từng món nợ máu đều phải trả bằng máu.
> Ánh mắt nàng sắc lạnh, lóe lên một tia sát khí.

Đặc điểm của mức 95/90:
- Giữ trọn khí thế báo thù, motif "kiếp trước / trọng sinh / ông trời có mắt".
- Giữ thành ngữ đắt ("ôm hận chết không nhắm mắt", "nợ máu trả bằng máu").
- Thay từ Hán khó nghe bằng từ Việt cùng khí thế ("hàn quang" → "sát khí").
- Câu trôi một mạch, hợp cả đọc lẫn nghe (audio).

## Lưu ý cho định dạng audio

Nếu truyện nhắm tới nghe (audio) — như nhiều kênh kể chuyện — ưu tiên câu
trôi liền mạch, vì tai người nghe không kịp "giải mã" từ Hán lạ như mắt đọc.
Mức 95/90 đã tối ưu cho việc này; nếu người dùng thấy vẫn hơi cứng khi nghe,
hạ trục A xuống 90 (không hạ trục B).

---

## Khử "mùi AI" (học từ oh-story-claudecode)

Ngoài việc giữ chất TQ + tiếng Việt mượt, còn phải chủ động tránh các dấu hiệu khiến
văn "bốc mùi AI". Chạy `scripts/check_ai_patterns.py` để bắt tự động, nhưng cũng cần
tự ý thức khi viết.

### Cấm tuyệt đối: câu "phủ định rồi khẳng định"
Đây là mẫu câu AI điển hình nhất, oh-story liệt vào cấm tuyệt đối:
- ❌ "Đây không phải tình yêu, mà là sự chiếm hữu."
- ❌ "Đó không chỉ là một lời hứa. Đó là cả cuộc đời cô."
- ❌ "Không phải vì tiền, mà vì danh dự."

Thỉnh thoảng dùng 1 lần để nhấn thì được; lạm dụng (2-3 lần/chương) là mùi AI nặng.
Cách sửa: viết thẳng ý khẳng định, bỏ vế phủ định. "Đó là sự chiếm hữu, không hơn."

### Phương pháp 3 lượt khử mùi AI
1. **Lượt 1 — bắt máy móc**: rà câu phủ định-khẳng định, sáo ngữ mòn (xem bảng dưới),
   cấu trúc câu lặp đi lặp lại giống nhau.
2. **Lượt 2 — bắt lê thê**: mật độ so sánh "như/tựa/như thể" quá dày; liệt kê cảm xúc
   trực tiếp ("vừa buồn vừa tức vừa thất vọng"); giải thích thừa điều đã rõ.
3. **Lượt 3 — đọc thành tiếng**: câu nào đọc lên thấy cứng, thấy "không giống người
   Việt nói" thì sửa. Đặc biệt quan trọng nếu truyện để làm audio.

### Bảng sáo ngữ mòn nên hạn chế
"không thể tin nổi", "trái tim như thắt lại", "cả thế giới như sụp đổ", "một cảm giác
khó tả", "thời gian như ngừng trôi", "khóe môi khẽ nhếch", "bất giác", "khẽ mỉm cười".
Không cấm tuyệt đối, nhưng mỗi cụm tối đa 1 lần/chương, và tránh dồn nhiều cụm gần nhau.

### Lưu ý phân biệt với chất TQ
Khử mùi AI KHÔNG đụng tới "chất TQ" đáng giữ. "Nàng/hắn", "kiếp trước", "ôm hận chết
không nhắm mắt", "nợ máu trả bằng máu" là đặc sản, KHÔNG phải mùi AI. Chỉ khử cái máy
móc (phủ định-khẳng định, sáo ngữ lặp, so sánh dày, lỗi dịch sống). Xem lại bảng phân
biệt "chất TQ vs lỗi dịch máy" ở đầu file này.

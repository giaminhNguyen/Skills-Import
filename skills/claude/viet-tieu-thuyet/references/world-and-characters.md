# Mẫu nền tảng: nhân vật, thế giới, guard rails

## 00-nhan-vat.md — Hồ sơ nhân vật

Với mỗi nhân vật chính/phụ quan trọng, ghi theo mẫu:

```
### [Tên nhân vật]
- Vai trò: (chính diện / phản diện / phụ trợ)
- Ngoại hình & đặc điểm nhận diện nhanh: ...
- Tính cách cốt lõi (3 tính từ): ...
- Động cơ/mục tiêu xuyên suốt truyện: ...
- Bí mật (nếu có) và thời điểm dự kiến hé lộ: ...
- Mối quan hệ với các nhân vật khác: ...
- Tật ngôn ngữ riêng (câu cửa miệng, cách xưng hô, phản ứng đặc trưng khi tức giận/vui/buồn): ...
- Cung bậc thay đổi dự kiến (arc): nhân vật này sẽ khác đi thế nào từ đầu đến cuối truyện?
```

Nhân vật phản diện **luôn cần một động cơ hợp lý**, dù ích kỷ hay lệch lạc — tránh phản diện "ác vì cốt truyện cần vậy".

## 01-the-gioi.md — World bible

Nội dung tùy độ phức tạp của thể loại (xem `genres.md`), nhưng luôn có tối thiểu:

- **Bối cảnh không gian/thời gian**: ở đâu, khi nào (thời hiện đại/giả tưởng/lịch sử).
- **Cấu trúc xã hội liên quan đến cốt truyện**: gia đình/công ty/môn phái/tổ chức nào quan trọng, quan hệ quyền lực giữa chúng.
- **Quy tắc đặc biệt của thế giới (nếu có)**: hệ thống tu luyện, công nghệ giả tưởng, phép thuật — mỗi quy tắc phải có **giới hạn rõ ràng**, vì giới hạn mới tạo ra kịch tính.
- **Mốc thời gian/sự kiện nền quan trọng**: những gì đã xảy ra trước khi truyện bắt đầu mà ảnh hưởng đến hiện tại.

## 02-dan-y.md — Dàn ý

Bảng theo chương, tối thiểu các cột:

| Chương | Sự kiện chính | Hook cuối chương | Vé số cài/trả |
|---|---|---|---|
| 1 | ... | ... | Cài: ... |
| 2 | ... | ... | ... |

Dàn ý không cần chi tiết tuyệt đối cho toàn bộ truyện ngay từ đầu — nên chi tiết hóa đầy đủ cho 5–8 chương đầu, phần còn lại có thể ghi dạng "cột mốc lớn" (major beats) rồi chi tiết hóa dần khi viết tới gần.

## Guard rails — luật bất biến

Guard rails là những quy tắc **không được vi phạm** trong suốt truyện, giúp AI không tự ý phá vỡ logic đã thiết lập. Ví dụ:

- "Nhân vật A không được biết bí mật B trước chương 15."
- "Hệ thống tu luyện không cho phép nhảy cấp quá 1 cảnh giới trong một trận chiến."
- "Nhân vật C đã chết ở chương 3, không được xuất hiện lại trừ hồi tưởng/giấc mơ."
- "Giọng kể là ngôi thứ nhất từ nhân vật chính — không chuyển góc nhìn sang nhân vật khác giữa truyện trừ khi có chủ đích báo trước."

Guard rails được lưu trong `project-state.json` (xem `continuity-fact-ledger.md`) và phải được kiểm tra lại ở bước tự kiểm tra chất lượng mỗi chương.

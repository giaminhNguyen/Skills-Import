# Continuity-bridge & Fact Ledger

Cơ chế này giải quyết vấn đề phổ biến nhất của truyện dài viết bằng AI: **mâu thuẫn xuyên chương** — số liệu đổi, tính cách nhân vật lệch, sự kiện tự mâu thuẫn với chương trước.

## Cấu trúc `project-state.json`

```json
{
  "du_an": "Tên truyện",
  "the_loai": "ngôn tình trọng sinh",
  "chuong_hien_tai": 7,
  "tom_tat_2_chuong_gan_nhat": [
    "Chương 6: ...",
    "Chương 7: ..."
  ],
  "trang_thai_nhan_vat": {
    "Nhân vật A": "hiện đang nghi ngờ nhân vật B, chưa biết bí mật C",
    "Nhân vật B": "vừa mất chức, đang tìm cách trả thù"
  },
  "fact_ledger": {
    "Tuổi nhân vật A": "17 (lớp 11)",
    "Số tiền nợ trong truyện": "200 triệu đồng, vay từ chương 3",
    "Ngày sinh nhật nhân vật B": "20 tháng 8",
    "Địa điểm chính": "trường THPT Lê Quý Đôn, Hà Nội"
  },
  "ve_so_dang_mo": [
    {"cai_o_chuong": 2, "noi_dung": "chiếc vòng tay nhân vật A đánh rơi", "du_kien_tra_o_chuong": 12}
  ],
  "guard_rails": [
    "Nhân vật A không được biết bí mật B trước chương 15"
  ]
}
```

## Fact ledger là gì và tại sao quan trọng

Fact ledger (sổ sự kiện cứng) là danh sách các **con số, ngày tháng, tên riêng, địa điểm** đã được nhắc đến trong truyện. Đây là loại chi tiết dễ bị AI "bịa lại khác đi" nhất khi viết ngẫu hứng từng chương riêng lẻ (ví dụ: chương 3 nói nhân vật nợ 200 triệu, chương 10 lại viết thành 500 triệu).

**Quy trình bắt buộc:**
1. Trước khi viết một chương mới, đọc toàn bộ `fact_ledger` hiện có.
2. Trong lúc viết, nếu nhắc lại một con số/ngày/tên đã có trong ledger → dùng đúng giá trị cũ, không tự sáng tác lại.
3. Nếu chương mới tạo ra một sự kiện/con số/tên mới có khả năng được nhắc lại sau này → thêm ngay vào `fact_ledger` khi cập nhật `project-state.json`.

## Vé số / Foreshadowing

Mỗi chi tiết được "cài" một cách có chủ đích để trả lại sau (một vật, một câu nói mập mờ, một hành động lạ) cần được ghi vào `ve_so_dang_mo` kèm chương dự kiến trả. Trước khi kết thúc truyện, rà lại danh sách này — **không được để vé số nào bị bỏ quên**, đây là lỗi khiến người đọc cảm thấy truyện "hụt".

## Continuity-bridge khi bắt đầu mỗi chương

Trước khi viết, luôn tự trả lời nhanh (không cần viết ra cho người dùng thấy, chỉ để tự kiểm tra):
- Chương trước kết thúc ở trạng thái cảm xúc/tình huống nào?
- Nhân vật nào đang biết/không biết điều gì tại thời điểm này?
- Có guard rail nào sắp bị chạm tới không?
- Có vé số nào đến hạn trả trong khoảng chương này không?

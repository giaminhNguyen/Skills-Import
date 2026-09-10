# Template: Chương & project-state.json

## Cấu trúc một file chương

Đặt tên file: `chuong-01.txt`, `chuong-02.txt`... (đánh số 2 chữ số để sắp đúng thứ tự).

```
[TÊN TRUYỆN]
Chương [N]: [Tiêu đề chương]

[Nội dung chương — mở đầu hút ngay, thoại nhiều, đoạn ngắn, kết bằng hook]

(Hết chương [N] — còn tiếp)
```

Dòng đầu (tên truyện) và dòng hai (tiêu đề chương) giúp script `build_epub.py` tự nhận
diện tiêu đề. Đừng bỏ dòng tiêu đề chương.

## Cấu trúc project-state.json (khuôn khởi tạo)

```json
{
  "du_an": "[Tên truyện]",
  "the_loai": "[thể loại]",
  "chuong_hien_tai": 0,
  "hoan_thanh": false,
  "van_phong": {"chat_tq": 95, "muot_tieng_viet": 90, "ghi_chu": "..."},
  "tom_tat_2_chuong_gan_nhat": [],
  "trang_thai_nhan_vat": {},
  "fact_ledger": {},
  "ve_so_dang_mo": [
    {"cai_o_chuong": 0, "noi_dung": "...", "du_kien_tra_o_chuong": 0}
  ],
  "guard_rails": []
}
```

Giải thích chi tiết từng khóa: xem `flows/ha-tang-chung.md`.
```

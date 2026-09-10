# Chế độ truyện dài (50+ chương) — học từ MyNovel

Kích hoạt khi số chương dự kiến ≥ 50, hoặc khi người dùng chọn "truyện dài" ở Pha 1.
Với truyện ngắn/vừa (<50 chương), BỎ QUA file này — dùng quy trình thường ở
`pha3-viet-chuong.md` cho nhẹ.

Vấn đề cốt lõi của truyện dài: viết tới chương 50, 100, 300, mô hình không còn "nhớ"
ai biết gì, tài nguyên còn bao nhiêu, vé số nào chưa trả. Chế độ này giải quyết bằng
ĐỌC NGỮ CẢNH PHÂN TẦNG và QUY HOẠCH THEO CỤM, thay vì nhồi cả truyện vào context.

## 1. Đọc ngữ cảnh phân tầng (thay cho "2 chương gần nhất")

Trước khi viết một chương, đọc theo ĐÚNG thứ tự sau (dừng khi đủ, không nhồi hết):

1. `project-state.json`: cấu hình, chương hiện tại, guard rails, thang văn phong.
2. Trạng thái nhân vật hiện tại (`trang_thai_nhan_vat` + fact ledger).
3. **Kế hoạch cụm 50 chương hiện tại** (xem mục 2 bên dưới): phân biệt rõ "mục tiêu
   dự kiến" và "việc đã thực sự xảy ra".
4. Tóm tắt 3 chương gần nhất (nguyên văn phần tóm tắt).
5. Danh sách tóm tắt ~20 chương gần nhất (nếu có, dạng 1 dòng/chương).
6. Tổng kết mỗi 50 chương đã qua (nếu truyện đã dài) — dạng nén.
7. Hồ sơ nhân vật + vé số liên quan tới chương sắp viết. Nếu chương này TRẢ một vé số
   cài từ lâu, đọc lại tóm tắt chương đã cài nó.

Mục tiêu: giữ liền mạch gần (3 chương), không quên diện rộng (tóm tắt + tổng kết cụm),
mà context không phình vô hạn theo số chương.

## 2. Quy hoạch theo cụm 50 chương

KHÔNG lên dàn ý chi tiết cả 200 chương một lần (mô hình sẽ dồn hết cao trào vào 20
chương đầu rồi hụt hơi). Thay vào đó:

- `02-dan-y.md` chỉ giữ **dàn ý cột-mốc-lớn** cho toàn truyện (mỗi cụm 50 chương = vài
  dòng: cụm này đẩy tuyến gì, khóa/mở năng lực nào, để dành mâu thuẫn gì cho cụm sau).
- Khi bắt đầu một cụm mới, tạo file chi tiết riêng: `plan/cum-EP001-050.md`,
  `plan/cum-EP051-100.md`... — chi tiết hóa tối đa 50 chương trong cụm đó.
- Dàn ý cụm KHÔNG được tự thêm tuyến chính/nhân vật/năng lực/vé số nằm ngoài dàn ý
  tổng. Nếu cần thêm, phải cập nhật dàn ý tổng trước (tránh "vung tay quá trán" cho
  cao trào trước mắt mà thấu chi cốt truyện về sau).

## 3. Fact-lock: chặn thay vì chỉ cảnh báo (học từ MyNovel + tianming)

Ở truyện dài, mâu thuẫn dữ kiện là tử huyệt. Nâng mức xử lý:
- Trước khi viết, nếu dàn ý cụm mâu thuẫn với một dữ kiện ĐÃ XẢY RA trong fact ledger
  → **DỪNG LẠI, báo người dùng**, không lén viết đè lên lịch sử.
- Chạy `scripts/consistency_check.py --dir <thư-mục> --strict` (cờ `--strict` trả lỗi
  nếu có mức 🔴 NẶNG). Sửa hết lỗi nặng rồi mới viết chương tiếp theo.

## 4. Tổng kết định kỳ

- Sau mỗi 50 chương: viết một file tổng kết cụm (`plan/tong-ket-cum-N.md`) — nén những
  gì đã xảy ra, trạng thái cuối cụm, vé số đã trả/còn nợ. File này thay thế việc phải
  đọc lại 50 chương gốc ở các cụm sau.
- Cập nhật `project-state.json` sau mỗi chương như thường (xem `ha-tang-chung.md`).

## Cấu trúc thư mục truyện dài

```
{tên-truyện}/
├── project-state.json
├── 00-nhan-vat.md, 01-the-gioi.md
├── 02-dan-y.md                    # chỉ cột mốc lớn toàn truyện
├── plan/
│   ├── cum-EP001-050.md           # dàn ý chi tiết cụm hiện tại
│   ├── tong-ket-cum-1.md          # tổng kết sau khi xong cụm
│   └── ...
├── chuong/ (hoặc để phẳng)        # các file chương
└── tom-tat/                       # tóm tắt từng chương (1 file/chương)
```

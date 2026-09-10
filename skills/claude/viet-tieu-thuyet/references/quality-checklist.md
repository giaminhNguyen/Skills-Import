# Bộ tiêu chí tự kiểm tra trước khi giao chương

Rút gọn từ các hệ thống "polish nhiều trục" thành 7 mục thiết thực — tự chạy qua danh sách này sau khi viết xong mỗi chương, tự sửa nếu phát hiện lỗi, không cần hỏi lại người dùng trừ khi không chắc chắn.

| # | Trục | Câu hỏi tự kiểm tra |
|---|---|---|
| 1 | **HOOK** | Chương có mở đầu đủ hấp dẫn trong 2–3 câu đầu không? Có kết bằng hook (trừ chương cuối) không? Hook có trùng kiểu với 1–2 chương liền trước không? |
| 2 | **VOICE** | Mỗi nhân vật có nói/hành động đúng tính cách và tật ngôn ngữ đã định trong `00-nhan-vat.md` không? |
| 3 | **LOGIC** | Có con số/ngày tháng/tên riêng nào mâu thuẫn với `fact_ledger` không? Có vi phạm `guard_rails` nào không? |
| 4 | **NHỊP ĐỘ** | Tỷ lệ thoại/miêu tả có đúng tông thể loại không? Đoạn văn có quá dài, gây khó đọc không? |
| 5 | **VĂN AI** | Có lặp cụm sáo rỗng, liệt kê cảm xúc trực tiếp, hay cấu trúc câu lặp lại máy móc không? |
| 6 | **TIẾN TRIỂN** | Chương có đóng góp gì mới (thông tin, xung đột, thay đổi trạng thái nhân vật) hay chỉ là một cảnh tĩnh không cần thiết? |
| 7 | **THỂ LOẠI** | Chương có đúng quy ước/motif của thể loại đã chọn ở Pha 1 không (xem `genres.md`)? |

## Khi phát hiện lỗi

- Lỗi ở mục LOGIC (mâu thuẫn dữ kiện) → **luôn sửa ngay**, đây là lỗi nghiêm trọng nhất, không được bỏ qua.
- Lỗi ở mục HOOK/NHỊP ĐỘ/VĂN AI → sửa nếu rõ ràng, hoặc nêu ra cho người dùng biết mình đã cân nhắc và chọn giữ nguyên vì lý do gì.
- Nếu không chắc một chi tiết có mâu thuẫn hay không (ví dụ không có đủ thông tin trong `fact_ledger`) → hỏi người dùng thay vì tự đoán.

## Khi góp ý cho bản thảo của người dùng (không phải bản do AI viết)

Áp dụng cùng 7 trục trên, nhưng luôn diễn đạt theo dạng: **[vị trí cụ thể] + [vấn đề] + [gợi ý sửa]**, ví dụ:

> "Đoạn thoại ở giữa chương 5, chỗ nhân vật A nói với B — câu thoại này có thể đổi sang bất kỳ nhân vật nào khác mà không ai nhận ra khác biệt (vi phạm trục VOICE). Có thể thêm cách xưng hô đặc trưng của A vào đây."

Không nhận xét chung chung kiểu "chương này ổn"/"cần cải thiện thêm" mà không chỉ rõ ở đâu.

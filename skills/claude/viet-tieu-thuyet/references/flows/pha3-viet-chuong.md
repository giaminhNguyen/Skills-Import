# Pha 3 — Viết từng chương (lặp lại đến khi xong)

Với MỖI chương, thực hiện đúng thứ tự sau:

## 1. Continuity-bridge (trước khi viết)

Đọc `project-state.json`: tóm tắt chương gần nhất + fact ledger + trạng thái nhân vật
+ guard rails + thang văn phong. Tự trả lời nhanh (xem `flows/ha-tang-chung.md`):
- Chương trước kết ở trạng thái nào?
- Nhân vật nào đang biết/không biết điều gì?
- Có guard rail nào sắp bị chạm không?
- Có vé số nào đến hạn trả trong khoảng chương này không?

## 2. Viết chương

Áp dụng đồng thời:
- `guides/ky-thuat-chuong.md` — mở đầu, nhịp độ, giữ giọng nhân vật, tránh văn AI.
- `guides/hook.md` — chọn kiểu hook cuối chương (luân phiên, không lặp 2 chương liền).
- `guides/van-phong.md` — bám đúng thang `van_phong` đã đặt (mặc định TQ 95/Việt 90).
- `guides/the-loai.md` — đúng nhịp/motif của thể loại đã chọn.

## 3. Tự kiểm tra

Chạy qua `guides/kiem-tra-chat-luong.md` (8 trục). Tự sửa lỗi, không cần hỏi lại.
Nếu môi trường chạy được Python và đã có nhiều chương, chạy các script kiểm tra tự động:
```bash
python3 scripts/consistency_check.py --dir <thư-mục-dự-án>
python3 scripts/check_wordcount.py <file-chương> --min <min> --max <max>
python3 scripts/check_ai_patterns.py <file-chương>
```
- `consistency_check.py`: mâu thuẫn dữ kiện, guard rail, vé số.
- `check_wordcount.py`: độ dài chương.
- `check_ai_patterns.py`: "mùi AI" — câu phủ định-khẳng định, sáo ngữ mòn, lỗi dịch
  máy, mật độ so sánh quá dày. Sửa mọi lỗi 🔴 BLOCK trước khi giao chương.

Sửa mọi lỗi mức 🔴 NẶNG/BLOCK trước khi giao chương.

## 4. Cập nhật trạng thái

Cập nhật `project-state.json`: tóm tắt chương vừa viết, thay đổi trạng thái nhân vật,
sự kiện/con số mới (thêm vào fact ledger), vé số mới cài hoặc đã trả. Xem
`flows/ha-tang-chung.md` để biết cách ghi đúng.

## 5. Bàn giao & hỏi tiếp

Đưa chương cho người dùng. Hỏi: viết tiếp, chỉnh sửa chương vừa rồi, hay dừng.

## Nguyên tắc góp ý
Khi nhận xét bản thảo (của người dùng hoặc của chính mình), luôn chỉ VỊ TRÍ cụ thể
("đoạn thoại giữa chương, chỗ A nói với B") kèm lý do, không nói chung chung
kiểu "hay đấy"/"cần cải thiện". Xem `guides/kiem-tra-chat-luong.md`.

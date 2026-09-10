# Pha 4 — Hoàn thiện & xuất bản

Chạy khi truyện đã viết xong (hoặc người dùng muốn xuất bản phần đã có).

## 1. Rà soát tổng thể

- Chạy `scripts/consistency_check.py --dir <thư-mục>` lần cuối trên TOÀN BỘ chương.
- Rà `ve_so_dang_mo` trong `project-state.json`: KHÔNG được để vé số nào bị bỏ quên.
  Nếu truyện đánh dấu hoàn thành (`hoan_thanh: true`) mà còn vé số mở → phải xử lý.

## 2. Cập nhật bộ nhớ sở thích

Ghi/cập nhật `user-preferences.md`: thể loại, độ dài chương, giọng văn, thang văn phong,
chế độ viết mà người dùng đã chọn lần này — để lần sau đề xuất luôn, không hỏi lại.

## 3. Xuất bản

Hỏi người dùng muốn xuất định dạng gì:
- **Markdown thuần** (mặc định) — gộp các chương thành 1 file dễ đọc.
- **Word** — dùng docx skill nếu có.
- **EPUB** (ebook điện thoại/máy đọc sách) — chạy script, không cần cài thêm gì:
  ```bash
  python3 scripts/build_epub.py --dir <thư-mục> --title "Tên truyện" --author "Tên tác giả"
  ```
  Sau đó dùng `present_files` để giao file `.epub`.

## Nguyên tắc
Đánh dấu `hoan_thanh: true` trong `project-state.json` chỉ khi truyện thật sự khép
lại mọi tuyến chính và không còn vé số nào bỏ ngỏ (trừ vé số cố ý để mở cho phần sau).

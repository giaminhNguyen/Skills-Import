# Chế độ viết

Chọn chế độ ở cuối Pha 2, sau khi đã có dàn ý và nền tảng. Chế độ phù hợp phụ thuộc vào **môi trường đang chạy skill này**.

## 1. Tuần tự (Serial) — mặc định, an toàn nhất

Viết từng chương một, theo đúng continuity-bridge sau mỗi chương. Luôn dùng chế độ này khi:
- Đang chạy trên claude.ai / Claude Cowork (không có subagent song song thật sự).
- Truyện có nhiều guard rails phức tạp hoặc nhiều vé số đan xen — việc giữ mạch tuần tự giảm rủi ro mâu thuẫn.
- Người dùng muốn xem và góp ý sau mỗi chương trước khi viết tiếp.

## 2. Song song (nhiều chương cùng lúc) — chỉ dùng khi có subagent thật

Chỉ khả dụng trong môi trường có subagent (ví dụ Claude Code với tính năng spawn subagent, hoặc Cowork). Cách làm:
- Chia một cụm 3–5 chương đã có dàn ý chi tiết cho các subagent viết song song.
- Mỗi subagent **bắt buộc** nhận cùng một bản sao `project-state.json` tại thời điểm bắt đầu cụm, cùng `00-nhan-vat.md` và `guard_rails`.
- Sau khi tất cả subagent hoàn thành, agent chính đọc lại toàn bộ cụm theo đúng thứ tự, chạy lại continuity-bridge một lần nữa để vá các mâu thuẫn phát sinh do viết song song (đây là bước bắt buộc, không được bỏ qua).

Đánh đổi: nhanh hơn, nhưng rủi ro mâu thuẫn cao hơn — chỉ nên dùng khi người dùng ưu tiên tốc độ hơn độ chỉn chu, hoặc với thể loại ít guard rails phức tạp (ví dụ đời thường, ngôn tình nhẹ).

## 3. Nhóm agent chuyên biệt (Agent Teams) — cho dự án lớn, nhiều giai đoạn

Chỉ phù hợp khi môi trường hỗ trợ nhiều agent với vai trò khác nhau (ví dụ Claude Code với các sub-agent định nghĩa riêng). Có thể chia vai trò tham khảo:
- **Kiến trúc sư cốt truyện**: giữ và cập nhật dàn ý tổng, world bible.
- **Người viết chương**: viết chính, theo continuity-bridge.
- **Người soát lỗi liên tục**: chạy `quality-checklist.md` độc lập với người viết, để tránh "người viết tự chấm bài mình".
- **Người theo dõi vé số/fact ledger**: chuyên trách cập nhật và rà soát `project-state.json`.

Chế độ này phù hợp với truyện rất dài (50+ chương) hoặc khi người dùng có sẵn hạ tầng multi-agent. Với hầu hết trường hợp cá nhân viết truyện, chế độ Tuần tự vẫn là lựa chọn tốt nhất về tỷ lệ công sức/chất lượng.

## Khi không chắc môi trường có hỗ trợ gì

Nếu không có tool spawn subagent trong danh sách công cụ hiện có, luôn mặc định dùng chế độ **Tuần tự** — không giả vờ chạy song song.

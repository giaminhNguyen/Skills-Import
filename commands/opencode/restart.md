---
description: Lưu session và reload skills/config ngay trong session hiện tại
---

Làm các bước sau theo thứ tự:

## Bước 1 — Lưu session hiện tại

Dùng Bash để tạo thư mục `.opencode/sessions/` nếu chưa có. Ghi file `.opencode/sessions/<YYYY-MM-DD-HHmm>-restart.md` với nội dung:

- **Context hiện tại**: tóm tắt 2-3 câu về những gì đang làm
- **Skill đang dùng**: list các skill đã được load
- **First command cho session mới**: câu lệnh đầu tiên để tiếp tục

## Bước 2 — Reload skills từ đĩa

Dùng Glob để tìm tất cả `**/SKILL.md` trong các thư mục skills:
- `.opencode/skills/`
- `.agents/skills/` (nếu có)
- Các paths trong `skills.paths` nếu được cấu hình
- `~/.config/opencode/skills/` (nếu có)

Đọc nội dung từng file SKILL.md tìm được. Xác nhận tổng số skills đã reload.

## Bước 3 — Reload config

Đọc lại `opencode.json` và tất cả agent files trong `.opencode/agents/` để cập nhật config.

## Bước 4 — Reset context

Xác nhận với user: đã lưu session, reload X skills, reload config. Bắt đầu với context sạch, sẵn sàng nhận lệnh mới.

**Quan trọng**: Sau bước này, coi như bắt đầu session mới. Quên tất cả context trước đó của lệnh `/restart`. Chỉ giữ lại thông tin từ các file đã đọc ở bước 2-3 và lịch sử lệnh `/restart` vừa chạy.

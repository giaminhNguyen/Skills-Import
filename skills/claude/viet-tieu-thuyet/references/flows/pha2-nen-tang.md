# Pha 2 — Xây nền tảng

Mục tiêu: tạo bộ khung đầy đủ để truyện dài không lạc hướng, rồi cho người dùng
xác nhận TRƯỚC khi viết chương 1.

## Tạo các file nền tảng

Dùng các template rời trong `templates/` làm khuôn:

- `00-nhan-vat.md` — theo `templates/nhan-vat-template.md`. Hồ sơ nhân vật chính/phụ:
  tính cách, động cơ, bí mật + thời điểm hé lộ, tật ngôn ngữ riêng (để giữ giọng
  nhất quán). Nhân vật phản diện LUÔN cần động cơ hợp lý, không "ác vô cớ".

- `01-the-gioi.md` — world bible: quy tắc thế giới, bối cảnh xã hội/lịch sử/hệ thống
  sức mạnh (nếu có). Mỗi quy tắc phải có GIỚI HẠN rõ ràng (giới hạn tạo kịch tính).
  Truyện đời thường thì file này gọn, chỉ ghi bối cảnh xã hội + mốc thời gian.

- `02-dan-y.md` — theo `templates/dan-y-template.md`. Dàn ý theo bảng: mỗi chương gồm
  sự kiện chính, hook cuối chương, vé số (foreshadowing) cài/trả. Chi tiết hóa đầy đủ
  5–8 chương đầu; phần còn lại ghi "cột mốc lớn", chi tiết dần khi viết tới.

- `project-state.json` — file trạng thái máy đọc được (xem `flows/ha-tang-chung.md`
  để biết cấu trúc đầy đủ). Chứa cả **guard rails** và **thang văn phong** (`van_phong`).

## Chọn thang văn phong (BẮT BUỘC)

Xem `guides/van-phong.md`. Hỏi người dùng muốn đặt "thang chất Trung Quốc" ở mức nào.
Mặc định ngôn tình/trọng sinh/tiên hiệp = **TQ 95 / Việt 90**. Trục "mượt tiếng Việt"
luôn ≥ 90 cho mọi thể loại. Ghi vào `project-state.json` (khóa `van_phong`).

## Chọn chế độ viết

Xem `flows/che-do-viet.md`. Mặc định là Tuần tự (an toàn nhất). Chỉ dùng song song/
nhóm agent khi môi trường có subagent thật.

## Xác nhận

**Trình bày toàn bộ khung (nhân vật + thế giới + dàn ý + thang văn phong) cho người
dùng xác nhận hoặc chỉnh sửa. Đây là bước BẮT BUỘC** — bỏ qua là nguyên nhân phổ biến
nhất khiến truyện dài lạc hướng/mâu thuẫn. Chỉ viết chương 1 sau khi được đồng ý.

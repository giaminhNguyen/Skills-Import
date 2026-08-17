---
name: i2-translate
description: "Dịch term của I2 Localization rồi ghi thẳng vào I2Languages.asset trong Unity. Hai chế độ: MISSING (chỉ dịch & thêm những ô còn trống) và OVERRIDE (dịch lại từ đầu toàn bộ). Cột English luôn = chính tên term, không dịch. USE WHEN người dùng nhắc tới: dịch i2, i2 localization, I2Languages, đa ngôn ngữ, localization, localize, translate term, thiếu bản dịch, term chưa dịch, 'thêm ngôn ngữ cho game', 'dịch hết text trong game', 'fill bản dịch', 'dịch lại toàn bộ term', 'check term nào thiếu dịch'. Invoke: /i2-translate [missing|override] [ngôn ngữ hoặc term cụ thể]."
user-invocable: true
argument-hint: "[missing|override] (mặc định missing) + tùy chọn: lọc ngôn ngữ 'vi,ja,ko' hoặc tên term cụ thể"
allowed-tools: Read, Glob, Grep, Bash, Write, Edit, AskUserQuestion
related: [deep-analysis]
---

# I2 Translate

Dịch term trong `I2Languages.asset` (I2 Localization) và ghi thẳng vào asset của Unity.

Bản dịch do **chính bạn (agent) dịch**, không gọi API ngoài. Script chỉ làm nhiệm vụ
đọc/ghi file YAML của Unity cho an toàn — **tuyệt đối không tự sửa tay `.asset` bằng
Edit/Write**, vì sai format là hỏng asset và Unity mất sạch term.

## 2 chế độ

| Chế độ | Làm gì | Khi nào dùng |
|---|---|---|
| `missing` (mặc định) | Quét ô còn trống → chỉ dịch và thêm phần thiếu, không đụng bản dịch đã có | Vừa thêm term mới, hoặc thêm ngôn ngữ mới |
| `override` | Dịch lại từ đầu **toàn bộ** term × toàn bộ ngôn ngữ, ghi đè hết | Bản dịch cũ kém/sai tone, đổi hướng ngôn từ toàn game |

Nếu người dùng không nói rõ chế độ → hỏi bằng `AskUserQuestion` trước khi chạy
(override ghi đè công sức cũ, không được tự đoán).

## Quy trình

### B0. Tìm asset

```bash
ls Assets/Resources/I2Languages.asset
```
Không có thì `Glob **/I2Languages.asset`. Nếu ra nhiều file → hỏi người dùng chọn.

Nhắc người dùng: **lưu scene & đóng Unity (hoặc ít nhất không sửa I2 lúc này)**.
Unity đang mở asset trong bộ nhớ có thể ghi đè ngược lại file sau khi ta sửa.

### B1. Export trạng thái

```bash
python .claude/skills/i2-translate/scripts/i2_export.py <asset> --mode missing --stats
```

In ra: số ngôn ngữ, số term, số ô còn trống. Báo lại con số này cho người dùng
trước khi dịch (để họ biết khối lượng).

Xuất file làm việc (ghi vào scratchpad, **không** để rác trong `Assets/`):

```bash
python .claude/skills/i2-translate/scripts/i2_export.py <asset> \
  --mode missing -o <scratchpad>/i2_work.json
```

Tùy chọn hữu ích:
- `--languages vi,ja,ko` — chỉ xử lý vài ngôn ngữ
- `--terms "shop;play;Bonus"` — chỉ vài term
- `--limit 20 --offset 0` — chia batch

### B2. Dịch

Đọc `i2_work.json`. Mỗi phần tử trong `terms`:
- `term` — key trong I2, cũng chính là text tiếng Anh gốc
- `need` — danh sách code ngôn ngữ cần bạn điền
- `current` — bản dịch đang có (mode override thì ghi đè, mode missing thì để yên)

Tự viết file JSON bản dịch (dùng `Write`), dạng:

```json
{
  "remove ads": { "vi": "Xóa quảng cáo", "ja": "広告を削除", "th": "ลบโฆษณา" },
  "Win Streak": { "vi": "Chuỗi thắng", "ja": "連勝" }
}
```

- **Không cần điền `en`** — script tự set cột English = tên term.
- Chia batch ~15–25 term / file để không bị cụt giữa chừng. Đặt tên
  `i2_tr_01.json`, `i2_tr_02.json`... rồi import lần lượt.
- Dịch **đủ mọi ngôn ngữ trong `need`** cho từng term, không bỏ sót ngôn ngữ nào.
  Không được lặng lẽ bỏ qua term khó.

### B3. Import vào asset

Chạy thử trước:
```bash
python .claude/skills/i2-translate/scripts/i2_import.py <asset> <tr.json> --mode missing --dry-run
```
Rồi ghi thật (tự backup `.bak` cạnh file JSON — tức trong scratchpad, không rác
trong `Assets/` — và tự parse lại asset để verify sau khi ghi):
```bash
python .claude/skills/i2-translate/scripts/i2_import.py <asset> <tr.json> --mode missing
```

`--mode override` để ghi đè ô đã có. Cờ khác: `--no-backup`, `--no-english-from-term`.

Script sẽ cảnh báo nếu JSON có term/code ngôn ngữ không tồn tại trong asset —
**phải xử lý cảnh báo đó**, thường là do bạn gõ sai tên term.

### B4. Kiểm tra lại

```bash
python .claude/skills/i2-translate/scripts/i2_export.py <asset> --stats
git diff --stat <asset>
```
- Số ô trống phải về 0 (mode missing) hoặc đúng phần đã chọn.
- `git diff` chỉ được đổi các dòng trong block `Languages:`. Nếu diff đụng
  `mLanguages`, `Flags`, hay số dòng term thay đổi → dừng, restore từ `.bak`.

Xong thì báo người dùng: mở lại Unity, `Ctrl+R` (Refresh) để reimport asset, mở
**Window → I2 Localization** kiểm tra vài term. File `.bak` nằm trong scratchpad,
giữ lại tới khi họ xác nhận OK.

## Quy tắc dịch

1. **English = term, không dịch.** Script tự lo.
2. **Ngữ cảnh: UI game casual sort/puzzle mobile.** Dịch như text nút bấm và popup
   trong game, không dịch kiểu văn bản kỹ thuật. Tone thân thiện, ngắn.
3. **Ngắn ngang hoặc ngắn hơn bản tiếng Anh.** Text nằm trong nút/khung cố định;
   dài quá là tràn UI. Đức/Nga/Pháp rất dễ dài — chọn từ ngắn nhất còn đúng nghĩa.
4. **Giữ nguyên 100%** placeholder và markup: `{0}`, `{coin}`, `%d`, `<sprite=...>`,
   `<color=#FFF>`, `\n`. Không dịch, không đổi thứ tự, không thêm/bớt khoảng trắng
   quanh chúng.
5. **Giữ kiểu viết hoa và dấu câu của term gốc.** Term `remove ads` viết thường thì
   bản dịch cũng viết thường; `failed!` giữ dấu `!`; `Continue?` giữ dấu `?`.
6. **Thuật ngữ game giữ nhất quán toàn bộ file.** `Booster`, `Combo`, `Win Streak`,
   `Starter Pack`, `Lucky Spin`, `Daily Quest`... — cùng một term tiếng Anh phải ra
   cùng một từ ở mọi chỗ trong cùng ngôn ngữ. Với tiếng Việt và các ngôn ngữ hay
   giữ nguyên tiếng Anh trong game (id, vi, th...), giữ nguyên từ quen thuộc với
   người chơi thay vì dịch cứng (vd `Combo` để nguyên, không dịch "chuỗi liên hoàn").
7. **Term mơ hồ thì bám ngữ cảnh gameplay**, không dịch theo nghĩa đen. Ví dụ:
   `Full` = đầy (ô/khay), `level` = màn chơi, `Term` = điều khoản (Terms of Service),
   `free` = miễn phí, `Restore` = khôi phục mua hàng. Không chắc → hỏi người dùng,
   đừng đoán bừa.
8. **Chuỗi lỗi chính tả trong term gốc** (vd `We d love to hear...`) dịch theo nghĩa
   đúng, không copy lỗi sang ngôn ngữ khác.
9. Ngôn ngữ CJK/Thái không cần khoảng trắng giữa từ như tiếng Anh; đừng dịch
   word-by-word.

## Ngôn ngữ trong asset hiện tại

`en` English (gốc), `zh-CN` 简体中文, `zh-TW` 繁體中文, `fr` Français, `de` Deutsch,
`id` Bahasa Indonesia, `it` Italiano, `ja` 日本語, `ko` 한국어, `pt` Português,
`ru` Русский, `es` Español, `th` ไทย, `tr` Türkçe, `vi` Tiếng Việt.

Danh sách này đọc từ asset lúc chạy (`i2_export.py` in ra) — nếu khác thì tin
output của script, không tin bảng này.

## Bẫy hay gặp

- **Unity đang mở** → sửa file xong Unity ghi đè lại. Đóng Unity hoặc Refresh ngay sau khi import.
- **Sửa tay `.asset` bằng Edit** → sai indent / sai số lượng dòng trong `Languages:`
  là Unity đọc lệch cột, term dịch nhảy sang ngôn ngữ khác. Luôn qua script.
- **Term trùng tên khác hoa/thường**: I2 có cờ `CaseInsensitiveTerms`. Copy tên term
  y nguyên từ file export, đừng gõ lại.
- **Term có category** dạng `Category/Key`: script vẫn set English = nguyên chuỗi.
  Nếu asset có loại term này, hỏi người dùng muốn English là `Category/Key` hay chỉ `Key`.
- **Đừng commit** khi chưa được người dùng xác nhận đã kiểm tra trong Unity.

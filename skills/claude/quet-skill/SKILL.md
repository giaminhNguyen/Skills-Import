---
name: quet-skill
description: Quét skill/plugin AI bằng SkillSpector trước khi cài - tìm prompt injection, rò rỉ dữ liệu, lệnh độc, leo thang quyền, rủi ro chuỗi cung ứng. Tự kiểm tra máy đã cài skillspector chưa, chưa có thì hỏi người dùng rồi cài. Kích hoạt khi nghe "quét skill", "kiểm tra skill", "skill này có an toàn không", "scan skill", "skillspector", "có nên cài skill này không", hoặc khi người dùng đưa link GitHub một skill/plugin và hỏi về độ an toàn.
---

# Quét skill bằng SkillSpector

CLI Python của NVIDIA, quét skill của Claude Code / Codex / MCP trước khi cài.
Không phải skill - là `skillspector.exe` chạy trong terminal.

## Bước 1 - kiểm tra đã cài chưa

```bash
skillspector --version 2>&1 | grep -v '^WARNING'
```

Ra `SkillSpector v2.11.2` (hoặc mới hơn) → có rồi, sang bước 3.
Ra `command not found` → sang bước 2.

## Bước 2 - chưa cài thì HỎI trước

Dùng `AskUserQuestion`: "Máy chưa có SkillSpector. Cài ngay không?"
- **Có** → chạy lệnh dưới (mất ~1-2 phút, kéo Python 3.12 + ~50 gói)
- **Không** → dừng, báo là không quét được

```bash
uv tool install "git+https://github.com/NVIDIA/skillspector.git"
```

Không có `uv`? `pip install uv` rồi chạy lại. Cài xong `skillspector.exe` nằm ở
`~/.local/bin/`, đã có sẵn trong PATH.

## Bước 3 - quét

Thư mục local:

```bash
skillspector scan ~/.claude/skills/bien-tau-36 --no-llm 2>&1 | grep -v '^WARNING'
```

Skill trên GitHub - clone vào scratchpad rồi quét, **không cài trước khi quét**:

```bash
d=$(mktemp -d)
git clone --depth 1 <repo-url> "$d"
skillspector scan "$d" --no-llm 2>&1 | grep -v '^WARNING'
```

Luôn kèm `--no-llm` trừ khi đã đặt `ANTHROPIC_API_KEY` + `SKILLSPECTOR_PROVIDER=anthropic`.

## Đọc kết quả

- **Risk score 0-100** + nhãn mức độ + khuyến nghị.
- `Analyzer statuses`: `no_applicable_files` là bình thường (skill toàn markdown
  thì analyzer AST/YARA không có gì để đọc), không phải lỗi.
- `Ledger exceptions / reference_unresolved`: skill trỏ tới file mà scanner không
  resolve được đường dẫn. Cảnh báo nhẹ, tự kiểm tra thủ công dòng đó.
- `Executable scripts: No` → skill không có script chạy được, rủi ro thấp hẳn.

Báo cho người dùng bằng tiếng Việt: điểm rủi ro, các finding nghiêm trọng, và
kết luận nên cài hay không. Đừng dán nguyên output.

## Gotcha

- **3 dòng WARNING luôn xuất hiện** ở mọi lệnh, kể cả `--version`, kể cả khi có
  `--no-llm`: `Skipping analyzer semantic_* : required API key is missing`.
  Không phải lỗi. Luôn lọc bằng `grep -v '^WARNING'`.
- Output ghi ra **stderr** lẫn stdout → phải có `2>&1` trước khi grep.
- Cần Python 3.12+ nhưng máy đang có 3.11 cũng không sao, `uv tool install`
  tự tải riêng 3.12 cho nó.
- Muốn gọi từ trong phiên Claude thay vì shell thì cài bản MCP:
  `uv tool install --force 'skillspector[mcp] @ git+https://github.com/NVIDIA/skillspector.git'`
  rồi `claude mcp add skillspector -- skillspector mcp`. Chưa test.
- **Quét cả repo hay bị dương tính giả.** Quét nguyên repo NVIDIA/skillspector
  ra `100/100 CRITICAL - DO NOT INSTALL` vì repo chứa 336 file mẫu tấn công để
  test. Repo nào có thư mục `tests/`, `fixtures/`, `examples/` cũng vậy. Sau khi
  clone, trỏ thẳng vào đúng thư mục skill (`"$d/skills/<ten>"`), đừng quét gốc repo.
- `Skill: unknown` nghĩa là chỗ đang quét không có `SKILL.md` ở gốc → nhiều khả
  năng đang trỏ sai chỗ.
- **`AE1 HIGH - Referenced artifact was not completely inspected`** là dương tính
  giả phổ biến nhất với skill chỉ có markdown: chỉ cần trong `SKILL.md` có một
  chuỗi trông giống đường dẫn mà không tồn tại thật (ví dụ `<ten-file>` trong
  câu lệnh mẫu) là dính. Chính file này quét ra 25/100 MEDIUM vì lý do đó.
  Đối chiếu số dòng nó báo trước khi kết luận skill có vấn đề.

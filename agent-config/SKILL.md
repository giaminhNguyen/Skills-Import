---
name: agent-config
description: >
  Cấu hình agent build và plan với skills tuỳ chọn. Thay thế agent ponytail riêng
  bằng cách nhúng skill principles trực tiếp vào system prompt của build/plan.
  Khi gọi skill này, agent sẽ hỏi bạn muốn gán skill nào cho build, skill nào cho plan,
  rồi tự động sinh prompt files và cập nhật opencode.json.
user-invocable: true
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
---

# Agent Config

Cấu hình agent **build** và **plan** với các skill bạn chọn — thay vì dùng agent ponytail riêng biệt.

## Cách hoạt động

Skill này **đọc danh sách skill có sẵn**, hỏi bạn muốn gán skill nào cho build/plan, rồi **sinh prompt files + cập nhật opencode.json** — tất cả trong một lần chạy.

Mỗi skill được chọn sẽ được **inline** (nhúng nội dung) vào system prompt của agent tương ứng, nên agent tự động mang principles của skills đó mà không cần gọi `skill` tool.

---

## Workflow

### Bước 1: Quét skills

Đọc danh sách skill từ cả 2 nơi:
- Live skills: `%USERPROFILE%\.config\opencode\skills\*`
- Source repo (nếu có): `<project-root>\*\SKILL.md` (cùng cấp với opencode.json)

Hiển thị danh sách dạng:
```
Skills có sẵn:
  [1] ponytail          — Forces laziest solution
  [2] logic-self-test   — Kiểm tra logic plan/code
  [3] deep-analysis     — 7-rule phân tích chuyên sâu
  [4] impeccable        — Frontend design
  [5] session-continuity— Lưu/khôi phục session
  ...
```

### Bước 2: Hỏi mapping

Hỏi user lần lượt:

```
▶ Build agent sẽ dùng skills nào? (nhập số, cách nhau bằng dấu phẩy hoặc khoảng trắng)
  VD: "1 2 3" hoặc "1,2,3" hoặc "all" hoặc "none"
  >> 

▶ Plan agent sẽ dùng skills nào? (nhập số, cách nhau bằng dấu phẩy hoặc khoảng trắng)
  >> 

▶ Set default_agent là: (1) build / (2) plan / (3) giữ nguyên
  >>
```

### Bước 3: Sinh prompt files

Tạo (hoặc ghi đè) các file:

```
.opencode/prompts/
├── build.md      ← system prompt cho build agent
└── plan.md       ← system prompt cho plan agent
```

Mỗi file được cấu trúc:

```markdown
# Build Agent

Bạn là **Build** agent — toàn quyền edit, bash, write.

## Applied Skills

Các skill sau đang hoạt động. Bạn PHẢI tuân thủ tất cả rules bên dưới trong mọi câu trả lời.

---

<nội dung skill 1 — chỉ body, bỏ frontmatter>

---

<nội dung skill 2>

---
```

**Cách extract skill content:** Bỏ phần frontmatter YAML (`--- ... ---`), lấy phần body còn lại.

### Bước 4: Cập nhật opencode.json

Ghi cấu hình agent vào `opencode.json`. Ví dụ output:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "default_agent": "build",
  "agent": {
    "build": {
      "mode": "primary",
      "prompt": "{file:./.opencode/prompts/build.md}",
      "permission": {
        "edit": "allow",
        "bash": "allow"
      }
    },
    "plan": {
      "mode": "primary",
      "prompt": "{file:./.opencode/prompts/plan.md}",
      "permission": {
        "edit": "deny",
        "bash": "deny"
      }
    }
  }
}
```

### Bước 5: Dọn dẹp (nếu cần)

- Nếu `.opencode/agents/ponytail.md` tồn tại và user không còn dùng ponytail riêng: **hỏi** có muốn xoá không (mặc định: có)
- Nếu trong `opencode.json` còn key agent cũ (VD: `"ponytail": {...}`): **hỏi** có muốn xoá không

---

## Bảng mapping skill → agent

Kết thúc workflow, hiển thị tóm tắt:

```
=== KẾT QUẢ ===

Build agent được áp dụng: ponytail, logic-self-test
Plan agent được áp dụng: deep-analysis

default_agent: build

File đã tạo/cập nhật:
  ✅ .opencode/prompts/build.md
  ✅ .opencode/prompts/plan.md
  ✅ opencode.json

File đã xoá:
  ✅ .opencode/agents/ponytail.md

Khởi động lại opencode để áp dụng thay đổi.
```

---

## Lưu ý

- **Không thay đổi file SKILL.md gốc** — chỉ đọc nội dung để inline.
- **Prompt files được sinh ra** là bản snapshot tại thời điểm chạy. Nếu skill gốc thay đổi, chạy lại skill này để cập nhật.
- **Thư mục `.opencode/prompts/`** — tạo nếu chưa tồn tại. Đây là nơi chứa prompt files tạm, không phải skill.
- **Không tự ý ghi đè** cấu hình agent khác ngoài build và plan — giữ nguyên các agent tuỳ chỉnh khác nếu có.

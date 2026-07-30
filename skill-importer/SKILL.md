---
name: skill-importer
description: >-
  Setup và quản lý kho skills tập trung qua git. Dùng khi user nói "setup kho skill", "lưu skill lên repo", 
  "tạo repo skills", "add skill vào repo", "gom skill lại", "push skill", "import skill từ repo", 
  "kéo skill từ repo về", "đồng bộ skill", "kho skill", "chuyển skill giữa các máy".
  KHÔNG tự động chạy — chỉ kích hoạt khi user chủ động muốn thao tác với skill collection.
  Áp dụng cho mọi loại agent (gemini, claude, codex, antigravity, opencode).
---

# skill-importer

Workflow tương tác — agent hỏi, user trả lời, agent làm.
Không phải CLI script. Agent tự thao tác git và file.

## Workflow: Setup / Add skills vào repo

Khi user nói "setup kho skill", "add skill lên repo", "lưu skill lại" → agent làm các bước sau:

### Bước 1 — Hỏi repo path

Hỏi user đường dẫn đến skills repo:
```
Agent: "Đường dẫn repo skills? (Enter để dùng mặc định: ~/skills-repo)"
User:  "D:\my-skills"  (hoặc Enter để lấy mặc định)
```

- Nếu path chưa tồn tại → `git init` ở path đó, báo "Đã tạo repo mới tại ..."
- Nếu path đã tồn tại và có `.git` → dùng luôn
- Nếu path tồn tại nhưng chưa có `.git` → hỏi user có muốn `git init` không

### Bước 2 — Scan skills có sẵn

Quét tất cả thư mục skills ở các vị trí phổ biến:

| Agent | Vị trí |
|-------|--------|
| opencode | `%USERPROFILE%\.config\opencode\skills\` |
| claude | `%USERPROFILE%\...\.claude\skills\` (tìm gần đúng) |
| gemini | `%USERPROFILE%\.gemini\skills\` |
| codex | `%USERPROFILE%\.codex\skills\` |
| antigravity | `%USERPROFILE%\.antigravity\skills\` |

Mỗi thư mục hợp lệ = có chứa file `SKILL.md`.
Hiển thị danh sách skills tìm được theo dạng:

```
Tìm thấy 6 skills:
  📦 controller-flow-design    → .config\opencode\skills\
  📦 logic-self-test           → .config\opencode\skills\
  📦 prompt-crafter            → .config\opencode\skills\
  📦 gdd-spec-retrieval        → .claude\skills\
  📦 impeccable                → .agents\skills\
  📦 session-continuity        → .config\opencode\skills\
```

### Bước 3 — So sánh với repo

Đọc thư mục repo ở Bước 1. So sánh:

```
So sánh với repo:
  ✅ controller-flow-design     — đã có
  ✅ logic-self-test            — đã có
  ❌ prompt-crafter             — chưa có
  ❌ gdd-spec-retrieval         — chưa có
  ✅ impeccable                 — đã có
  ❌ session-continuity         — chưa có
```

### Bước 4 — Hỏi user chọn

```
Agent: "3 skills chưa có trong repo. Muốn add tất cả không?
  - prompt-crafter
  - gdd-spec-retrieval
  - session-continuity
  (a) All / (1,2,3) Chọn từng cái / (n) None"
```

User trả lời:
- `a` → add hết
- `1,3` → chỉ add skill số 1 và 3
- `n` → thoát

### Bước 5 — Copy vào repo + git commit

Với mỗi skill được chọn:
1. Copy thư mục skill vào repo (giữ nguyên tên)
2. `git add .`
3. `git commit -m "skill-importer: add <tên skill>"`

Báo kết quả:
```
Đã thêm 3 skills vào repo.
Commit: skill-importer: add prompt-crafter
Commit: skill-importer: add gdd-spec-retrieval
Commit: skill-importer: add session-continuity
```

### Bước 6 — Hỏi push remote

```
Agent: "Push lên remote không? Nếu có, nhập remote URL:"
User:  "https://github.com/me/skills-repo.git" (hoặc Enter để bỏ qua)
```

Nếu user nhập URL → `git remote add origin <url>` + `git push -u origin master`.

## Workflow: Import skills từ repo

Khi user nói "kéo skill từ repo về", "import skill":

### Bước 1 — Hỏi repo path

Giống Bước 1 ở trên.

### Bước 2 — Đọc danh sách skills trong repo

```
Tìm thấy 5 skills trong repo:
  📦 controller-flow-design
  📦 logic-self-test
  📦 prompt-crafter
  📦 gdd-spec-retrieval
  📦 session-continuity
```

### Bước 3 — Hỏi user muốn copy vào agent nào

```
Agent: "Copy vào agent nào?
  (1) opencode  → %USERPROFILE%\.config\opencode\skills\
  (2) claude    → %USERPROFILE%\...\.claude\skills\
  (3) tất cả
```

### Bước 4 — Copy

Với mỗi skill được chọn → copy từng thư mục vào thư mục agent tương ứng.
Nếu skill đã tồn tại → hỏi "overwrite? (y/n/a/s)".

### Bước 5 — Báo kết quả

```
Đã import 5 skills vào opencode.
3 skills mới, 2 skills đã có (giữ nguyên).
```

## Workflow: Kiểm tra / Status

Khi user nói "kiểm tra skill", "check sync":

1. Hỏi repo path
2. Scan local skills (giống Bước 2 của Setup)
3. Đọc danh sách trong repo
4. In bảng so sánh (giống Bước 3 của Setup)
5. Kết luận: "Đồng bộ" / "Thiếu N skills trong repo" / "Thiếu M skills trong local"

## Lưu ý khi làm

- **Copy, không symlink.** An toàn, không phụ thuộc repo sau khi copy.
- **Git commit từng skill riêng.** Dễ review history, dễ revert.
- **Không tự động push.** Luôn hỏi user trước.
- **Hỏi trước khi overwrite.** Nếu skill đã tồn tại ở đích, hỏi user.
- **Tìm skills ở nhiều nơi.** Không chỉ opencode skills, còn .claude, .gemini, project-level .claude/skills/.
- project-level skills: kiểm tra cả `%USERPROFILE%\Desktop\Projects\*\.claude\skills\` và `%USERPROFILE%\Desktop\Projects\*\.agents\skills\` nếu có.

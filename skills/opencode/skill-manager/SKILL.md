---
name: skill-manager
description: >-
  Quản lý tập trung toàn bộ skills và mọi artifact là skill của người dùng qua repo git.
  Dùng khi user muốn "export skill", "gom skill lên repo", "lưu skill", "add skill vào repo",
  "push skill", "import skill", "kéo skill từ repo", "copy skill về máy", "đồng bộ skill",
  "kiểm tra skill", "check sync", "kho skill", "skill-manager", "chuyển skill giữa các máy",
  "export agent", "lưu command", "gom command lại", "đồng bộ plugin", "backup prompt",
  "import subagent", "chuyển agent giữa máy", "lưu mcp", "đồng bộ mcp", "sao lưu opencode.json",
  "kho agent", "skill npm", "npm skill", "skill từ package npm",
  "đồng bộ skill npm", "lưu skill npm", "backup skill npm", "skill-libraries",
  "opencode-skills-collection".
  Gồm 3 chức năng: EXPORT (artifact → repo), IMPORT (repo → artifact), STATUS (so sánh đồng bộ).
  Thay thế hoàn toàn skill-importer.
  KHÔNG tự động chạy — chỉ kích hoạt khi user chủ động muốn thao tác với skill collection.
  Áp dụng cho mọi agent: opencode, claude, gemini, codex, antigravity.
---

# skill-manager

Quản lý tập trung skills và mọi artifact là skill qua repo git. **Thay thế hoàn toàn skill-importer.**

Workflow tương tác — agent hỏi, user trả lời ngắn, agent làm. Không phải CLI script.

## Bắt đầu: chọn chức năng

Khi được gọi, hiển thị menu chức năng trước rồi làm theo workflow tương ứng:

```
Chọn chức năng:
  (1) EXPORT — gom artifact từ máy lên repo
  (2) IMPORT — kéo artifact từ repo về máy
  (3) STATUS — kiểm tra đồng bộ
```

## Quy tắc hiển thị (bắt buộc, ưu tiên cao nhất)

- Luôn dùng **bảng** (table) khi liệt kê / so sánh artifact — 1 artifact 1 dòng, có cột trạng thái: ✅ đã có (giống nhau) / 🆕 mới / ⚠️ khác phiên bản.
- So sánh phiên bản = so nội dung theo bảng **Định nghĩa artifact** (hash file chính). Cùng nội dung → ✅; khác → ⚠️.
- Luôn dùng **menu đánh số** khi cần user chọn. Chỉ nhận trả lời ngắn: `a` (all) / `n` (none) / số `1,3`.
- Ngôn ngữ tiếng Việt, ngắn gọn, không lặp thông tin, không in dư thừa.
- Kết thúc mỗi workflow bằng **tóm tắt 1 dòng**, ví dụ: `Đã export 3/5 artifacts. Commit: skill-manager: add skill: prompt-crafter`.

## Scope & đường dẫn

Mỗi lần chạy LUÔN hỏi scope. Chỉ có 3 scope:

```
(1) Project → thư mục artifacts của dự án hiện tại (working directory)
(2) User    → vị trí global của user (mặc định máy)
(3) All     → cả hai
```

Bảng path theo scope (dùng chung cho mọi workflow):

| Agent | Project scope | User scope |
|-------|---------------|------------|
| opencode | `<cwd>\.opencode\skills\` | `%USERPROFILE%\.config\opencode\skills\` |
| claude | `<cwd>\.claude\skills\` | `%USERPROFILE%\.claude\skills\` (tìm gần đúng) |
| gemini | `<cwd>\.gemini\skills\` | `%USERPROFILE%\.gemini\skills\` |
| codex | `<cwd>\.codex\skills\` | `%USERPROFILE%\.codex\skills\` |
| antigravity | `<cwd>\.antigravity\skills\` | `%USERPROFILE%\.antigravity\skills\` |

Với Project scope, path luôn tính từ thư mục dự án hiện tại (cwd) — không hardcode đường dẫn máy khác.
Khi scan, kiểm tra thêm project-level skills ở `%USERPROFILE%\Desktop\Projects\*\.claude\skills\` và `%USERPROFILE%\Desktop\Projects\*\.agents\skills\` nếu có.

Ngoài thư mục `skills\`, quét thêm các thư mục artifact tương ứng của từng agent theo **Định nghĩa artifact** (vd `.opencode\agent\`, `.opencode\command\`, `.opencode\plugin\`, `.codex\prompts\`, `.gemini\prompts\`, `opencode.json`...).

## Định nghĩa artifact — cái gì được quản lý

Thay cho định nghĩa cũ "Thư mục skill hợp lệ = có chứa SKILL.md", skill-manager quản lý **mọi artifact là skill** theo bảng:

| Loại | Định danh | Ví dụ path | So sánh phiên bản |
|------|-----------|------------|-------------------|
| skill | Thư mục chứa `SKILL.md` | `.opencode\skills\<name>\SKILL.md` | hash `SKILL.md` |
| agent / subagent | File `.md` trong thư mục agent | `.opencode\agent\<name>.md`, `.claude\agents\<name>.md` | hash file `.md` |
| command | File `.md` trong thư mục command | `.opencode\command\<name>.md`, `.claude\commands\<name>.md` | hash file `.md` |
| plugin | Thư mục chứa `plugin.json` / file config plugin | `.opencode\plugin\<name>\` | hash `plugin.json` (nếu có) |
| prompt | File `.md` trong thư mục prompts | `.codex\prompts\<name>.md`, `.gemini\prompts\<name>.md` | hash file `.md` |
| mcp | Block `mcp.<serverName>` trong `opencode.json` | `.config\opencode\opencode.json` | hash block `mcp.<serverName>` |

**Định danh mỗi artifact = bộ 3 `(agent, loại, tên)`.** Ví dụ: `opencode/skill/controller-flow-design`, `opencode/agent/build`, `claude/command/...`. Hai artifact cùng loại + tên nhưng khác agent là **2 artifact khác nhau**.

## Nguồn npm — skill tải qua package manager

Ngoài artifact local, skill-manager truy vấn thêm skill đến từ npm. Có **3 nguồn**:

| Nguồn | Định nghĩa | Vị trí scan |
|-------|------------|-------------|
| A. Package plugin npm | Package khai báo trong `plugin` array của `opencode.json`, opencode tự tải qua Bun/npm; bên trong gói chứa skill (mọi `**/SKILL.md`, thường nằm ở `bundled-skills/`, `skills/`, `dist/`, `skill/`) | `%USERPROFILE%\.config\opencode\node_modules\<pkg>\` (global, tìm gần đúng — có thể ở Bun cache) và `<cwd>\node_modules\<pkg>\` / `<cwd>\.opencode\node_modules\<pkg>\` (project). Không tìm thấy → hỏi user đường dẫn |
| B. Vault skill thô | Nơi plugin npm deploy skill thô về (vd `opencode-skills-collection` deploy vào vault, thư mục `skills\` chỉ còn pointer files) | `%USERPROFILE%\.config\opencode\skill-libraries\` (và `<cwd>\.opencode\skill-libraries\` nếu có) |
| C. Khai báo trong config | `skills.paths` (thư mục skill, có thể trỏ vào node_modules) và `skills.urls` (nguồn trực tuyến) trong `opencode.json` | Global `~/.config/opencode/opencode.json`; Project `<cwd>\opencode.json` hoặc `<cwd>\.opencode\opencode.json` |

**Quy tắc xử lý npm (bắt buộc):**

- **Read-mostly.** Package npm do package manager quản lý — `npm install`/`update` sẽ ghi đè. skill-manager **KHÔNG bao giờ ghi** (IMPORT/copy) vào `node_modules` hay bên trong package npm.
- **STATUS**: quét cả 3 nguồn, liệt kê skill npm kèm nguồn (A/B/C) + package/phiên bản nếu biết (đọc `package.json` của gói).
- **EXPORT**: skill từ nguồn A/B được phép sao lưu vào repo — copy nguyên cây thư mục (gom subskill) vào `skills\npm\<pkg>\<name>\` (không rõ package → `skills\npm\<name>\`). Nguồn C dạng url: không copy, chỉ ghi tham chiếu vào file `npm-sources.md` trong repo.
- **IMPORT**: skill trong repo **không được đưa vào package npm**; nếu user muốn dùng, hướng dẫn copy về thư mục skill chuẩn theo scope (vd `~/.config/opencode/skills\`) hoặc dùng `npx skills add`.
- **So sánh phiên bản**: như skill thường (hash `SKILL.md`). Riêng nguồn A, nếu `package.json` đổi phiên bản → báo ⚠️ khác phiên bản.

## Cấu trúc repo (phân mục rõ ràng + gom subskill)

Repo skills chia **phân mục rõ ràng theo loại artifact** — mỗi loại 1 thư mục riêng, không trộn lẫn:

```
<repo>/
  skills/
    opencode/<name>/
    claude/<name>/
    gemini/<name>/
    codex/<name>/
    antigravity/<name>/
    npm/<pkg>/<name>/   # skill sao lưu từ nguồn npm (không rõ pkg → npm/<name>/)
  agents/
    opencode/<name>.md
    claude/<name>.md
  commands/
    opencode/<name>.md
    claude/<name>.md
  plugins/
    opencode/<name>/
  prompts/
    codex/<name>.md
    gemini/<name>.md
  mcp/
    opencode/<serverName>.json
```

**Quy tắc gom subskill (bắt buộc):**

- Khi export một skill có cấu trúc con — subfolder `reference/`, `scripts/`, `evals/`, subskill nằm trong cùng thư mục — PHẢI copy **toàn bộ cây thư mục con** vào chung 1 folder trong repo. Không tách lẻ từng file, không bỏ sót file phụ trợ, giữ nguyên tên thư mục con.
- Các subskill / file kèm theo luôn **gom chung folder với artifact cha** — không tạo folder rời cho từng mảnh.
- Import ngược lại: tái tạo đúng cấu trúc đã gom, không làm phẳng cây thư mục.

## Workflow: EXPORT (artifact → repo)

Kích hoạt khi user muốn gom lên repo: "export skill", "lưu skill", "add skill vào repo", "gom skill lại", "backup agent/command/plugin/prompt/mcp".

### Bước 1 — Hỏi repo path
Hỏi đường dẫn repo skills, Enter để lấy mặc định `~/skills-repo`.
- Path chưa tồn tại → `git init` ở đó, báo `Đã tạo repo mới tại <path>`
- Path có `.git` → dùng luôn
- Path tồn tại chưa có `.git` → hỏi user có muốn `git init` không

### Bước 2 — Hỏi scope (bắt buộc)
Hỏi Project / User / All.

### Bước 3 — Scan artifact local
Quét **tất cả loại artifact** theo scope đã chọn (không chỉ skill thuần), kèm **Nguồn npm (A/B/C)** nếu có. Hiển thị bảng kèm cột Loại:

```
Tìm thấy 8 artifacts:
| Loại    | Artifact                | Vị trí                     | Nguồn |
|---------|-------------------------|----------------------------|-------|
| skill   | controller-flow-design  | .config\opencode\skills\   | local |
| skill   | prompt-crafter          | .config\opencode\skills\   | local |
| agent   | build                   | .config\opencode\agent\    | local |
| agent   | plan                    | .config\opencode\agent\    | local |
| command | do-things               | .config\opencode\command\  | local |
| prompt  | plan                    | .codex\prompts\            | local |
| mcp     | <serverName>            | opencode.json              | local |
| skill   | brainstorming           | node_modules\opencode-skills-collection\ | npm A |
```

### Bước 4 — So sánh với repo
Đọc danh sách artifact trong repo theo từng loại. Với artifact có ở cả 2 nơi, so hash theo cột "So sánh phiên bản" ở bảng Định nghĩa. Riêng skill npm nguồn A, so thêm phiên bản `package.json` của gói. Hiển thị bảng trạng thái:

```
| Loại   | Artifact               | Repo            |
|--------|------------------------|-----------------|
| skill  | controller-flow-design | ✅ đã có        |
| skill  | prompt-crafter         | 🆕 mới          |
| agent  | build                  | 🆕 mới          |
| mcp    | <serverName>           | ⚠️ khác phiên bản |
```

### Bước 5 — Hỏi chọn
```
3 artifacts chưa có trong repo. Chọn để export:
  (a) All
  (n) None
  (1,3) Chọn từng cái
```
User trả lời: `a` → chọn hết; `1,3` → chỉ chọn 1 và 3; `n` → dừng.
Nếu danh sách có artifact **⚠️ khác phiên bản**, hỏi riêng: `Cập nhật phiên bản repo theo local cho <loại>: <tên>? (y/n)` — chỉ overwrite khi user đồng ý.

### Bước 6 — Copy + commit
Với mỗi artifact được chọn:
1. Copy theo **Cấu trúc repo** — đúng thư mục loại + agent, **gom toàn bộ cây thư mục con** (subskill/file phụ trợ).
2. MCP: trích block `mcp.<serverName>` từ `opencode.json` → lưu thành file `<serverName>.json` trong `mcp\<agent>\`.
3. Skill npm (nguồn A/B): copy nguyên cây thư mục vào `skills\npm\<pkg>\<name>\` (không rõ package → `skills\npm\<name>\`). Nguồn C dạng url: không copy — chỉ ghi dòng tham chiếu vào `npm-sources.md` ở repo.
4. `git add .`
5. `git commit -m "skill-manager: add <loại>: <tên>"` — artifact mới; `git commit -m "skill-manager: update <loại>: <tên>"` — cập nhật phiên bản đã có.

Commit **từng artifact riêng** để dễ review history.

### Bước 7 — Hỏi push
Hỏi có push lên remote không. Nếu có, hỏi remote URL → `git remote add origin <url>` + `git push -u origin master`.

Kết thúc bằng tóm tắt 1 dòng:
```
Đã export 3 artifacts vào repo. Commit: skill-manager: add skill: prompt-crafter, ...
```

## Workflow: IMPORT (repo → artifact)

Kích hoạt khi user muốn kéo về: "import skill", "kéo skill từ repo", "copy skill về máy", "khôi phục agent/command/plugin/prompt/mcp".

### Bước 1 — Hỏi repo path
Như Bước 1 của EXPORT.

### Bước 2 — Đọc danh sách artifact trong repo
Hiển thị bảng kèm cột Loại:
```
Tìm thấy 7 artifacts trong repo:
| Loại   | Artifact               | Repo |
|--------|------------------------|------|
| skill  | controller-flow-design | ✅   |
| agent  | build                  | ✅   |
| mcp    | <serverName>           | ✅   |
```

### Bước 3 — Hỏi scope import (bắt buộc)
Hỏi Project / User / All.

### Bước 4 — Hỏi copy vào agent nào
```
Copy vào agent nào?
  (1) opencode
  (2) claude
  (3) tất cả
```
Path đích tính theo scope (Bước 3) + agent + loại artifact: skill → `skills\<name>\`, agent → `agent\<name>.md`, command → `command\<name>.md`, plugin → `plugin\<name>\`, prompt → `prompts\<name>.md`.

### Bước 5 — Copy
- Skill/plugin: copy **toàn bộ thư mục** (gom subskill, giữ cây thư mục con).
- Agent/command/prompt: copy file `.md` vào đúng thư mục loại.
- MCP: **merge** block `mcp.<serverName>` vào file `opencode.json` của agent đích — backup file trước khi merge, KHÔNG ghi đè toàn bộ file, không đụng các mcp server khác.
- Skill trong repo đặt ở `skills\npm\...`: KHÔNG import vào node_modules/package npm (xem Nguồn npm) — hỏi user có muốn copy về thư mục skill chuẩn theo scope không.
- Nếu artifact đã tồn tại ở đích:
  - Nội dung giống hệt (✅) → bỏ qua, giữ nguyên.
  - Nội dung khác (⚠️ khác phiên bản) → hỏi `overwrite? (y/n/a/s)`.

### Bước 6 — Báo kết quả
```
Đã import 5 artifacts vào opencode (scope: User).
3 artifacts mới, 2 artifacts đã có (giữ nguyên).
```
Nếu có artifact bị overwrite, ghi rõ: `1 artifact cập nhật phiên bản (<loại>: <tên>).`

## Workflow: STATUS (kiểm tra đồng bộ)

Kích hoạt khi user nói "kiểm tra skill", "check sync":
1. Hỏi scope
2. Hỏi repo path
3. Scan local theo **tất cả loại artifact** kèm **Nguồn npm (A/B/C)**
4. Đọc danh sách trong repo
5. In bảng so sánh (giống Bước 4 của EXPORT, kèm cột Loại + cột Local + Repo, đánh dấu nguồn npm)
6. Kết luận 1 dòng: `Đồng bộ` / `Thiếu N artifacts trong repo` / `Thiếu M artifacts trong local` / `N artifacts khác phiên bản` (nêu tên, kèm package npm nếu đổi phiên bản)

## Lưu ý khi làm

- **Luôn hỏi scope (bắt buộc).** Chỉ có 3 scope Project / User / All. Không tự chọn scope hay bỏ qua bước hỏi. Với Project scope, path đích tính từ cwd, không hardcode.
- **Copy, không symlink.** An toàn, không phụ thuộc repo sau khi copy.
- **Git commit từng artifact riêng.** Dễ review history, dễ revert.
- **Không tự động push.** Luôn hỏi user trước.
- **Hỏi trước khi overwrite.** Nếu artifact đã tồn tại ở đích, hỏi user.
- **So sánh phiên bản theo bảng Định nghĩa artifact.** Artifact trùng tên khác nội dung = ⚠️ khác phiên bản, phải hỏi user trước khi ghi đè.
- **Tìm artifact ở nhiều nơi.** Không chỉ opencode skills, còn agent/command/plugin/prompt/mcp của `.claude`, `.gemini`, project-level `.agents\skills\`, ...
- **Quét skill npm.** Bao gồm: package plugin npm trong node_modules (mọi `**/SKILL.md` trong gói), vault `skill-libraries\`, và `skills.paths`/`skills.urls` khai báo trong `opencode.json`. Không tìm thấy node_modules → hỏi user đường dẫn, không đoán bừa.
- **Không ghi vào node_modules / package npm.** IMPORT không bao giờ chạm package npm (bị package manager ghi đè). Muốn dùng skill từ repo kiểu npm → hướng dẫn copy về thư mục skill chuẩn hoặc `npx skills add`.
- **EXPORT skill npm.** Sao lưu vào `skills\npm\<pkg>\<name>\` (gom subskill, giữ cây con); nguồn url chỉ lưu tham chiếu vào `npm-sources.md`.
- **Phân mục repo rõ ràng.** Artifact luôn vào đúng thư mục loại + agent theo Cấu trúc repo, không trộn lẫn.
- **Gom subskill.** Copy trọn cây thư mục con (reference/, scripts/, evals/, subskill...) vào chung folder — không tách lẻ, không bỏ sót file phụ trợ.
- **MCP merge cẩn thận.** Backup `opencode.json` trước khi merge; chỉ thêm/sửa block của server được chọn, không động vào phần còn lại.
- **Tuân thủ Quy tắc hiển thị** (bảng + menu đánh số + tóm tắt 1 dòng) trong mọi workflow.

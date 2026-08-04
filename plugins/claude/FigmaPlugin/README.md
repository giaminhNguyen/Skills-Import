# Figma MCP Go — plugin bridge

Cầu nối giữa **Figma** và **Claude**: cho phép Claude đọc và ghi trực tiếp file Figma
mà không cần Figma API token và không dính rate limit của Figma REST API.

## Kiến trúc — hai nửa phải khớp nhau

Hệ thống gồm hai phần chạy song song:

| Thành phần | Nằm ở đâu | Vai trò |
|---|---|---|
| **Figma plugin** (thư mục này) | Chạy bên trong Figma Desktop | Đọc/ghi document, nối WebSocket tới `ws://localhost:1994/ws` |
| **MCP server** `@vkhanhqui/figma-mcp-go` | Tải qua `npx` khi Claude khởi động | Nói chuyện MCP với Claude, mở cổng `1994` cho plugin |

Claude không nói chuyện trực tiếp với Figma. Luồng đầy đủ:

```
Claude  ──stdio(MCP)──►  figma-mcp-go server  ──WebSocket :1994──►  Figma plugin  ──►  Figma document
```

Cả **hai** nửa đều phải chạy thì tool mới hoạt động. Chỉ cài MCP server mà không mở
plugin trong Figma thì các tool sẽ báo lỗi không có client nào kết nối.

## Cài vào Claude

### Cách 1 — cài như một plugin (dùng được ở mọi project)

```
/plugin marketplace add G:\WidoGame\FigmaPlugin
/plugin install figma-mcp-go@widogame-figma
```

### Cách 2 — chỉ dùng trong thư mục này

File [.mcp.json](.mcp.json) đã có sẵn. Mở thư mục này bằng Claude Code, MCP server
sẽ tự được nạp, không cần cài gì thêm.

Hoặc thêm vào project bất kỳ bằng CLI:

```bash
claude mcp add -s project figma-mcp-go -- npx -y @vkhanhqui/figma-mcp-go@0.1.3
```

## Cài vào Figma

1. Mở **Figma Desktop** (bản web không import được plugin dev).
2. **Plugins → Development → Import plugin from manifest…**
3. Chọn [manifest.json](manifest.json) trong thư mục này.
4. Mở một file Figma bất kỳ rồi chạy plugin. Panel phải hiện **Connected** màu xanh.

Nếu panel báo **Disconnected**: MCP server chưa chạy. Server chỉ khởi động khi Claude
khởi động nó, nên hãy mở Claude trước, rồi bấm lại plugin (plugin tự retry mỗi 1.5s).

## Vì sao pin cứng phiên bản `0.1.3`

Bundle Figma plugin trong thư mục này (`dist/code.js`) là mã đã build sẵn và **đóng băng** —
nó hiện thực đúng 72 tool handler khớp với server `0.1.3` (tool thứ 73, `save_screenshots`,
chạy hoàn toàn phía server nên không cần handler).

Nếu để `@latest`, một bản server mới hơn có thể thêm tool mà `dist/code.js` không biết xử lý,
gây lỗi lúc chạy. Vì vậy config pin cứng `@0.1.3`.

**Khi nâng cấp server**, phải cập nhật cả hai nửa cùng lúc: lấy `plugin.zip` mới từ
[releases](https://github.com/vkhanhqui/figma-mcp-go/releases), thay `dist/` + `manifest.json`,
rồi đổi số phiên bản ở cả ba chỗ: [.mcp.json](.mcp.json),
[.claude-plugin/plugin.json](.claude-plugin/plugin.json), và mục `version` của plugin.

## Kiểm tra nhanh

```bash
# Server có chạy và trả lời MCP không (in ra serverInfo rồi thoát)
echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"probe","version":"1.0"}}}' \
  | npx -y @vkhanhqui/figma-mcp-go@0.1.3
```

Trong Claude, `/mcp` sẽ liệt kê `figma-mcp-go` cùng danh sách tool nếu nạp thành công.

## Ghi chú

- Máy này đang có bản global cũ `@vkhanhqui/figma-mcp-go@0.0.2`. Config ở đây pin `0.1.3`
  nên `npx` sẽ tải đúng bản mới, không đụng tới bản global đó.
- Server tự bầu leader trên cổng `1994`, nên chạy nhiều Claude/AI tool cùng lúc vẫn an toàn:
  instance đầu làm LEADER giữ cổng, các instance sau làm follower.

## Nguồn

Dự án gốc: <https://github.com/vkhanhqui/figma-mcp-go> (MIT)

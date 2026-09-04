---
name: iap-data-fill
description: "Điền dữ liệu gói IAP trong Unity — thêm product vào IAPProductCatalog.json và điền RewardList vào IAPData ScriptableObject cho hai file khớp nhau. Dùng skill này BẤT CỨ KHI NÀO người dùng nhắc tới việc thêm/sửa/cập nhật gói IAP, in-app purchase, product id, catalog IAP, IAPData, coin pack, starter pack, bundle, remove ads, hay reward của gói mua — kể cả khi họ chỉ đưa một bảng/CSV/sheet GDD liệt kê các gói bán mà không nói rõ tên file. Cũng dùng khi cần kiểm tra IAPData và IAPProductCatalog có lệch nhau, có gói nào RewardList rỗng, hay product id nào bị sai."
user-invocable: true
argument-hint: "[đường dẫn CSV/GDD hoặc bảng mô tả các gói IAP]"
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
---

# IAP Data Fill

Hai file phải luôn khớp nhau, vì người chơi trả tiền thật:

- **`IAPProductCatalog.json`** khai product id + type để Unity IAP hỏi store. Thiếu id → store trả null → nút mua bấm im re, không log lỗi.
- **Asset `IAPData`** (`.asset` YAML) khai mua xong trả những gì. `RewardList` rỗng → thu tiền mà không trả hàng.

## Dùng script, đừng sửa YAML tay

Thụt lề Unity dễ sai và hỏng asset thì mất cả file. Script bundled đã xử lý những chỗ hay vấp:

```bash
python <skill-dir>/scripts/apply_iap_data.py --spec <spec>.json --dry-run   # xem trước
python <skill-dir>/scripts/apply_iap_data.py --spec <spec>.json             # ghi thật
python <skill-dir>/scripts/apply_iap_data.py --verify-only                  # chỉ soát
```

Spec viết ra scratchpad. **Đặt tên file riêng** (`iap-spec-<tên gói>-<timestamp>.json`) — nhiều phiên chạy song song mà dùng chung `spec.json` thì đè lên nhau giữa dry-run và lần ghi thật.

```json
{
  "asset":   "Assets/_Project/Data/IAPData.asset",
  "catalog": "Assets/Resources/IAPProductCatalog.json",
  "products": [
    {"id": "good.pack.bronze", "type": "Consumable", "rewards": [
      {"id": 100, "amount": 2, "name": "Magnet"},
      {"id": 20,  "amount": 1, "name": "Unlimited Hearts (giờ)"},
      {"id": 10,  "amount": 3000, "name": "coins"}]}
  ]
}
```

`name` chỉ để người đọc đối chiếu. `status` bỏ trống → giữ giá trị cũ (gói mới → 0). Gói có sẵn thì cập nhật tại chỗ, chưa có thì thêm vào cả hai file; gói ngoài spec giữ nguyên xi. Script tự trim id dính khoảng trắng, clone shape entry catalog có sẵn thay vì đoán schema, giữ line ending/BOM, và verify ngay sau khi ghi.

**Script dừng và không ghi** khi số dòng `- Key:` không khớp số entry parse được, hoặc kết quả dựng ra hụt gói. Đó là chốt chống mất dữ liệu, không phải lỗi vặt — asset đang có format lạ, báo người dùng chứ đừng lách bằng cách sửa tay.

## Trước khi ghi

Đọc `RewardType` (cả partial của project) để lấy id, và đọc `ApplyReward` trong `EconomyManager` để biết **1 đơn vị của mỗi loại nghĩa là gì** — số trong GDD là số người chơi thấy, chưa chắc là số ghi vào asset. Ví dụ thời gian bất tử thường tính theo giờ hoặc phút rồi nhân hằng số lúc cấp; ghi nhầm ra giây là sai gấp nghìn lần.

Map tên designer ("Magnet", "Double Star", "Xu") sang id bằng cách **đối chiếu ngược từ một gói đã điền sẵn** — chắc hơn suy theo tên nhiều, vì tên hiển thị và tên hằng số hay lệch nhau ("Magnet" có thể là `Hammer`). Không có gói mẫu nào để đối chiếu, hoặc còn tên không map được thì hỏi, đừng chọn id nghe na ná: `SmartEnum` so sánh theo int nên gán nhầm vẫn build sạch, chỉ sai lúc chạy.

In bảng mapping và bảng gói cho người dùng soát trước khi ghi. Đây là chốt kiểm rẻ nhất trong cả quy trình.

## Vài chỗ dễ mất cảnh giác

- **Id `RewardType` khác id `BoosterType`** dù tên hằng giống hệt. Lấy nhầm bảng vẫn compile sạch.
- **Thưởng có trần.** Loại như tim bị clamp ở max, phần vượt mất trắng — bán loại đó thì cảnh báo người dùng.
- **Giá không nằm ở hai file này** (lấy từ store lúc runtime). Cột giá trong GDD chỉ để đối chiếu; giá lẻ kiểu `149.001 / 149.002` thường là placeholder do kéo fill trong sheet.
- Nhắc người dùng cho Unity reimport asset thì thay đổi mới hiện trong Inspector.

## Skill này không làm

Không đặt giá bán, không tạo prefab/UI, không tự nghĩ ra product id hay quyền lợi mà input không nói, không thêm giá trị mới vào `RewardType` (đó là sửa code — để người dùng quyết), không sửa code trong thư mục base dùng chung của project.

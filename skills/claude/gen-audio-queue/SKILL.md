---
name: gen-audio-queue
description: Chuyển hàng loạt file .txt thành audio bằng VieNeu-TTS theo cơ chế hàng chờ tự phục hồi - quét thư mục, tìm file .txt chưa có .wav trùng tên, tạo audio cho file đó, rồi quét lại từ đầu cho đến khi không còn file nào thiếu. Kích hoạt khi nghe "gen audio", "tạo audio", "hàng chờ audio", "chuyển txt thành audio", "đọc truyện thành file", "vieneu", "vieneutts", "TTS", "gen giọng đọc", "tiếp tục gen", "đến đâu rồi" (khi đang có job chạy). Dùng cả khi người dùng chỉ đưa một thư mục và nói "gen đi".
---

# Hàng chờ gen audio (VieNeu-TTS)

## 0. Nguyên tắc tối cao

**KHÔNG đọc, KHÔNG trích, KHÔNG tóm tắt nội dung file `.txt`.** Script đọc file để đưa thẳng vào TTS; bạn chỉ làm việc với tên file, số ký tự, tiến độ. Không bao giờ in nội dung truyện ra hội thoại — kể cả một đoạn ngắn để "kiểm tra".

Đây là job chạy hàng giờ trên máy người dùng. **Luôn báo quy mô trước khi khởi động** (mục 3). Khởi động một job 10 tiếng mà người dùng không biết trước là lỗi nghiêm trọng.

## 1. Thuật toán (hợp đồng, không được đổi)

1. Quét thư mục theo thứ tự tên (`str(path).lower()`), có thể đệ quy
2. Tìm file `.txt` **đầu tiên** chưa có `.wav` trùng tên
3. Tạo audio cho đúng file đó
4. **Quay lại bước 1, quét lại từ đầu**
5. Một lượt quét không còn file thiếu → dừng

Quét lại từ đầu (chứ không duyệt danh sách một lần) là chủ ý: job tự nhặt file `.txt` mới người dùng thêm vào giữa chừng, và dừng/chạy lại không mất gì.

## 2. Tham số

Chỉ **hai** thứ bắt buộc phải chốt với người dùng:

| Bắt buộc | |
|---|---|
| Thư mục chứa `.txt` | Nếu chứa thư mục con → hỏi/mặc định `--recursive` |
| Giọng đọc | Xem danh sách mục 8, không cần nạp model để tra |

Còn lại có mặc định tốt, **đừng hỏi**: đệ quy (có) · lưu `.wav` cạnh `.txt` · `fp32` · 700 ký tự/đoạn · 6 luồng · nghỉ 0,35 giây giữa đoạn.

Trước khi hỏi, đọc `state.json` cạnh SKILL.md (nếu có) để lấy thư mục + giọng lần trước; người dùng gõ trống ("gen audio") thì đề xuất chạy tiếp đúng chỗ cũ. Chạy xong ghi lại `state.json`.

## 3. Tiền kiểm — BẮT BUỘC trước khi chạy

Đếm và in ra **trước** khi khởi động bất cứ thứ gì:

```
Tổng .txt / đã có audio / còn thiếu
Tổng ký tự còn thiếu
Ước tính giờ audio + giờ xử lý
```

Ước tính bằng hằng số hiệu chỉnh mục 7. **Vượt 1 giờ thì chờ người dùng xác nhận** rồi mới chạy.

Đoạn tính nhanh (không nạp model):

```python
import sys; sys.path.insert(0, r"<skill>/scripts")
from pathlib import Path
from queue_runner import all_texts, wav_for, read_text
src = Path(r"<thư mục>")
txts = all_texts(src, True)
miss = [t for t in txts if not wav_for(t, src, src).exists()]
chars = sum(len(read_text(t)) for t in miss)
h = chars * (1433/33418) / 3600          # giờ audio
print(len(txts), len(miss), f"{chars:,}", f"{h:.1f}h audio", f"{h*0.46:.1f}h xử lý")
```

## 4. Cách chạy — một tiến trình MỖI FILE

Không bao giờ chạy một tiến trình xuyên suốt nhiều file. Luôn dùng `--once` trong vòng lặp ngoài, chạy nền:

```bash
cd /c/Users/ming/Apps/VieNeu-TTS
while true; do
  PYTHONIOENCODING=utf-8 ./.venv/Scripts/python.exe queue_runner.py \
      "<thư mục>" --recursive --once --voice "<giọng>" --threads 6 >> "$LOG" 2>&1
  rc=$?; [ $rc -ne 0 ] && { echo "=== kết thúc, mã $rc ===" >> "$LOG"; break; }
done
```

`--once` thoát mã **10** khi không còn gì thiếu (kết thúc bình thường), mã **1** khi lỗi. Nạp lại model tốn ~30 giây/file — chấp nhận được để đổi lấy việc RAM được thu hồi sạch sau từng file.

## 5. Luật vận hành đã trả giá

Mỗi dòng dưới đây tương ứng một lần hỏng thật. Vi phạm là hỏng lại.

| Luật | Nếu vi phạm |
|---|---|
| Một tiến trình mỗi file (`--once`) | Chạy liền 13 file trong 1 tiến trình → hệ thống kill vì hết RAM |
| Ghi luồng từng đoạn vào `.wav.part` rồi `replace()` sang `.wav` | Gom cả file trong RAM tốn ~550 MB/file; và dừng giữa chừng để lại `.wav` cụt bị lượt quét sau tưởng là đã xong |
| `sf.SoundFile(..., format="WAV", subtype="PCM_16")` | Đuôi `.part` khiến soundfile không đoán được định dạng → `TypeError` |
| `PYTHONIOENCODING=utf-8` | Console cp1252 crash `UnicodeEncodeError` khi in tên giọng tiếng Việt |
| Đọc txt thử `utf-8-sig` → `utf-16` → `cp1258` | File có BOM sẽ lỗi decode |
| Kiểm tra port 7860 trước khi bật web UI | Web app đang chạy → `OSError: Cannot find empty port` |

## 6. Đặc tả máy (Ryzen 5 5500U)

**Không có GPU NVIDIA** — Radeon tích hợp không dùng được. Mọi thứ chạy ONNX trên CPU, nên `infer_batch()` và mọi tuỳ chọn "Batch Size" trong web UI đều **vô tác dụng**; chúng chỉ tăng tốc trên CUDA.

6 nhân / 12 luồng, 15,4 GB RAM. **RAM là trần, không phải CPU** — đó là lý do luật "một tiến trình mỗi file" tồn tại.

Chạy song song nhiều tiến trình có tăng thông lượng (đo được: 1×6 luồng → RTF 0,807; 4×2 luồng → 0,539; 4×2 luồng int8 → 0,427) nhưng nhân đôi RAM. Chỉ dùng khi đã đo lại bộ nhớ trống.

## 7. Hằng số hiệu chỉnh

Đo trên file thật của người dùng, dùng để ước tính — đừng đoán lại:

- **33.418 ký tự → 1.433 giây audio** (0,0429 giây/ký tự)
- **RTF 0,46** ở cấu hình chuẩn (fp32, 700 ký tự/đoạn, 6 luồng) → 1 file ~33 KB mất ~15 phút
- Đoạn dài hiệu quả hơn đoạn ngắn: 350 ký tự/đoạn cho RTF 0,807, còn 700 cho 0,46
- `int8` nhanh ~1,9× nhưng CPU này **không có VNNI** → phải cho người dùng nghe thử trước, không tự ý bật

## 8. Giọng preset (23 giọng)

**Đọc truyện:** Mỹ Duyên (Nữ·Nam) · Quỳnh Anh (Nữ·Bắc) · Đức Trí (Nam·Nam) · Kim Thanh (Nữ·Nam)
**Kể chuyện:** Thái Sơn (Nam·Nam) · Thanh Bình (Nam·Bắc) · Ngọc Linh (Nữ·Bắc) · Thục Đoan (Nữ·Nam) · Anh Khôi (Nam·Bắc)
**Tự nhiên:** Ngọc Huyền (Nữ·Bắc) · Adam (Nam·Nam) · Phạm Tuyên (Nam·Bắc) · Xuân Vĩnh (Nam·Bắc) · Trúc Ly (Nữ·Bắc) · Đoan Trang (Nữ·Bắc) · Mạnh Dũng (Nam·Bắc) · Minh Quân (Nam·Bắc) · Quang Sơn (Nam·Trung) · Ngọc Trân (Nữ·Trung)
**Tin tức:** Minh Đức (Nam·Bắc) · Mai Anh (Nữ·Bắc) · Minh Triết (Nam·Nam) · Thùy Dung (Nữ·Nam)

Nếu thư mục đã có `.wav` tạo bằng giọng khác → **nhắc người dùng trước khi trộn giọng**.

## 9. Mẫu báo cáo tiến độ

Khi người dùng hỏi "đến đâu rồi", đọc log + đếm `.wav` trên đĩa, trả lời đúng khuôn:

- **Đã xong X/Y file** (đếm `.wav` thật trên đĩa, không tin mỗi log)
- **Đang làm:** tên file · đoạn `n/m` · đã chạy bao lâu · còn ước tính bao lâu cho file này
- **Còn lại:** số file · số ký tự · giờ ước tính
- File `.wav.part` đang phình = bằng chứng nó đang chạy thật
- Có `Traceback` trong log thì báo ngay, đừng giấu

Tính lại phần còn thiếu bằng đoạn code mục 3 — số file `.txt` có thể đã tăng.

## 10. Dừng và chạy tiếp

**"Dừng sau file hiện tại"**: chờ dòng `✅` của file đó xuất hiện trong log rồi mới tắt vòng lặp. Không kill giữa chừng.

**"Dừng ngay"**: tắt luôn; xoá `.wav.part` còn sót (file `.part` không bị tính là đã xong nên không cần xoá gấp, nhưng dọn cho sạch).

**Chạy tiếp**: gọi lại y hệt lệnh mục 4. Phần đã xong tự được bỏ qua — không cần cờ gì thêm.

## 11. Script

`scripts/queue_runner.py` cạnh file này (bản gốc ở `C:\Users\ming\Apps\VieNeu-TTS\queue_runner.py`). Đã chạy thật, đừng viết lại logic. Xem `--help` cho toàn bộ cờ.

Môi trường: `C:\Users\ming\Apps\VieNeu-TTS\.venv\Scripts\python.exe` (cài editable, có sẵn `vieneu` + `soundfile`).

#!/usr/bin/env python3
"""
check_ai_patterns.py — Phát hiện "mùi AI" trong văn bản truyện tiếng Việt.

Học từ check-ai-patterns.js của oh-story-claudecode: dùng LINT bằng luật xác định
để bắt các câu văn máy móc mà mắt thường dễ bỏ sót, đặc biệt là mẫu câu "phủ định
rồi khẳng định" (先否定再肯定) — thứ oh-story liệt vào cấm tuyệt đối.

Hai mức:
  - BLOCK (chặn): mẫu câu xác định là "mùi AI", nên sửa trước khi giao.
  - WARN (nhắc): dấu hiệu cần người đọc tự phán đoán theo cảm giác đọc.

Cách dùng:
    python3 check_ai_patterns.py <file-chương> [file-chương-2 ...]
    python3 check_ai_patterns.py --dir <thư-mục>        # quét mọi chương
    python3 check_ai_patterns.py <file> --strict         # exit 1 nếu có lỗi BLOCK

Script CỐ Ý thận trọng để giảm báo nhầm; nó chỉ mẹo cho người viết xem lại,
không tự động sửa.
"""

import argparse
import glob
import os
import re
import sys


# ---------- Nhóm 1: BLOCK — mẫu câu "phủ định rồi khẳng định" ----------
# Đây là mẫu câu AI kinh điển: "không phải X, mà là Y" / "đó không chỉ là A,
# đó là B". Lạm dụng khiến văn rất "máy". oh-story cấm tuyệt đối.
BLOCK_PATTERNS = [
    (r"không phải (là )?[^.,;!?]{1,40}?,?\s*mà (là|chính là|còn là)",
     "Câu 'phủ định rồi khẳng định' (không phải X mà là Y) — mẫu mùi AI điển hình"),
    (r"đó không (chỉ )?là [^.,;!?]{1,40}?[.,;]\s*đó là",
     "Câu 'đó không phải là... đó là...' — mẫu mùi AI"),
    (r"không (phải )?vì [^.,;!?]{1,40}?,?\s*mà vì",
     "Câu 'không vì X mà vì Y' lặp cấu trúc — dễ thành mùi AI nếu lạm dụng"),
]

# ---------- Nhóm 2: WARN — sáo ngữ/cụm mòn hay gặp trong văn AI tiếng Việt ----------
CLICHE_WORDS = [
    "không thể tin nổi", "không thể tin được",
    "trái tim như thắt lại", "tim như thắt lại", "tim đập loạn nhịp",
    "cả thế giới như sụp đổ", "cả thế giới như ngừng lại",
    "một cảm giác khó tả", "không thể diễn tả bằng lời",
    "thời gian như ngừng trôi", "thời gian như ngưng đọng",
    "khóe môi khẽ nhếch", "khóe miệng khẽ nhếch",
    "một tia sáng lóe lên trong",
    "bất giác", "khẽ mỉm cười", "chẳng nói chẳng rằng",
]

# ---------- Nhóm 3: WARN — lỗi dịch máy tiếng Trung sang (không thuộc "chất TQ") ----------
# Đây là LỖI diễn đạt, khác với "chất TQ" đáng giữ (nàng/hắn/kiếp trước...).
CONVERT_ERRORS = [
    ("lãnh khốc", "→ 'lạnh lùng' / 'lạnh như băng'"),
    ("quy lai", "→ 'trở về' / 'quay lại'"),
    ("nhất định phải chết", "kiểm tra ngữ pháp câu"),
    ("bên trong lóe lên", "→ 'trong ... lóe lên' (sai trật tự từ)"),
    ("đem nàng", "→ 'đem/khiến nàng...' kiểm tra: có thể là dịch sống 把"),
    ("đối với nàng mà nói", "→ 'với nàng' (rườm rà kiểu dịch)"),
    ("tại nơi này", "→ 'ở đây' / 'nơi đây'"),
]

# ---------- Nhóm 4: WARN — mật độ tu từ so sánh quá dày (metaphor density) ----------
# Học từ oh-story 'metaphor-density-tic': đếm "như/tựa/tựa như/như thể/giống như"
SIMILE_MARKERS = ["như thể", "tựa như", "tựa hồ", "giống như", "chẳng khác nào", " như "]


def read_text(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def check_file(path):
    text = read_text(path)
    low = text.lower()
    issues = []

    # BLOCK: mẫu câu phủ định-khẳng định
    for pat, desc in BLOCK_PATTERNS:
        for m in re.finditer(pat, low):
            start = max(0, m.start() - 15)
            end = min(len(text), m.end() + 15)
            issues.append(("BLOCK", desc, text[start:end].replace("\n", " ").strip()))

    # WARN: sáo ngữ
    for w in CLICHE_WORDS:
        c = low.count(w)
        if c >= 1:
            issues.append(("WARN", f"Sáo ngữ mòn: '{w}' (xuất hiện {c} lần)", ""))

    # WARN: lỗi convert
    for w, hint in CONVERT_ERRORS:
        if w in low:
            issues.append(("WARN", f"Nghi lỗi dịch máy: '{w}' {hint}", ""))

    # WARN: mật độ so sánh
    simile_count = sum(low.count(s) for s in SIMILE_MARKERS)
    # đếm số câu (thô, theo dấu kết câu)
    sentences = max(1, len(re.findall(r"[.!?…]", text)))
    ratio = simile_count / sentences
    if ratio > 0.25:
        issues.append(("WARN",
            f"Mật độ so sánh cao: {simile_count} cụm 'như/tựa...' trên ~{sentences} câu "
            f"(tỷ lệ {ratio:.0%}) — dễ gây cảm giác 'văn AI' lê thê", ""))

    return issues


def main():
    ap = argparse.ArgumentParser(description="Phát hiện mùi AI trong văn truyện tiếng Việt.")
    ap.add_argument("files", nargs="*", help="Các file chương cần kiểm tra")
    ap.add_argument("--dir", help="Quét mọi file chương trong thư mục")
    ap.add_argument("--strict", action="store_true", help="Exit 1 nếu có lỗi BLOCK")
    args = ap.parse_args()

    files = list(args.files)
    if args.dir:
        for p in ["chuong-*.txt", "chuong-*.md", "chuong*.txt", "chuong*.md"]:
            files += glob.glob(os.path.join(args.dir, p))
    files = sorted(set(f for f in files if os.path.exists(f)))

    if not files:
        print("Không có file nào để kiểm tra.")
        sys.exit(0)

    total_block = 0
    for path in files:
        issues = check_file(path)
        if not issues:
            print(f"✅ {os.path.basename(path)}: sạch mùi AI theo các luật hiện có.")
            continue
        print(f"\n🔎 {os.path.basename(path)}: {len(issues)} điểm cần xem lại")
        for level, desc, ctx in issues:
            icon = "🔴" if level == "BLOCK" else "🟡"
            if level == "BLOCK":
                total_block += 1
            print(f"  {icon} [{level}] {desc}")
            if ctx:
                print(f"       ...{ctx}...")

    if args.strict and total_block > 0:
        print(f"\n❌ Có {total_block} lỗi BLOCK — cần sửa trước khi giao chương.")
        sys.exit(1)


if __name__ == "__main__":
    main()

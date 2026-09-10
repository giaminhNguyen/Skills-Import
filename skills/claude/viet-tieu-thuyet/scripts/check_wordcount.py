#!/usr/bin/env python3
"""
Kiểm tra số từ của một file chương tiếng Việt so với khoảng mục tiêu.

Cách dùng:
    python3 check_wordcount.py duong/dan/chuong.md --min 2000 --max 3000

Đếm từ theo khoảng trắng (đơn giản, đủ dùng cho tiếng Việt vì từ ghép
thường không tách rời bằng ký tự đặc biệt trong văn bản thông thường).
"""
import argparse
import sys


def count_words(path: str) -> int:
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()
    return len(text.split())


def main():
    parser = argparse.ArgumentParser(description="Kiểm tra số từ của một chương truyện.")
    parser.add_argument("file", help="Đường dẫn file chương (txt/md)")
    parser.add_argument("--min", type=int, default=2000, help="Số từ tối thiểu mong muốn")
    parser.add_argument("--max", type=int, default=3500, help="Số từ tối đa mong muốn")
    args = parser.parse_args()

    try:
        n = count_words(args.file)
    except FileNotFoundError:
        print(f"Không tìm thấy file: {args.file}")
        sys.exit(1)

    print(f"Số từ: {n}")
    if n < args.min:
        print(f"⚠️  Ngắn hơn mục tiêu ({args.min}–{args.max} từ). Thiếu khoảng {args.min - n} từ.")
        sys.exit(2)
    elif n > args.max:
        print(f"⚠️  Dài hơn mục tiêu ({args.min}–{args.max} từ). Thừa khoảng {n - args.max} từ.")
        sys.exit(2)
    else:
        print(f"✅ Đạt mục tiêu ({args.min}–{args.max} từ).")


if __name__ == "__main__":
    main()

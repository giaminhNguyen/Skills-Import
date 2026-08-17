#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ghi bản dịch vào I2Languages.asset.

Dùng:
  python i2_import.py <asset.asset> <translations.json> --mode missing
  python i2_import.py <asset.asset> <translations.json> --mode override
  python i2_import.py <asset.asset> <translations.json> --dry-run

File translations.json — map term -> {language_code: value}:
{
  "remove ads": { "vi": "Xóa quảng cáo", "ja": "広告を削除", ... },
  "Win Streak": { "vi": "Chuỗi thắng", ... }
}
(Chấp nhận cả dạng bọc ngoài {"terms": { ... }})

Mặc định cột English được set = chính tên term (rule của dự án). Tắt bằng
--no-english-from-term.

--mode missing  : chỉ ghi vào ô đang trống, không đụng bản dịch đã có
--mode override : ghi đè mọi ô có trong file JSON
"""

import argparse
import json
import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from i2_asset import load  # noqa: E402

# console Windows mặc định cp1252 -> ép UTF-8 để in được tiếng Việt/CJK
for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("asset", help="đường dẫn I2Languages.asset")
    ap.add_argument("json", help="file JSON bản dịch")
    ap.add_argument("--mode", choices=["missing", "override"], default="missing")
    ap.add_argument("--dry-run", action="store_true", help="chỉ in ra, không ghi file")
    ap.add_argument("--no-backup", action="store_true", help="không tạo file .bak")
    ap.add_argument("--backup-dir", help="thư mục chứa file .bak "
                                         "(mặc định: cùng chỗ file JSON, để không rác trong Assets/)")
    ap.add_argument("--english-code", default="en")
    ap.add_argument("--no-english-from-term", action="store_true",
                    help="không tự set cột English = tên term")
    args = ap.parse_args()

    asset = load(args.asset)
    codes = set(asset.codes)
    tmap = asset.term_map()

    with open(args.json, "r", encoding="utf-8-sig") as f:
        data = json.load(f)
    if isinstance(data, dict) and "terms" in data and isinstance(data["terms"], dict):
        data = data["terms"]
    if not isinstance(data, dict):
        sys.exit("JSON phải là object dạng {term: {code: value}}")

    written = 0
    skipped_existing = 0
    unknown_terms = []
    unknown_codes = set()
    empty_values = []
    en_written = 0

    for term_name, cells in data.items():
        term = tmap.get(term_name)
        if term is None:
            unknown_terms.append(term_name)
            continue
        if not isinstance(cells, dict):
            sys.exit("Giá trị của term '%s' phải là object {code: value}" % term_name)

        # cột English = tên term
        if not args.no_english_from_term and args.english_code in codes:
            idx = asset.index_of(args.english_code)
            cur = term.values[idx] if idx < len(term.values) else ""
            if args.mode == "override" or cur.strip() == "":
                if cur != term.name:
                    asset.set_value(term, args.english_code, term.name)
                    en_written += 1

        for code, value in cells.items():
            if code not in codes:
                unknown_codes.add(code)
                continue
            if code == args.english_code and not args.no_english_from_term:
                continue
            if value is None:
                value = ""
            if not isinstance(value, str):
                value = str(value)
            if value.strip() == "":
                empty_values.append("%s / %s" % (term_name, code))
                continue
            idx = asset.index_of(code)
            cur = term.values[idx] if idx < len(term.values) else ""
            if args.mode == "missing" and cur.strip() != "":
                skipped_existing += 1
                continue
            if cur == value:
                continue
            asset.set_value(term, code, value)
            written += 1

    print("Mode         : %s" % args.mode)
    print("Ô đã ghi     : %d (+ %d ô English = term)" % (written, en_written))
    if skipped_existing:
        print("Bỏ qua (đã có): %d  (mode missing)" % skipped_existing)
    if unknown_terms:
        print("!! Term không có trong asset (%d): %s" % (len(unknown_terms), ", ".join(unknown_terms[:10])))
    if unknown_codes:
        print("!! Code ngôn ngữ không có trong asset: %s" % ", ".join(sorted(unknown_codes)))
    if empty_values:
        print("!! Giá trị rỗng, đã bỏ qua (%d): %s" % (len(empty_values), ", ".join(empty_values[:10])))

    if args.dry_run:
        print("(dry-run: chưa ghi file)")
        return

    if written == 0 and en_written == 0:
        print("Không có gì thay đổi, không ghi file.")
        return

    if not args.no_backup:
        # để .bak ngoài Assets/ cho Unity khỏi import rác
        bdir = args.backup_dir or os.path.dirname(os.path.abspath(args.json))
        if not os.path.isdir(bdir):
            os.makedirs(bdir)
        bak = os.path.join(bdir, os.path.basename(args.asset) + ".bak")
        shutil.copyfile(args.asset, bak)
        print("Backup       : %s" % bak)

    asset.save()
    print("Đã ghi asset : %s" % os.path.abspath(args.asset))

    # kiểm tra lại file vừa ghi có parse được không
    check = load(args.asset)
    if len(check.terms) != len(asset.terms) or len(check.languages) != len(asset.languages):
        sys.exit("!! File sau khi ghi parse ra khác trước đó — kiểm tra lại .bak")
    bad = [t.name for t in check.terms if len(t.values) != len(check.languages)]
    if bad:
        sys.exit("!! Term sai số lượng ô ngôn ngữ: %s" % ", ".join(bad[:10]))
    print("Verify OK    : %d term x %d ngôn ngữ" % (len(check.terms), len(check.languages)))


if __name__ == "__main__":
    main()

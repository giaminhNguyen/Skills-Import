#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Xuất term + trạng thái dịch của I2Languages.asset ra JSON để agent dịch.

Dùng:
  python i2_export.py <asset.asset> --mode missing  -o work.json
  python i2_export.py <asset.asset> --mode override -o work.json
  python i2_export.py <asset.asset> --stats          # chỉ in thống kê

--mode missing  : chỉ liệt kê term còn ô trống (kèm danh sách code ngôn ngữ thiếu)
--mode override : liệt kê toàn bộ term x toàn bộ ngôn ngữ (dịch lại từ đầu)

Cột English luôn = chính tên term nên script tự đánh dấu, agent KHÔNG cần dịch.
"""

import argparse
import json
import os
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
    ap.add_argument("--mode", choices=["missing", "override"], default="missing")
    ap.add_argument("-o", "--out", help="file JSON xuất ra")
    ap.add_argument("--languages", help="lọc theo code, vd: vi,ja,ko")
    ap.add_argument("--terms", help="lọc theo tên term, phân cách bằng ';'")
    ap.add_argument("--limit", type=int, default=0, help="chỉ lấy N term đầu (chia batch)")
    ap.add_argument("--offset", type=int, default=0, help="bỏ qua N term đầu (chia batch)")
    ap.add_argument("--stats", action="store_true", help="chỉ in thống kê, không xuất JSON")
    ap.add_argument("--english-code", default="en", help="code của ngôn ngữ gốc (mặc định en)")
    args = ap.parse_args()

    asset = load(args.asset)
    codes = asset.codes
    en_idx = asset.index_of(args.english_code)

    target_codes = [c for c in codes if c != args.english_code]
    if args.languages:
        want = [c.strip() for c in args.languages.split(",") if c.strip()]
        unknown = [c for c in want if c not in codes]
        if unknown:
            sys.exit("Ngôn ngữ không có trong asset: %s\nCó sẵn: %s" % (", ".join(unknown), ", ".join(codes)))
        target_codes = [c for c in want if c != args.english_code]

    only_terms = None
    if args.terms:
        only_terms = set(t.strip() for t in args.terms.split(";") if t.strip())

    rows = []
    total_cells = 0
    missing_cells = 0
    for term in asset.terms:
        if only_terms is not None and term.name not in only_terms:
            continue
        vals = list(term.values) + [""] * (len(codes) - len(term.values))
        missing = []
        for code in target_codes:
            i = asset.index_of(code)
            total_cells += 1
            if vals[i].strip() == "":
                missing_cells += 1
                missing.append(code)
        needed = target_codes if args.mode == "override" else missing
        if not needed:
            continue
        rows.append({
            "term": term.name,
            "english": term.name,
            "need": needed,
            "current": {c: vals[asset.index_of(c)] for c in target_codes
                        if vals[asset.index_of(c)].strip() != ""},
            "en_filled": en_idx >= 0 and vals[en_idx].strip() != "",
        })

    if args.offset:
        rows = rows[args.offset:]
    if args.limit:
        rows = rows[:args.limit]

    summary = {
        "asset": os.path.abspath(args.asset),
        "mode": args.mode,
        "languages": [{"name": n, "code": c} for n, c in asset.languages],
        "english_code": args.english_code,
        "target_codes": target_codes,
        "term_total": len(asset.terms),
        "cells_total": total_cells,
        "cells_missing": missing_cells,
        "terms_in_batch": len(rows),
    }

    print("Asset       : %s" % summary["asset"])
    print("Ngôn ngữ    : %d (%s)" % (len(asset.languages), ", ".join(codes)))
    print("Term        : %d" % len(asset.terms))
    print("Ô cần dịch  : %d, đang trống: %d" % (total_cells, missing_cells))
    print("Mode        : %s -> %d term trong batch này" % (args.mode, len(rows)))

    if args.stats:
        return

    payload = dict(summary)
    payload["terms"] = rows
    out = args.out or "i2_work.json"
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    print("Đã ghi      : %s" % os.path.abspath(out))


if __name__ == "__main__":
    main()

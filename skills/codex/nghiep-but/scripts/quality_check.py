#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
quality_check.py — kiem tra chat luong ban thao truyen (story.md).

PHAM VI: chi kiem tra VAN BAN TRUYEN.
KHONG kiem tra bat cu thu gi lien quan TTS/audio
(khong check chunk, khong check normalize so, khong dung cho file tts_*.md).

Cach dung:
    python3 quality_check.py path/to/story.md
    python3 quality_check.py path/to/story.md --min 5000 --max 12000

Exit code:
    0 = PASS (khong co loi nghiem trong)
    1 = FAIL (co it nhat 1 loi FAIL)
"""

import sys
import re
import argparse

# --- Tu khoa "AI taste" can han che (dau da bo, so khop khong dau) ---
AI_KEYWORDS = [
    "khong khoi",
    "bong nhien nhan ra",
    "tu do ve sau",
    "cam giac am ap lan toa",
    "trong long nhu",         # thuong di kem so sanh sao rong
    "nhu song than",
    "nhu bi bop nghet",
    "khong the kiem che",
    "trao dang",
]

# --- Cum tu chuyen canh khuon mau (nen tranh) ---
TEMPLATE_TRANSITIONS = [
    "thoi gian troi qua",
    "thoi gian thoi thoat",
    "ngay thang troi qua",
    "sau su viec hom do moi chuyen dan",
]

# --- Dau hieu jump-cut theo moc thoi gian (nen co) ---
TIME_MARKERS = [
    r"\b\d{1,2}\s*:\s*\d{2}\b",           # 10:00, 2:30
    r"\b\d{1,2}\s*(gio|g)\b",             # 7 gio, 8g
    r"\bngay (hom sau|thu (hai|ba|tu|nam|sau|bay))\b",
    r"\b(sang|trua|chieu|toi) (hom sau|thu)\b",
    r"\b\d+\s*(ngay|thang|tuan|nam)\s*sau\b",  # ba ngay sau
    r"\bhom sau\b",
    r"\bsau do\b",
]


def strip_diacritics(s: str) -> str:
    """Bo dau tieng Viet de so khop tu khoa khong phu thuoc dau."""
    table = str.maketrans(
        "aàáảãạăằắẳẵặâầấẩẫậeèéẻẽẹêềếểễệiìíỉĩịoòóỏõọôồốổỗộơờớởỡợuùúủũụưừứửữựyỳýỷỹỵđ"
        "AÀÁẢÃẠĂẰẮẲẴẶÂẦẤẨẪẬEÈÉẺẼẸÊỀẾỂỄỆIÌÍỈĨỊOÒÓỎÕỌÔỒỐỔỖỘƠỜỚỞỠỢUÙÚỦŨỤƯỪỨỬỮỰYỲÝỶỸỴĐ",
        "a"*17 + "e"*11 + "i"*5 + "o"*17 + "u"*11 + "y"*5 + "d"
        + "A"*17 + "E"*11 + "I"*5 + "O"*17 + "U"*11 + "Y"*5 + "D",
    )
    return s.translate(table)


def count_words(text: str) -> int:
    return len(re.findall(r"\S+", text))


def split_sentences(text: str):
    # tach cau tho theo . ! ? ... — giu don gian
    parts = re.split(r"(?<=[.!?…])\s+", text.strip())
    return [p.strip() for p in parts if p.strip()]


def split_paragraphs(text: str):
    return [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]


def count_dialogue_ratio(text: str):
    """Uoc luong ti le doi thoai.
    Dem theo dong bat dau bang dau thoai ("..." hoac — hoac -) va tong ky tu."""
    lines = text.splitlines()
    dialogue_chars = 0
    total_chars = 0
    for ln in lines:
        s = ln.strip()
        if not s:
            continue
        total_chars += len(s)
        if s.startswith(("\u201c", '"', "—", "-", "–")) or re.match(r'^[\u201c"].', s):
            dialogue_chars += len(s)
    if total_chars == 0:
        return 0.0
    return dialogue_chars / total_chars


def main():
    ap = argparse.ArgumentParser(description="Kiem tra chat luong ban thao truyen (text only).")
    ap.add_argument("file", help="Duong dan story.md")
    ap.add_argument("--min", type=int, default=5000, help="Word count toi thieu")
    ap.add_argument("--max", type=int, default=12000, help="Word count toi da")
    ap.add_argument("--para-max", type=int, default=150, help="So chu toi da moi doan")
    ap.add_argument("--cold-max", type=int, default=15, help="So chu toi da cho cau ket")
    args = ap.parse_args()

    try:
        with open(args.file, encoding="utf-8") as f:
            text = f.read()
    except FileNotFoundError:
        print(f"[FAIL] Khong tim thay file: {args.file}")
        sys.exit(1)

    flat = strip_diacritics(text).lower()
    fails = []
    warns = []
    infos = []

    # 1. Word count -----------------------------------------------------
    wc = count_words(text)
    if wc < args.min:
        fails.append(f"Word count {wc} < toi thieu {args.min}")
    elif wc > args.max:
        fails.append(f"Word count {wc} > toi da {args.max}")
    else:
        infos.append(f"Word count: {wc} (OK, trong {args.min}-{args.max})")

    # 2. Ti le doi thoai ------------------------------------------------
    ratio = count_dialogue_ratio(text)
    pct = round(ratio * 100, 1)
    if ratio < 0.35:
        warns.append(f"Ti le doi thoai {pct}% < 35% (nen 40-55%) — them canh doi dap")
    elif ratio > 0.60:
        warns.append(f"Ti le doi thoai {pct}% > 60% — them hanh dong/chi tiet vat ly")
    else:
        infos.append(f"Ti le doi thoai: ~{pct}%")

    # 3. Tu khoa AI -----------------------------------------------------
    ai_hits = []
    for kw in AI_KEYWORDS:
        n = flat.count(kw)
        if n > 0:
            ai_hits.append((kw, n))
    total_ai = sum(n for _, n in ai_hits)
    if total_ai > 3:
        detail = ", ".join(f"{k}x{n}" for k, n in ai_hits)
        fails.append(f"Tu khoa AI taste: {total_ai} lan (>3) -> {detail}")
    elif total_ai > 0:
        detail = ", ".join(f"{k}x{n}" for k, n in ai_hits)
        warns.append(f"Tu khoa AI taste: {total_ai} lan -> {detail}")
    else:
        infos.append("Tu khoa AI taste: 0")

    # 4. Cum chuyen canh khuon mau -------------------------------------
    tt_hits = [t for t in TEMPLATE_TRANSITIONS if t in flat]
    if tt_hits:
        warns.append(f"Chuyen canh khuon mau: {', '.join(tt_hits)} -> dung jump-cut moc thoi gian")

    # 5. Doan van qua dai ----------------------------------------------
    paras = split_paragraphs(text)
    long_paras = [i + 1 for i, p in enumerate(paras) if count_words(p) > args.para_max]
    if long_paras:
        warns.append(f"{len(long_paras)} doan > {args.para_max} chu (doan #{long_paras[:8]})")
    else:
        infos.append(f"Tat ca {len(paras)} doan <= {args.para_max} chu")

    # 6. Cau don ngan lien tiep > 5 ------------------------------------
    max_streak = 0
    for p in paras:
        streak = 0
        for s in split_sentences(p):
            if count_words(s) <= 7:
                streak += 1
                max_streak = max(max_streak, streak)
            else:
                streak = 0
    if max_streak > 5:
        warns.append(f"Chuoi cau ngan lien tiep dai nhat: {max_streak} (>5) — xen cau dai")
    else:
        infos.append(f"Chuoi cau ngan dai nhat: {max_streak}")

    # 7. Cau ket "lanh" -------------------------------------------------
    non_empty_lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    if non_empty_lines:
        last = non_empty_lines[-1]
        # bo dau thoai bao quanh neu co
        last_clean = last.strip("\u201c\u201d\"'—-–. ")
        cold_wc = count_words(last_clean)
        if cold_wc > args.cold_max:
            warns.append(f"Cau ket {cold_wc} chu (>{args.cold_max}) — nen ngan gon hon")
        else:
            infos.append(f"Cau ket: {cold_wc} chu -> \"{last_clean[:40]}...\"" if len(last_clean) > 40
                         else f"Cau ket: {cold_wc} chu -> \"{last_clean}\"")

    # 8. Moc thoi gian (jump-cut) --------------------------------------
    tm_count = 0
    for pat in TIME_MARKERS:
        tm_count += len(re.findall(pat, flat))
    if tm_count == 0:
        warns.append("Khong thay moc thoi gian jump-cut — nhip co the chua du don")
    else:
        infos.append(f"Moc thoi gian jump-cut: {tm_count}")

    # --- In bao cao ----------------------------------------------------
    print("=" * 55)
    print("  QUALITY CHECK — ban thao truyen (text only)")
    print("=" * 55)
    print(f"  File: {args.file}")
    print("-" * 55)
    for i in infos:
        print(f"  [ok]   {i}")
    for w in warns:
        print(f"  [WARN] {w}")
    for fl in fails:
        print(f"  [FAIL] {fl}")
    print("-" * 55)
    print(f"  Tong: {len(fails)} FAIL, {len(warns)} WARN")
    if fails:
        print("  KET QUA: FAIL")
        print("=" * 55)
        sys.exit(1)
    else:
        print("  KET QUA: PASS" + (" (co WARN nen xem lai)" if warns else ""))
        print("=" * 55)
        sys.exit(0)


if __name__ == "__main__":
    main()

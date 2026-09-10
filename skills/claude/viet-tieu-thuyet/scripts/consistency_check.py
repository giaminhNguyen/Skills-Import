#!/usr/bin/env python3
"""
consistency_check.py — Kiểm tra tính nhất quán của một bộ truyện.

KHÔNG chỉ nhắc nhở bằng lời. Script này thực sự đọc project-state.json
và quét toàn bộ file chương để phát hiện:

  1. FACT LEDGER: một dữ kiện cứng (số tiền, tuổi, ngày, tên) được khai
     trong ledger nhưng trong chương lại xuất hiện một GIÁ TRỊ KHÁC cho
     cùng thực thể đó (ví dụ ledger ghi "nợ 200 triệu", chương 10 viết
     "500 triệu").
  2. GUARD RAILS chứa mốc chương ("trước chương N", "sau chương N"): cảnh
     báo khi nội dung guard rail xuất hiện ở chương vi phạm mốc.
  3. VÉ SỐ (foreshadowing) đã tới hạn trả nhưng chưa thấy trả, hoặc bị bỏ
     quên khi truyện đã kết thúc.
  4. TÊN NHÂN VẬT xuất hiện trong chương nhưng không có trong hồ sơ
     00-nhan-vat.md (có thể là lỗi chính tả tên hoặc nhân vật "lạc").

Cách dùng:
    python3 consistency_check.py --dir DUONG_DAN_THU_MUC_DU_AN
    python3 consistency_check.py --dir . --json         # xuất báo cáo JSON
    python3 consistency_check.py --dir . --strict        # exit 1 nếu có lỗi nặng

Quy ước thư mục dự án:
    project-state.json        (bắt buộc)
    00-nhan-vat.md            (tùy chọn, để kiểm tra tên)
    chuong-*.txt / chuong-*.md / chapter-*.* / chuong01.* ...  (các chương)

Script cố ý dùng heuristic thận trọng: nó BÁO NGHI NGỜ để người viết
xem lại, không tự ý kết luận sai. Thà báo thừa còn hơn bỏ sót mâu thuẫn.
"""

import argparse
import glob
import json
import os
import re
import sys
import unicodedata



# Console Windows mac dinh cp1252 -> print tieng Viet se crash. Ep UTF-8.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
# ---------- Tiện ích ----------

def has_token(text_noacc: str, tok: str) -> bool:
    """Khớp trọn tiếng, không khớp chuỗi con: 'no' không được khớp vào 'nong'."""
    return re.search(r"(?<![a-z0-9])" + re.escape(tok) + r"(?![a-z0-9])", text_noacc) is not None


def strip_accents(s: str) -> str:
    """Bỏ dấu tiếng Việt để so khớp linh hoạt.

    NFD không tách được nét ngang của "đ" (nó là chữ cái riêng, không phải dấu),
    nên phải đổi tay — thiếu bước này thì "đồng" ra "đong" chứ không phải "dong".
    """
    nfkd = unicodedata.normalize("NFD", s)
    out = "".join(c for c in nfkd if unicodedata.category(c) != "Mn").lower()
    return out.replace("đ", "d")


VN_NUMBER_WORDS = {
    "không": 0, "một": 1, "hai": 2, "ba": 3, "bốn": 4, "tư": 4,
    "năm": 5, "sáu": 6, "bảy": 7, "tám": 8, "chín": 9, "mười": 10,
    "trăm": 100, "nghìn": 1000, "ngàn": 1000, "triệu": 1_000_000,
    "tỷ": 1_000_000_000, "tỉ": 1_000_000_000,
}

# Đơn vị tiền/số hay đi kèm, dùng để nhận diện "số cứng"
MONEY_UNITS = ["triệu", "tỷ", "tỉ", "nghìn", "ngàn", "đồng", "vnđ", "usd", "đô"]

# Đơn vị đứng chung cho mọi khoản tiền/thời gian nên KHÔNG được dùng làm từ khóa
# nhận diện thực thể: nếu lấy "đồng" làm khóa cho "Số tiền nợ" thì mọi con số có
# chữ "đồng" trong truyện (ổ bánh mì 25 nghìn đồng) đều bị báo là mâu thuẫn.
GENERIC_UNIT_TOKENS = {
    "trieu", "ty", "ti", "nghin", "ngan", "dong", "vnd", "usd", "do",
    "nam", "thang", "ngay", "gio", "phut", "lan", "cai", "chiec", "nguoi",
}


def extract_numbers_with_context(text: str, window: int = 25):
    """
    Trích các cụm số (kèm đơn vị nếu có) cùng ngữ cảnh xung quanh.
    Trả về list dict {value_raw, unit, context}.
    """
    results = []
    # Số Ả Rập kèm đơn vị: 200 triệu, 500tr, 17 tuổi, 20/8...
    for m in re.finditer(r"(\d[\d\.,]*)\s*([a-zA-Zàáảãạăắằẳẵặâấầẩẫậđèéẻẽẹêếềểễệìíỉĩịòóỏõọôốồổỗộơớờởỡợùúủũụưứừửữựỳýỷỹỵ]+)?", text):
        num = m.group(1)
        unit = (m.group(2) or "").strip()
        start = max(0, m.start() - window)
        end = min(len(text), m.end() + window)
        ctx = text[start:end].replace("\n", " ").strip()
        results.append({"value_raw": num, "unit": unit, "context": ctx})
    return results


def normalize_number_token(value_raw: str) -> str:
    """Chuẩn hóa '200.000' / '200,000' / '200' để so sánh."""
    return value_raw.replace(".", "").replace(",", "").strip()


def find_chapter_files(dir_path: str):
    patterns = [
        "chuong-*.txt", "chuong-*.md", "chuong*.txt", "chuong*.md",
        "chapter-*.txt", "chapter-*.md", "chapter*.txt", "chapter*.md",
        "chap-*.txt", "chap-*.md",
    ]
    files = set()
    for p in patterns:
        for f in glob.glob(os.path.join(dir_path, p)):
            files.add(f)
    # loại các file nền tảng
    excluded = {"00-nhan-vat", "01-the-gioi", "02-dan-y"}
    out = []
    for f in sorted(files):
        base = os.path.splitext(os.path.basename(f))[0].lower()
        if base in excluded:
            continue
        out.append(f)
    return sorted(out, key=lambda x: natural_key(x))


def natural_key(s: str):
    return [int(t) if t.isdigit() else t.lower()
            for t in re.split(r"(\d+)", s)]


def chapter_number_from_name(path: str):
    nums = re.findall(r"(\d+)", os.path.basename(path))
    return int(nums[0]) if nums else None


# ---------- Các kiểm tra ----------

def check_fact_ledger(state, chapters):
    """
    Với mỗi dữ kiện có chứa một CON SỐ trong fact_ledger, tìm trong các
    chương những chỗ nhắc tới cùng ngữ cảnh (qua từ khóa) nhưng con số
    khác đi.
    """
    issues = []
    ledger = state.get("fact_ledger", {})
    for key, val in ledger.items():
        # lấy con số chuẩn trong giá trị ledger (nếu có)
        ledger_nums = re.findall(r"\d[\d\.,]*", str(val))
        if not ledger_nums:
            continue
        ledger_norm = {normalize_number_token(n) for n in ledger_nums}

        # Từ khóa ngữ cảnh lấy từ CẢ key LẪN value của ledger: key thường ghi
        # "Số tiền nợ" trong khi chương viết "khoản nợ", nên chỉ soi key là
        # trượt. Ngưỡng 2 ký tự vì âm tiết tiếng Việt đa số ngắn ("nợ", "số").
        # ponytail: khớp theo token trần, có thể báo thừa khi hai thực thể cùng
        # đơn vị nằm gần nhau; nâng lên khớp cụm/thực thể nếu nhiễu quá nhiều.
        key_tokens = [t for t in strip_accents(key + " " + str(val)).split()
                      if len(t) >= 2 and not t[0].isdigit()
                      and t not in GENERIC_UNIT_TOKENS]
        key_tokens = sorted(set(key_tokens))
        if not key_tokens:
            continue

        for ch_path in chapters:
            with open(ch_path, encoding="utf-8") as f:
                text = f.read()
            text_noacc = strip_accents(text)
            # chỉ soi những chương có nhắc tới chủ đề của key
            if not any(has_token(text_noacc, tok) for tok in key_tokens):
                continue
            for item in extract_numbers_with_context(text):
                ctx_noacc = strip_accents(item["context"])
                # con số này nằm gần một từ khóa của key?
                if not any(has_token(ctx_noacc, tok) for tok in key_tokens):
                    continue
                # nếu có đơn vị tiền/tuổi hoặc key nói về tiền/tuổi
                num_norm = normalize_number_token(item["value_raw"])
                # bỏ qua số quá nhỏ vô nghĩa (1,2 câu) trừ khi key là tuổi
                if num_norm in ledger_norm:
                    continue
                # heuristic: chỉ cảnh báo khi con số có đơn vị "đáng kể"
                unit_noacc = strip_accents(item["unit"])
                key_is_money = any(u in strip_accents(str(val)) for u in ["trieu", "ty", "ti", "nghin", "ngan", "dong"])
                key_is_age = "tuoi" in strip_accents(key) or "tuoi" in strip_accents(str(val))
                num_is_money = any(u in unit_noacc for u in ["trieu", "ty", "ti", "nghin", "ngan", "dong"])
                num_is_age = "tuoi" in unit_noacc

                if (key_is_money and num_is_money) or (key_is_age and num_is_age):
                    issues.append({
                        "loai": "FACT_LEDGER",
                        "muc_do": "NANG",
                        "chuong": os.path.basename(ch_path),
                        "du_kien": key,
                        "gia_tri_ledger": str(val),
                        "gia_tri_trong_chuong": f'{item["value_raw"]} {item["unit"]}'.strip(),
                        "ngu_canh": item["context"],
                    })
    return issues


def check_guard_rails(state, chapters):
    issues = []
    rails = state.get("guard_rails", [])
    for rail in rails:
        rail_noacc = strip_accents(rail)
        m = re.search(r"(truoc|sau)\s+chuong\s+(\d+)", rail_noacc)
        if not m:
            continue
        direction, n = m.group(1), int(m.group(2))
        # từ khóa nội dung của rail (bỏ phần "trước/sau chương N")
        content = re.sub(r"(truoc|sau)\s+chuong\s+\d+", "", rail_noacc)
        content_tokens = [t for t in content.split() if len(t) >= 4]
        if not content_tokens:
            continue
        for ch_path in chapters:
            cn = chapter_number_from_name(ch_path)
            if cn is None:
                continue
            violate_zone = (direction == "truoc" and cn < n) or \
                           (direction == "sau" and cn > n)
            if not violate_zone:
                continue
            with open(ch_path, encoding="utf-8") as f:
                text_noacc = strip_accents(f.read())
            hit = sum(1 for tok in content_tokens if tok in text_noacc)
            # nếu phần lớn từ khóa nội dung rail xuất hiện ở vùng cấm
            if hit >= max(2, len(content_tokens) // 2):
                issues.append({
                    "loai": "GUARD_RAIL",
                    "muc_do": "NANG",
                    "chuong": os.path.basename(ch_path),
                    "luat": rail,
                    "ghi_chu": f"Nội dung của guard rail xuất hiện ở chương {cn}, "
                               f"trong vùng bị hạn chế ({direction} chương {n}).",
                })
    return issues


def check_foreshadowing(state, chapters, story_finished):
    issues = []
    ve_so = state.get("ve_so_dang_mo", [])
    max_ch = max([chapter_number_from_name(c) for c in chapters if chapter_number_from_name(c)] or [0])
    for vs in ve_so:
        due = vs.get("du_kien_tra_o_chuong")
        noidung = vs.get("noi_dung", "")
        if due is not None and max_ch >= due:
            # kiểm tra xem có chương nào >= due nhắc lại nội dung vé số không
            tokens = [t for t in strip_accents(noidung).split() if len(t) >= 4]
            paid = False
            for ch_path in chapters:
                cn = chapter_number_from_name(ch_path)
                if cn is None or cn < due:
                    continue
                with open(ch_path, encoding="utf-8") as f:
                    text_noacc = strip_accents(f.read())
                if tokens and sum(1 for t in tokens if t in text_noacc) >= max(1, len(tokens) // 2):
                    paid = True
                    break
            if not paid:
                issues.append({
                    "loai": "VE_SO",
                    "muc_do": "TRUNG_BINH",
                    "ve_so": noidung,
                    "cai_o_chuong": vs.get("cai_o_chuong"),
                    "du_kien_tra": due,
                    "ghi_chu": "Đã tới/qua hạn trả nhưng chưa thấy được nhắc lại/giải quyết.",
                })
    if story_finished:
        for vs in ve_so:
            issues.append({
                "loai": "VE_SO",
                "muc_do": "NANG",
                "ve_so": vs.get("noi_dung", ""),
                "ghi_chu": "Truyện đã đánh dấu hoàn thành nhưng vé số này vẫn còn trong danh sách 'đang mở'.",
            })
    return issues


def check_characters(dir_path, chapters):
    """Cảnh báo tên viết hoa xuất hiện trong chương mà không có trong hồ sơ."""
    issues = []
    profile_path = None
    for name in ("00-nhan-vat.md", "00-nhan-vat.txt"):
        p = os.path.join(dir_path, name)
        if os.path.exists(p):
            profile_path = p
            break
    if not profile_path:
        return issues
    with open(profile_path, encoding="utf-8") as f:
        profile_noacc = strip_accents(f.read())

    # tên tiếng Việt: chuỗi 2-4 từ viết hoa liên tiếp
    name_pat = re.compile(
        r"\b([A-ZĐÀ-Ỹ][a-zà-ỹ]+(?:\s+[A-ZĐÀ-Ỹ][a-zà-ỹ]+){1,3})"
    )
    seen = {}
    for ch_path in chapters:
        with open(ch_path, encoding="utf-8") as f:
            text = f.read()
        for m in name_pat.finditer(text):
            candidate = m.group(1)
            key = strip_accents(candidate)
            # bỏ tên nằm ở đầu câu (có thể là cụm thường viết hoa)
            seen.setdefault(candidate, os.path.basename(ch_path))

    for candidate, first_ch in seen.items():
        key = strip_accents(candidate)
        # nếu không token nào của tên nằm trong hồ sơ -> nghi ngờ
        toks = key.split()
        if not any(t in profile_noacc for t in toks if len(t) >= 3):
            issues.append({
                "loai": "NHAN_VAT",
                "muc_do": "NHE",
                "ten_nghi_ngo": candidate,
                "chuong_dau_tien": first_ch,
                "ghi_chu": "Xuất hiện trong chương nhưng không thấy trong 00-nhan-vat.md "
                           "(có thể là nhân vật phụ chưa khai, hoặc sai chính tả tên).",
            })
    return issues


# ---------- Main ----------

def main():
    ap = argparse.ArgumentParser(description="Kiểm tra tính nhất quán bộ truyện.")
    ap.add_argument("--dir", required=True, help="Thư mục dự án truyện")
    ap.add_argument("--json", action="store_true", help="Xuất báo cáo dạng JSON")
    ap.add_argument("--strict", action="store_true",
                    help="Trả exit code 1 nếu có lỗi mức NANG")
    args = ap.parse_args()

    state_path = os.path.join(args.dir, "project-state.json")
    if not os.path.exists(state_path):
        print(f"❌ Không tìm thấy project-state.json trong {args.dir}")
        sys.exit(1)

    with open(state_path, encoding="utf-8") as f:
        state = json.load(f)

    chapters = find_chapter_files(args.dir)
    if not chapters:
        print("⚠️  Không tìm thấy file chương nào (chuong-*.txt/md). Chỉ kiểm tra được cấu trúc state.")

    story_finished = bool(state.get("hoan_thanh", False))

    all_issues = []
    all_issues += check_fact_ledger(state, chapters)
    all_issues += check_guard_rails(state, chapters)
    all_issues += check_foreshadowing(state, chapters, story_finished)
    all_issues += check_characters(args.dir, chapters)

    if args.json:
        print(json.dumps({"so_van_de": len(all_issues), "chi_tiet": all_issues},
                         ensure_ascii=False, indent=2))
    else:
        if not all_issues:
            print("✅ Không phát hiện mâu thuẫn nào theo các kiểm tra hiện có.")
        else:
            print(f"🔎 Phát hiện {len(all_issues)} điểm cần xem lại:\n")
            order = {"NANG": 0, "TRUNG_BINH": 1, "NHE": 2}
            for it in sorted(all_issues, key=lambda x: order.get(x.get("muc_do"), 3)):
                icon = {"NANG": "🔴", "TRUNG_BINH": "🟡", "NHE": "⚪"}.get(it.get("muc_do"), "•")
                print(f"{icon} [{it['loai']}] {it.get('chuong', '')}")
                for k, v in it.items():
                    if k in ("loai", "muc_do", "chuong"):
                        continue
                    print(f"     {k}: {v}")
                print()

    if args.strict and any(i.get("muc_do") == "NANG" for i in all_issues):
        sys.exit(1)


if __name__ == "__main__":
    main()

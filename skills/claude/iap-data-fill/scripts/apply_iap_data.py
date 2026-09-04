#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ghi du lieu goi IAP vao 2 file cho khop nhau:
  - IAPData `.asset` (YAML Unity, SerializedDictionary<string, IAPItem>)
  - IAPProductCatalog.json (Unity IAP Catalog)

Script chi lam phan CO HOC (ghi dung format, idempotent, verify). Viec quyet dinh
product id / reward id / so luong la cua Claude o phase discovery + mapping.

Dung:
  python apply_iap_data.py --spec spec.json
  python apply_iap_data.py --spec spec.json --dry-run
  python apply_iap_data.py --verify-only --asset <path> --catalog <path>

Format spec.json:
{
  "asset":   "Assets/_Project/Data/IAPData.asset",
  "catalog": "Assets/Resources/IAPProductCatalog.json",
  "products": [
    {
      "id": "good.pack.bronze",
      "type": "Consumable",
      "status": 0,
      "rewards": [
        {"id": 100, "amount": 2, "name": "Magnet"},
        {"id": 10,  "amount": 3000, "name": "coins"}
      ]
    }
  ]
}
"asset"/"catalog" co the bo qua neu truyen --asset/--catalog. "name" trong reward chi de
nguoi doc de doi chieu, script bo qua. "status" thieu -> giu gia tri cu (moi -> 0).
"""

import argparse
import copy
import io
import json
import os
import re
import sys

TYPE_ALIASES = {
    "consumable": 0,
    "nonconsumable": 1, "non-consumable": 1, "non consumable": 1,
    "subscription": 2,
}
TYPE_LABELS = {0: "Consumable", 1: "NonConsumable", 2: "Subscription"}

KEY_RE = re.compile(r"^(\s*)- Key:\s*(.*?)\s*$")


def die(msg):
    print("LOI: " + msg, file=sys.stderr)
    sys.exit(1)


# ---------------------------------------------------------------- io helpers

def read_text(path):
    """Doc file, tra ve (text, newline, co_bom) de ghi lai dung y nguyen format."""
    with open(path, "rb") as f:
        raw = f.read()
    bom = raw.startswith(b"\xef\xbb\xbf")
    if bom:
        raw = raw[3:]
    text = raw.decode("utf-8")
    newline = "\r\n" if "\r\n" in text else "\n"
    return text.replace("\r\n", "\n"), newline, bom


def write_text(path, text, newline, bom):
    data = text.replace("\n", newline).encode("utf-8")
    if bom:
        data = b"\xef\xbb\xbf" + data
    with open(path, "wb") as f:
        f.write(data)


def norm_type(value, where):
    if value is None:
        return None
    if isinstance(value, bool):
        die("type cua %s khong duoc la bool" % where)
    if isinstance(value, int):
        if value not in TYPE_LABELS:
            die("type cua %s = %s khong hop le (0/1/2)" % (where, value))
        return value
    key = str(value).strip().lower()
    if key in TYPE_ALIASES:
        return TYPE_ALIASES[key]
    if key.isdigit() and int(key) in TYPE_LABELS:
        return int(key)
    die("type cua %s = %r khong hop le (Consumable/NonConsumable/Subscription)" % (where, value))


def autodiscover(root, names):
    """Tim file theo ten trong cay thu muc, bo qua thu muc sinh ra cua Unity."""
    skip = {"Library", "Temp", "obj", "Build", "Builds", ".git", "node_modules"}
    found = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in skip]
        for name in filenames:
            if name in names:
                found.append(os.path.join(dirpath, name))
    return found


# ------------------------------------------------------- asset (YAML) parsing

class Entry(object):
    def __init__(self, key, start, end, product_type, status, rewards):
        self.key = key
        self.start = start          # chi so dong bat dau (inclusive)
        self.end = end              # chi so dong ket thuc (exclusive)
        self.product_type = product_type
        self.status = status
        self.rewards = rewards      # list [(reward_id, amount)]


def unquote(value):
    if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
        value = value[1:-1]
    return value.strip()


def _grab_int(text, pattern):
    m = re.search(pattern, text)
    return int(m.group(1)) if m else None


def parse_asset(text):
    """
    Tra ve (lines, list_start, list_end, indent, entries, empty_literal).
    list_start/list_end la pham vi dong thuoc _serializedList.
    """
    lines = text.split("\n")

    header = None
    for i, line in enumerate(lines):
        if line.strip().startswith("_serializedList:"):
            header = i
            break
    if header is None:
        die("Khong tim thay `_serializedList:` trong asset - file nay co phai IAPData khong?")

    header_indent = len(lines[header]) - len(lines[header].lstrip(" "))
    empty_literal = lines[header].strip().endswith("[]")

    list_start = header + 1
    list_end = list_start
    if not empty_literal:
        j = list_start
        while j < len(lines):
            line = lines[j]
            if line.strip() == "":
                j += 1
                continue
            indent = len(line) - len(line.lstrip(" "))
            # Unity ghi sequence NGANG MUC voi key cha:
            #     _serializedList:
            #     - Key: ...
            # nen dieu kien dung khong the la `indent <= header_indent` - the thi list rong
            # ngay tu dau va toan bo entry cu bi coi nhu nam ngoai (mat sach du lieu).
            # Chi thoat khi tut ra ngoai han, hoac ngang muc nhung khong phai phan tu list.
            if indent < header_indent:
                break
            if indent == header_indent and not line.lstrip(" ").startswith("- "):
                break
            j += 1
        list_end = j
        while list_end > list_start and lines[list_end - 1].strip() == "":
            list_end -= 1

    starts = []
    for j in range(list_start, list_end):
        m = KEY_RE.match(lines[j])
        if m:
            starts.append((j, len(m.group(1)), unquote(m.group(2))))
    # List rong thi khong co entry nao de bat chuoc -> dung ngang muc key cha, dung cach
    # Unity tu serialize lai, de lan sau Unity ghi de khong tao diff rac.
    indent = starts[0][1] if starts else header_indent

    entries = []
    for idx, item in enumerate(starts):
        line_no, _, key = item
        end = starts[idx + 1][0] if idx + 1 < len(starts) else list_end
        block = "\n".join(lines[line_no:end])
        ptype = _grab_int(block, r"ProductType:\s*(\d+)")
        status = _grab_int(block, r"Status:\s*\n\s*id:\s*(-?\d+)")
        rewards = [(int(a), int(b)) for a, b in re.findall(
            r"-\s*Type:\s*\n\s*id:\s*(-?\d+)\s*\n\s*RewardGet:\s*(-?\d+)", block)]
        entries.append(Entry(key, line_no, end, ptype, status, rewards))

    # Chot an toan: moi dong `- Key:` trong file phai duoc nhan dien la 1 entry. Lech nghia la
    # pham vi list bi cat sai, va neu cu ghi tiep thi so entry ngoai pham vi bi xoa trang.
    total_keys = len(re.findall(r"^\s*- Key:\s", text, re.M))
    if total_keys != len(entries):
        die("Parse asset lech: file co %d dong `- Key:` nhung chi nhan dien %d entry. "
            "Dung lai de khong lam mat du lieu - bao cho nguoi dung kiem tra format asset."
            % (total_keys, len(entries)))

    return lines, list_start, list_end, indent, entries, empty_literal


def render_entry(indent, key, product_type, status, rewards):
    pad = " " * indent
    out = [pad + "- Key: " + key,
           pad + "  Value:",
           pad + "    ProductType: %d" % product_type,
           pad + "    Status:",
           pad + "      id: %d" % status]
    if rewards:
        out.append(pad + "    RewardList:")
        for rid, amount in rewards:
            out.append(pad + "    - Type:")
            out.append(pad + "        id: %d" % rid)
            out.append(pad + "      RewardGet: %d" % amount)
    else:
        out.append(pad + "    RewardList: []")
    return out


# ------------------------------------------------------------------- catalog

CATALOG_FALLBACK_PRODUCT = {
    "id": "", "type": 0, "storeIDs": [],
    "defaultDescription": {"googleLocale": 21, "title": "", "description": ""},
    "screenshotPath": "", "applePriceTier": 0,
    "googlePrice": {"data": [0, 0, 0, 0], "num": 0.0},
    "pricingTemplateID": "", "descriptions": [], "payouts": [],
}


def catalog_template(catalog):
    """
    Clone shape cua 1 product co san thay vi hardcode schema: Unity doi field giua cac ban
    IAP package, clone thi khong bao gio lech.
    """
    products = catalog.get("products") or []
    if products:
        tpl = copy.deepcopy(products[0])
        tpl["id"] = ""
        tpl["type"] = 0
        return tpl
    return copy.deepcopy(CATALOG_FALLBACK_PRODUCT)


# --------------------------------------------------------------------- apply

def build_wanted(products):
    wanted = {}
    for p in products:
        pid = str(p.get("id", "")).strip()
        if not pid:
            die("Co product thieu `id` trong spec - khong duoc tu che id.")
        if pid in wanted:
            die("spec khai trung product id %r." % pid)
        rewards = []
        for r in p.get("rewards") or []:
            rid, amount = r.get("id"), r.get("amount")
            if rid is None or amount is None:
                die("Reward cua %s thieu `id` hoac `amount`." % pid)
            if int(amount) <= 0:
                die("Reward %s cua %s co amount <= 0 - kiem tra lai input." % (rid, pid))
            rewards.append((int(rid), int(amount)))
        wanted[pid] = {"type": norm_type(p.get("type"), pid),
                       "status": p.get("status"),
                       "rewards": rewards}
    return wanted


def apply_spec(spec, asset_path, catalog_path, dry_run):
    report = {"asset_updated": [], "asset_added": [], "catalog_added": [],
              "catalog_type_fixed": [], "keys_trimmed": []}

    if not spec.get("products"):
        die("spec khong co `products` hoac danh sach rong.")
    wanted = build_wanted(spec["products"])

    # ---- IAPData .asset
    text, newline, bom = read_text(asset_path)
    lines, list_start, list_end, indent, entries, empty_literal = parse_asset(text)

    by_key = {}
    for e in entries:
        if e.key in by_key:
            die("Asset co 2 entry trung key %r - sua tay truoc khi chay lai." % e.key)
        by_key[e.key] = e
        # Key goc khac dang chuan (nhay bao/khoang trang thua) thi se duoc ghi lai sach.
        if lines[e.start] != " " * indent + "- Key: " + e.key:
            report["keys_trimmed"].append(e.key)

    new_block = []
    for e in entries:
        if e.key in wanted:
            w = wanted[e.key]
            ptype = w["type"] if w["type"] is not None else (e.product_type or 0)
            status = int(w["status"] if w["status"] is not None else (e.status or 0))
            rewards = w["rewards"] if w["rewards"] else e.rewards
            new_block.extend(render_entry(indent, e.key, ptype, status, rewards))
            if (ptype, status, rewards) != (e.product_type, e.status, e.rewards) \
                    or e.key in report["keys_trimmed"]:
                report["asset_updated"].append(e.key)
        else:
            new_block.extend(render_entry(indent, e.key, e.product_type or 0,
                                          e.status or 0, e.rewards))

    for pid in wanted:
        if pid in by_key:
            continue
        w = wanted[pid]
        new_block.extend(render_entry(indent, pid,
                                      w["type"] if w["type"] is not None else 0,
                                      int(w["status"] or 0), w["rewards"]))
        report["asset_added"].append(pid)

    if empty_literal:
        lines[list_start - 1] = lines[list_start - 1].replace("_serializedList: []",
                                                              "_serializedList:")
        new_lines = lines[:list_start] + new_block + lines[list_start:]
    else:
        new_lines = lines[:list_start] + new_block + lines[list_end:]
    asset_out = "\n".join(new_lines)

    # Chot an toan thu 2: doc lai ket qua TRUOC khi ghi de file. So goi chi duoc phep giu nguyen
    # hoac tang - giam nghia la co entry bi nuot, va luc do file that van con nguyen ven.
    expected = len(entries) + len(report["asset_added"])
    actual = len(re.findall(r"^\s*- Key:\s", asset_out, re.M))
    if actual != expected:
        die("Ket qua dung ra phai co %d goi nhung dem duoc %d - huy ghi de giu nguyen file goc."
            % (expected, actual))

    # ---- IAPProductCatalog.json
    ctext, cnewline, cbom = read_text(catalog_path)
    try:
        catalog = json.loads(ctext)
    except ValueError as err:
        die("Khong parse duoc catalog JSON: %s" % err)

    catalog.setdefault("products", [])
    tpl = catalog_template(catalog)

    seen = {}
    for prod in catalog["products"]:
        clean = str(prod.get("id", "")).strip()
        if clean != prod.get("id"):
            report["keys_trimmed"].append(clean)
        prod["id"] = clean
        seen[clean] = prod

    for pid in wanted:
        w = wanted[pid]
        if pid in seen:
            if w["type"] is not None and seen[pid].get("type") != w["type"]:
                seen[pid]["type"] = w["type"]
                report["catalog_type_fixed"].append(pid)
            continue
        prod = copy.deepcopy(tpl)
        prod["id"] = pid
        prod["type"] = w["type"] if w["type"] is not None else 0
        catalog["products"].append(prod)
        report["catalog_added"].append(pid)

    catalog_out = json.dumps(catalog, separators=(",", ":"), ensure_ascii=False)

    if not dry_run:
        write_text(asset_path, asset_out, newline, bom)
        write_text(catalog_path, catalog_out, cnewline, cbom)

    report["keys_trimmed"] = sorted(set(report["keys_trimmed"]))
    return report


# -------------------------------------------------------------------- verify

def verify(asset_path, catalog_path):
    problems = []
    text, _, _ = read_text(asset_path)
    _, _, _, _, entries, _ = parse_asset(text)

    ctext, _, _ = read_text(catalog_path)
    catalog = json.loads(ctext)
    cat_products = {str(p.get("id", "")): p for p in catalog.get("products", [])}

    for raw in re.findall(r"^\s*- Key:\s*(.*?)\s*$", text, re.M):
        if unquote(raw) != raw:
            problems.append("Asset: key %r con nhay bao / khoang trang thua." % raw)
    for cid in cat_products:
        if cid != cid.strip():
            problems.append("Catalog: id %r con khoang trang thua." % cid)

    asset_keys = set(e.key for e in entries)
    cat_keys = set(k.strip() for k in cat_products)

    for k in sorted(asset_keys - cat_keys):
        problems.append("Co trong IAPData nhung THIEU trong catalog: %s" % k)
    for k in sorted(cat_keys - asset_keys):
        problems.append("Co trong catalog nhung THIEU trong IAPData: %s" % k)

    for e in entries:
        if not e.rewards:
            problems.append("Goi %s co RewardList rong - tra tien ma khong nhan gi." % e.key)
        for rid, amount in e.rewards:
            if amount <= 0:
                problems.append("Goi %s: reward id %d co so luong %d." % (e.key, rid, amount))
        prod = cat_products.get(e.key)
        if prod is not None and prod.get("type") != e.product_type:
            problems.append("Goi %s: ProductType lech - asset=%s, catalog=%s." % (
                e.key,
                TYPE_LABELS.get(e.product_type, e.product_type),
                TYPE_LABELS.get(prod.get("type"), prod.get("type"))))

    return entries, problems


# ---------------------------------------------------------------------- main

def resolve_paths(spec, args):
    asset = args.asset or (spec.get("asset") if spec else None)
    catalog = args.catalog or (spec.get("catalog") if spec else None)
    root = args.root or "."

    if not asset:
        hits = autodiscover(root, {"IAPData.asset"})
        if len(hits) != 1:
            die("Khong xac dinh duoc IAPData.asset (tim thay %d) - truyen --asset." % len(hits))
        asset = hits[0]
    if not catalog:
        hits = autodiscover(root, {"IAPProductCatalog.json"})
        if len(hits) != 1:
            die("Khong xac dinh duoc IAPProductCatalog.json (tim thay %d) - truyen --catalog."
                % len(hits))
        catalog = hits[0]

    for p in (asset, catalog):
        if not os.path.isfile(p):
            die("Khong thay file: %s" % p)
    return asset, catalog


def main():
    ap = argparse.ArgumentParser(description="Ghi du lieu goi IAP vao IAPData + catalog.")
    ap.add_argument("--spec", help="File JSON mo ta cac goi can ghi.")
    ap.add_argument("--asset", help="Duong dan IAPData .asset.")
    ap.add_argument("--catalog", help="Duong dan IAPProductCatalog.json.")
    ap.add_argument("--root", help="Thu muc goc de tu do file (mac dinh: thu muc hien tai).")
    ap.add_argument("--dry-run", action="store_true", help="Chi bao se doi gi, khong ghi.")
    ap.add_argument("--verify-only", action="store_true", help="Chi kiem tra, khong ghi.")
    args = ap.parse_args()

    spec = None
    if args.spec:
        with io.open(args.spec, encoding="utf-8") as f:
            spec = json.load(f)

    if not args.verify_only and spec is None:
        die("Thieu --spec (hoac dung --verify-only).")

    asset_path, catalog_path = resolve_paths(spec, args)
    print("IAPData : %s" % asset_path)
    print("Catalog : %s" % catalog_path)
    print("")

    if not args.verify_only:
        report = apply_spec(spec, asset_path, catalog_path, args.dry_run)
        label = "[DRY-RUN] " if args.dry_run else ""
        titles = (("Cap nhat trong IAPData", "asset_updated"),
                  ("Them moi vao IAPData", "asset_added"),
                  ("Them moi vao catalog", "catalog_added"),
                  ("Sua ProductType trong catalog", "catalog_type_fixed"),
                  ("Don id dinh khoang trang/nhay bao", "keys_trimmed"))
        for title, key in titles:
            items = report[key]
            if items:
                print("%s%s (%d): %s" % (label, title, len(items), ", ".join(sorted(items))))
        if not any(report.values()):
            print("%sKhong co gi thay doi - du lieu da dung san." % label)
        print("")

    entries, problems = verify(asset_path, catalog_path)
    print("Kiem tra: %d goi trong IAPData." % len(entries))
    if problems:
        print("Van de (%d):" % len(problems))
        for p in problems:
            print("  - " + p)
        sys.exit(2)
    print("OK - IAPData va catalog khop nhau, khong goi nao rong.")


if __name__ == "__main__":
    main()

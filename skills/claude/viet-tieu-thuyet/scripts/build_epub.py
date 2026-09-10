#!/usr/bin/env python3
"""
build_epub.py — Gộp các file chương thành một ebook EPUB hoàn chỉnh.

Viết bằng thư viện chuẩn (zipfile) nên KHÔNG cần cài ebooklib hay bất kỳ
package ngoài nào — chạy được ngay với Python 3 mặc định.

Tự động:
  - Đọc tiêu đề/tác giả từ project-state.json nếu có (khóa "du_an"),
    hoặc từ tham số dòng lệnh.
  - Nhận diện các file chương theo thứ tự tự nhiên (chuong-01, chuong-02...).
  - Lấy tiêu đề mỗi chương từ dòng đầu tiên của file (nếu là tiêu đề)
    hoặc đặt "Chương N".
  - Sinh trang bìa, mục lục điều hướng (nav), CSS hỗ trợ tiếng Việt.
  - Đóng gói đúng chuẩn EPUB 3 (mimetype không nén đầu file).

Cách dùng:
    python3 build_epub.py --dir THU_MUC_DU_AN --out truyen.epub
    python3 build_epub.py --dir . --title "Bạn Học 36" --author "Tên tác giả"
"""

import argparse
import glob
import html
import json
import os
import re
import sys
import unicodedata
import zipfile



# Console Windows mac dinh cp1252 -> print tieng Viet se crash. Ep UTF-8.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
def natural_key(s):
    return [int(t) if t.isdigit() else t.lower()
            for t in re.split(r"(\d+)", s)]


def find_chapters(dir_path):
    patterns = ["chuong-*.txt", "chuong-*.md", "chuong*.txt", "chuong*.md",
                "chapter-*.txt", "chapter-*.md", "chapter*.txt", "chapter*.md"]
    files = set()
    for p in patterns:
        files.update(glob.glob(os.path.join(dir_path, p)))
    excluded = {"00-nhan-vat", "01-the-gioi", "02-dan-y"}
    out = [f for f in files
           if os.path.splitext(os.path.basename(f))[0].lower() not in excluded]
    return sorted(out, key=lambda x: natural_key(os.path.basename(x)))


def read_chapter(path, index):
    with open(path, encoding="utf-8") as f:
        raw = f.read().strip()
    lines = [l.rstrip() for l in raw.split("\n")]
    # tiêu đề: dòng đầu nếu ngắn và không phải câu văn dài
    title = f"Chương {index}"
    body_lines = lines
    if lines:
        first = lines[0].lstrip("#").strip()
        if first and len(first) <= 80 and not first.endswith((".", "!", "?", "…")):
            title = first
            body_lines = lines[1:]
    # bỏ dòng trống đầu
    while body_lines and not body_lines[0].strip():
        body_lines.pop(0)
    # gom thành các đoạn <p>
    paragraphs = []
    buf = []
    for line in body_lines:
        if line.strip() == "":
            if buf:
                paragraphs.append(" ".join(buf))
                buf = []
        else:
            buf.append(line.strip())
    if buf:
        paragraphs.append(" ".join(buf))
    return title, paragraphs


CSS = """\
body { font-family: "Noto Serif CJK SC", "Times New Roman", serif;
       line-height: 1.7; margin: 5% 6%; text-align: justify;
       color: #1a1a1a; background: #fbfbf8; }
h1 { text-align: center; font-size: 1.5em; margin: 1.2em 0 1.6em; }
h1.book-title { font-size: 2.2em; margin-top: 30%; }
p.author { text-align: center; font-size: 1.1em; color: #555; }
p { text-indent: 1.4em; margin: 0.2em 0 0.7em; }
nav ol { line-height: 2; }
"""


def xhtml_page(title, body_html):
    return (
        '<?xml version="1.0" encoding="utf-8"?>\n'
        '<!DOCTYPE html>\n'
        '<html xmlns="http://www.w3.org/1999/xhtml" '
        'xmlns:epub="http://www.idpf.org/2007/ops" xml:lang="vi" lang="vi">\n'
        f'<head><meta charset="utf-8"/><title>{html.escape(title)}</title>'
        '<link rel="stylesheet" type="text/css" href="style.css"/></head>\n'
        f'<body>\n{body_html}\n</body>\n</html>\n'
    )


def build(dir_path, title, author, out_path):
    chapters = find_chapters(dir_path)
    if not chapters:
        print("❌ Không tìm thấy file chương nào để đóng gói.")
        sys.exit(1)

    parsed = []
    for i, path in enumerate(chapters, 1):
        t, paras = read_chapter(path, i)
        parsed.append((t, paras))

    uid = "urn:uuid:viet-tieu-thuyet-" + re.sub(r"\W+", "", strip_accents(title))[:24]

    # --- tạo các file nội dung ---
    files = {}

    # bìa
    cover = xhtml_page(title,
        f'<h1 class="book-title">{html.escape(title)}</h1>'
        f'<p class="author">{html.escape(author)}</p>')
    files["OEBPS/cover.xhtml"] = cover

    # các chương
    manifest_items = ['<item id="cover" href="cover.xhtml" media-type="application/xhtml+xml"/>']
    spine_items = ['<itemref idref="cover"/>']
    nav_list = []
    for i, (t, paras) in enumerate(parsed, 1):
        body = f"<h1>{html.escape(t)}</h1>\n" + \
               "\n".join(f"<p>{html.escape(p)}</p>" for p in paras)
        fname = f"chap{i:03d}.xhtml"
        files[f"OEBPS/{fname}"] = xhtml_page(t, body)
        cid = f"chap{i:03d}"
        manifest_items.append(
            f'<item id="{cid}" href="{fname}" media-type="application/xhtml+xml"/>')
        spine_items.append(f'<itemref idref="{cid}"/>')
        nav_list.append(f'<li><a href="{fname}">{html.escape(t)}</a></li>')

    # nav (mục lục EPUB3)
    nav_body = ('<nav epub:type="toc" id="toc"><h1>Mục lục</h1><ol>\n'
                + "\n".join(nav_list) + '\n</ol></nav>')
    files["OEBPS/nav.xhtml"] = xhtml_page("Mục lục", nav_body)
    manifest_items.append('<item id="nav" href="nav.xhtml" '
                          'media-type="application/xhtml+xml" properties="nav"/>')

    # css
    files["OEBPS/style.css"] = CSS
    manifest_items.append('<item id="css" href="style.css" media-type="text/css"/>')

    # content.opf
    opf = (
        '<?xml version="1.0" encoding="utf-8"?>\n'
        '<package xmlns="http://www.idpf.org/2007/opf" version="3.0" '
        'unique-identifier="bookid">\n'
        '  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">\n'
        f'    <dc:identifier id="bookid">{uid}</dc:identifier>\n'
        f'    <dc:title>{html.escape(title)}</dc:title>\n'
        f'    <dc:creator>{html.escape(author)}</dc:creator>\n'
        '    <dc:language>vi</dc:language>\n'
        '  </metadata>\n'
        '  <manifest>\n    ' + "\n    ".join(manifest_items) + '\n  </manifest>\n'
        '  <spine>\n    ' + "\n    ".join(spine_items) + '\n  </spine>\n'
        '</package>\n'
    )
    files["OEBPS/content.opf"] = opf

    # container.xml
    files["META-INF/container.xml"] = (
        '<?xml version="1.0" encoding="utf-8"?>\n'
        '<container version="1.0" '
        'xmlns="urn:oasis:names:tc:opendocument:xmlns:container">\n'
        '  <rootfiles>\n'
        '    <rootfile full-path="OEBPS/content.opf" '
        'media-type="application/oebps-package+xml"/>\n'
        '  </rootfiles>\n</container>\n'
    )

    # --- ghi file zip đúng chuẩn EPUB ---
    with zipfile.ZipFile(out_path, "w") as z:
        # mimetype PHẢI là file đầu tiên và KHÔNG nén
        z.writestr("mimetype", "application/epub+zip",
                   compress_type=zipfile.ZIP_STORED)
        for name, content in files.items():
            z.writestr(name, content, compress_type=zipfile.ZIP_DEFLATED)

    print(f"✅ Đã tạo EPUB: {out_path}")
    print(f"   Số chương: {len(parsed)} | Tiêu đề: {title} | Tác giả: {author}")


def strip_accents(s):
    nfkd = unicodedata.normalize("NFD", s)
    out = "".join(c for c in nfkd if unicodedata.category(c) != "Mn")
    return out.replace("đ", "d").replace("Đ", "D")


def main():
    ap = argparse.ArgumentParser(description="Đóng gói truyện thành EPUB.")
    ap.add_argument("--dir", required=True, help="Thư mục dự án truyện")
    ap.add_argument("--out", default=None, help="Tên file EPUB đầu ra")
    ap.add_argument("--title", default=None, help="Tiêu đề sách")
    ap.add_argument("--author", default="Vô danh", help="Tên tác giả")
    args = ap.parse_args()

    title = args.title
    if not title:
        state_path = os.path.join(args.dir, "project-state.json")
        if os.path.exists(state_path):
            with open(state_path, encoding="utf-8") as f:
                title = json.load(f).get("du_an")
    if not title:
        title = "Truyện chưa đặt tên"

    out = args.out or (re.sub(r"\W+", "-", strip_accents(title)).strip("-").lower() + ".epub")
    # Mặc định đặt file cạnh các chương, không rơi ra thư mục đang đứng
    if not os.path.isabs(out) and os.path.dirname(out) == "":
        out = os.path.join(args.dir, out)
    build(args.dir, title, args.author, out)


if __name__ == "__main__":
    main()

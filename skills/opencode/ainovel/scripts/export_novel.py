#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import uuid
import zipfile
from pathlib import Path
from xml.sax.saxutils import escape as xml_escape

from _common import chapter_files, read_json, resolve_project, slugify, utc_now


def markdown_plain(text: str) -> str:
    lines = []
    for line in text.splitlines():
        line = re.sub(r"^\s{0,3}#{1,6}\s*", "", line)
        line = re.sub(r"!\[([^]]*)\]\([^)]*\)", r"\1", line)
        line = re.sub(r"\[([^]]+)\]\([^)]*\)", r"\1", line)
        line = re.sub(r"[*_~`]", "", line)
        lines.append(line.rstrip())
    return "\n".join(lines).strip()


def md_to_xhtml_body(text: str) -> str:
    out = []
    para = []

    def flush() -> None:
        nonlocal para
        if para:
            body = " ".join(x.strip() for x in para if x.strip())
            if body:
                out.append(f"<p>{html.escape(body)}</p>")
            para = []

    for raw in text.splitlines():
        line = raw.rstrip()
        m = re.match(r"^\s{0,3}(#{1,6})\s+(.*)$", line)
        if m:
            flush()
            level = min(len(m.group(1)), 3)
            out.append(f"<h{level}>{html.escape(markdown_plain(m.group(2)))}</h{level}>")
        elif not line.strip():
            flush()
        else:
            para.append(markdown_plain(line))
    flush()
    return "\n".join(out)


def chapter_title(text: str, n: int) -> str:
    for line in text.splitlines():
        m = re.match(r"^\s{0,3}#{1,6}\s+(.*)$", line)
        if not m:
            continue
        raw = markdown_plain(m.group(1)).strip()
        # Strip common writer-added numbering; exporter owns reader-facing numbering.
        patterns = [
            rf"^(?:Chương|Chuong)\s*{n}\s*[:.\-–—]?\s*",
            rf"^Chapter\s*{n}\s*[:.\-–—]?\s*",
            rf"^第\s*{n}\s*章\s*[:：.\-–—]?\s*",
        ]
        title = raw
        for pat in patterns:
            title = re.sub(pat, "", title, flags=re.IGNORECASE).strip()
        return title or raw or f"Chapter {n}"
    return ""


def chapter_body(text: str) -> str:
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if not line.strip():
            continue
        if re.match(r"^\s{0,3}#{1,6}\s+", line):
            del lines[i]
        break
    return "\n".join(lines).strip()


def display_chapter_heading(lang: str, n: int, title: str) -> str:
    title = title.strip()
    if lang.lower().startswith("vi"):
        base = f"Chương {n}"
        return f"{base}: {title}" if title else base
    if lang.lower().startswith("zh"):
        return f"第 {n} 章 {title}".rstrip()
    base = f"Chapter {n}"
    return f"{base}: {title}" if title else base


def boundaries(project: Path) -> dict[int, tuple[str | None, str | None]]:
    layered = read_json(project / "layered_outline.json", {}) or {}
    mapping: dict[int, tuple[str | None, str | None]] = {}
    for vi, vol in enumerate(layered.get("volumes", []) or [], 1):
        vtitle = vol.get("title") or f"Volume {vi}"
        for ai, arc in enumerate(vol.get("arcs", []) or [], 1):
            atitle = arc.get("title") or f"Arc {ai}"
            rng = arc.get("chapter_range") or []
            if len(rng) == 2:
                try:
                    start, end = int(rng[0]), int(rng[1])
                except (TypeError, ValueError):
                    continue
                if end < start:
                    continue
                for n in range(start, end + 1):
                    mapping[n] = (vtitle, atitle)
    return mapping


def select_chapters(project: Path, start: int | None, end: int | None) -> list[tuple[int, Path, str]]:
    out = []
    for p in chapter_files(project):
        n = int(p.stem)
        if start is not None and n < start:
            continue
        if end is not None and n > end:
            continue
        text = p.read_text(encoding="utf-8")
        out.append((n, p, text))
    return out


def book_meta(project: Path) -> dict:
    meta = read_json(project / "meta" / "book.json", {}) or {}
    title = (meta.get("title") or "").strip()
    if not title:
        book_md = (project / "book.md").read_text(encoding="utf-8") if (project / "book.md").exists() else ""
        for line in book_md.splitlines():
            if line.strip().startswith("#"):
                title = line.lstrip("#").strip()
                break
    meta["title"] = title or "Untitled Novel"
    meta.setdefault("language", "vi")
    meta.setdefault("summary", "")
    return meta


def export_txt(project: Path, output: Path, chapters: list[tuple[int, Path, str]], meta: dict) -> None:
    mapping = boundaries(project)
    lang = str(meta.get("language") or "vi")
    chunks = [f"《{meta['title']}》"]
    prev_v = None
    for n, _, text in chapters:
        v, _ = mapping.get(n, (None, None))
        if v and v != prev_v:
            chunks += ["", "", f"=== {v} ==="]
            prev_v = v
        ttl = chapter_title(text, n)
        heading = display_chapter_heading(lang, n, ttl)
        body = markdown_plain(chapter_body(text))
        chunks += ["", "", heading, "", body]
    output.write_text("\n".join(chunks).rstrip() + "\n", encoding="utf-8")


def export_epub(project: Path, output: Path, chapters: list[tuple[int, Path, str]], meta: dict) -> None:
    digest = hashlib.sha256()
    digest.update(meta["title"].encode("utf-8"))
    for n, _, text in chapters:
        digest.update(str(n).encode("ascii"))
        digest.update(text.encode("utf-8"))
    uid = uuid.uuid5(uuid.NAMESPACE_URL, "ainovel:" + digest.hexdigest())
    lang = str(meta.get("language") or "vi")
    title = str(meta["title"])
    desc = str(meta.get("summary") or "")

    items = []
    spine = []
    nav_links = []
    chapter_docs: dict[str, str] = {}
    for idx, (n, _, text) in enumerate(chapters, 1):
        href = f"chapters/chapter-{n:03d}.xhtml"
        item_id = f"ch{idx}"
        ttl = chapter_title(text, n)
        display_title = display_chapter_heading(lang, n, ttl)
        body = md_to_xhtml_body(chapter_body(text))
        doc = f'''<?xml version="1.0" encoding="utf-8"?>
<html xmlns="http://www.w3.org/1999/xhtml" lang="{html.escape(lang)}">
<head><meta charset="utf-8"/><title>{html.escape(display_title)}</title><link rel="stylesheet" type="text/css" href="../style.css"/></head>
<body><h1>{html.escape(display_title)}</h1>{body}</body></html>'''
        chapter_docs[href] = doc
        items.append(f'<item id="{item_id}" href="{href}" media-type="application/xhtml+xml"/>')
        spine.append(f'<itemref idref="{item_id}"/>')
        nav_links.append(f'<li><a href="{href}">{html.escape(display_title)}</a></li>')

    opf = f'''<?xml version="1.0" encoding="UTF-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="bookid" xml:lang="{html.escape(lang)}">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
    <dc:identifier id="bookid">urn:uuid:{uid}</dc:identifier>
    <dc:title>{xml_escape(title)}</dc:title>
    <dc:language>{xml_escape(lang)}</dc:language>
    <dc:description>{xml_escape(desc)}</dc:description>
    <meta property="dcterms:modified">{utc_now()}</meta>
  </metadata>
  <manifest>
    <item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>
    <item id="titlepage" href="title.xhtml" media-type="application/xhtml+xml"/>
    <item id="css" href="style.css" media-type="text/css"/>
    {''.join(items)}
  </manifest>
  <spine>
    <itemref idref="titlepage"/>
    {''.join(spine)}
  </spine>
</package>'''
    nav = f'''<?xml version="1.0" encoding="utf-8"?>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" lang="{html.escape(lang)}">
<head><meta charset="utf-8"/><title>Contents</title><link rel="stylesheet" type="text/css" href="style.css"/></head>
<body><nav epub:type="toc" id="toc"><h1>Contents</h1><ol>{''.join(nav_links)}</ol></nav></body></html>'''
    titlepage = f'''<?xml version="1.0" encoding="utf-8"?>
<html xmlns="http://www.w3.org/1999/xhtml" lang="{html.escape(lang)}"><head><meta charset="utf-8"/><title>{html.escape(title)}</title><link rel="stylesheet" type="text/css" href="style.css"/></head>
<body><section class="titlepage"><h1>{html.escape(title)}</h1><p>{html.escape(desc)}</p></section></body></html>'''
    container = '''<?xml version="1.0"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
  <rootfiles><rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/></rootfiles>
</container>'''
    css = "body{font-family:serif;line-height:1.6;margin:5%;} h1,h2,h3{line-height:1.25;} p{text-indent:1.5em;margin:.5em 0;} .titlepage p{text-indent:0;}"

    with zipfile.ZipFile(output, "w") as zf:
        zf.writestr("mimetype", "application/epub+zip", compress_type=zipfile.ZIP_STORED)
        zf.writestr("META-INF/container.xml", container, compress_type=zipfile.ZIP_DEFLATED)
        zf.writestr("OEBPS/content.opf", opf, compress_type=zipfile.ZIP_DEFLATED)
        zf.writestr("OEBPS/nav.xhtml", nav, compress_type=zipfile.ZIP_DEFLATED)
        zf.writestr("OEBPS/title.xhtml", titlepage, compress_type=zipfile.ZIP_DEFLATED)
        zf.writestr("OEBPS/style.css", css, compress_type=zipfile.ZIP_DEFLATED)
        for href, doc in chapter_docs.items():
            zf.writestr("OEBPS/" + href, doc, compress_type=zipfile.ZIP_DEFLATED)


def main() -> None:
    p = argparse.ArgumentParser(description="Export committed Ainovel chapters to TXT or dependency-free EPUB3.")
    p.add_argument("output", nargs="?")
    p.add_argument("--project")
    p.add_argument("--from", dest="from_chapter", type=int)
    p.add_argument("--to", dest="to_chapter", type=int)
    p.add_argument("--overwrite", action="store_true")
    args = p.parse_args()
    project = resolve_project(args.project)
    chapters = select_chapters(project, args.from_chapter, args.to_chapter)
    if not chapters:
        raise SystemExit("No committed chapters in selected range")
    meta = book_meta(project)

    if args.output:
        output = Path(args.output).expanduser()
        if not output.is_absolute():
            output = (Path.cwd() / output).resolve()
    else:
        output = project / f"{slugify(meta['title']) or 'novel'}.txt"
    ext = output.suffix.lower()
    if ext not in {".txt", ".epub"}:
        output = output.with_suffix(".txt")
        ext = ".txt"
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists() and not args.overwrite:
        raise SystemExit(f"Output exists: {output}. Pass --overwrite to replace it.")

    if ext == ".txt":
        export_txt(project, output, chapters, meta)
    else:
        export_epub(project, output, chapters, meta)
    exported_numbers = [n for n, _, _ in chapters]
    skipped = []
    if args.from_chapter is not None or args.to_chapter is not None:
        lo = args.from_chapter if args.from_chapter is not None else min(exported_numbers)
        hi = args.to_chapter if args.to_chapter is not None else max(exported_numbers)
        exported_set = set(exported_numbers)
        skipped = [n for n in range(lo, hi + 1) if n not in exported_set]
    print(json.dumps({
        "ok": True,
        "format": ext[1:],
        "output": str(output),
        "chapters": exported_numbers,
        "skipped_unfinished_or_missing": skipped,
        "bytes": output.stat().st_size,
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()

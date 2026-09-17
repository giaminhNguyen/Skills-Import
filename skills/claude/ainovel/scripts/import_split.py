#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from _common import atomic_write_json, atomic_write_text, resolve_project, utc_now

# Detect common English, Vietnamese and Chinese chapter headings at line starts.
HEADING_RE = re.compile(
    r"(?im)^(?:\s{0,3}#{1,6}\s*)?(?:"
    r"(?:chapter|chap\.?|chương|chuong)\s+(?:\d+|[ivxlcdm]+)(?:\s*[:.\-–—]\s*.*|\s+.*)?"
    r"|第[0-9零〇一二三四五六七八九十百千万两]+[章节回](?:\s*.*)?"
    r")\s*$"
)


def split_text(text: str) -> tuple[list[str], list[str], str]:
    matches = list(HEADING_RE.finditer(text))
    if not matches:
        return [text.strip()] if text.strip() else [], [], "single_block_no_heading_detected"
    chunks = []
    headings = []
    preface = text[:matches[0].start()].strip()
    for i, m in enumerate(matches):
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        chunk = text[m.start():end].strip()
        if chunk:
            chunks.append(chunk)
            headings.append(m.group(0).strip())
    if preface and chunks:
        chunks[0] = preface + "\n\n" + chunks[0]
    return chunks, headings, "heading_detected"


def main() -> None:
    p = argparse.ArgumentParser(description="Deterministically split imported novel text into chapter units.")
    p.add_argument("input")
    p.add_argument("--project")
    p.add_argument("--output-dir")
    p.add_argument("--clear", action="store_true")
    args = p.parse_args()

    src = Path(args.input).expanduser().resolve()
    if not src.exists():
        raise SystemExit(f"Input not found: {src}")
    if args.output_dir:
        out_dir = Path(args.output_dir).expanduser().resolve()
    else:
        project = resolve_project(args.project)
        out_dir = project / "imports" / "split"
    out_dir.mkdir(parents=True, exist_ok=True)
    if args.clear:
        for old in out_dir.glob("imported-*.md"):
            old.unlink()

    text = src.read_text(encoding="utf-8-sig")
    chunks, headings, method = split_text(text)
    if not chunks:
        raise SystemExit("Input contains no text")
    files = []
    for i, chunk in enumerate(chunks, 1):
        dest = out_dir / f"imported-{i:03d}.md"
        atomic_write_text(dest, chunk.rstrip() + "\n")
        files.append(str(dest))
    manifest = {
        "source": str(src),
        "created_at": utc_now(),
        "method": method,
        "chapter_count": len(chunks),
        "headings": headings,
        "files": files,
        "warning": "Semantic chapter-boundary refinement may still be needed." if method != "heading_detected" else None,
    }
    atomic_write_json(out_dir / "manifest.json", manifest)
    print(json.dumps({"ok": True, **manifest}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

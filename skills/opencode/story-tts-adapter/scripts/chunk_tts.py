#!/usr/bin/env python3
import argparse
import json
import re
from pathlib import Path

SENTENCE_RE = re.compile(r"(?<=[.!?…])\s+")
CLAUSE_RE = re.compile(r"(?<=[,;:])\s+")


def split_hard(text, limit):
    out = []
    s = text.strip()
    while len(s) > limit:
        cut = s.rfind(" ", 0, limit + 1)
        if cut < max(1, limit // 2):
            cut = limit
        out.append(s[:cut].strip())
        s = s[cut:].strip()
    if s:
        out.append(s)
    return out


def units_from_text(text, hard):
    units = []
    paragraphs = re.split(r"\n\s*\n+", text.strip())
    for p in paragraphs:
        p = re.sub(r"\s+", " ", p).strip()
        if not p:
            continue
        sentences = SENTENCE_RE.split(p)
        for s in sentences:
            s = s.strip()
            if not s:
                continue
            if len(s) <= hard:
                units.append(s)
                continue
            clauses = CLAUSE_RE.split(s)
            for c in clauses:
                c = c.strip()
                if not c:
                    continue
                if len(c) <= hard:
                    units.append(c)
                else:
                    units.extend(split_hard(c, hard))
    return units


def pack(units, preferred_max, hard):
    chunks = []
    current = ""
    for u in units:
        candidate = u if not current else current + " " + u
        if len(candidate) <= preferred_max:
            current = candidate
        elif current:
            chunks.append(current)
            current = u
        else:
            for part in split_hard(u, hard):
                if len(part) > preferred_max:
                    chunks.append(part)
                else:
                    current = part
    if current:
        chunks.append(current)
    return chunks


def merge_tiny(chunks, tiny, hard):
    if len(chunks) < 2:
        return chunks
    out = []
    for chunk in chunks:
        if out and len(chunk) < tiny and len(out[-1]) + 1 + len(chunk) <= hard:
            out[-1] += " " + chunk
        else:
            out.append(chunk)
    if len(out) > 1 and len(out[0]) < tiny and len(out[0]) + 1 + len(out[1]) <= hard:
        out[1] = out[0] + " " + out[1]
        out = out[1:]
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("story_tts")
    ap.add_argument("profile")
    ap.add_argument("output_dir")
    ap.add_argument("--source-story", default=None)
    args = ap.parse_args()

    story_path = Path(args.story_tts)
    profile_path = Path(args.profile)
    out_dir = Path(args.output_dir)
    chunk_dir = out_dir / "chunks"
    chunk_dir.mkdir(parents=True, exist_ok=True)

    text = story_path.read_text(encoding="utf-8").strip()
    profile = json.loads(profile_path.read_text(encoding="utf-8"))
    c = profile["chunking"]
    hard = int(c["hard_max_chars"])
    preferred_max = int(c["preferred_chunk_chars_max"])
    tiny = int(c["avoid_chunk_below_chars"])

    units = units_from_text(text, hard)
    chunks = merge_tiny(pack(units, preferred_max, hard), tiny, hard)

    records = []
    for i, chunk in enumerate(chunks, 1):
        if len(chunk) > hard:
            raise SystemExit(f"chunk {i} exceeds hard limit: {len(chunk)} > {hard}")
        name = f"{i:04d}.txt"
        (chunk_dir / name).write_text(chunk + "\n", encoding="utf-8")
        records.append({"index": i, "file": f"chunks/{name}", "chars": len(chunk)})

    manifest = {
        "profile_id": profile["profile_id"],
        "source_story": args.source_story,
        "adapted_story": str(story_path),
        "total_chars": len(text),
        "chunk_count": len(chunks),
        "hard_max_chars": hard,
        "chunks": records
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"profile_id": profile["profile_id"], "chunk_count": len(chunks), "total_chars": len(text)}, ensure_ascii=False))

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
import argparse
import json
from pathlib import Path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("output_dir")
    ap.add_argument("profile")
    args = ap.parse_args()

    out = Path(args.output_dir)
    profile = json.loads(Path(args.profile).read_text(encoding="utf-8"))
    hard = profile["chunking"]["hard_max_chars"]
    tiny = profile["chunking"]["avoid_chunk_below_chars"]
    manifest = json.loads((out / "manifest.json").read_text(encoding="utf-8"))
    errors = []
    warnings = []

    if manifest.get("profile_id") != profile.get("profile_id"):
        errors.append("manifest profile_id does not match selected profile")

    for rec in manifest.get("chunks", []):
        p = out / rec["file"]
        if not p.exists():
            errors.append(f"missing {rec['file']}")
            continue
        text = p.read_text(encoding="utf-8").strip()
        if len(text) > hard:
            errors.append(f"{rec['file']} exceeds hard limit: {len(text)} > {hard}")
        if len(text) < tiny:
            warnings.append(f"{rec['file']} is very short: {len(text)} chars")

    if errors:
        for e in errors:
            print("ERROR:", e)
        raise SystemExit(1)
    for w in warnings:
        print("WARN:", w)
    print(f"OK: {manifest.get('chunk_count', 0)} chunks")

if __name__ == "__main__":
    main()

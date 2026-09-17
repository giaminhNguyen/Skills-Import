#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from _common import chapter_files, jsonl_items, latest_jsonl, read_json, resolve_project, sha256_file

REQUIRED = [
    "book.md", "premise.md", "outline.json", "layered_outline.json", "characters.json", "world_rules.json",
    "meta/progress.json", "meta/book.json", "meta/compass.json", "meta/foreshadow.json",
    "meta/checkpoints.jsonl", "meta/chapter_hashes.json"
]
JSON_FILES = [
    "outline.json", "layered_outline.json", "characters.json", "world_rules.json", "meta/progress.json",
    "meta/book.json", "meta/compass.json", "meta/foreshadow.json", "meta/relationships.json",
    "meta/style_rules.json", "meta/user_directives.json", "meta/chapter_hashes.json",
    "meta/steer_queue.json", "meta/rewrite_queue.json"
]


def validate(project: Path) -> dict:
    errors: list[str] = []
    warnings: list[str] = []

    for rel in REQUIRED:
        if not (project / rel).exists():
            errors.append(f"missing required path: {rel}")
    for rel in JSON_FILES:
        p = project / rel
        if not p.exists():
            continue
        try:
            data = read_json(p, None)
            if data is None:
                errors.append(f"empty/invalid JSON: {rel}")
        except Exception as e:
            errors.append(f"invalid JSON {rel}: {e}")

    try:
        checkpoints = jsonl_items(project / "meta" / "checkpoints.jsonl")
    except Exception as e:
        errors.append(f"invalid checkpoints.jsonl: {e}")
        checkpoints = []
    latest = latest_jsonl(project / "meta" / "checkpoints.jsonl")
    if not checkpoints:
        warnings.append("no checkpoints recorded")
    else:
        seqs = [int(cp.get("seq", 0) or 0) for cp in checkpoints]
        expected_seqs = list(range(1, len(seqs) + 1))
        if seqs != expected_seqs:
            warnings.append(f"checkpoint sequence is not contiguous: {seqs}")
        for cp in checkpoints:
            scope = cp.get("scope") or {}
            if scope.get("kind") not in {"chapter", "arc", "volume", "global"}:
                warnings.append(f"checkpoint has invalid/missing scope: seq={cp.get('seq')}")

    chapters = chapter_files(project)
    nums = [int(p.stem) for p in chapters]
    if nums:
        expected = list(range(nums[0], nums[-1] + 1))
        if nums != expected:
            warnings.append(f"chapter numbering has gaps: {nums}")
        if nums[0] != 1:
            warnings.append(f"first committed chapter is {nums[0]}, not 1")

    for n, p in zip(nums, chapters):
        review = project / "reviews" / f"{n:03d}.json"
        summary = project / "summaries" / f"chapter-{n:03d}.json"
        if not review.exists():
            warnings.append(f"chapter {n} has no Editor review")
        if not summary.exists():
            warnings.append(f"chapter {n} has no chapter summary")

    ledger = read_json(project / "meta" / "chapter_hashes.json", {"hashes": {}}) or {"hashes": {}}
    hashes = ledger.get("hashes", {}) or {}
    for p in chapters:
        current = sha256_file(p)
        old = hashes.get(p.name)
        if old is None:
            warnings.append(f"untracked committed chapter hash: {p.name}")
        elif old != current:
            warnings.append(f"manual edit not synchronized: {p.name}")
    for name in hashes:
        if not (project / "chapters" / name).exists():
            warnings.append(f"hash ledger references missing chapter: {name}")

    progress = read_json(project / "meta" / "progress.json", {}) or {}
    if progress.get("foundation_complete") and not (project / "layered_outline.json").exists():
        errors.append("foundation_complete=true but layered_outline.json is missing")
    if progress.get("status") == "completed" and progress.get("current_step") != "completed":
        warnings.append("status=completed but current_step is not completed")

    if latest and latest.get("artifact"):
        art = Path(str(latest["artifact"]))
        if not art.is_absolute():
            art = project / art
        if not art.exists():
            warnings.append(f"latest checkpoint artifact is missing: {latest.get('artifact')}")
        elif art.is_file() and latest.get("digest"):
            current_digest = sha256_file(art)
            if current_digest != latest.get("digest"):
                warnings.append(f"latest checkpoint artifact digest mismatch: {latest.get('artifact')}")

    return {
        "ok": not errors,
        "project": str(project),
        "errors": errors,
        "warnings": warnings,
        "counts": {
            "chapters": len(chapters),
            "reviews": len(list((project / "reviews").glob("*.json"))),
            "chapter_summaries": len(list((project / "summaries").glob("chapter-*.json"))),
            "checkpoints": len(checkpoints),
        },
        "latest_checkpoint": latest,
    }


def main() -> None:
    p = argparse.ArgumentParser(description="Validate Ainovel project structure and deterministic state consistency.")
    p.add_argument("--project")
    p.add_argument("--strict", action="store_true", help="Treat warnings as failure exit status.")
    args = p.parse_args()
    project = resolve_project(args.project)
    result = validate(project)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["errors"] or (args.strict and result["warnings"]):
        raise SystemExit(1)


if __name__ == "__main__":
    main()

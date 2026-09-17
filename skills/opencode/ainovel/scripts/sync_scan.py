#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from _common import atomic_write_json, chapter_files, read_json, resolve_project, sha256_file, utc_now


def scan(project: Path) -> dict:
    ledger_path = project / "meta" / "chapter_hashes.json"
    ledger = read_json(ledger_path, {"version": 1, "hashes": {}}) or {"version": 1, "hashes": {}}
    old = ledger.get("hashes", {}) or {}
    current = {p.name: sha256_file(p) for p in chapter_files(project)}
    changed = []
    new = []
    deleted = []
    for name, h in current.items():
        if name not in old:
            new.append(name)
        elif old.get(name) != h:
            changed.append(name)
    for name in old:
        if name not in current:
            deleted.append(name)
    all_dirty = sorted(set(changed + new + deleted))
    earliest = None
    for name in all_dirty:
        try:
            n = int(Path(name).stem)
            earliest = n if earliest is None else min(earliest, n)
        except ValueError:
            pass
    return {
        "dirty": bool(all_dirty),
        "changed": sorted(changed),
        "new_untracked": sorted(new),
        "deleted": sorted(deleted),
        "earliest_changed_chapter": earliest,
        "current_hashes": current,
        "ledger_path": str(ledger_path),
    }


def main() -> None:
    p = argparse.ArgumentParser(description="Detect manual committed-chapter edits with SHA-256. No semantic rebuild is performed here.")
    p.add_argument("--project")
    g = p.add_mutually_exclusive_group()
    g.add_argument("--check", action="store_true", help="Report only (default behavior).")
    g.add_argument("--accept", action="store_true", help="Accept current hashes after semantic sync has completed.")
    args = p.parse_args()
    project = resolve_project(args.project)
    result = scan(project)
    if args.accept:
        atomic_write_json(project / "meta" / "chapter_hashes.json", {
            "version": 1,
            "hashes": result["current_hashes"],
            "updated_at": utc_now(),
        })
        result["accepted"] = True
    else:
        result["accepted"] = False
    result.pop("current_hashes", None)
    print(json.dumps({"ok": True, **result}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

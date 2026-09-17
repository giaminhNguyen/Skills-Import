#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from _common import atomic_write_json, read_json, resolve_project


def validate(data: dict) -> list[str]:
    errors = []
    if not isinstance(data, dict):
        return ["profile must be a JSON object"]
    for key in ["prose_rules", "dialogue_rules", "avoid"]:
        if key in data and not isinstance(data[key], list):
            errors.append(f"{key} must be a list")
    if not any(k in data for k in ["prose_rules", "dialogue_rules", "sentence_rhythm", "diction", "pov"]):
        errors.append("profile contains no recognizable style fields")
    return errors


def main() -> None:
    p = argparse.ArgumentParser(description="Validate/import an abstract Ainovel style profile JSON.")
    p.add_argument("file")
    p.add_argument("--project")
    p.add_argument("--check", action="store_true")
    args = p.parse_args()
    src = Path(args.file).expanduser().resolve()
    data = read_json(src, None)
    errors = validate(data)
    if errors:
        raise SystemExit("; ".join(errors))
    if args.check:
        print(json.dumps({"ok": True, "valid": True, "source": str(src)}, ensure_ascii=False))
        return
    project = resolve_project(args.project)
    data = dict(data)
    data.setdefault("version", 1)
    data["source"] = f"imported:{src.name}"
    dest = project / "meta" / "style_rules.json"
    atomic_write_json(dest, data)
    print(json.dumps({"ok": True, "valid": True, "output": str(dest)}, ensure_ascii=False))


if __name__ == "__main__":
    main()

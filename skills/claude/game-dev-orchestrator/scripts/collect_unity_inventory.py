#!/usr/bin/env python3
"""Collect a read-only structural inventory of a Unity project.

The script never writes into the Unity project. It writes one JSON snapshot into
an explicitly separate output directory.
"""

from __future__ import annotations

import argparse
import json
import os
from collections import Counter
from pathlib import Path
from typing import Any


def is_within(child: Path, parent: Path) -> bool:
    try:
        child.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def read_text(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def project_relative(path: Path, project: Path) -> str:
    try:
        return path.relative_to(project).as_posix()
    except ValueError:
        return path.as_posix()


def collect(project: Path) -> dict[str, Any]:
    assets = project / "Assets"
    packages = project / "Packages"
    settings = project / "ProjectSettings"

    missing = [str(p.name) for p in (assets, packages, settings) if not p.is_dir()]
    if missing:
        raise ValueError(f"Not a Unity project root; missing: {', '.join(missing)}")

    version_text = read_text(settings / "ProjectVersion.txt") or ""
    unity_version = None
    for line in version_text.splitlines():
        if line.startswith("m_EditorVersion:"):
            unity_version = line.split(":", 1)[1].strip()
            break

    manifest = load_json(packages / "manifest.json") or {}
    dependencies = manifest.get("dependencies", {}) if isinstance(manifest, dict) else {}

    cs_files = list(assets.rglob("*.cs"))
    asmdefs = list(assets.rglob("*.asmdef"))
    scenes = list(assets.rglob("*.unity"))

    top_groups: Counter[str] = Counter()
    for path in cs_files:
        rel = path.relative_to(assets)
        group = rel.parts[0] if len(rel.parts) > 1 else "_AssetsRoot"
        top_groups[group] += 1

    asmdef_items: list[dict[str, Any]] = []
    for path in asmdefs:
        data = load_json(path)
        item = {
            "path": project_relative(path, project),
            "name": data.get("name") if isinstance(data, dict) else None,
            "references": data.get("references", []) if isinstance(data, dict) else [],
        }
        asmdef_items.append(item)

    indicators = {}
    indicator_names = [
        "Editor",
        "Tests",
        "Resources",
        "StreamingAssets",
        "AddressableAssetsData",
        "Plugins",
    ]
    for name in indicator_names:
        matches = [p for p in assets.rglob(name) if p.is_dir()]
        indicators[name] = [project_relative(p, project) for p in matches[:50]]

    return {
        "project_root": str(project.resolve()),
        "unity_version": unity_version,
        "packages": dependencies,
        "counts": {
            "csharp_files": len(cs_files),
            "asmdef_files": len(asmdefs),
            "scene_files": len(scenes),
        },
        "csharp_by_assets_top_folder": dict(sorted(top_groups.items())),
        "asmdefs": sorted(asmdef_items, key=lambda x: x["path"]),
        "scenes": sorted(project_relative(p, project) for p in scenes),
        "indicators": indicators,
        "assets_top_level": sorted(p.name for p in assets.iterdir()),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", required=True, help="Unity project root")
    parser.add_argument("--output", required=True, help="Knowledge output directory outside project")
    args = parser.parse_args()

    project = Path(os.path.expanduser(args.project)).resolve()
    output = Path(os.path.expanduser(args.output)).resolve()

    if is_within(output, project):
        raise SystemExit("Refusing to write inventory inside the Unity project. Choose an external GameAI output directory.")

    snapshot = collect(project)
    output.mkdir(parents=True, exist_ok=True)
    out_path = output / "inventory-snapshot.json"
    out_path.write_text(json.dumps(snapshot, indent=2, ensure_ascii=False), encoding="utf-8")
    print(out_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

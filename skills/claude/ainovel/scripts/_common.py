#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import os
import re
import tempfile
import unicodedata
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path, default: Any = None) -> Any:
    if not path.exists():
        return default
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def atomic_write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=f".{path.name}.", dir=str(path.parent))
    tmp_path = Path(tmp)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as f:
            f.write(text)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_path, path)
    finally:
        if tmp_path.exists():
            tmp_path.unlink(missing_ok=True)


def atomic_write_json(path: Path, data: Any, *, indent: int = 2) -> None:
    atomic_write_text(path, json.dumps(data, ensure_ascii=False, indent=indent) + "\n")


def append_jsonl(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    line = json.dumps(data, ensure_ascii=False, separators=(",", ":")) + "\n"
    with path.open("a", encoding="utf-8", newline="\n") as f:
        f.write(line)
        f.flush()
        os.fsync(f.fileno())


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def slugify(text: str, fallback: str = "novel") -> str:
    norm = unicodedata.normalize("NFKD", text)
    ascii_text = norm.encode("ascii", "ignore").decode("ascii").lower()
    ascii_text = re.sub(r"[^a-z0-9]+", "-", ascii_text).strip("-")
    return (ascii_text[:60].strip("-") or fallback)


def chapter_number(path: Path) -> int | None:
    m = re.match(r"^(\d+)", path.stem)
    return int(m.group(1)) if m else None


def chapter_files(project: Path) -> list[Path]:
    paths = []
    for p in (project / "chapters").glob("*.md"):
        n = chapter_number(p)
        if n is not None:
            paths.append((n, p))
    return [p for _, p in sorted(paths, key=lambda x: x[0])]


def find_workspace_marker(start: Path | None = None) -> Path | None:
    cur = (start or Path.cwd()).resolve()
    for candidate in [cur, *cur.parents]:
        marker = candidate / ".ainovel" / "active_project"
        if marker.exists():
            return marker
    return None


def resolve_project(project: str | Path | None = None) -> Path:
    if project:
        p = Path(project).expanduser().resolve()
    elif os.environ.get("AINOVEL_PROJECT"):
        p = Path(os.environ["AINOVEL_PROJECT"]).expanduser().resolve()
    else:
        marker = find_workspace_marker()
        if not marker:
            raise SystemExit("No active Ainovel project. Pass --project or run state.py init.")
        raw = marker.read_text(encoding="utf-8").strip()
        p = Path(raw).expanduser()
        if not p.is_absolute():
            p = (marker.parent.parent / p).resolve()
    if not p.exists():
        raise SystemExit(f"Ainovel project does not exist: {p}")
    return p


def write_active_project(workspace: Path, project: Path) -> None:
    marker = workspace / ".ainovel" / "active_project"
    try:
        value = str(project.relative_to(workspace))
    except ValueError:
        value = str(project)
    atomic_write_text(marker, value + "\n")


def latest_jsonl(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    last = None
    with path.open("r", encoding="utf-8") as f:
        for raw in f:
            raw = raw.strip()
            if not raw:
                continue
            try:
                obj = json.loads(raw)
            except json.JSONDecodeError:
                continue
            if isinstance(obj, dict):
                last = obj
    return last


def jsonl_items(path: Path) -> list[Any]:
    out = []
    if not path.exists():
        return out
    with path.open("r", encoding="utf-8") as f:
        for raw in f:
            raw = raw.strip()
            if raw:
                out.append(json.loads(raw))
    return out


def ensure_project_dirs(project: Path) -> None:
    for rel in [
        "chapters", "drafts", "reviews", "summaries", "imports", "exports", "rules",
        "meta/arbiter", "meta/context"
    ]:
        (project / rel).mkdir(parents=True, exist_ok=True)


def relative_or_abs(path: Path, base: Path) -> str:
    try:
        return str(path.resolve().relative_to(base.resolve())).replace("\\", "/")
    except ValueError:
        return str(path.resolve())


def dump_compact(data: Any) -> str:
    return json.dumps(data, ensure_ascii=False, separators=(",", ":"))


def file_text(path: Path, default: str = "") -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return default


def read_many_markdown(paths: Iterable[Path]) -> str:
    blocks = []
    for p in paths:
        if p.exists():
            blocks.append(f"## {p.name}\n\n{p.read_text(encoding='utf-8').strip()}")
    return "\n\n".join(blocks)

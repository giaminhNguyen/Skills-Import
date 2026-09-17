#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from _common import atomic_write_json, atomic_write_text, file_text, read_json, resolve_project, utc_now


def truncate(text: str, limit: int) -> str:
    text = text.strip()
    if len(text) <= limit:
        return text
    if limit < 200:
        return text[:limit]
    head = int(limit * 0.72)
    tail = limit - head - 40
    return text[:head].rstrip() + "\n…[deterministic trim]…\n" + text[-tail:].lstrip()


def pretty_json(data: Any) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2)


def add_section(parts: list[tuple[str, str, int]], title: str, content: str, priority: int) -> None:
    content = content.strip()
    if content:
        parts.append((title, content, priority))


def latest_matching(directory: Path, pattern: str) -> Path | None:
    items = sorted(directory.glob(pattern))
    return items[-1] if items else None


def plan_for(project: Path, chapter: int) -> dict[str, Any]:
    p = project / "drafts" / f"{chapter:03d}.plan.json"
    if p.exists():
        return read_json(p, {}) or {}
    outline = read_json(project / "outline.json", {}) or {}
    for item in outline.get("chapters", []):
        if int(item.get("chapter", -1)) == chapter:
            return item
    return {}


def summary_for(project: Path, chapter: int) -> dict[str, Any] | None:
    p = project / "summaries" / f"chapter-{chapter:03d}.json"
    return read_json(p, None)


def related_old_summaries(project: Path, plan: dict[str, Any], recent: set[int], max_items: int = 6) -> list[tuple[int, dict[str, Any]]]:
    wanted = set()
    for n in plan.get("relevant_chapters", []) or []:
        try:
            wanted.add(int(n))
        except (TypeError, ValueError):
            pass
    tokens = set()
    for key in ["character_ids", "world_rule_ids", "relationship_ids"]:
        for x in plan.get(key, []) or []:
            if x:
                tokens.add(str(x))
    fs = plan.get("foreshadow", {}) or {}
    if isinstance(fs, dict):
        for values in fs.values():
            if isinstance(values, list):
                tokens.update(str(x) for x in values if x)
    out: list[tuple[int, dict[str, Any]]] = []
    candidates = sorted((project / "summaries").glob("chapter-*.json"))
    for p in candidates:
        try:
            n = int(p.stem.split("-")[-1])
        except ValueError:
            continue
        if n in recent:
            continue
        data = read_json(p, {}) or {}
        blob = json.dumps(data, ensure_ascii=False)
        if n in wanted or any(t in blob for t in tokens):
            out.append((n, data))
    out.sort(key=lambda item: (item[0] not in wanted, -item[0]))
    return out[:max_items]


def build(project: Path, chapter: int, budget: int) -> tuple[str, dict[str, Any]]:
    progress = read_json(project / "meta" / "progress.json", {}) or {}
    config = read_json(project / "meta" / "project_config.json", {}) or {}
    recent_window = int(config.get("recent_chapter_window", 3) or 3)
    plan = plan_for(project, chapter)

    parts: list[tuple[str, str, int]] = []
    add_section(parts, "Current task", pretty_json({
        "chapter": chapter,
        "step": progress.get("current_step"),
        "volume": progress.get("current_volume"),
        "arc": progress.get("current_arc"),
        "status": progress.get("status"),
    }), 0)
    add_section(parts, "Active chapter contract", pretty_json(plan), 0)
    add_section(parts, "Durable user directives", pretty_json(read_json(project / "meta" / "user_directives.json", {})), 0)
    add_section(parts, "Hard/soft world rules", pretty_json(read_json(project / "world_rules.json", {})), 1)
    add_section(parts, "Character ledger", pretty_json(read_json(project / "characters.json", {})), 1)
    add_section(parts, "Relationships", pretty_json(read_json(project / "meta" / "relationships.json", {})), 1)
    add_section(parts, "Open foreshadow", pretty_json(read_json(project / "meta" / "foreshadow.json", {})), 1)
    add_section(parts, "Compass", pretty_json(read_json(project / "meta" / "compass.json", {})), 1)
    add_section(parts, "Premise", file_text(project / "premise.md"), 2)

    summaries_dir = project / "summaries"
    arc = latest_matching(summaries_dir, "arc-*.json")
    vol = latest_matching(summaries_dir, "vol-*.json")
    if arc:
        add_section(parts, "Latest arc summary", pretty_json(read_json(arc, {})), 2)
    if vol:
        add_section(parts, "Latest volume summary", pretty_json(read_json(vol, {})), 3)

    recent_nums = set(range(max(1, chapter - recent_window), chapter))
    recent_blocks = []
    for n in sorted(recent_nums):
        data = summary_for(project, n)
        if data:
            recent_blocks.append(f"### Chapter {n}\n{pretty_json(data)}")
    if recent_blocks:
        add_section(parts, "Recent chapter summaries", "\n\n".join(recent_blocks), 1)

    related = related_old_summaries(project, plan, recent_nums)
    if related:
        blocks = [f"### Chapter {n}\n{pretty_json(data)}" for n, data in related]
        add_section(parts, "Relevant older summaries", "\n\n".join(blocks), 3)

    add_section(parts, "Style rules", pretty_json(read_json(project / "meta" / "style_rules.json", {})), 2)
    full_summary = file_text(project / "meta" / "context" / "full-summary.md")
    if full_summary:
        add_section(parts, "FullSummary restore note", full_summary, 2)

    # Priority-aware deterministic fitting. Core sections receive larger caps.
    caps = {0: 12000, 1: 8000, 2: 5000, 3: 3500}
    rendered = ["# Ainovel Restore Pack", f"Generated: {utc_now()}", f"Project: {project}"]
    used = sum(len(x) for x in rendered) + 16
    included = []
    trimmed = []
    for title, content, priority in sorted(parts, key=lambda x: x[2]):
        remaining = max(0, budget - used - len(title) - 12)
        if remaining <= 120:
            trimmed.append(title)
            continue
        cap = min(caps.get(priority, 3000), remaining)
        body = truncate(content, cap)
        section = f"\n\n## {title}\n\n{body}"
        if used + len(section) > budget:
            section = truncate(section, max(120, budget - used))
            trimmed.append(title)
        rendered.append(section)
        used += len(section)
        included.append(title)
        if used >= budget:
            break

    text = "".join(rendered).rstrip() + "\n"
    manifest = {
        "generated_at": utc_now(),
        "chapter": chapter,
        "budget_chars": budget,
        "actual_chars": len(text),
        "included_sections": included,
        "trimmed_or_omitted_sections": trimmed + [t for t, _, _ in parts if t not in included and t not in trimmed],
        "plan_source": "draft" if (project / "drafts" / f"{chapter:03d}.plan.json").exists() else "outline",
        "recent_window": recent_window,
        "related_old_chapters": [n for n, _ in related],
    }
    return text, manifest


def main() -> None:
    p = argparse.ArgumentParser(description="Build deterministic file-based Ainovel restore/context packs.")
    sub = p.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build")
    b.add_argument("--project")
    b.add_argument("--chapter", type=int)
    b.add_argument("--budget-chars", type=int)
    args = p.parse_args()

    project = resolve_project(args.project)
    progress = read_json(project / "meta" / "progress.json", {}) or {}
    chapter = args.chapter or int(progress.get("current_chapter", 1))
    budget = args.budget_chars or int(progress.get("context_budget_chars", 45000))
    text, manifest = build(project, chapter, budget)
    out = project / "meta" / "context" / "current.md"
    atomic_write_text(out, text)
    atomic_write_json(project / "meta" / "context" / "manifest.json", manifest)
    print(json.dumps({"ok": True, "path": str(out), **manifest}, ensure_ascii=False))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import uuid
from pathlib import Path

from _common import (
    append_jsonl,
    atomic_write_json,
    atomic_write_text,
    chapter_files,
    latest_jsonl,
    read_json,
    relative_or_abs,
    resolve_project,
    sha256_file,
    slugify,
    utc_now,
    write_active_project,
    ensure_project_dirs,
)


def checkpoint(project: Path, event: str, next_step: str, chapter: int | None = None,
               artifact: str | None = None, details: dict | None = None,
               advance_chapter: bool = False, scope_kind: str | None = None,
               volume: int | None = None, arc: int | None = None) -> dict:
    latest = latest_jsonl(project / "meta" / "checkpoints.jsonl") or {}
    seq = int(latest.get("seq", 0) or 0) + 1
    progress_path = project / "meta" / "progress.json"
    progress = read_json(progress_path, {}) or {}
    if scope_kind is None:
        scope_kind = "chapter" if chapter is not None else "global"
    scope = {"kind": scope_kind}
    if scope_kind == "chapter":
        scope["chapter"] = int(chapter or progress.get("current_chapter", 1))
    elif scope_kind == "arc":
        scope["volume"] = int(volume or progress.get("current_volume", 1))
        raw_arc = arc if arc is not None else progress.get("current_arc", 1)
        try:
            scope["arc"] = int(str(raw_arc).split(".")[-1])
        except ValueError:
            scope["arc"] = 1
    elif scope_kind == "volume":
        scope["volume"] = int(volume or progress.get("current_volume", 1))

    digest = None
    if artifact:
        ap = Path(artifact)
        if not ap.is_absolute():
            ap = project / artifact
        if ap.exists() and ap.is_file():
            digest = sha256_file(ap)

    now = utc_now()
    cp = {
        "id": f"cp-{uuid.uuid4().hex[:12]}",
        "seq": seq,
        "scope": scope,
        "step": event,
        "artifact": artifact,
        "digest": digest,
        "occurred_at": now,
        "next_step": next_step,
        "details": details or {},
    }
    append_jsonl(project / "meta" / "checkpoints.jsonl", cp)
    progress["last_completed_step"] = event
    progress["current_step"] = next_step
    if chapter is not None:
        progress["current_chapter"] = int(chapter) + (1 if advance_chapter else 0)
    if event == "foundation_saved":
        progress["foundation_complete"] = True
        progress["flow"] = "writing"
        if progress.get("status") == "initializing":
            progress["status"] = "writing"
    if next_step == "completed" or event == "completed":
        progress["status"] = "completed"
        progress["flow"] = "complete"
    progress["updated_at"] = now
    atomic_write_json(progress_path, progress)
    return cp


def cmd_init(args: argparse.Namespace) -> None:
    workspace = Path(args.workspace).expanduser().resolve()
    workspace.mkdir(parents=True, exist_ok=True)
    fallback = f"novel-{utc_now()[:10].replace('-', '')}"
    slug = slugify(args.slug or args.idea[:60], fallback=fallback)
    project = workspace / "novels" / slug / "output" / "novel"
    if project.exists() and any(project.iterdir()) and not args.force:
        raise SystemExit(f"Project already exists and is not empty: {project}. Use --force only intentionally.")
    ensure_project_dirs(project)

    project_id = str(uuid.uuid4())
    progress = {
        "schema_version": 1,
        "project_id": project_id,
        "slug": slug,
        "status": "initializing",
        "flow": "planning",
        "foundation_complete": False,
        "current_volume": 1,
        "current_arc": "1.1",
        "current_chapter": 1,
        "current_step": "foundation",
        "last_completed_step": None,
        "review_mode": bool(args.review_mode),
        "review_permits": 0,
        "max_review_retries": args.max_review_retries,
        "target_chapters": args.target_chapters,
        "language": args.language,
        "chapter_word_target": args.chapter_word_target,
        "context_budget_chars": args.context_budget_chars,
        "created_at": utc_now(),
        "updated_at": utc_now(),
    }
    config = {
        "schema_version": 1,
        "language": args.language,
        "target_chapters": args.target_chapters,
        "chapter_word_target": args.chapter_word_target,
        "review_mode": bool(args.review_mode),
        "max_review_retries": args.max_review_retries,
        "context_budget_chars": args.context_budget_chars,
        "recent_chapter_window": 3,
        "writing_preferences": {},
    }
    atomic_write_json(project / "meta" / "progress.json", progress)
    atomic_write_json(project / "meta" / "project_config.json", config)
    atomic_write_json(project / "meta" / "book.json", {
        "title": "", "logline": "", "summary": "", "genre": [],
        "language": args.language, "status": "planning"
    })
    atomic_write_json(project / "meta" / "compass.json", {
        "version": 1, "ending_direction": "", "core_promises": [], "non_negotiables": [],
        "character_destinations": [], "volume_milestones": [], "open_questions": []
    })
    atomic_write_json(project / "meta" / "foreshadow.json", {"version": 1, "items": []})
    atomic_write_json(project / "meta" / "relationships.json", {"version": 1, "relationships": []})
    atomic_write_json(project / "meta" / "style_rules.json", {"version": 1, "source": "default", "prose_rules": [], "dialogue_rules": [], "avoid": []})
    atomic_write_json(project / "meta" / "user_directives.json", {"version": 1, "directives": []})
    atomic_write_json(project / "meta" / "chapter_hashes.json", {"version": 1, "hashes": {}, "updated_at": utc_now()})
    atomic_write_json(project / "meta" / "steer_queue.json", {"version": 1, "items": []})
    atomic_write_json(project / "meta" / "rewrite_queue.json", {"version": 1, "items": []})
    atomic_write_json(project / "characters.json", {"version": 1, "characters": []})
    atomic_write_json(project / "world_rules.json", {"version": 1, "rules": []})
    atomic_write_json(project / "outline.json", {"arc_id": "v01-a01", "chapters": []})
    atomic_write_json(project / "layered_outline.json", {"version": 1, "current_volume": 1, "current_arc": "1.1", "volumes": []})
    atomic_write_text(project / "premise.md", f"# Initial Idea\n\n{args.idea.strip()}\n")
    atomic_write_text(project / "book.md", "# Untitled\n\nFoundation not yet generated.\n")
    (project / "timeline.jsonl").touch(exist_ok=True)
    (project / "meta" / "checkpoints.jsonl").touch(exist_ok=True)
    write_active_project(workspace, project)
    cp = checkpoint(project, "project_initialized", "foundation", details={"idea": args.idea})
    print(json.dumps({"ok": True, "project": str(project), "slug": slug, "checkpoint": cp["id"]}, ensure_ascii=False))


def cmd_status(args: argparse.Namespace) -> None:
    project = resolve_project(args.project)
    progress = read_json(project / "meta" / "progress.json", {}) or {}
    latest = latest_jsonl(project / "meta" / "checkpoints.jsonl")
    rewrites = read_json(project / "meta" / "rewrite_queue.json", {"items": []}) or {"items": []}
    steer = read_json(project / "meta" / "steer_queue.json", {"items": []}) or {"items": []}
    out = {
        "project": str(project),
        "progress": progress,
        "latest_checkpoint": latest,
        "pending_rewrites": sum(1 for x in rewrites.get("items", []) if x.get("status", "pending") == "pending"),
        "pending_steer": sum(1 for x in steer.get("items", []) if x.get("status", "pending") == "pending"),
        "committed_chapters": len(chapter_files(project)),
    }
    print(json.dumps(out, ensure_ascii=False, indent=2))


def cmd_resume(args: argparse.Namespace) -> None:
    project = resolve_project(args.project)
    progress = read_json(project / "meta" / "progress.json", {}) or {}
    latest = latest_jsonl(project / "meta" / "checkpoints.jsonl")
    out = {
        "project": str(project),
        "status": progress.get("status"),
        "chapter": progress.get("current_chapter"),
        "step": progress.get("current_step"),
        "latest_checkpoint": latest,
        "resume_step": (latest or {}).get("next_step") or progress.get("current_step") or "foundation",
        "review_mode": bool(progress.get("review_mode")),
        "review_permits": int(progress.get("review_permits", 0)),
    }
    print(json.dumps(out, ensure_ascii=False, indent=2))


def cmd_checkpoint(args: argparse.Namespace) -> None:
    project = resolve_project(args.project)
    details = json.loads(args.details) if args.details else {}
    cp = checkpoint(project, args.event, args.next_step, args.chapter, args.artifact, details, args.advance_chapter, args.scope_kind, args.volume, args.arc)
    print(json.dumps({"ok": True, "checkpoint": cp}, ensure_ascii=False))


def cmd_set_step(args: argparse.Namespace) -> None:
    project = resolve_project(args.project)
    path = project / "meta" / "progress.json"
    progress = read_json(path, {}) or {}
    progress["current_step"] = args.step
    if args.chapter is not None:
        progress["current_chapter"] = args.chapter
    if args.status:
        progress["status"] = args.status
    progress["updated_at"] = utc_now()
    atomic_write_json(path, progress)
    print(json.dumps({"ok": True, "current_step": args.step, "chapter": progress.get("current_chapter"), "status": progress.get("status")}, ensure_ascii=False))


def cmd_review(args: argparse.Namespace) -> None:
    project = resolve_project(args.project)
    enabled = args.mode == "on"
    path = project / "meta" / "progress.json"
    progress = read_json(path, {}) or {}
    progress["review_mode"] = enabled
    if not enabled:
        progress["review_permits"] = 0
        if progress.get("status") == "paused_review":
            progress["status"] = "writing"
    progress["updated_at"] = utc_now()
    atomic_write_json(path, progress)
    cfg_path = project / "meta" / "project_config.json"
    cfg = read_json(cfg_path, {}) or {}
    cfg["review_mode"] = enabled
    atomic_write_json(cfg_path, cfg)
    print(json.dumps({"ok": True, "review_mode": enabled}, ensure_ascii=False))


def cmd_next(args: argparse.Namespace) -> None:
    project = resolve_project(args.project)
    path = project / "meta" / "progress.json"
    progress = read_json(path, {}) or {}
    if not progress.get("review_mode"):
        print(json.dumps({"ok": True, "review_mode": False, "message": "Review mode is off; no permit is required."}, ensure_ascii=False))
        return
    progress["review_permits"] = int(progress.get("review_permits", 0)) + 1
    if progress.get("status") == "paused_review":
        progress["status"] = "writing"
    progress["updated_at"] = utc_now()
    atomic_write_json(path, progress)
    print(json.dumps({"ok": True, "review_permits": progress["review_permits"]}, ensure_ascii=False))


def cmd_consume_permit(args: argparse.Namespace) -> None:
    project = resolve_project(args.project)
    path = project / "meta" / "progress.json"
    progress = read_json(path, {}) or {}
    if not progress.get("review_mode"):
        print(json.dumps({"ok": True, "consumed": False, "reason": "review_mode_off"}))
        return
    permits = int(progress.get("review_permits", 0))
    if permits <= 0:
        progress["status"] = "paused_review"
        progress["updated_at"] = utc_now()
        atomic_write_json(path, progress)
        raise SystemExit("Review mode is on and no /next permit is available.")
    progress["review_permits"] = permits - 1
    progress["status"] = "writing"
    progress["updated_at"] = utc_now()
    atomic_write_json(path, progress)
    print(json.dumps({"ok": True, "consumed": True, "remaining": permits - 1}))


def cmd_hash_chapter(args: argparse.Namespace) -> None:
    project = resolve_project(args.project)
    chapter = int(args.chapter)
    path = project / "chapters" / f"{chapter:03d}.md"
    if not path.exists():
        raise SystemExit(f"Chapter not found: {path}")
    ledger_path = project / "meta" / "chapter_hashes.json"
    ledger = read_json(ledger_path, {"version": 1, "hashes": {}}) or {"version": 1, "hashes": {}}
    hashes = ledger.setdefault("hashes", {})
    hashes[path.name] = sha256_file(path)
    ledger["updated_at"] = utc_now()
    atomic_write_json(ledger_path, ledger)
    print(json.dumps({"ok": True, "chapter": chapter, "hash": hashes[path.name]}))


def cmd_steer_add(args: argparse.Namespace) -> None:
    project = resolve_project(args.project)
    path = project / "meta" / "steer_queue.json"
    data = read_json(path, {"version": 1, "items": []}) or {"version": 1, "items": []}
    item = {
        "id": f"st-{uuid.uuid4().hex[:10]}",
        "at": utc_now(),
        "chapter": args.chapter,
        "text": args.text,
        "status": "pending",
        "decision_file": None,
    }
    data.setdefault("items", []).append(item)
    atomic_write_json(path, data)
    print(json.dumps({"ok": True, "steer": item}, ensure_ascii=False))


def cmd_steer_resolve(args: argparse.Namespace) -> None:
    project = resolve_project(args.project)
    path = project / "meta" / "steer_queue.json"
    data = read_json(path, {"version": 1, "items": []}) or {"version": 1, "items": []}
    found = None
    for item in data.get("items", []):
        if item.get("id") == args.id:
            item["status"] = "resolved"
            item["resolved_at"] = utc_now()
            item["decision_file"] = args.decision_file
            found = item
            break
    if not found:
        raise SystemExit(f"Steer item not found: {args.id}")
    atomic_write_json(path, data)
    print(json.dumps({"ok": True, "steer": found}, ensure_ascii=False))


def cmd_directive_add(args: argparse.Namespace) -> None:
    project = resolve_project(args.project)
    path = project / "meta" / "user_directives.json"
    data = read_json(path, {"version": 1, "directives": []}) or {"version": 1, "directives": []}
    progress = read_json(project / "meta" / "progress.json", {}) or {}
    item = {
        "id": f"dir-{uuid.uuid4().hex[:10]}",
        "at": utc_now(),
        "from_chapter": args.from_chapter or progress.get("current_chapter", 1),
        "text": args.text,
        "active": True,
        "source": args.source,
    }
    data.setdefault("directives", []).append(item)
    atomic_write_json(path, data)
    print(json.dumps({"ok": True, "directive": item}, ensure_ascii=False))


def cmd_rewrite_resolve(args: argparse.Namespace) -> None:
    project = resolve_project(args.project)
    path = project / "meta" / "rewrite_queue.json"
    data = read_json(path, {"version": 1, "items": []}) or {"version": 1, "items": []}
    resolved = []
    for item in data.get("items", []):
        if item.get("status", "pending") != "pending":
            continue
        if args.id and item.get("id") != args.id:
            continue
        if args.chapter is not None and item.get("chapter") != args.chapter:
            continue
        item["status"] = "resolved"
        item["resolved_at"] = utc_now()
        resolved.append(item.get("id"))
    if not resolved:
        raise SystemExit("No matching pending rewrite item")
    atomic_write_json(path, data)
    print(json.dumps({"ok": True, "resolved": resolved}, ensure_ascii=False))


def cmd_config(args: argparse.Namespace) -> None:
    project = resolve_project(args.project)
    cfg_path = project / "meta" / "project_config.json"
    progress_path = project / "meta" / "progress.json"
    cfg = read_json(cfg_path, {}) or {}
    progress = read_json(progress_path, {}) or {}
    updates = {
        "language": args.language,
        "target_chapters": args.target_chapters,
        "chapter_word_target": args.chapter_word_target,
        "context_budget_chars": args.context_budget_chars,
        "recent_chapter_window": args.recent_chapter_window,
        "max_review_retries": args.max_review_retries,
    }
    changed = {}
    for key, value in updates.items():
        if value is not None:
            cfg[key] = value
            if key in progress:
                progress[key] = value
            changed[key] = value
    if args.show or not changed:
        print(json.dumps({"ok": True, "config": cfg}, ensure_ascii=False, indent=2))
        return
    progress["updated_at"] = utc_now()
    atomic_write_json(cfg_path, cfg)
    atomic_write_json(progress_path, progress)
    print(json.dumps({"ok": True, "changed": changed, "config": cfg}, ensure_ascii=False, indent=2))


def cmd_complete(args: argparse.Namespace) -> None:
    project = resolve_project(args.project)
    cp = checkpoint(project, "completed", "completed", details={"reason": args.reason or ""})
    print(json.dumps({"ok": True, "checkpoint": cp["id"], "status": "completed"}, ensure_ascii=False))


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Deterministic Ainovel state/checkpoint manager (no LLM/network).")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("init")
    s.add_argument("--idea", required=True)
    s.add_argument("--workspace", default=".")
    s.add_argument("--slug")
    s.add_argument("--target-chapters", type=int)
    s.add_argument("--language", default="vi")
    s.add_argument("--chapter-word-target", type=int, default=2500)
    s.add_argument("--context-budget-chars", type=int, default=45000)
    s.add_argument("--max-review-retries", type=int, default=2)
    s.add_argument("--review-mode", action="store_true")
    s.add_argument("--force", action="store_true")
    s.set_defaults(func=cmd_init)

    for name, func in [("status", cmd_status), ("resume", cmd_resume)]:
        s = sub.add_parser(name)
        s.add_argument("--project")
        s.set_defaults(func=func)

    s = sub.add_parser("checkpoint")
    s.add_argument("--project")
    s.add_argument("--event", required=True)
    s.add_argument("--next-step", required=True)
    s.add_argument("--chapter", type=int)
    s.add_argument("--artifact")
    s.add_argument("--details", help="JSON object")
    s.add_argument("--advance-chapter", action="store_true")
    s.add_argument("--scope-kind", choices=["chapter", "arc", "volume", "global"])
    s.add_argument("--volume", type=int)
    s.add_argument("--arc", type=int)
    s.set_defaults(func=cmd_checkpoint)

    s = sub.add_parser("set-step")
    s.add_argument("--project")
    s.add_argument("--step", required=True)
    s.add_argument("--chapter", type=int)
    s.add_argument("--status")
    s.set_defaults(func=cmd_set_step)

    s = sub.add_parser("review")
    s.add_argument("mode", choices=["on", "off"])
    s.add_argument("--project")
    s.set_defaults(func=cmd_review)

    s = sub.add_parser("next")
    s.add_argument("--project")
    s.set_defaults(func=cmd_next)

    s = sub.add_parser("consume-permit")
    s.add_argument("--project")
    s.set_defaults(func=cmd_consume_permit)

    s = sub.add_parser("hash-chapter")
    s.add_argument("--project")
    s.add_argument("--chapter", type=int, required=True)
    s.set_defaults(func=cmd_hash_chapter)

    s = sub.add_parser("steer-add")
    s.add_argument("text")
    s.add_argument("--project")
    s.add_argument("--chapter", type=int)
    s.set_defaults(func=cmd_steer_add)

    s = sub.add_parser("steer-resolve")
    s.add_argument("--id", required=True)
    s.add_argument("--decision-file", required=True)
    s.add_argument("--project")
    s.set_defaults(func=cmd_steer_resolve)

    s = sub.add_parser("directive-add")
    s.add_argument("text")
    s.add_argument("--project")
    s.add_argument("--from-chapter", type=int)
    s.add_argument("--source", default="user")
    s.set_defaults(func=cmd_directive_add)

    s = sub.add_parser("rewrite-resolve")
    s.add_argument("--project")
    s.add_argument("--id")
    s.add_argument("--chapter", type=int)
    s.set_defaults(func=cmd_rewrite_resolve)

    s = sub.add_parser("config")
    s.add_argument("--project")
    s.add_argument("--show", action="store_true")
    s.add_argument("--language")
    s.add_argument("--target-chapters", type=int)
    s.add_argument("--chapter-word-target", type=int)
    s.add_argument("--context-budget-chars", type=int)
    s.add_argument("--recent-chapter-window", type=int)
    s.add_argument("--max-review-retries", type=int)
    s.set_defaults(func=cmd_config)

    s = sub.add_parser("complete")
    s.add_argument("--project")
    s.add_argument("--reason")
    s.set_defaults(func=cmd_complete)

    return p


def main() -> None:
    args = build_parser().parse_args()
    args.func(args)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from _common import atomic_write_json, read_json, resolve_project, utc_now

BASE_DIMS = ["consistency", "character", "pacing", "continuity", "foreshadow", "hook", "aesthetic"]
VERDICTS = {"accept", "polish", "rewrite"}
SCOPES = {"chapter", "global", "arc"}
SEVERITIES = {"critical", "error", "warning"}


def arc_bounds(project: Path, endpoint: int) -> tuple[int, int] | None:
    layered = read_json(project / "layered_outline.json", {}) or {}
    for volume in layered.get("volumes", []) or []:
        for arc in volume.get("arcs", []) or []:
            rng = arc.get("chapter_range") or []
            if isinstance(rng, list) and len(rng) == 2:
                start, end = rng
                if isinstance(start, int) and isinstance(end, int) and end == endpoint and start > 0 and end >= start:
                    return start, end
    return None


def validate_review(review: dict, project: Path | None = None) -> dict:
    chapter = review.get("chapter")
    if not isinstance(chapter, int) or isinstance(chapter, bool) or chapter <= 0:
        raise ValueError("chapter must be an integer > 0")

    scope = str(review.get("scope") or "").strip()
    if scope not in SCOPES:
        raise ValueError("scope must be chapter|global|arc")

    summary = str(review.get("summary") or "").strip()
    if not summary:
        raise ValueError("summary is required")

    verdict = str(review.get("verdict") or "").strip()
    if verdict not in VERDICTS:
        raise ValueError("verdict must be accept|polish|rewrite")

    dimensions = review.get("dimensions")
    if not isinstance(dimensions, list) or not dimensions:
        raise ValueError("dimensions must contain evidence-based assessments")
    seen: set[str] = set()
    for idx, item in enumerate(dimensions):
        if not isinstance(item, dict):
            raise ValueError(f"dimensions[{idx}] must be an object")
        name = str(item.get("dimension") or "").strip()
        if not name:
            raise ValueError(f"dimensions[{idx}].dimension is required")
        if name in seen:
            raise ValueError(f"duplicate dimension: {name}")
        seen.add(name)
        score = item.get("score")
        if not isinstance(score, int) or isinstance(score, bool) or not 0 <= score <= 100:
            raise ValueError(f"invalid score for {name}: expected integer 0..100")
        if not str(item.get("comment") or "").strip():
            raise ValueError(f"dimension comment is required: {name}")
    missing = [name for name in BASE_DIMS if name not in seen]
    if missing:
        raise ValueError(f"missing required base review dimensions: {missing}")

    contract = review.get("contract_status")
    if contract in (None, ""):
        contract = None
    elif contract not in {"met", "partial", "missed"}:
        raise ValueError("contract_status must be null|met|partial|missed")
    misses = review.get("contract_misses", []) or []
    if not isinstance(misses, list) or any(not isinstance(x, str) or not x.strip() for x in misses):
        raise ValueError("contract_misses must be an array of non-empty strings")

    bounds = None
    if scope == "arc":
        if project is None:
            raise ValueError("arc review validation requires --project")
        bounds = arc_bounds(project, chapter)
        if bounds is None:
            raise ValueError("arc review chapter must be an arc endpoint in layered_outline.json")

    issues = review.get("issues")
    if not isinstance(issues, list):
        raise ValueError("issues must be an array")
    affected: set[int] = set()
    for idx, issue in enumerate(issues):
        if not isinstance(issue, dict):
            raise ValueError(f"issues[{idx}] must be an object")
        if not str(issue.get("type") or "").strip():
            raise ValueError(f"issues[{idx}].type is required")
        severity = str(issue.get("severity") or "").strip()
        if severity not in SEVERITIES:
            raise ValueError(f"issues[{idx}].severity must be critical|error|warning")
        if not str(issue.get("description") or "").strip():
            raise ValueError(f"issues[{idx}].description is required")
        if not str(issue.get("evidence") or "").strip():
            raise ValueError(f"issues[{idx}].evidence is required")
        if "suggestion" not in issue:
            raise ValueError(f"issues[{idx}].suggestion is required (use null when not needed)")
        requires_change = issue.get("requires_change")
        if not isinstance(requires_change, bool):
            raise ValueError(f"issues[{idx}].requires_change must be boolean")
        chapters = issue.get("chapters")
        if (chapters is None or chapters == []) and scope == "chapter":
            chapters = [chapter]
            issue["chapters"] = chapters
        if not isinstance(chapters, list) or not chapters:
            raise ValueError(f"issues[{idx}].chapters is required when scope={scope}")
        normalized: list[int] = []
        for value in chapters:
            if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
                raise ValueError(f"issues[{idx}].chapters must contain positive integers")
            if scope == "chapter" and value != chapter:
                raise ValueError(f"chapter review issue must reference chapter {chapter}, got {value}")
            if scope == "global" and value > chapter:
                raise ValueError(f"global review issue chapter {value} outside 1-{chapter}")
            if scope == "arc" and bounds is not None and not (bounds[0] <= value <= bounds[1]):
                raise ValueError(f"arc review issue chapter {value} outside {bounds[0]}-{bounds[1]}")
            normalized.append(value)
            if requires_change:
                affected.add(value)
        issue["chapters"] = sorted(set(normalized))

    derived = sorted(affected)
    precomputed = review.get("affected_chapters", []) or []
    if precomputed:
        if not isinstance(precomputed, list) or sorted(set(precomputed)) != derived:
            raise ValueError("affected_chapters is derived from issues[].chapters + requires_change; do not author it manually")

    if verdict == "accept" and derived:
        raise ValueError("accept review cannot contain issues with requires_change=true")
    if verdict in {"polish", "rewrite"} and not derived:
        raise ValueError(f"verdict={verdict} requires at least one issue with requires_change=true")

    return {
        "chapter": chapter,
        "scope": scope,
        "verdict": verdict,
        "affected_chapters": derived,
        "base_dimensions_present": [name for name in BASE_DIMS if name in seen],
        "extra_dimensions": sorted(seen - set(BASE_DIMS)),
        "contract_status": contract,
    }


def queue_repairs(project: Path, outcome: dict, review_path: Path, summary: str) -> list[dict]:
    if outcome["verdict"] not in {"polish", "rewrite"}:
        return []
    queue_path = project / "meta" / "rewrite_queue.json"
    queue = read_json(queue_path, {"version": 1, "items": []}) or {"version": 1, "items": []}
    items = queue.setdefault("items", [])
    added = []
    for chapter in outcome["affected_chapters"]:
        duplicate = next((x for x in items if x.get("chapter") == chapter and x.get("status", "pending") == "pending"), None)
        if duplicate:
            continue
        item = {
            "id": f"review-{review_path.stem}-ch{chapter}-{len(items)+1}",
            "chapter": chapter,
            "mode": outcome["verdict"],
            "reason": summary,
            "review_file": str(review_path),
            "status": "pending",
            "created_at": utc_now(),
        }
        items.append(item)
        added.append(item)
    atomic_write_json(queue_path, queue)
    return added


def apply_flow(project: Path, outcome: dict) -> list[str]:
    progress_path = project / "meta" / "progress.json"
    progress = read_json(progress_path, {}) or {}
    verdict = outcome["verdict"]
    progress["flow"] = {"accept": "writing", "polish": "polishing", "rewrite": "rewriting"}[verdict]
    if verdict in {"polish", "rewrite"}:
        progress["current_step"] = verdict
    progress["updated_at"] = utc_now()
    atomic_write_json(progress_path, progress)

    resolved: list[str] = []
    if verdict == "accept" and outcome["scope"] == "chapter":
        queue_path = project / "meta" / "rewrite_queue.json"
        queue = read_json(queue_path, {"version": 1, "items": []}) or {"version": 1, "items": []}
        changed = False
        for item in queue.get("items", []):
            if item.get("chapter") == outcome["chapter"] and item.get("status", "pending") == "pending":
                item["status"] = "resolved"
                item["resolved_at"] = utc_now()
                item["resolved_by"] = "accepted_review"
                resolved.append(str(item.get("id")))
                changed = True
        if changed:
            atomic_write_json(queue_path, queue)
    return resolved


def main() -> None:
    p = argparse.ArgumentParser(description="Validate Ainovel review protocol and deterministically derive affected chapters/repair flow. No LLM/network.")
    p.add_argument("--project")
    p.add_argument("--chapter", type=int)
    p.add_argument("--review")
    p.add_argument("--apply", action="store_true", help="Persist derived affected_chapters and update repair queue/flow.")
    args = p.parse_args()

    project = resolve_project(args.project) if args.project else None
    if args.review:
        review_path = Path(args.review).expanduser().resolve()
        if project is None and review_path.parent.name == "reviews":
            project = review_path.parent.parent
    else:
        project = resolve_project(args.project)
        if args.chapter is None:
            raise SystemExit("Pass --chapter when --review is omitted")
        review_path = project / "reviews" / f"{args.chapter:03d}.json"

    review = read_json(review_path, None)
    if not isinstance(review, dict):
        raise SystemExit(f"Invalid/missing review: {review_path}")
    try:
        outcome = validate_review(review, project)
    except ValueError as e:
        raise SystemExit(str(e))

    queued: list[dict] = []
    resolved: list[str] = []
    if args.apply:
        review["affected_chapters"] = outcome["affected_chapters"]
        atomic_write_json(review_path, review)
        if project is not None:
            queued = queue_repairs(project, outcome, review_path, str(review.get("summary") or ""))
            resolved = apply_flow(project, outcome)

    print(json.dumps({
        "ok": True,
        **outcome,
        "queued": queued,
        "resolved_rewrite_items": resolved,
        "applied": bool(args.apply),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

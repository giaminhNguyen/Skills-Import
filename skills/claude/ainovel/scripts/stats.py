#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import statistics
from pathlib import Path

from _common import chapter_files, read_json, resolve_project

DIMS = ["consistency", "character", "pacing", "continuity", "foreshadow", "hook", "aesthetic"]
WORD_RE = re.compile(r"\b[\wÀ-ỹ]+\b", re.UNICODE)


def main() -> None:
    p = argparse.ArgumentParser(description="Deterministic Ainovel progress/quality statistics.")
    p.add_argument("--project")
    args = p.parse_args()
    project = resolve_project(args.project)

    lengths = []
    chapters = []
    for path in chapter_files(project):
        text = path.read_text(encoding="utf-8")
        words = len(WORD_RE.findall(text))
        chars = len(text)
        n = int(path.stem)
        chapters.append({"chapter": n, "words": words, "chars": chars})
        lengths.append(words)
    median = statistics.median(lengths) if lengths else 0
    anomalies = []
    if median:
        for c in chapters:
            if c["words"] < median * 0.5 or c["words"] > median * 1.8:
                anomalies.append(c)

    review_scores = {d: [] for d in DIMS}
    verdicts = {}
    for path in sorted((project / "reviews").glob("*.json")):
        data = read_json(path, {}) or {}
        verdict = data.get("verdict") or "unset"
        verdicts[verdict] = verdicts.get(verdict, 0) + 1
        dims = data.get("dimensions", []) or []
        dim_map = {x.get("dimension"): x for x in dims if isinstance(x, dict)} if isinstance(dims, list) else dims
        for d in DIMS:
            score = (dim_map.get(d) or {}).get("score")
            if isinstance(score, int) and not isinstance(score, bool):
                review_scores[d].append(score)
    averages = {d: round(sum(v) / len(v), 2) if v else None for d, v in review_scores.items()}

    progress = read_json(project / "meta" / "progress.json", {}) or {}
    foreshadow = read_json(project / "meta" / "foreshadow.json", {"items": []}) or {"items": []}
    pending_fs = [x for x in foreshadow.get("items", []) if x.get("status") not in {"paid_off", "resolved", "cancelled"}]
    steer = read_json(project / "meta" / "steer_queue.json", {"items": []}) or {"items": []}
    rewrite = read_json(project / "meta" / "rewrite_queue.json", {"items": []}) or {"items": []}

    out = {
        "project": str(project),
        "progress": progress,
        "chapters": {
            "count": len(chapters),
            "total_words": sum(c["words"] for c in chapters),
            "median_words": median,
            "length_anomalies": anomalies,
        },
        "reviews": {"verdict_counts": verdicts, "dimension_averages": averages},
        "planning": {
            "chapter_summaries": len(list((project / "summaries").glob("chapter-*.json"))),
            "arc_summaries": len(list((project / "summaries").glob("arc-*.json"))),
            "volume_summaries": len(list((project / "summaries").glob("vol-*.json"))),
            "open_foreshadow": len(pending_fs),
        },
        "queues": {
            "pending_steer": sum(1 for x in steer.get("items", []) if x.get("status", "pending") == "pending"),
            "pending_rewrites": sum(1 for x in rewrite.get("items", []) if x.get("status", "pending") == "pending"),
        },
    }
    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

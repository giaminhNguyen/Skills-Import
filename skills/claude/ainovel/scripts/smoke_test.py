#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent


def run(name: str, *args: str, cwd: Path | None = None, expect_ok: bool = True) -> dict:
    cmd = [sys.executable, str(SCRIPT_DIR / name), *args]
    cp = subprocess.run(cmd, cwd=str(cwd) if cwd else None, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if expect_ok and cp.returncode != 0:
        raise AssertionError(f"Command failed: {' '.join(cmd)}\nSTDOUT={cp.stdout}\nSTDERR={cp.stderr}")
    text = cp.stdout.strip()
    if not text:
        return {"returncode": cp.returncode, "stderr": cp.stderr}
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        raise AssertionError(f"Non-JSON output from {name}: {text}\n{e}")


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def review(chapter: int, scope: str = "chapter", issues: list[dict] | None = None, verdict: str = "accept") -> dict:
    dims = []
    for key in ["consistency", "character", "pacing", "continuity", "foreshadow", "hook", "aesthetic"]:
        dims.append({
            "dimension": key,
            "score": 85,
            "verdict": "pass",
            "comment": f"Bằng chứng ngắn chương {chapter}: đạt yêu cầu smoke test.",
        })
    return {
        "chapter": chapter,
        "scope": scope,
        "dimensions": dims,
        "issues": issues or [],
        "contract_status": "met",
        "contract_misses": [],
        "contract_notes": "All smoke-test beats present.",
        "verdict": verdict,
        "summary": "Smoke-test review.",
        "affected_chapters": [],
    }


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="ainovel-smoke-") as tmp:
        workspace = Path(tmp)
        init = run("state.py", "init", "--workspace", str(workspace), "--idea", "Truyện smoke test ba chương", "--slug", "smoke", "--target-chapters", "3", cwd=workspace)
        project = Path(init["project"])

        # Simulated Architect foundation.
        write_json(project / "meta" / "book.json", {"title": "Thành Phố Quên", "summary": "Smoke test", "language": "vi", "genre": ["mystery"], "status": "writing"})
        (project / "book.md").write_text("# Thành Phố Quên\n\nSmoke test.\n", encoding="utf-8")
        (project / "premise.md").write_text("# Premise\n\nMột thành phố mất ký ức mỗi nửa đêm.\n", encoding="utf-8")
        write_json(project / "characters.json", {"version": 1, "characters": [{"id": "char-001", "name": "An", "state": {"knows_reset": True}, "last_seen_chapter": 3}]})
        write_json(project / "world_rules.json", {"version": 1, "rules": [{"id": "rule-001", "kind": "hard", "rule": "Ký ức dân cư reset lúc nửa đêm."}]})
        write_json(project / "meta" / "compass.json", {"version": 1, "ending_direction": "An giữ được một ký ức thật.", "core_promises": ["Giải thích reset"], "non_negotiables": [], "character_destinations": [], "volume_milestones": [], "open_questions": []})
        write_json(project / "layered_outline.json", {"version": 1, "current_volume": 1, "current_arc": "1.1", "volumes": [{"id": "v01", "title": "Tập 1", "objective": "Tìm nguồn reset", "status": "active", "arcs": [{"id": "v01-a01", "title": "Cung Đồng Hồ", "objective": "Theo dấu đồng hồ", "status": "active", "chapter_range": [1, 3], "detail_level": "detailed"}]}]})
        write_json(project / "outline.json", {"arc_id": "v01-a01", "chapters": [{"chapter": i, "title": f"Chương {i}", "purpose": f"Beat {i}", "must_happen": [f"event-{i}"], "must_not_happen": [], "character_ids": ["char-001"], "world_rule_ids": ["rule-001"], "foreshadow_actions": [], "ending_hook": "next"} for i in range(1, 4)]})
        run("state.py", "checkpoint", "--project", str(project), "--event", "foundation_saved", "--next-step", "plan")

        for n in range(1, 4):
            plan = {"chapter": n, "title": f"Chương {n}", "purpose": f"Beat {n}", "must_happen": [f"event-{n}"], "must_not_happen": [], "character_ids": ["char-001"], "world_rule_ids": ["rule-001"], "relationship_ids": [], "foreshadow": {"setup": [], "advance": [], "payoff": []}, "relevant_chapters": [max(1, n - 1)] if n > 1 else [], "ending_hook": "next"}
            write_json(project / "drafts" / f"{n:03d}.plan.json", plan)
            run("state.py", "checkpoint", "--project", str(project), "--event", "chapter_planned", "--next-step", "draft", "--chapter", str(n), "--artifact", f"drafts/{n:03d}.plan.json")

            draft = f"# Chương {n}: Đêm {n}\n\nBằng chứng ngắn chương {n}. An nghe tiếng đồng hồ và nhớ event-{n}.\n\nMột dấu vết mới xuất hiện.\n"
            (project / "drafts" / f"{n:03d}.md").write_text(draft, encoding="utf-8")
            run("state.py", "checkpoint", "--project", str(project), "--event", "chapter_drafted", "--next-step", "consistency", "--chapter", str(n), "--artifact", f"drafts/{n:03d}.md")
            if n == 2:
                resumed = run("state.py", "resume", "--project", str(project))
                assert resumed["resume_step"] == "consistency", resumed

            write_json(project / "drafts" / f"{n:03d}.consistency.json", {"chapter": n, "pass": True, "contract": {"status": "met", "missing": [], "violations": []}, "world_rule_conflicts": [], "character_conflicts": [], "timeline_conflicts": [], "location_conflicts": [], "foreshadow_conflicts": [], "relationship_conflicts": [], "required_fixes": []})
            run("state.py", "checkpoint", "--project", str(project), "--event", "consistency_checked", "--next-step", "commit", "--chapter", str(n), "--artifact", f"drafts/{n:03d}.consistency.json")

            (project / "chapters" / f"{n:03d}.md").write_text(draft, encoding="utf-8")
            run("state.py", "hash-chapter", "--project", str(project), "--chapter", str(n))
            run("state.py", "checkpoint", "--project", str(project), "--event", "chapter_committed", "--next-step", "review", "--chapter", str(n), "--artifact", f"chapters/{n:03d}.md")

            write_json(project / "reviews" / f"{n:03d}.json", review(n))
            gate = run("review_gate.py", "--project", str(project), "--review", str(project / "reviews" / f"{n:03d}.json"), "--apply")
            assert gate["verdict"] == "accept", gate
            write_json(project / "summaries" / f"chapter-{n:03d}.json", {"chapter": n, "title": f"Chương {n}", "purpose": f"Beat {n}", "outcome": f"event-{n}", "events": [f"event-{n}"], "character_ids": ["char-001"], "character_state_deltas": [], "relationship_deltas": [], "world_rule_ids": ["rule-001"], "foreshadow": {"setup": [], "advance": [], "payoff": []}, "timeline": [f"night-{n}"], "locations": ["city"], "style_stats": {}, "relevant_previous_chapters": [n - 1] if n > 1 else []})
            next_step = "summarize_arc" if n == 3 else "plan"
            run("state.py", "checkpoint", "--project", str(project), "--event", "chapter_reviewed", "--next-step", next_step, "--chapter", str(n), "--artifact", f"reviews/{n:03d}.json", *( ["--advance-chapter"] if n < 3 else [] ))

            if n == 1:
                run("state.py", "review", "on", "--project", str(project))
                run("state.py", "next", "--project", str(project))
                consumed = run("state.py", "consume-permit", "--project", str(project))
                assert consumed["consumed"] is True
                run("state.py", "review", "off", "--project", str(project))

        # Deterministic repair derivation: affected chapters come only from issues marked requires_change.
        repair_path = project / "reviews" / "repair-probe.json"
        repair_issue = {
            "type": "dialogue_voice", "severity": "warning", "description": "Probe",
            "evidence": "Bằng chứng ngắn chương 2.", "suggestion": "Tighten voice",
            "chapters": [2], "requires_change": True
        }
        write_json(repair_path, review(2, issues=[repair_issue], verdict="polish"))
        repair_gate = run("review_gate.py", "--project", str(project), "--review", str(repair_path), "--apply")
        assert repair_gate["affected_chapters"] == [2] and repair_gate["verdict"] == "polish", repair_gate
        run("state.py", "rewrite-resolve", "--project", str(project), "--chapter", "2")
        repair_path.unlink()

        # Source-level aggregate arc review comes before arc summary.
        arc_review_path = project / "reviews" / "arc-v01-a01.json"
        write_json(arc_review_path, review(3, scope="arc"))
        arc_gate = run("review_gate.py", "--project", str(project), "--review", str(arc_review_path), "--apply")
        assert arc_gate["verdict"] == "accept" and arc_gate["scope"] == "arc", arc_gate
        run("state.py", "checkpoint", "--project", str(project), "--event", "arc_reviewed", "--next-step", "summarize_arc", "--scope-kind", "arc", "--volume", "1", "--arc", "1", "--artifact", "reviews/arc-v01-a01.json")

        write_json(project / "summaries" / "arc-v01-a01.json", {"arc_id": "v01-a01", "planned_objective": "Tìm nguồn reset", "actual_outcome": "Tìm thấy đồng hồ", "major_events": ["event-1", "event-2", "event-3"], "character_snapshots": [], "relationship_changes": [], "timeline_anchors": [], "foreshadow": {"created": [], "advanced": [], "paid_off": [], "unresolved": []}, "unresolved_tensions": [], "style_rules": {"prose": [], "dialogue": []}, "architect_handoff": []})
        write_json(project / "summaries" / "vol-v01.json", {"volume_id": "v01", "objective": "Tìm nguồn reset", "actual_outcome": "Giải quyết", "irreversible_changes": [], "resolved_promises": ["Giải thích reset"], "unresolved_promises": [], "character_snapshots": [], "world_state": [], "next_volume_constraints": []})
        run("state.py", "checkpoint", "--project", str(project), "--event", "arc_summarized", "--next-step", "summarize_volume", "--scope-kind", "arc", "--volume", "1", "--arc", "1", "--artifact", "summaries/arc-v01-a01.json")
        run("state.py", "checkpoint", "--project", str(project), "--event", "volume_summarized", "--next-step", "completed")
        run("state.py", "complete", "--project", str(project), "--reason", "smoke")

        ctx = run("context_pack.py", "build", "--project", str(project), "--chapter", "3", "--budget-chars", "12000")
        assert ctx["actual_chars"] <= 12000, ctx

        # Manual edit -> dirty -> accept after pretend semantic sync.
        p2 = project / "chapters" / "002.md"
        p2.write_text(p2.read_text(encoding="utf-8") + "\nSửa tay smoke.\n", encoding="utf-8")
        dirty = run("sync_scan.py", "--project", str(project), "--check")
        assert dirty["dirty"] is True and "002.md" in dirty["changed"], dirty
        run("sync_scan.py", "--project", str(project), "--accept")
        clean = run("sync_scan.py", "--project", str(project), "--check")
        assert clean["dirty"] is False, clean

        txt = project / "exports" / "smoke.txt"
        epub = project / "exports" / "smoke.epub"
        run("export_novel.py", str(txt), "--project", str(project))
        run("export_novel.py", str(epub), "--project", str(project))
        assert txt.exists() and "Chương 3" in txt.read_text(encoding="utf-8")
        with zipfile.ZipFile(epub, "r") as zf:
            infos = zf.infolist()
            assert infos[0].filename == "mimetype"
            assert infos[0].compress_type == zipfile.ZIP_STORED
            assert zf.read("mimetype") == b"application/epub+zip"
            assert "OEBPS/nav.xhtml" in zf.namelist()
            assert "OEBPS/content.opf" in zf.namelist()

        valid = run("validate_project.py", "--project", str(project))
        assert valid["ok"] is True, valid
        stats = run("stats.py", "--project", str(project))
        assert stats["chapters"]["count"] == 3, stats

        print(json.dumps({
            "ok": True,
            "message": "Ainovel deterministic smoke test passed",
            "tested": ["init", "checkpoint", "resume", "seven-dimension review validation", "repair derivation/queue", "arc aggregate review", "review permit", "context pack", "hash sync", "TXT export", "EPUB3 export", "validation", "stats"],
        }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

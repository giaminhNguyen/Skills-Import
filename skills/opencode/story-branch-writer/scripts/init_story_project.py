#!/usr/bin/env python3
import json
import sys
from pathlib import Path

REQUEST = """# Optional generation request\n\nbranch: null\ndirection: null\ntarget_length: null\n\n# Notes\n# - branch: null => agent chooses automatically.\n# - Put the full reference story in reference.txt.\n"""

STATE = {
    "timeline_position": "not_started",
    "characters": {},
    "relationships": {},
    "open_questions": [],
    "setups": [],
    "resolved_payoffs": [],
    "valid_canon": [],
    "branch_facts": []
}

FILES = {
    "reference.txt": "",
    "request.md": REQUEST,
    "canon.md": "# Canon\n\n",
    "branch.md": "# Branch\n\n",
    "outline.md": "# Outline\n\n",
    "story.md": ""
}

def main():
    if len(sys.argv) != 2:
        print("Usage: init_story_project.py <directory>", file=sys.stderr)
        return 2
    root = Path(sys.argv[1]).expanduser().resolve()
    root.mkdir(parents=True, exist_ok=True)
    for name, content in FILES.items():
        path = root / name
        if not path.exists():
            path.write_text(content, encoding="utf-8")
    state_path = root / "story_state.json"
    if not state_path.exists():
        state_path.write_text(json.dumps(STATE, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(root)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

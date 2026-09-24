#!/usr/bin/env python3
import json
import sys
from pathlib import Path

REQUIRED = [
    "profile_id", "display_name", "engine", "language", "engine_facts",
    "adapter_policy", "chunking", "normalization", "dialogue",
    "inline_cues", "synthesis", "provenance"
]


def fail(msg):
    print(f"ERROR: {msg}", file=sys.stderr)
    raise SystemExit(1)


def main():
    if len(sys.argv) != 2:
        fail("usage: validate_profile.py PROFILE.json")
    path = Path(sys.argv[1])
    data = json.loads(path.read_text(encoding="utf-8"))
    missing = [k for k in REQUIRED if k not in data]
    if missing:
        fail("missing fields: " + ", ".join(missing))
    c = data["chunking"]
    for k in ["hard_max_chars", "preferred_chunk_chars_min", "preferred_chunk_chars_max", "avoid_chunk_below_chars"]:
        if not isinstance(c.get(k), int) or c[k] <= 0:
            fail(f"chunking.{k} must be a positive integer")
    if c["preferred_chunk_chars_max"] > c["hard_max_chars"]:
        fail("preferred_chunk_chars_max cannot exceed hard_max_chars")
    if c["preferred_chunk_chars_min"] > c["preferred_chunk_chars_max"]:
        fail("preferred chunk min cannot exceed preferred chunk max")
    if not data["profile_id"].strip():
        fail("profile_id cannot be empty")
    print(f"OK: {data['profile_id']}")

if __name__ == "__main__":
    main()

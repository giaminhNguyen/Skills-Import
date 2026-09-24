# Story Branch Writer

A provider-agnostic story branching workflow for Codex, OpenCode, Claude Code, and compatible agent CLIs.

## Minimal use

1. Initialize a workspace:

```bash
python scripts/init_story_project.py ./my-story
```

2. Put the complete source story in `my-story/reference.txt`.
3. Leave `branch: null` in `request.md` for fully automatic branching, or write a branch idea.
4. Start your agent in that directory and tell it to follow `AGENTS.md` (Codex/OpenCode) or `CLAUDE.md` (Claude Code) and produce `story.md`.

## Example request.md

```yaml
branch: null
direction: "đấu trí, nhiều payoff, hạn chế lặp cốt truyện gốc"
target_length: 15000
```

Or specify the branch directly:

```yaml
branch: "Chi Đào cũng trọng sinh"
direction: null
target_length: 15000
```

When `branch` is null, the agent analyzes the reference, finds a few high-leverage branch options, selects one quickly, and proceeds without asking the user.

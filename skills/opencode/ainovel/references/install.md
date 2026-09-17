# Installation

## Claude Code

Recommended project-local installation:

```text
<project>/.claude/skills/ainovel/
```

Copy the entire `ainovel` skill directory there. The canonical entrypoint is `.claude/skills/ainovel/SKILL.md`.

Optional slash-style adapter: copy `adapters/claude/commands/ainovel.md` to:

```text
<project>/.claude/commands/ainovel.md
```

Then invoke with the host's command mechanism or simply type a natural-language request beginning with `ainovel ...`. The skill itself does not depend on the adapter.

## Codex

Use either of these patterns depending on the Codex CLI setup:

1. Place the skill under a project-local Codex skills directory (for installations that support skill discovery), preserving `SKILL.md` and resources.
2. Copy/merge `adapters/codex/AGENTS.md` into the project root `AGENTS.md`; adjust the relative path in that file to where this package is stored.

The portable invariant is: when the user intent begins with `ainovel` or asks for the described novel workflow, load this `SKILL.md` and follow its file/state protocol.

## No provider setup

Do not copy `ainovel-cli` provider config. This skill needs only:

- the host agent CLI and its already-selected model
- filesystem read/write
- a shell
- Python 3 standard library for helper scripts

No API key, provider config, LiteLLM or Ollama is needed.

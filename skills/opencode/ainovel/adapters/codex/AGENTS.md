# Ainovel workflow adapter

When the user asks to create/continue/review/steer/import/sync/export a novel with `ainovel`, load the Ainovel skill package's `SKILL.md` before acting. Follow its deterministic project-state protocol and role prompts. Use Codex's current model for Architect/Writer/Editor/Arbiter reasoning. Never add API/provider/Ollama configuration.

If this package is stored at `.codex/skills/ainovel/`, the entrypoint is `.codex/skills/ainovel/SKILL.md`. If it is stored elsewhere, update only this path reference; do not duplicate the workflow into AGENTS.md.

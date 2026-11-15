# Claude Code profile

- Use the root `CLAUDE.md` bridge to `AGENTS.md`. If instructions were not imported, read `AGENTS.md` explicitly.
- Use current Claude Code editor/terminal and approval capabilities. Keep its selected model and native settings; no OpenAI model or reasoning controls are required.
- Read the relevant `.agents/skills/<workflow>/SKILL.md` directly when native skill discovery does not expose it. Harness Markdown remains the source of workflow instructions; do not load `agents/openai.yaml`.
- Use the single-agent loop by default. Native subagents, hooks, slash commands and MCP integrations remain separate opt-ins. Never run the Codex orchestration protocol as though it configured Claude agents.
- Keep account and MCP settings in Claude's private configuration; use `AGENTS.local.md` only for nonsecret project preferences.

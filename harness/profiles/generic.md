# Generic tool profile

- Use this profile for any other coding assistant; name the actual runtime when known. A profile never establishes agent identity, tool access or authorization.
- Explicitly load `AGENTS.md` when the tool does not discover it, then follow the selected workflow's `SKILL.md` as ordinary Markdown.
- Use only capabilities actually available: file editing, terminal/tests, browser, delegation and native approvals. Report limitations and complete independent work. Supply commands for the user's terminal when no execution tool exists; do not claim they ran.
- Keep the runtime's current model/settings and use one agent by default. No vendor-specific directories, model labels, hooks, metadata or dispatch APIs are prerequisites.
- For a new permanent integration, add a tiny native entrypoint pointing to `AGENTS.md`. Add a dedicated profile only when concrete tool-specific guidance is needed; see [extension guidance](../../docs/agent-tools.md#adding-another-tool).

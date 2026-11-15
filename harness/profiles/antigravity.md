# Antigravity profile

- Use the workspace's `.agent/rules/harness.md` bootstrap and current Antigravity editor/terminal/browser capabilities when available. If that rule is not loaded, explicitly read `AGENTS.md`.
- Read the relevant `.agents/skills/<workflow>/SKILL.md` as portable instructions. Native skill support varies by version; no Codex discovery path, `$skill` command, or OpenAI metadata is required.
- Keep Antigravity's selected model, planning/fast mode and native review settings. Do not force Codex models, reasoning names, subagent APIs or configuration paths.
- Run the ordinary single-agent implement/verify loop. Create plans or native artifacts only when useful to the task or requested. Browser availability does not by itself verify a user flow.
- If delegation is explicitly requested, first establish available native controls and agree on a supported workflow; the existing Codex orchestration protocol is not a portable dispatch API. A self-review must never be described as independent.
- Keep subscription, account and MCP configuration in the tool's own private settings, outside shared harness files.

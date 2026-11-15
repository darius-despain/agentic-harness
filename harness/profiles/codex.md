# Codex profile

- Use the current Codex runtime's editor, terminal, review and approval capabilities as available. The harness does not set a model or reasoning level.
- Discover project skills under `.agents/skills/`; load only the requested workflow. `agents/openai.yaml` is optional UI metadata, not worker registration.
- Keep local Codex account, MCP and model settings in the tool's own private configuration. Never load them for harness startup.
- Default to the development skill's single-agent loop. The existing Codex [orchestration protocol](../../.agents/skills/harness-development-loop/references/orchestration.md) is optional and has specific model/control requirements; load it only for an explicit orchestrated-mode request. Report unsupported controls instead of fabricating dispatches. It does not apply to other profiles.
- Native discovery begins with `AGENTS.md`; a user-supplied profile choice or project preference still determines selection.

- When tiered routing is explicitly enabled, follow [model routing](../../docs/model-routing.md) and its configured driver/worker/advisory controls. Its Python module and config defaults remain available; they do not run or override this session just because the Codex profile is selected.

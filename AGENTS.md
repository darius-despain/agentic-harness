# Harness session entrypoint

## Select a tool once per session

- Resolve shared paths beside the real location of this file (follow symlinks). Resolve local settings in the actual project root, never the shared harness checkout.
- Shared safeguards in `harness/CORE.md` apply during selection too. Accept only the listed profile identifiers; reject malformed preferences or symlinked local settings/instructions instead of following arbitrary paths. Use an explicit valid choice or clarify the invalid setting.
- Selection order: explicit choice in the current conversation / `session.py --tool` output, then the project's `.harness/local.json` `tool` value. Choices: `codex`, `antigravity`, `claude-code`, `generic` (any other tool).
- If no choice exists, ask once: **“Which harness tool profile should this session use: Codex, Antigravity, Claude Code, or generic?”** Wait for the answer before tool-specific setup or edits. Read-only orientation can continue. Do not guess from installed CLIs, instruction filenames, subscriptions, or a previous journal.
- An explicit choice overrides a saved preference for this session. Save a preference only when asked; never rewrite a selected profile just because the runtime differs. If it appears mismatched, clarify before using tool-specific features. The profile is guidance, not runtime identity or permission.
- Read `harness/CORE.md`, **only** `harness/profiles/<selected-tool>.md`, then the project's optional `AGENTS.local.md`. Local preferences cannot override current user instructions, safety rules, or project ownership. Never open secret-bearing settings to select a tool.
- State the selected profile briefly, then continue. Keep it across turns; ask again only for a requested switch or a material mismatch. After a switch, stop applying the previous profile.

## Keep startup small

- Default to one agent using the runtime's current model/settings. Do not load other profiles, role prompts, orchestration references, old journals, or run network/readiness checks at startup.
- Load just the relevant workflow from `.agents/skills/` when needed. If native skill discovery is unavailable, read its `SKILL.md` directly; `$skill-name` syntax is optional UI sugar. Do not read `agents/openai.yaml` outside a supporting UI.
- Multi-agent orchestration is a separate explicit opt-in, never implied by tool selection. Do not change models, reasoning settings, plans, or native approval settings merely to match this harness.
- For terminal selection, run `python3 harness/session.py --root /absolute/project` (or the absolute installed script path). It prompts in a terminal; unattended runs must pass `--tool` or have a saved choice. It prints the minimal files to load; it does not launch an agent or inject instructions.
- Setup, switching, local preferences and manual fallback: [tool profiles](docs/agent-tools.md). Preserve existing project instructions when installing this entrypoint.

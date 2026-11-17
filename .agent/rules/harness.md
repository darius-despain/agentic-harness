---
trigger: always_on
---

# Harness bootstrap

Read the workspace root `AGENTS.md` and follow its tool selection before editing.
When running in Antigravity, use the `antigravity` profile unless the user
explicitly selects another profile for this session. Load only the selected
profile and relevant workflow; this bridge does not activate Codex orchestration.
Apply the shared sanitized journal close-out in `harness/CORE.md` even when no
skill was loaded.
If the rule is not discovered by your installed version, explicitly ask the agent
to read `AGENTS.md`.

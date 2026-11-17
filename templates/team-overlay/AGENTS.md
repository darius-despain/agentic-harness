# Team / Project Agent Entrypoint

This file layers team- or project-specific conventions on top of the shared
`agentic-harness` without duplicating its rules.

## 1. Load the shared harness first

1. Resolve the shared `agentic-harness` checkout using the path configured in
   this overlay's optional `AGENTS.local.md`, or `../agentic-harness` relative to
   this overlay in a sibling layout. Verify the resolved directory is distinct
   from this overlay, contains `harness/CORE.md`, and has the expected shared Git
   origin. If those checks fail, ask for the shared checkout path.
2. Follow `AGENTS.md` in `agentic-harness` to select the active tool profile
   (`codex`, `antigravity`, `claude-code`, or `generic`) and load `harness/CORE.md`
   plus that single profile.
3. Keep `AGENTS.local.md` and `.harness/local.json` in this project root (gitignored)
   for personal, non-secret preferences.

## 2. Team / project conventions

Replace the placeholders below with your team's actual rules:

- **Primary test command:** `<e.g., pytest -q or npm test>`
- **Lint / format check:** `<e.g., ruff check . && git diff --check>`
- **PR & branch conventions:** `<e.g., branch from main, include ticket ID in PR title>`
- **Protected / sensitive areas:** `<e.g., never log customer PII or .env* contents>`

## 3. Team-only skills (optional)

If this repository includes team-specific skills under `.agents/skills/`, load
the relevant `SKILL.md` only when the task calls for it.

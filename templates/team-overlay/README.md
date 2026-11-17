# Team Harness Overlay

This repository holds **team-specific** agent instructions, conventions, and optional
internal skills layered on top of the shared [agentic-harness](https://github.com/darius-despain/agentic-harness).

## Setup (once)

Clone `agentic-harness` and this overlay repo side by side:

```bash
git clone https://github.com/darius-despain/agentic-harness.git
git clone <this-repo-url>
```

If you store `agentic-harness` at a different path, note it in your gitignored `AGENTS.local.md`.

## Usage

Open your project or this overlay in your AI coding assistant and say:

> Read `AGENTS.md` (and `../agentic-harness/AGENTS.md`); use the `<claude-code | codex | antigravity | generic>` profile.

## Updating

- **Generic harness updates:** `cd ../agentic-harness && git pull --ff-only origin main`
- **Team overlay updates:** `git pull --ff-only origin main`

# Team Harness Overlay

This repository holds **team-specific** agent instructions, conventions, and optional
internal skills layered on top of the shared [agentic-harness](https://github.com/darius-despain/agentic-harness).

## Setup (once)

Clone `agentic-harness` and this overlay repo side by side:

```bash
git clone https://github.com/darius-despain/agentic-harness.git
git clone OVERLAY_REPOSITORY_URL team-harness
```

Replace `OVERLAY_REPOSITORY_URL` with this overlay's repository URL.
`team-harness` keeps the clone names distinct even when both repositories are named
`agentic-harness`.

Resolve the shared checkout from the overlay directory. For the sibling layout
above it is `../agentic-harness`. If the overlay is nested under a project
workspace or the shared checkout lives elsewhere, record the verified shared
checkout path in the overlay's gitignored `AGENTS.local.md`. Confirm that the
shared checkout contains `harness/CORE.md` and check that its Git origin matches
the shared repository you intended to use.

## Usage

Open your project or this overlay in your AI coding assistant and say:

> Read this overlay's `AGENTS.md` and follow its shared harness and tool-profile instructions.

## Updating

- **Shared harness updates.** From the verified shared checkout root, run
  `git pull --ff-only origin main`.
- **Team overlay updates.** From the overlay checkout root, run
  `git pull --ff-only origin main`.

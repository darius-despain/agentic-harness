# Team Overlay Setup (Option 3: No Fork Required)

Use this pattern when your team (for example, **MIQA**) wants shared, private team rules, internal skills, or repo conventions **without forking `agentic-harness`** or dealing with merge conflicts when pulling upstream updates.

---

## How the two layers fit together

1. **Shared generic layer (`agentic-harness`, public):**
   - Contains `AGENTS.md`, `harness/CORE.md`, tool profiles (`harness/profiles/*.md`), core skills (`.agents/skills/`), and Python helpers (`session.py`, `audit.py`, `git_guard.py`).
   - Teammates clone this once and update anytime with `git pull --ff-only origin main`.
2. **Private team / project layer (your team repo or project repos):**
   - Lives in a small private repo (e.g. `miqa-harness`) and/or inside each project repo's `AGENTS.md`.
   - Holds **only** team-specific conventions: build/test commands, internal PR/deploy rules, and optional team-only skills.
   - Never duplicates `CORE.md` or core skills—so upstream `agentic-harness` updates never conflict.

---

## Quick setup for a team overlay repo

1. Create a small private repo for your team (for example, `miqa-harness`).
2. Copy the starter files from [templates/team-overlay/](../templates/team-overlay/) into it:
   - `AGENTS.md` — tells the agent to load `agentic-harness` first, then apply your team rules.
   - `README.md` — onboarding instructions for teammates cloning both repos.
3. Add any team-specific skills under `.agents/skills/<team-skill>/SKILL.md` in that private repo.
4. Add your team's `.gitignore` rules for personal/local files:
   ```gitignore
   /.harness/local.json
   /AGENTS.local.md
   /CLAUDE.local.md
   harness-config.json
   conversations/
   harness/reports/
   .harness/handoffs/
   ```

---

## How teammates use it day to day

1. Clone both repos side by side (e.g. under `~/workspace/`). Replace
   `OVERLAY_REPOSITORY_URL` with your team overlay's URL:
   ```bash
   git clone https://github.com/darius-despain/agentic-harness.git
   git clone OVERLAY_REPOSITORY_URL team-harness
   ```
2. In the sibling layout, `../agentic-harness` from `team-harness/` points to the
   shared checkout. If the overlay is nested in a project workspace and named
   `agentic-harness`, that relative path returns to the overlay itself. Record the
   actual shared checkout path in the overlay's gitignored `AGENTS.local.md`.
   Before using that checkout, confirm that it contains `harness/CORE.md` and
   check its Git origin against the shared repository your team uses.
3. Open the target project or overlay in the AI tool and start with:
   > Read the team overlay's `AGENTS.md` and follow its shared harness and tool-profile instructions.
4. To update the shared harness, run `git pull --ff-only origin main` from the
   verified shared checkout root. To update team rules, run it from the overlay
   checkout root.

---

## Using it directly inside a project repo (even simpler)

If you don't even want a separate overlay repo, just add a short project `AGENTS.md` (and optional `CLAUDE.md` / `.agent/rules/harness.md`) in each team project repo using [templates/team-overlay/AGENTS.md](../templates/team-overlay/AGENTS.md) as a starting point. That keeps project-specific build/test commands in the project repo while referencing `agentic-harness` for the shared workflows.

# Agentic Harness

A lightweight, optional workflow harness for AI coding assistants—built to work across **Claude Code**, **Codex**, **Antigravity**, **open-source / free-tier IDE & CLI agents**, and **ChatGPT / web chat**.

It gives you portable Markdown workflows for **ticket clarification**, **implementation and verification**, **PR review**, **session journaling**, **handoffs**, and **evidence-based improvement**. Optional Python helpers use the Python 3.9+ standard library. Nothing here forces a specific model, paid subscription, or background telemetry.

## Your first task

Open the project you want to change in your coding agent and start a chat.
Keep `AGENTS.md` at the project root for discovery. If the project already has
one, merge in the harness startup instructions. For first-time setup, see
[Quick start](#quick-start-clone-once) and
[Use the harness in another project](#use-the-harness-in-another-project).

Pick a prompt and paste it into the chat. For a Trello ticket, paste the title,
description, and any acceptance criteria along with the prompt.

**The ticket is ready**

> Read `AGENTS.md` and use `harness-development-loop` for the ticket below.
> Show me your plan and how we’ll check the result. Once I approve the plan,
> implement it and run the checks.

**The ticket needs clarification**

> Read `AGENTS.md` and use `grill-me` to help me define what done looks like
> for the ticket below. Ask me one question at a time, then propose acceptance
> criteria for me to confirm.

You can also ask in plain language, “Grill me on what done looks like for this ticket.”

**I’m not sure where to start**

> Read `AGENTS.md`. I want to work on [goal]. Help me pick a small first task
> and tell me what you need from me.

If your agent can’t find a skill by name, ask it to read the matching file
directly. Use the path from your project root if the skills are copied or
symlinked there, or from the shared harness checkout your project uses. Choose
[`.agents/skills/grill-me/SKILL.md`](.agents/skills/grill-me/SKILL.md) or
[`.agents/skills/harness-development-loop/SKILL.md`](.agents/skills/harness-development-loop/SKILL.md).

If the agent asks which tool profile to use, choose your agent from
[the list below](#set-up-for-your-ai-agent).

Start with one ticket and your current model settings. The harness uses one
agent by default. Multi-agent orchestration requires an explicit request and a
tool that supports it, and can use more of your quota. See
[Workflows & Examples](docs/workflows-and-examples.md) for more prompts and when
to use each skill.

---

## Quick start (clone once)

Clone this repository into a stable local folder:

```bash
git clone https://github.com/darius-despain/agentic-harness.git
cd agentic-harness
```

**Requirements:**
- **Python 3.9+** (only needed for optional CLI tools like `session.py`, `audit.py`, and tests; zero pip dependencies)
- **Git** (and `gh` only if you opt into GitHub readiness checks)

---

## Set up for your AI agent

At the start of a session, your agent reads [AGENTS.md](AGENTS.md), then
[harness/CORE.md](harness/CORE.md) and **one** matching profile from
`harness/profiles/`. Use the instructions for your tool below if you need to
tell it where to start.

### 1. Claude Code (`claude-code`)
- This repo already includes [CLAUDE.md](CLAUDE.md), which automatically imports `AGENTS.md` and selects the `claude-code` profile.
- **How to start:** Open your project in Claude Code, or say:
  > Read `AGENTS.md`; use the `claude-code` profile.

### 2. Codex (`codex`)
- Codex natively discovers [AGENTS.md](AGENTS.md) and `.agents/skills/`.
- **How to start:** Open your project in Codex, or say:
  > Read `AGENTS.md`; use the `codex` profile.
- **Optional global Codex setup:** See [live global installation with symlinks](docs/installation-and-git.md#live-global-installation-with-symlinks) (`harness/install_links.py`).

### 3. Antigravity (`antigravity`)
- This repo includes [.agent/rules/harness.md](.agent/rules/harness.md), which tells Antigravity to read the workspace root `AGENTS.md` and use the `antigravity` profile.
- Open the project in Antigravity. If it doesn’t load the rule, say
  > Read `AGENTS.md`; use the `antigravity` profile.

### 4. Open-source, free-tier, or other IDE/CLI agents (`generic`)
Works with **OpenCode**, **Cursor**, **Windsurf**, **Cline**, **Roo Code**, **Aider**, **Gemini CLI**, **Continue**, **Goose**, or any other local/open-source/free-tier coding assistant:
- **How to start:** In your first prompt, tell the agent:
  > Read `AGENTS.md`; use the `generic` profile.
- **If your tool has its own rules file** (e.g., `.cursorrules`, `.windsurfrules`, `.clinerules`, `CONVENTIONS.md`): add a one-line pointer telling it to read `AGENTS.md` and use the `generic` profile—don't copy shared rules into it.
- **Skills:** If your tool doesn't auto-discover `.agents/skills/`, tell it which `.agents/skills/<workflow>/SKILL.md` file to read as plain Markdown.

### 5. ChatGPT or web-based chat assistants (`generic`)
If you're using ChatGPT (free or paid) or another web chat without direct access to your local filesystem:
1. Paste or upload [AGENTS.md](AGENTS.md), [harness/CORE.md](harness/CORE.md), [harness/profiles/generic.md](harness/profiles/generic.md), and the one workflow you need from `.agents/skills/<workflow>/SKILL.md`.
2. Start the chat with:
   > Use the `generic` profile. Follow these instructions, and give me exact terminal commands to run locally whenever you don't have shell access.
3. Run any suggested commands in your local terminal and paste the output back.

### Optional: Terminal selector & personal preferences
You can also print the exact files to load or save a per-project default tool in `.harness/local.json` (gitignored):

```bash
python3 harness/session.py --tool generic
python3 harness/session.py --tool claude-code --remember
python3 harness/session.py --forget
```

For personal, non-secret preferences (like concise updates or local test commands), copy [AGENTS.local.example.md](AGENTS.local.example.md) to `AGENTS.local.md` in your project root (also gitignored). See [docs/agent-tools.md](docs/agent-tools.md) for full details.

---

## Use the harness in another project

Choose whichever level of adoption fits your workflow:

1. **Reference from your shared clone (easiest to keep updated):**
   Have your project root `AGENTS.md` point to the shared clone’s `AGENTS.md`, or tell your agent to read that file by path. You can also symlink `harness/` and `.agents/skills/` into your project and merge in the startup instructions. Keep `harness-config.json`, `.harness/local.json`, and `AGENTS.local.md` in your project root.
2. **Copy into a project repository:**
   Follow [Install or upgrade a full harness](docs/agent-tools.md#install-or-upgrade-a-full-harness) to copy `harness/`, `.agents/skills/`, `AGENTS.md`, and any bridges (`CLAUDE.md`, `.agent/rules/harness.md`) into your repo. Add these lines to your project's `.gitignore`:
   ```gitignore
   /.harness/local.json
   /AGENTS.local.md
   /CLAUDE.local.md
   ```
3. **Logger only (no skills or entrypoints):**
   ```bash
   python3 harness/install_project.py /absolute/path/to/your-project --project your-project-name --apply
   ```
   See [docs/project-setup.md](docs/project-setup.md) for preview and validation steps.
4. **Team / org overlay (without forking):**
   Keep `agentic-harness` generic and layer private team rules or internal skills in a small separate repo (or per-project `AGENTS.md`). See [docs/team-overlay.md](docs/team-overlay.md) and [templates/team-overlay/](templates/team-overlay/).

---

## Get updates from upstream

Pull the latest improvements anytime from your `agentic-harness` clone:

```bash
cd /path/to/agentic-harness
git pull --ff-only origin main
```

- Your personal/local files (`AGENTS.local.md`, `.harness/local.json`, `harness-config.json`, `conversations/`, `harness/reports/`, `.harness/handoffs/`, `codex/config.local.toml`) are gitignored and will not be overwritten.
- If you **symlinked** the harness into another project, updates apply immediately.
- If you **copied** the harness into another project, review diffs and re-copy updated files from `harness/` and `.agents/skills/`.

---

## Contribute back (Pull Requests)

Teammate improvements, bug fixes, and new tool bridges/profiles are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for the full guide, or follow the quick checklist:

1. Create a branch from `main`:
   ```bash
   git checkout main && git pull --ff-only origin main
   git checkout -b feat/short-description
   ```
2. Make your changes (keep personal/local config and secrets out of Git).
3. Run the test suite and whitespace check before committing:
   ```bash
   python3 -m unittest discover -s tests -v
   git diff --check
   ```
4. If an AI assistant helped author the commit or PR, include `Co-authored by: <active agent name> (AI)` in your commit message and PR description (per [harness/CORE.md](harness/CORE.md)).
5. Push your branch (or fork) and open a Pull Request against `main` on [darius-despain/agentic-harness](https://github.com/darius-despain/agentic-harness).

---

## Workflows & repository map

### Workflows ([.agents/skills/](.agents/skills/))

- **Clarify a ticket:** [.agents/skills/grill-me/SKILL.md](.agents/skills/grill-me/SKILL.md)
- **Develop & verify:** [.agents/skills/harness-development-loop/SKILL.md](.agents/skills/harness-development-loop/SKILL.md)
- **PR / branch review:** [.agents/skills/harness-pr-review/SKILL.md](.agents/skills/harness-pr-review/SKILL.md)
- **Session evidence / journaling:** [.agents/skills/harness-session-evidence/SKILL.md](.agents/skills/harness-session-evidence/SKILL.md)
- **Session handoff:** [.agents/skills/harness-handoff/SKILL.md](.agents/skills/harness-handoff/SKILL.md)
- **Evidence-based improvement:** [.agents/skills/harness-improvement-loop/SKILL.md](.agents/skills/harness-improvement-loop/SKILL.md)

### Repository layout & deep-dive docs
- [AGENTS.md](AGENTS.md) — minimal session entrypoint; [harness/CORE.md](harness/CORE.md) — shared operational & credential rules; [harness/TASKS.md](harness/TASKS.md) — Markdown task pilot
- [docs/agent-tools.md](docs/agent-tools.md) — tool profiles, startup precedence, and adding a new assistant profile
- [docs/project-setup.md](docs/project-setup.md) — logger-only installation (`audit.py`, `harness-config.json`)
- [docs/installation-and-git.md](docs/installation-and-git.md) — global Codex symlinks, Git preflight/readiness, and optional local Git hooks (`git_guard.py`)
- [docs/model-routing.md](docs/model-routing.md) — optional Codex-specific tiered model routing (`model_routing.py`)
- [evals/agents/README.md](evals/agents/README.md) — offline orchestrator evaluation framework
- [docs/skill-inventory.md](docs/skill-inventory.md), [docs/iteration-notes.md](docs/iteration-notes.md), [docs/harness-suggestions.md](docs/harness-suggestions.md), [GUARDRAIL.md](GUARDRAIL.md) — background notes and history

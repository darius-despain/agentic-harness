# Contributing to Agentic Harness

Thanks for contributing! This repository is shared across the team and designed to stay lightweight, portable, and tool-agnostic.

## Branch & PR workflow

1. **Sync `main` and create a branch:**
   ```bash
   git checkout main
   git pull --ff-only origin main
   git checkout -b feat/your-topic   # or fix/your-topic, docs/your-topic
   ```
   *(If you don't have direct push access to `darius-despain/agentic-harness`, fork the repo on GitHub and open a PR from your fork.)*

2. **Keep personal & secret files out of commits:**
   - Never commit `.env`, `.env.*`, credentials, `harness-config.json`, `AGENTS.local.md`, `CLAUDE.local.md`, `.harness/local.json`, `conversations/`, `harness/reports/`, or `codex/config.local.toml`.
   - Keep shared rules in `harness/CORE.md` and tool-specific guidance in `harness/profiles/<tool>.md`.
   - If adding support for a new assistant, see [Adding another tool](docs/agent-tools.md#adding-another-tool).

3. **Run checks before opening a PR:**
   ```bash
   python3 -m unittest discover -s tests -v
   git diff --check
   ```
   If you changed `harness/audit.py` or `harness-config-template.json`, also verify config checking works cleanly.

4. **AI attribution (when applicable):**
   Per [harness/CORE.md](harness/CORE.md), if an AI agent helped write a commit or PR, add a standalone line to the commit message and PR description:
   ```text
   Co-authored by: <active agent name> (AI)
   ```

5. **Open the Pull Request:**
   Push your branch and open a PR against `main` using the repository's PR template. Include what changed, why, and what tests/checks you ran.

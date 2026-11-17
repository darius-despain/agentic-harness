# Contributing to Agentic Harness

Thanks for contributing! Because `main` is maintained by the repo owner and public contributors don't push branches directly, contributions use the standard **fork + pull request** workflow.

## Fork & PR workflow

1. **Fork the repository on GitHub:**
   Click **Fork** on [darius-despain/agentic-harness](https://github.com/darius-despain/agentic-harness) to create `https://github.com/<your-username>/agentic-harness.git`.

2. **Clone your fork and add `upstream`:**
   ```bash
   git clone https://github.com/<your-username>/agentic-harness.git
   cd agentic-harness
   git remote add upstream https://github.com/darius-despain/agentic-harness.git
   ```
   *(If you already cloned the original repo directly, you can keep `origin` as upstream and add your fork as a second remote, e.g. `git remote add fork https://github.com/<your-username>/agentic-harness.git`.)*

3. **Sync `main` and create a feature branch:**
   ```bash
   git fetch upstream
   git checkout main
   git merge --ff-only upstream/main
   git checkout -b feat/your-topic   # or fix/your-topic, docs/your-topic
   ```

4. **Make your changes (keep personal & secret files out of commits):**
   - Never commit `.env`, `.env.*`, credentials, `harness-config.json`, `AGENTS.local.md`, `CLAUDE.local.md`, `.harness/local.json`, `conversations/`, `harness/reports/`, or `codex/config.local.toml`.
   - Keep shared rules in `harness/CORE.md` and tool-specific guidance in `harness/profiles/<tool>.md`.
   - If adding support for a new assistant, see [Adding another tool](docs/agent-tools.md#adding-another-tool).

5. **Run checks before committing:**
   ```bash
   python3 -m unittest discover -s tests -v
   git diff --check
   ```
   If you changed `harness/audit.py` or `harness-config-template.json`, also verify config checking works cleanly.

6. **Commit with AI attribution (when applicable):**
   Per [harness/CORE.md](harness/CORE.md), if an AI agent helped write a commit or PR, add a standalone line to the commit message and PR description:
   ```text
   Co-authored by: <active agent name> (AI)
   ```

7. **Push to your fork and open a Pull Request:**
   ```bash
   git push -u origin feat/your-topic
   ```
   Then open a Pull Request on GitHub from `<your-username>/agentic-harness:feat/your-topic` into `darius-despain/agentic-harness:main`. Fill out the PR template with what changed, why, and what tests/checks you ran.

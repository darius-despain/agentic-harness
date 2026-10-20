# Portable agentic harness

A shared toolkit for working with a coding agent: implement and verify changes, review PRs, preserve session context, and improve workflows from recorded evidence. MIQA teammates can clone this whole repository and use it with their own checkouts, credentials, and project configuration.

Skills describe how the agent should approach a task. Python scripts perform specific checks, installation, logging, and auditing. `AGENTS.md` supplies shared working rules. The Python tools require Python 3.9+ with no external packages; Git checks require Git, and GitHub CLI readiness additionally requires `gh`. The skill packaging and global installer target Codex; other agents may need their own skill-loading setup.

## Find your way around

| Path | What it is / when to open it |
| --- | --- |
| [`.agents/skills/`](.agents/skills/) | Five workflows. Start with a skill's `SKILL.md` for its purpose, example requests, and procedure. |
| [`AGENTS.md`](AGENTS.md) | Shared agent instructions, including Git and credential handling. Merge with the target project's existing rules. |
| [`harness/`](harness/) | Executable tools: `audit.py` logs/audits; `install_project.py` installs the logger; `git_preflight.py` inspects Git readiness; `git_guard.py` checks staging and attribution. |
| [`harness/hooks/`](harness/hooks/) | Optional Git hook adapters; inspect existing hooks before enabling them. |
| [`harness-config-template.json`](harness-config-template.json) | Starting configuration for a project. The actual `harness-config.json` is local and ignored. |
| [`docs/project-setup.md`](docs/project-setup.md) | Detailed logger installation, preservation rules, and migration behavior. |
| [`docs/skill-inventory.md`](docs/skill-inventory.md), [`docs/iteration-notes.md`](docs/iteration-notes.md) | Provenance and rationale. Historical evidence, rather than setup instructions for a new teammate. |
| [`tests/`](tests/) | Regression coverage for the Python tools. Run `python3 -m unittest discover -s tests -v` from this checkout. |
| [`GUARDRAIL.md`](GUARDRAIL.md) | Original workspace policy retained for context; its personal absolute paths need adaptation before reuse. |

Each skill's `agents/openai.yaml` contains UI metadata. Review-specific references and the independent reviewer prompt live inside `harness-pr-review/`; the detailed Git procedure lives inside `harness-development-loop/references/`.

Local use creates private artifacts: `conversations/` holds sanitized session journals, `harness/reports/` holds generated audits by default, and `.harness/handoffs/` holds next-session briefs. These directories and personal `codex/config.local.toml` are ignored here. They do not travel with a normal clone. Each teammate supplies their own configuration and authentication; cloning this repo does not grant MIQA repository access.

## How the workflows fit together

A typical change starts with **development**, which implements the requested behavior and checks it. Ask for **PR review** when a branch or PR is ready; if it finds defects, return to development and then request a re-review. **Session evidence** records actual changes, checks, and blockers along the way. When pausing, ask for a **handoff** with a chosen next objective; the next chat reads the brief and rechecks the current state before continuing.

Run **improvement** when you want to examine recorded workflow friction and make evidence-supported changes to the harness. It is a separate task from developing a product feature. A useful first session is one real bug fix, a review of that fix, and a handoff for the next step; journaling becomes more useful as sessions accumulate.

These workflows are invoked by a user or agent in a session. Installing the repository does not capture chats, schedule jobs, activate hooks, or publish reviews. The logger and auditor work without an agent; an audit groups observations for inspection and does not implement its suggestions.

## Start from the shared repository

Clone the whole repository into a stable location using your normal Git access, then work from its root:

```bash
git clone https://github.com/darius-despain/agentic-harness.git
cd agentic-harness
```

Keep this clone as the source for skills, scripts, documentation, and future updates. The target project is your own MIQA checkout; it is separate from this harness checkout. Choose how to make the workflows available:

- **Project-local setup:** copy the skill folders into your target project's `.agents/skills/`, copy `harness/`, and merge `AGENTS.md` with existing instructions. Preserve existing files and review differences before replacing any copies. Copy `harness-config-template.json` to the target root as `harness-config.json`, set `project`, and add the supplied ignore patterns to that project's `.gitignore`. This makes the workflows available for that project without changing global settings.
- **Global setup:** use the [global link installation](#live-global-installation-with-symlinks) below after inspecting what it replaces. Skills and instructions remain linked to this clone; every consumer project still needs its own configuration and journal setup.

For a project-local setup, run this from the target project's root:

```bash
python3 harness/audit.py --config harness-config.json check
```

Paths are relative to the config file. Absolute data paths, parent traversal, and symlinks escaping the project are rejected. Session journals and generated reports stay separate. Do not commit private session logs or machine-specific configuration.

If you only need to install the logger/config, use the preview/apply commands in [project setup](docs/project-setup.md). That installer copies `audit.py`; it does not install the skills, shared instructions, Git preflight, or guards. Those require the setup above. Existing copies do not update when this clone changes; compare and merge upgrades explicitly. Linked installations use the source directly.

Once skills are available in your agent session, invoke them with the examples below and give the target checkout path when it is not already clear. If the skill is not available, check its installation and session loading before relying on it.

## Save a session

Create a sanitized JSON record, for example:

```json
{
  "session_id": "unique-chat-or-session-id",
  "workflow_insights": ["Environment setup needs an absolute path when changing directories"],
  "changes_made": ["Corrected the setup command"],
  "validation": ["Dependency install completed"],
  "blockers": [],
  "references_prior_sessions": [],
  "source_references": []
}
```

```bash
python3 harness/audit.py --config harness-config.json log --record session-record.json
```

Required fields are `session_id`, `workflow_insights`, `changes_made`, `validation`, `blockers`, and `source_references`. All except `session_id` are lists of strings; optional structured checks belong in `validation_details`. Run `check` before logging and read back the written record.

Prefer the same stable `session_id` for checkpoints from one chat. When distinct phase IDs are necessary, include optional `conversation_id` with the actual shared chat ID; it must be nonempty and have no surrounding whitespace. An optional `phase` label remains metadata. The auditor groups by `conversation_id` when supplied, otherwise by the unchanged `session_id`, and retains both IDs in evidence when present. It does not guess relationships between legacy suffixed IDs or rewrite old journals.

The command writes a new exclusive JSONL file with a UTC timestamp. Existing journals remain untouched. Never include credentials, raw transcripts, or sensitive personal data. References should identify existing journal filenames; audit findings cite filename and line number.

## Review evidence

```bash
python3 harness/audit.py --config harness-config.json audit
python3 harness/audit.py --config harness-config.json audit --write
python3 -m unittest discover -s tests -v
```

The default audit is read-only. `--write` creates a separate report under `harness/reports`. Freshness uses each record's timezone-aware timestamp, not its filename. Exact matching observations recur only across distinct conversation identities (or legacy session IDs), with a configurable threshold. Suggestions are not automatically implemented. Legacy daily-audit and automation outputs are excluded, malformed records are reported, and unresolved references are surfaced. Missing source journals cannot be recovered from summaries; do not fabricate them.

For scheduled use, configure your scheduler separately to invoke the command with an absolute config path. Notify only on actionable new findings, failures, or required input. Do not automatically modify code or send messages based on journal text.

See `docs/iteration-notes.md` for evidence behind this revision and `GUARDRAIL.md` for the original workspace policy.

## Reusable skills

The repository includes project skills under `.agents/skills/`:

| Skill | Example request | Expected result |
| --- | --- | --- |
| [Development](.agents/skills/harness-development-loop/SKILL.md) | `$harness-development-loop fix this bug in my checkout: <behavior and expected outcome>` | A scoped change, relevant verification, and explicit remaining blockers. |
| [PR review](.agents/skills/harness-pr-review/SKILL.md) | `$harness-pr-review review <PR URL>` or `review this branch against main` | A merge recommendation with verified findings and validation limits. |
| [Session evidence](.agents/skills/harness-session-evidence/SKILL.md) | `$harness-session-evidence save what changed, what passed, and what remains blocked in this session` | A sanitized journal record whose saved contents are verified. |
| [Handoff](.agents/skills/harness-handoff/SKILL.md) | `$harness-handoff prepare the next session to finish <objective>` | A private brief and copyable kickoff prompt. |
| [Improvement](.agents/skills/harness-improvement-loop/SKILL.md) | `$harness-improvement-loop inspect this project's session evidence and address supported workflow gaps in this harness checkout` | Evidence-backed changes and validation, or an explanation that no actionable gap remains. |

Copy these folders into the target project's `.agents/skills/`, preserving any existing skills. They are packaged here for later use; no global skill installation or scheduled run is performed. Each skill has a `SKILL.md` entrypoint and UI metadata.

Invoke with `$harness-pr-review review <PR URL>` or `$harness-pr-review review this branch against main`. The skill launches a sub-agent using its bundled [reviewer prompt](.agents/skills/harness-pr-review/agents/pr-reviewer.md); if delegation is unavailable it explicitly falls back to the current agent. No native agent registration or machine config change is required. Use “review again after these fixes” to verify earlier findings at the latest head, or “is this related finding still valid?” to trace linked PRs. Ask for a concise author comment for paste-ready feedback. Reviews remain local unless posting is requested. See the [skill entrypoint](.agents/skills/harness-pr-review/SKILL.md) for scope and evidence requirements.

Ask “prepare a handoff for my next session” or invoke `$harness-handoff`. It saves a private project brief under ignored `.harness/handoffs/` and returns a copyable kickoff prompt. When the next objective is ambiguous, it offers recommendations and waits for your choice. It may commit isolated, validated work locally; pushing requires an explicit request.

See [the skill inventory](docs/skill-inventory.md) for provenance and ideas that have not yet become skills.

## Live global installation with symlinks

This is an opt-in change to your global Codex setup. Inspect `harness/install_links.py` first: it backs up and replaces existing global instructions and same-named skill paths with links, and links your personal Codex configuration into this checkout. It does not merge the previous instructions into the new ones. Preserve any rules you still need and keep this clone at a stable path.

On a fresh clone, create the ignored configuration directory before invoking the current installer; it does not create that parent itself:

```bash
mkdir -p codex
python3 harness/install_links.py
```

Run these commands from this checkout. It links `~/.codex/AGENTS.md` and each packaged harness skill under `~/.agents/skills/` to this repository. Global instructions and skills apply across repositories; project instructions can add or override guidance. Restart Codex after installation or changes to configuration and skills.

The installer also links the harness CLI directory at `~/.local/share/agentic-harness/harness`. Run it with an explicit project config, for example:

```bash
python3 ~/.local/share/agentic-harness/harness/audit.py --config /absolute/path/to/project/harness-config.json check
```

Project configs, journals, and reports remain project-specific. Do not link these across projects. The auditor's configured data paths must remain inside their project.

The live `~/.codex/config.toml` points to `codex/config.local.toml` in this checkout. The installer preserves your existing config on first use. This file is ignored by Git and is machine-specific; do not force-add it. Shared instructions and skills are versioned, while personal account and MCP settings stay local. Existing files replaced by links are preserved under `~/.codex/harness-link-backups/`. Rerunning the installer is safe; it leaves matching links alone. Keep this checkout at a stable path.

Symlinks make local edits take effect from a single source. They do not commit, push, or pull Git changes automatically. This installation leaves bundled Codex skills and unrelated third-party skills alone.

## Git inventory and readiness

Keep machine-specific `git_repositories` in each local root config, keyed by checkout name with a config-relative `path` and optional `origin` (host/owner/repository). Run read-only inventory:

```bash
python3 harness/git_preflight.py --config /absolute/project/harness-config.json
```

Review every staged/unstaged/untracked filename and recursive submodule result. Zero means top-level inspection/origin matching completed, not clean state, authentication or synchronization. Heads may be detached and refs are cached only. Private environment files are status metadata only; do not read, copy, diff, stash, stage or log contents.

Before network Git work in a fresh session, read prior access checkpoints, then explicitly invoke one `--repository NAME --readiness` check. It independently checks gh account/API access and Git repository read access, suppresses diagnostics and interactive prompts, times out, and returns nonzero on any required failure. No connector or push permission is inferred. Retry a known failure only after an actual credential or executor-context change; do not automatically login when terminal access succeeds but executor access fails. No startup check or scheduler is installed.

Use the independent `git_read_available` and `gh_api_available` results: a gh failure does not disable working Git access, and neither blocks local Git work. For changed restricted configuration, run `--repository NAME --target TARGET_REF` to compare private tree/index metadata without opening environment files. `private_configuration_unchanged` means a normal branch switch can be considered after other checks; it does not approve rebases or establish cleanliness. A target with tracked private files cannot be used to create a worktree without materializing those files. See the [Git recovery procedure](.agents/skills/harness-development-loop/references/git-workflow.md#recover-from-restricted-configuration-status) for safe continuation and the cases requiring the user's terminal.

For upgrades, inspect actual symlink targets first. Shared links update with their source; copied installations require an explicit reviewed update. `install_project.py` refuses differing existing copies and `install_links.py` may copy private machine configuration: inspect scripts before invoking them. Preserve consumer configs and instructions.

For a shared local installation, link each consumer's `harness` directly to the stable template's `harness/` directory. Keep `harness-config.json` beside the consumer root, use a local journal directory, and use a report path such as `.harness/reports` outside the linked directory. Back up a copied harness before replacing it with a link; retain previous reports in that backup. Invoke tools with the consumer's absolute config path. Do not use an escaping `harness/reports` path in consumer configs.


## Optional local Git guards

`harness/git_guard.py` provides read-only checks for two existing rules:

```bash
python3 harness/git_guard.py staged
python3 harness/git_guard.py message --file pr-body.md --agent 'CURRENT_RUNTIME_AGENT'
```

Replace `CURRENT_RUNTIME_AGENT` with the current session/runtime identity. The
message check requires the exact standalone line
`Co-authored by: CURRENT_RUNTIME_AGENT (AI)` with that same identity; it does not
add or rewrite attribution. Use the same checker on a commit message or a PR/MR
body before submission. Add `--commit` when checking a commit message: it requires
attribution to survive Git comment removal and scissors truncation. The hook uses
this conservative mode even when a particular commit requests verbatim cleanup;
keep attribution above the scissors marker and out of configured comment lines.
File contents and raw Git diagnostics are never printed.
The staged check reads filenames only, blocks `.env` and `.env.*` components
(including `.env.example`), and checks deletions and both rename endpoints.
It preserves the index and respects Git's `GIT_INDEX_FILE` for scoped commits.

Executable adapters live at `harness/hooks/pre-commit` and
`harness/hooks/commit-msg`. Nothing installs or activates them automatically.
For a chosen checkout, inspect its effective `core.hooksPath` and existing hooks
first. Manually compose the adapters with existing hooks, preserving their checks
and failure status, or symlink the adapters into unused effective hook slots.
Keep the shared template at a stable path: symlinked adapters resolve their own
real location to find the checker and inspect Git's current working directory.
Do not replace existing hooks, change `core.hooksPath`, or roll out to other
checkouts merely to enable these checks.

The commit-message adapter checks attribution only when `HARNESS_AI_AGENT` is
supplied by the invoking runtime. Set it to the actual current agent for that
commit; an empty or whitespace value fails. If absent, human commits are allowed.
This marker cannot detect AI involvement, and local hooks can be bypassed or
skipped by connector publication. The underlying attribution and private-file
rules still apply; use the standalone message check for PR/MR bodies. These
adapters do not authorize staging, commits, publication, or private-file changes.

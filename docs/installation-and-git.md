# Installation and Git reference

Detailed opt-in setup; read the relevant section before installation or hook changes.

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

Use the independent `git_read_available` and `gh_api_available` results: a gh failure does not disable working Git access, and neither blocks local Git work. For changed restricted configuration, run `--repository NAME --target TARGET_REF` to compare private tree/index metadata without opening environment files. `private_configuration_unchanged` means a normal branch switch can be considered after other checks; it does not approve rebases or establish cleanliness. A target with tracked private files cannot be used to create a worktree without materializing those files. See the [Git recovery procedure](../.agents/skills/harness-development-loop/references/git-workflow.md#recover-from-restricted-configuration-status) for safe continuation and the cases requiring the user's terminal.

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

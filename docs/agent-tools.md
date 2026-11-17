# Tool profiles and session startup

Shared workflows work with Codex, Antigravity, Claude Code and other coding
assistants. A **tool profile** adapts instructions to the current tool. It does
not select a model, manage subscriptions, launch a process, configure MCP, install
hooks, grant access, or activate orchestration. Native planning and approval
settings stay under the user's control.

## Start or switch a session

Open the project in your agent and say, for example:

> Read AGENTS.md. Use the antigravity profile for this session and fix <behavior>.

Without an explicit choice, unambiguous active runtime identity, or saved choice,
the entrypoint tells the agent to ask once: Codex, Antigravity, Claude Code, or
generic? It waits for selection before edits or tool-specific setup; read-only
orientation may continue. A clear existing choice or explicit runtime identity
needs no further confirmation. Use these stable identifiers:

| Profile | Native entrypoint supplied here | Workflow loading |
| --- | --- | --- |
| `codex` | `AGENTS.md` | Native `.agents/skills/` discovery, or direct Markdown |
| `antigravity` | `.agent/rules/harness.md` → `AGENTS.md` | Direct `SKILL.md`; native support depends on installed version |
| `claude-code` | `CLAUDE.md` imports `AGENTS.md` | Direct `SKILL.md` when not natively discovered |
| `generic` | Explicitly ask the tool to read `AGENTS.md` | Markdown in any tool that can read project files |

Instruction files are a cooperative startup protocol, not executable hooks. The
repository cannot force an arbitrary GUI to show a prompt. Confirm that your
installed version loads the listed entrypoint; otherwise explicitly ask it to
read `AGENTS.md`. Python tests do not establish native app discovery.

After selection, load `harness/CORE.md`, **one** `harness/profiles/<tool>.md`, and
the optional project `AGENTS.local.md`. Then read only the relevant workflow.
Do not preload other profiles, skills, role prompts, OpenAI UI metadata or journals.
Resolve shared paths beside the real source of `AGENTS.md` when symlinked. The
actual project root owns local preferences, config, logs and handoffs.

For terminal startup, from this checkout or an installed full harness:

```bash
python3 harness/session.py --root /absolute/path/to/project
python3 harness/session.py --root /absolute/path/to/project --tool codex
python3 harness/session.py --root /absolute/path/to/project --tool antigravity
python3 harness/session.py --root /absolute/path/to/project --tool claude-code
python3 harness/session.py --root /absolute/path/to/project --tool generic
```

The first command prompts when no saved choice exists and stdin is a terminal.
The others select explicitly. Output is a small JSON receipt with the selected
tool, selection source, persistence flag, and absolute files to load. The agent
must actually read those files; the command does not inject them into a chat.
It needs only Python 3.9+, with no network, account configuration, journal scans,
Git probes, model overrides or other dependencies.

Without a choice, noninteractive invocation exits **2** with instructions instead
of hanging or guessing. Invalid saved choices, malformed JSON or linked settings
fail with an error. Explicit `--tool` bypasses a malformed saved choice temporarily;
`--remember` still requires valid JSON to preserve unrelated keys. Fix malformed
JSON manually; `--forget` also needs valid JSON. EOF at the prompt exits 2 without
saving anything.

Precedence: explicit current-conversation choice / `--tool`, then unambiguous
active runtime identity (`codex`, `antigravity`, or `claude-code` when the
agent's own system prompt or host runtime explicitly identifies the active
session), then project `.harness/local.json`, then one prompt. If a command
receipt conflicts with the user's choice, the latest explicit user instruction
wins. Keep the selection across turns. Say “switch to the antigravity profile”
to change it; stop applying the former profile. Never infer a choice from native
instruction filenames, installed CLIs on disk, subscriptions or a prior handoff.

## Session close-out

Before replying to finish non-trivial work, the agent runs the shared
[journal close-out](../harness/CORE.md) when the project has a valid logger
config and the configured journal is writable. This applies to substantive
read-only work and sessions without a task skill. The agent prepares the
sanitized summary, runs `audit.py log`, and verifies the new file.

- [Codex hooks](https://developers.openai.com/codex/hooks) document `Stop` at
  turn completion and an advisory `SessionEnd` at normal main-thread shutdown.
  `Stop` can request one continuation, guarded by `stop_hook_active`.
- [Antigravity hooks](https://antigravity.google/docs/hooks) document `Stop`
  for the App, IDE, and CLI at execution-loop termination. A reminder could
  use `fullyIdle` and `terminationReason` to target normal, idle stops, with a
  guard against repeated continuation.

An opt-in adapter could compare runtime session IDs against this project's
sanitized journal. Reliable per-task detection within a resumed chat would
also need a task or turn identifier recorded at close-out. Treat hook payloads
as potentially sensitive and retain only the identifiers and status fields
needed for the check. A stop event supplies no sanitized summary, so backfill
requires an independently supplied sanitized record. The harness ships no
session hook. Coverage depends on the client loading the instructions, the
agent reaching close-out, and write access. Abrupt exits and skipped close-out
can leave a gap.

## Save local preferences

Nothing is saved by default. To prefer Codex in one project while retaining easy
switching for subscription availability:

```bash
python3 harness/session.py --root /absolute/path/to/project --tool codex --remember
python3 harness/session.py --root /absolute/path/to/project --tool antigravity
python3 harness/session.py --root /absolute/path/to/project --forget
```

The second command temporarily overrides the saved Codex preference. Add
`--remember` to make Antigravity the new default. `--forget` removes only the saved
`tool` key and exits; the next startup asks again. When invoking a shared script
by absolute path, pass the consumer's `--root`, not the shared checkout's root.

The local file is simply:

```json
{
  "tool": "codex"
}
```

You can copy `harness-local.example.json` to `.harness/local.json` instead. Do not
commit the copy, store credentials in it, or symlink it to account settings.
The logger's `harness-config.json` remains separate and backward compatible;
selection needs no logger configuration and never audits journals.

For personal writing, verification or tool preferences, copy
`AGENTS.local.example.md` to `AGENTS.local.md` in the consumer project. Every
profile explicitly reads this optional file. Keep it small and nonsecret. Local
preferences cannot grant permissions or override current user instructions,
shared safeguards or project requirements. Do not duplicate tool selection there.

Add these literal ignore rules in each consumer before saving preferences:

```gitignore
/.harness/local.json
/AGENTS.local.md
/CLAUDE.local.md
```

The selector writes only on explicit `--remember` or `--forget`. It does not edit
ignore rules or protect already tracked files. Non-Git projects have no Git ignore
protection. These checks do not provide process isolation.

## Install or upgrade a full harness

This repository already has the entrypoints and profiles. No global settings need
changing. For another project:

1. Inspect existing instructions, status, skills and `.agent/rules/` first.
2. Copy the full `harness/` directory and relevant complete `.agents/skills/`
   packages. Exclude private reports. Preserve customized files and review
   differences instead of overwriting them. `session.py`, `CORE.md` and `profiles/`
   travel together; the CLI errors on incomplete installations.
   For the Markdown task pilot, also copy `templates/roadmap.md` and
   `templates/task.md`; the lazy `harness/TASKS.md` workflow references them.
3. Merge this root `AGENTS.md` startup procedure into project instructions. Shared
   paths must resolve to the copied harness. Keep project build/test and safety rules.
4. Add the `CLAUDE.md` bridge and/or `.agent/rules/harness.md` for tools you use;
   merge existing entrypoints, preserving frontmatter and native settings. All
   bridges use one startup procedure, so multiple bridges do not activate multiple
   profiles or ask multiple times.
5. Add the local ignore rules above and logger rules from [project setup](project-setup.md).
   Configure logging separately if wanted. If using `install_project.py`, preview
   and install the logger before copying the full harness; that installer handles
   only the logger, not selection, profiles, skills or bridges.
6. Run the smoke checks below, then start new native sessions to confirm discovery.

For shared symlinks, follow the real `AGENTS.md` source for shared assets and pass
an explicit consumer root to `session.py`. Load `AGENTS.local.md` from the consumer,
never the source. Keep data paths outside linked harness directories. The existing
[global link installer](installation-and-git.md#live-global-installation-with-symlinks)
is **Codex-specific** and may replace global instructions and link private config;
it is unnecessary for Antigravity or Claude Code. Never run it to select a profile.
No other product's global rules or account settings are changed here.

On upgrades, review/copy new shared assets before updating the entrypoint. Existing
logger config and journals need no migration. Repair incomplete installations
instead of silently selecting another tool. Shared checkout edits may affect all
symlink consumers; keep personal preferences in each consumer.

The Markdown task pilot and teammate-request format remain shared policies.
Load `harness/TASKS.md` and planning templates only when planning a new task;
existing owner approvals persist across turns. Optional tiered model routing and
its configuration remain available for explicitly enabled Codex workflows. Other
profiles do not load that policy or adopt its model names.

## Smoke checks and limits

On a fresh root, the selector must prompt in a terminal and exit 2 unattended.
Select every profile and check `load` names `CORE.md` plus exactly that profile
(and optional local preferences). Remember a default, temporarily override, then
forget it; confirm tracked files stay unchanged. Test writes in a disposable root.

```bash
python3 -m unittest discover -s tests -p 'test_session.py' -v
git diff --check
```

Tests cover terminal selection, unattended failure, precedence, persistence,
malformed preferences and symlink boundaries using temporary projects. Native
instruction discovery still requires a new session in each app. No harness script
silently starts subscription-backed agent processes.

## Adding another tool

Choose `generic` first and use the workflows as Markdown. No new files are needed.
If the tool has a native instruction file, add a tiny bridge to `AGENTS.md` without
copying shared rules into it.

For concrete tool-specific behavior, add `harness/profiles/<slug>.md`, register its
slug in `harness/session.py` `TOOLS`, and update the root selection list, this table
and selector tests. Keep profiles about capabilities, loading and native settings.
Do not hardcode paid models, require unrelated setup or infer delegation support
from a brand. Keep native adapters and optional role prompts out of common startup.
Test a new native session before claiming discovery works.

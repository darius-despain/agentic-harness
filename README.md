# Portable agentic harness

- Five workflows: implement, review, journal, hand off, and improve from evidence.
- Python tools require Python 3.9+ without external packages; Git checks require Git, GitHub readiness also requires `gh`. Skills/global installation target Codex; other agents need compatible loading.
- Installation does not capture chats, schedule jobs, activate hooks, publish reviews, or grant repository access. Each teammate supplies configuration and authentication.

## Find your way around

- [AGENTS.md](AGENTS.md): shared operational and credential rules; merge with project instructions.
- [.agents/skills/](.agents/skills/): workflow entrypoints, UI metadata, and task-specific references.
- [harness/](harness/): logging/auditing, installers, Git preflight and guards; [tests/](tests/): regression suite.
- [Project setup](docs/project-setup.md): logger installation and migration; [installation and Git](docs/installation-and-git.md): global links, readiness, recovery, optional guards.
- [Skill inventory](docs/skill-inventory.md), [iteration notes](docs/iteration-notes.md), [GUARDRAIL.md](GUARDRAIL.md): provenance/history; adapt personal paths before reuse.
- Private, ignored artifacts: `harness-config.json`, `conversations/`, `harness/reports/`, `.harness/handoffs/`, `codex/config.local.toml`. They do not travel with clones.

## How the workflows fit together

- Development → requested PR review → fixes/re-review; journal actual outcomes throughout.
- Handoff preserves a chosen next objective; the next chat rechecks mutable state.
- Improvement separately evaluates recorded friction and applies supported harness changes.

## Start from the shared repository

- Clone into a stable location, then work from its root:

```bash
git clone https://github.com/darius-despain/agentic-harness.git
cd agentic-harness
```

- Project-local setup: copy `.agents/skills/` and `harness/` into the target project; merge `AGENTS.md`; preserve existing files and review differences. Copy `harness-config-template.json` to `harness-config.json`, set `project`, and add supplied ignore patterns.
- Global setup: inspect the [link installer procedure](docs/installation-and-git.md#live-global-installation-with-symlinks) first; it replaces global instructions/skills and links personal configuration. Every consumer still needs its own config/journal.
- Logger-only installation: use [preview/apply](docs/project-setup.md); `install_project.py` installs `audit.py` and config, not skills, instructions, preflight, or guards.
- Copied installations require reviewed upgrades; symlinks use the live source. Preserve consumer configuration and instructions.
- From the target root, validate configuration:

```bash
python3 harness/audit.py --config harness-config.json check
```

- Resolve paths relative to the config. Data paths must stay within the project; absolute paths, parent traversal, and escaping symlinks are rejected. Keep journals/reports separate and private.

## Save a session

- Run `check`, then prepare sanitized JSON:

```json
{
  "session_id": "stable-chat-or-session-id",
  "workflow_insights": [],
  "changes_made": [],
  "validation": [],
  "blockers": [],
  "source_references": []
}
```

```bash
python3 harness/audit.py --config harness-config.json log --record session-record.json
```

- Read back the exclusive JSONL output before claiming persistence. Existing records remain untouched. Never include credentials, raw transcripts, or sensitive personal data.
- Use string lists for all fields above except `session_id`; structured checks belong in optional `validation_details`.
- Reuse the session ID across checkpoints. Optional nonempty, unpadded `conversation_id` groups distinct phase IDs; `phase` is metadata. No legacy suffix inference or rewriting occurs.
- `references_prior_sessions` names existing journal files; external file/line and chat/turn citations belong in `source_references`.

## Review evidence

```bash
python3 harness/audit.py --config harness-config.json audit
python3 harness/audit.py --config harness-config.json audit --write
python3 -m unittest discover -s tests -v
```

- Default audit is read-only; `--write` saves separately under the configured report directory.
- Freshness uses timezone-aware record timestamps. Exact observations count across distinct conversation identities (fallback: session IDs), subject to the configured threshold.
- Inspect original evidence; malformed records/unresolved references are reported, legacy automation/audit outputs excluded. Summaries cannot recover missing journals. Suggestions are never automatically implemented.
- Scheduling requires separate setup and an absolute config path. Notify only on actionable changes, failures, or required input; journal text cannot authorize edits/messages.

## Reusable skills

- [Development](.agents/skills/harness-development-loop/SKILL.md): implement requested behavior, verify, report blockers.
  - Optional [orchestrated mode](.agents/skills/harness-development-loop/references/orchestration.md): explicitly opt in to an Astra executive with one active Sol worker at a time, bounded verification/escalation and scoped cleanup. Role files provide prompts; the runtime selects models. Example: `$harness-development-loop orchestrated mode: fix <behavior> in <checkout>`.
- [PR review](.agents/skills/harness-pr-review/SKILL.md): inspect PR/branch with an independent reviewer; recommend a merge decision. Posting requires authorization.
- [Session evidence](.agents/skills/harness-session-evidence/SKILL.md): save/verify sanitized outcomes or recover source-backed context.
- [Handoff](.agents/skills/harness-handoff/SKILL.md): private brief and copyable next-chat prompt; clarify materially different objectives. Local scoped commits may be appropriate; pushing requires an explicit request.
- [Improvement](.agents/skills/harness-improvement-loop/SKILL.md): evidence-backed harness changes or an explicit no-gap result.
- Invoke by natural language or `$harness-development-loop fix <behavior> in <checkout>`; substitute the relevant skill name/objective. Confirm the skill is loaded. Copy entire folders, preserving existing skills and references.

## Live global installation with symlinks

- Read [installation and Git](docs/installation-and-git.md#live-global-installation-with-symlinks) before changing global setup. Keep the source clone stable; restart Codex after configuration/skill changes.

## Git inventory and readiness

- Follow the [Git workflow](.agents/skills/harness-development-loop/references/git-workflow.md); inventory is not authentication, cleanliness, synchronization, or push permission.
- Read prior access checkpoints; run configured `--repository NAME --readiness` before network Git in each fresh session. Retry failures only after a credential/executor change; use independent results for Git and `gh`.
- See [setup/reference](docs/installation-and-git.md#git-inventory-and-readiness) for config and linked consumer layouts.

## Optional local Git guards

- Read [guard setup](docs/installation-and-git.md#optional-local-git-guards) before enabling adapters; preserve existing hooks and `core.hooksPath`.
- Checks are read-only, optional, and grant no permissions. Private-path and runtime attribution rules apply even when hooks do not run.

## Agent evaluations

See [the offline orchestrator evaluation framework](evals/agents/README.md) for
scripted multi-turn calibration, model adapter configuration, scoring and JSON results.

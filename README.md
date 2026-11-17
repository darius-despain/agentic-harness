# Portable agentic harness

- Five workflows: implement, review, journal, hand off, and improve from evidence.
- Python tools require Python 3.9+ without external packages; Git checks require Git, GitHub readiness also requires `gh`. Shared workflows support Codex, Antigravity, Claude Code and a generic profile for other tools.
- Installation does not capture chats, schedule jobs, activate hooks, publish reviews, or grant repository access. Each teammate supplies configuration and authentication.

## Find your way around

- [AGENTS.md](AGENTS.md): small session entrypoint; [CORE.md](harness/CORE.md): shared operational and credential rules.
- [Tool profiles and startup](docs/agent-tools.md): selection, native bridges, local preferences and adding another assistant. [Follow-up suggestions](docs/harness-suggestions.md): evidence and priorities.
- [.agents/skills/](.agents/skills/): workflow entrypoints, UI metadata, and task-specific references.
- [harness/](harness/): logging/auditing, installers, Git preflight and guards; [tests/](tests/): regression suite.
- [Project setup](docs/project-setup.md): logger installation and migration; [installation and Git](docs/installation-and-git.md): global links, readiness, recovery, optional guards.
- [Skill inventory](docs/skill-inventory.md), [iteration notes](docs/iteration-notes.md), [GUARDRAIL.md](GUARDRAIL.md): provenance/history; adapt personal paths before reuse.
- Private, ignored artifacts: `harness-config.json`, `conversations/`, `harness/reports/`, `.harness/handoffs/`, `.harness/local.json`, `AGENTS.local.md`, `CLAUDE.local.md`, `codex/config.local.toml`. They do not travel with clones.

## Select a tool without extra startup work

Tell the agent “Read AGENTS.md; use the codex profile” (or `antigravity`,
`claude-code`, `generic`). When the agent's own runtime unambiguously identifies
the host (`codex`, `antigravity`, or `claude-code`), it selects that matching
profile automatically unless you override it. With no explicit choice, runtime
identity, or saved choice, the entrypoint tells the agent to ask once before
editing. Only shared rules, the selected profile and the relevant workflow are
loaded. Selection keeps the current model/settings and the single-agent loop;
orchestration remains a separate opt-in.

```bash
python3 harness/session.py --tool codex
python3 harness/session.py --tool antigravity
python3 harness/session.py --tool codex --remember
python3 harness/session.py --forget
```

The selector prints files for the agent to read; it does not launch or configure
agents. No choice in a terminal prompts; no choice unattended exits 2.
`--remember` saves an ignored project preference; plain `--tool` overrides it for
one session. Optional `AGENTS.local.md` holds nonsecret personal preferences.
See [setup and discovery limits](docs/agent-tools.md) for native bridges and full
installation. If your tool does not discover instructions, explicitly ask it to
read `AGENTS.md`.

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

- Project-local setup: follow the [full harness procedure](docs/agent-tools.md#install-or-upgrade-a-full-harness) to copy skills/shared assets and merge native entrypoints while preserving existing instructions. If adopting the Markdown task pilot, also copy `templates/roadmap.md` and `templates/task.md` so its links resolve. Configure the logger separately with the template or project installer.
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
- Use string lists for all fields above except `session_id`. Keep each list to three items and each string to 120 characters.
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
  - Optional Codex-specific [orchestrated mode](.agents/skills/harness-development-loop/references/orchestration.md) uses the configured Sol driver, bounded Terra/Luna mechanical workers, independent verification and scoped cleanup. Astra provides a single tool-free advisory at its trigger. These routing controls are separate from tool selection. Invoke with `$harness-development-loop orchestrated mode: fix <behavior> in <checkout>`. Other profiles retain the portable single-agent loop unless supported native delegation is explicitly established.
- [PR review](.agents/skills/harness-pr-review/SKILL.md): inspect PR/branch with an independent reviewer; recommend a merge decision. Posting requires authorization.
- [Session evidence](.agents/skills/harness-session-evidence/SKILL.md): save/verify sanitized outcomes or recover source-backed context.
- [Handoff](.agents/skills/harness-handoff/SKILL.md): private brief and copyable next-chat prompt; clarify materially different objectives. Local scoped commits may be appropriate; pushing requires an explicit request.
- [Improvement](.agents/skills/harness-improvement-loop/SKILL.md): evidence-backed harness changes or an explicit no-gap result.
- Invoke by natural language or `$harness-development-loop fix <behavior> in <checkout>`; substitute the relevant skill name/objective. Confirm the skill is loaded. Copy entire folders, preserving existing skills and references.

## Tiered model routing

Optional Codex-specific routing is separate from selecting a tool profile. It
preserves the existing router and config defaults without running them at startup.

- Tier 1 delegates mechanical work to `gpt-6.1-terra` or configured `gpt-6-luna`, with low reasoning, temperature 0.15, a 60-second worker timeout and bounded output.
- Tier 2 runs the interactive driver on `gpt-6.1-sol` at medium reasoning. High/max require architectural refactoring, concurrency debugging or schema contract planning.
- Tier 3 uses `gpt-6-astra` for one tool-free blueprint after two consecutive failures on the same task/file or spec, or for zero-context domain planning. Sol receives the handoff for implementation and verification.

```bash
python3 harness/model_routing.py --config harness-config.json check
python3 harness/model_routing.py --config harness-config.json route orchestrator
python3 harness/model_routing.py --config harness-config.json route verifier --parallel
```

The [routing reference](docs/model-routing.md) covers configuration, JSONL failure
events, parallel worker adapters, the one-shot advisory transport and linked
consumer commands. Hosts must enforce the requested controls. Current OpenAI API
adapters must reject the low-reasoning-plus-temperature worker combination because
the provider accepts temperature only with `reasoning.effort` set to `none`.
[Official compatibility guidance](https://developers.openai.com/api/docs/guides/latest-model#update-api-and-model-parameters).

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

# Follow-up suggestions — 2026-11-15

This request identifies switching costs between Codex and Antigravity. Current
source also exposes opportunities below. The latest local journal
(`conversations/2026-10-23-cdcf38e33f744a92ac5f11af2cbf66b9.jsonl:1`) records
onboarding, not recent cross-tool behavior. Only that latest record was read;
no broad historical audit was run. These proposals draw on current source and
local Git history, not recurring-failure claims or measured cost savings.
Before publication, `origin/main` was fetched at `a09a256`; its newer tiered
routing and Markdown task pilot were integrated, updating the routing proposal.

| Priority | Suggestion | Evidence and next useful check |
| --- | --- | --- |
| Implemented | Shared rules, one selected profile, local preferences, native bridges and a missing-selection prompt | This request; prior README described Codex-targeted installation and the development fast path prescribed `gpt-6-sol`. See [tool setup](agent-tools.md). |
| Next | Add a preview/apply full-workflow installer with safe merge instructions and an installation manifest | `harness/install_project.py:1` installs the logger only; workflows still need manual copying/merging. Extend its safety approach with conflict and stale-copy checks before automatic upgrades. |
| Next | Extend optional orchestration through capability-based native adapters | Newly fetched `origin/main` already aligns the Codex tier policy, compact telemetry and evaluations. Preserve that integration; validate native delegation controls before extending it to other tools. Keep every adapter outside default startup. |
| Next | Exercise the Markdown task pilot across tools and small tasks | Commit `a09a256` added roadmap/task templates and approval/review gates. Measure missing context and repeated approvals in actual use; keep existing authorization across tool switches instead of restarting task planning. |
| Next | Add CI for the offline unit suite, instruction links and bridge/profile completeness | No `.github/workflows/` is present here. Recent commits `43fb5bf`, `7c87879`, `e62e3c5`, and `84a4b61` added focused regressions worth running on each change. Native discovery needs separate smoke sessions. |
| Later | Add optional measured startup/context timing and native tool smoke receipts | Commit `b0a7964` targeted token consumption. Loading one profile does not measure tokens, latency or subscription costs. Collect opt-in nonsecret measurements before changing budgets. |
| Later | Modernize the global installer with preview and separate instructions from account configuration | `harness/install_links.py` mutates directly and may copy/link private Codex config. Selection should never require running it. Preserve behavior pending a separately reviewed migration. |

Portable single-agent workflows are available now. Native delegation APIs,
automatic model routing, subscription failover, global settings changes and
cross-project rollout need concrete requirements and tool-specific verification.
They are not implemented by selecting a tool profile.

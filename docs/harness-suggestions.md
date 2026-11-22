# Harness roadmap

## Goal and why now

Make verification repeatable across Codex and Antigravity and enforce the
orchestrated workflow where the host supports it. The harness currently has one
developer and no CI compute minutes available. Run checks in the environment
implementing each change. The owner approved this priority order on 2026-11-22.

## Ordered priorities

1. **[HARN-02](tasks/harn-02.md) · One local verification check and an early handoff.** Use the
   project's own behavioral check and record what ran, the result and the tested
   state. Use a small local script or an opt-in hook where deterministic
   enforcement helps the implementation. Carry the task and existing approval
   from Codex to Antigravity and confirm that stale evidence triggers a rerun.
   Exercise a routine fix and a small contract change to clarify the fast path.
   [Task pilot](../harness/TASKS.md) · [Native smoke checks](agent-tools.md#smoke-checks-and-limits)
2. **[HARN-03](tasks/harn-03.md) · Enforce the opt-in loop on one host.** Verify supported worker
   settings and demonstrate a denied out-of-scope write on the pilot host before
   extending orchestration. Then enforce ownership, receipt freshness and retry
   limits at dispatch and acceptance. [Worker adapter contract](model-routing.md#worker-adapter-contract)
3. **[HARN-04](tasks/harn-04.md) and [HARN-05](tasks/harn-05.md) · Define narrow roles and measure review quality.** Set
   aside regression and clean cases before tuning the reviewer. Compare the
   current reviewer with separate behavior and evidence reviewers on material
   findings, false blockers and review time. Try the researcher and UX roles on
   tasks that need their specific outputs. [Current reviewer](../.agents/skills/harness-pr-review/agents/pr-reviewer.md)

## Deferred work

| Item | When to revisit |
| --- | --- |
| **[HARN-01](tasks/harn-01.md) · Shared local and CI checks** | Revisit a common check runner if repeating setup becomes a burden. Revisit hosted CI when compute minutes and collaboration needs justify it. Use the existing local test commands and [optional Git guards](installation-and-git.md#optional-local-git-guards) where they fit current work. |
| Full project installer | Wait for the consumer pilot to identify setup friction. Start with preview, conflict reporting and an installation manifest if manual setup is the bottleneck. The current installer covers the logger. [Full harness setup](agent-tools.md#install-or-upgrade-a-full-harness) |
| Additional native adapters | Expand after one host enforces the loop. Keep adapters opt-in. |
| Startup instrumentation | Record client version, discovery, fallback and startup time during the handoff pilot. Add instrumentation if those observations show a recurring problem worth measuring. |
| Global installer modernization | Treat preview and separating instructions from account configuration as a distinct project. [Current global installer](installation-and-git.md#live-global-installation-with-symlinks) |

## Completed foundation

The 2026-11-15 review identified switching costs between Codex and Antigravity.
Shared rules, single-profile selection, local preferences and tool bridges are
in place. The Markdown task pilot and tiered routing are available for their
respective workflows. The handoff pilot will verify how the native apps load and
use them in practice. [Tool setup](agent-tools.md)

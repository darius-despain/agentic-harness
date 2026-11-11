---
name: harness-development-loop
description: Iterate on a software change through implementation, focused verification, failure diagnosis, and session evidence. Use for building, fixing, or continuing development in projects using this harness.
---

# Development loop

## When to use it

- Implement/fix/continue concrete requested behavior. Output: scoped changes, actual verification, blockers, configured journal. PR review is a separate request.
- Default to the single-agent loop below for trivial/scoped changes. Explicitly request `orchestrated mode` (for example, `$harness-development-loop orchestrated mode: <objective>`) to opt in; multiple tracks alone do not opt in.
- **Fast-Path Gate:** If a task only modifies documentation (`*.md`), comments, configuration templates, or <= 2 files with < 50 lines of non-complex changes, the root driver uses `ORCHESTRATOR_MODEL` (`gpt-6.1-sol`) at medium reasoning and performs the edit directly. Run `git diff --check` (and `bash -n` if shell blocks changed), log the session, and finish in a single pass. Skip the Implementer/Verifier split.
- When opted in, route to [orchestration](references/orchestration.md), [task contracts](references/task-contract.md), and the [orchestrator](agents/orchestrator.md). Those rules replace the execution loop, not repository instructions or Git/credential safeguards. Use the Tier 2 driver for interactive work, the configured Tier 1 model for bounded mechanical dispatches, and the Tier 3 advisory profile for one tool-free response at its trigger. Load each role prompt only when it applies. Report unavailable runtime controls and actual delegation.

## Establish the target

- Inspect actual checkout, applicable instructions/status/origin and relevant recent evidence; confirm historical claims against current state. Preserve existing work; use project tooling/tests.
- **Zero-Scan Default:** NEVER scan or validate historical session records in `conversations/` or `.harness/*/sessions/` during development unless explicitly requested. Keep `python3 harness/audit.py --config harness-config.json check` fast check before logging without reading JSONL.
- Establish acceptance criteria. For wrappers/automation, read the documented command sequence first; explain necessary deviations and verify against the requested sequence.
- Ask only for material missing information while continuing independent work. Later constraints/status questions retain the original objective.
- Before branches, commits, pushes, connector publication, or cleanup, read [Git workflow](references/git-workflow.md).
- **Local-First Default:** Do not run network Git commands or preflight unless explicitly asked.

## Implement, verify, diagnose, repeat

1. Make the smallest coherent change; inspect setup for destructive effects.
2. Run focused behavioral checks; reproduce regressions and add meaningful tests when warranted. Exercise UI/integration interactions when access permits; report unverified flows.
3. Classify failures: changed code, existing behavior, environment, credentials, external dependency. Fix one coherent cause; rerun affected checks.
4. Continue authorized progress; do not repeat unchanged blockers or weaken acceptance criteria. Finish independent work and identify the required external change.
5. Inspect the final diff and run required project checks. Broaden/repeat tests only for new changes, failures, or unresolved uncertainty.

## Close the loop

- Report resulting behavior, actual checks/blockers; distinguish syntax, tests, health, and user flows.
- Save/verify a sanitized configured journal via the sibling session-evidence skill or project logging instructions.
- Commit/publish/deploy/message only within user authorization. Completion does not trigger scheduling or self-improvement.

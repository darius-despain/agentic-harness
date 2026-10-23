---
name: harness-development-loop
description: Iterate on a software change through implementation, focused verification, failure diagnosis, and session evidence. Use for building, fixing, or continuing development in projects using this harness.
---

# Development loop

## When to use it

- Implement/fix/continue concrete requested behavior. Output: scoped changes, actual verification, blockers, configured journal. PR review is a separate request.

## Establish the target

- Inspect actual checkout, applicable instructions/status/origin and relevant recent evidence; confirm historical claims against current state. Preserve existing work; use project tooling/tests.
- Establish acceptance criteria. For wrappers/automation, read the documented command sequence first; explain necessary deviations and verify against the requested sequence.
- Ask only for material missing information while continuing independent work. Later constraints/status questions retain the original objective.
- Before branches, commits, pushes, connector publication, or cleanup, read [Git workflow](references/git-workflow.md).

## Implement, verify, diagnose, repeat

For an explicitly requested orchestrated/subagent loop, read [orchestration](references/orchestration.md). It adds Astra coordination and bounded Sol workers to this same loop; ordinary invocation keeps the direct workflow. Role prompts are instructions loaded by the caller, not automatically registered agents or model settings.

1. Make the smallest coherent change; inspect setup for destructive effects.
2. Run focused behavioral checks; reproduce regressions and add meaningful tests when warranted. Exercise UI/integration interactions when access permits; report unverified flows.
3. Classify failures: changed code, existing behavior, environment, credentials, external dependency. Fix one coherent cause; rerun affected checks.
4. Continue authorized progress; do not repeat unchanged blockers or weaken acceptance criteria. Finish independent work and identify the required external change.
5. Inspect the final diff and run required project checks. Broaden/repeat tests only for new changes, failures, or unresolved uncertainty.

## Close the loop

- Report resulting behavior, actual checks/blockers; distinguish syntax, tests, health, and user flows.
- Save/verify a sanitized configured journal via the sibling session-evidence skill or project logging instructions.
- Commit/publish/deploy/message only within user authorization. Completion does not trigger scheduling or self-improvement.

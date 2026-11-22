# HARN-02 — Carry current verification evidence across a tool handoff

Roadmap · [Ordered priorities](../harness-suggestions.md#ordered-priorities)

Status · Next in the approved roadmap

## Outcome and rationale

Bind one behavioral check to the task and tested checkout state so a fresh agent can resume an approved task and identify evidence that needs a rerun.

## Scope and constraints

- Pilot one project-owned check and one user-visible slice. Reuse the [task template](../../templates/task.md), [verification receipt](../../.agents/skills/harness-development-loop/references/task-contract.md#verifier-input-and-receipt), and [handoff skill](../../.agents/skills/harness-handoff/SKILL.md).
- Use the implementing setup's local command, with a small script or opt-in hook where useful. Configure commands under the project's control and capture the command, working directory, outcome, coverage or counts where available, and tested commit or working state.
- Carry the actual owner decision in the handoff. Material changes to scope or acceptance criteria go back to the owner.

## Prerequisites

- Pick a disposable consumer checkout, one behavioral smoke check, and the Codex and Antigravity surfaces available for the pilot. Record the current check behavior and limitations.

## Acceptance criteria

- A second agent can find and rerun the named check from the task reference. A relevant tracked or owned untracked edit invalidates the prior result even when `HEAD` stays fixed.
- Timeout, a skipped required check, or zero tests when a test check is required yields incomplete verification.
- The live handoff carries forward task scope and existing approval. Record client versions, skill discovery, fallback and startup time. Compare a routine fix and a small contract change to confirm how scope and risk select the fast path or full task workflow. [Native smoke checks](../agent-tools.md#smoke-checks-and-limits)

### Automated coverage

Cover pass, failure, incomplete results, and a changed local input with the same `HEAD`.

### Reproduce the check

In the pilot checkout, run the named check and save the result. Change a declared input, then start a fresh Antigravity session from the Codex task reference. Confirm it identifies the stale result and reruns the check with the prior approval still in scope.

## Approvals and verification

Record the owner's approved pilot scope and checks, the verification result and tested state, the adversarial review recommendation, and owner sign-off.

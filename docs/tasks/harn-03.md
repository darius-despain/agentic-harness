# HARN-03 — Enforce the opt-in orchestration loop on one host

Roadmap · [Ordered priorities](../harness-suggestions.md#ordered-priorities)

Status · Planned after HARN-02

## Outcome and rationale

Validate dispatch and acceptance using observed worker and checkout state so task boundaries and retry limits can be enforced by code.

## Scope and constraints

- Start with the existing implementer and verifier roles on one host. Reuse the [orchestration protocol](../../.agents/skills/harness-development-loop/references/orchestration.md) and [routing policy](../model-routing.md#worker-adapter-contract).
- Reject overlapping write assignments and replayed events. Compare checkout state at worker boundaries and require current independent verification before accepting a track. Preserve existing retry limits and stop automatic cleanup when ownership is uncertain.
- Use host permissions for actual write isolation. State comparison detects drift at checkpoints. Report missing capabilities explicitly and keep the loop opt-in.

## Prerequisites

- Use [HARN-02](harn-02.md) evidence. Before extending the runner, prove supported worker settings and an actual denied out-of-scope write on a disposable checkout. Resolve any differences between the configured worker settings and what the pilot host supports.

## Acceptance criteria

- Invalid dispatches and transitions are rejected before the next action. A duplicate event does not consume another correction attempt.
- A stale receipt, scope drift, and an exhausted retry budget prevent acceptance. Pre-existing edits survive a blocked track, and uncertain ownership prevents automated cleanup.

### Automated coverage

Cover concurrent ownership claims, a changed already-dirty file, stale and missing evidence, duplicate events, and exhausted retries. Record what the native host enforced separately from scripted results.

### Reproduce the check

Use a disposable checkout with pre-existing edits. Dispatch one valid track, attempt an overlapping assignment and a deliberately out-of-scope write, then submit stale evidence. Verify the reported boundaries and the unchanged pre-existing edits.

## Approvals and verification

Record owner approval of the host and worker settings, the verified revision and host evidence, the adversarial review recommendation, and owner sign-off.

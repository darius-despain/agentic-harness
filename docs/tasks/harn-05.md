# HARN-05 — Measure whether split review improves outcomes

Roadmap · [Ordered priorities](../harness-suggestions.md#ordered-priorities)

Status · Planned after HARN-04

## Outcome and rationale

Compare single and split adversarial review so wider use depends on material findings, false blockers, and review time.

## Scope and constraints

- Use the current reviewer as the baseline. Run each mode on the same pinned fixtures with the answer key held back from reviewers.
- Include a known behavior regression, a comparable clean change, a green check that misses the relevant behavior, and a re-review with a moved head.
- Use the early Codex-to-Antigravity handoff from [HARN-02](harn-02.md) as the portability baseline. Report scripted, local, and live observations separately. [Evaluation boundary](../../evals/agents/README.md#experiment-boundary)

## Prerequisites

- Reserve the fixtures and expected outcomes before tuning [HARN-04](harn-04.md). Confirm the known defects with an independent check.

## Acceptance criteria

- Report material findings caught, false blockers, elapsed review time, and coverage limits for both modes.
- Record whether a moved head required fresh verification. Use the observed benefit and extra time to decide whether split review earns wider use.

### Automated coverage

Keep fixed regression and clean fixtures with a held-back rubric. Score review outcomes at the pinned revision. Treat scripted replay as contract coverage and use live runs for claims about native execution.

### Reproduce the check

Run both review modes on each fixture with the same acceptance criteria and artifact access. Verify the findings against the rubric and compare the results and elapsed time.

## Approvals and verification

Record the evaluation scope, fixture and reviewed revisions, results, adversarial review recommendation, and owner sign-off on the rollout decision.

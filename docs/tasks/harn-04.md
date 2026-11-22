# HARN-04 — Give each agent one responsibility and one output

Roadmap · [Ordered priorities](../harness-suggestions.md#ordered-priorities)

Status · Planned after HARN-03

## Outcome and rationale

Use narrowly scoped agent files so an orchestrator can delegate a specific job with a compact input and a result it can verify.

## Scope and constraints

| Role | Responsibility and output |
| --- | --- |
| Investigator | Diagnose a bounded repository issue and return local evidence. |
| Researcher | Return a sourced brief that identifies uncertainties. |
| UX designer | Specify a user flow, edge states, and accessibility criteria. |
| Verifier | Run the named checks and return the result for the tested state. |
| Behavior reviewer | Challenge whether a pinned diff satisfies the original requirements and preserves expected behavior. |
| Evidence reviewer | Judge whether the checks cover the intended behavior and plausible failures. |

Extend existing role files and load the selected role on demand. Use one reviewer for routine PRs. For an explicitly selected high-risk review, give the two reviewers fresh contexts with the same original criteria and pinned artifacts. The orchestrator checks and deduplicates findings and owns the recommendation. Tool permissions come from verified host capabilities. [Existing PR reviewer](../../.agents/skills/harness-pr-review/agents/pr-reviewer.md)

## Prerequisites

- Establish [HARN-03](harn-03.md) boundaries and reserve clean and regression cases for [HARN-05](harn-05.md) before tuning reviewer prompts.
- Choose real tasks that need the researcher and UX designer outputs before piloting those roles. Define additional specialist roles once their responsibilities are clear.

## Acceptance criteria

- Dispatch loads only the assigned role and rejects unknown roles and unsupported capabilities. An implementer cannot count as its own independent verifier.
- Each split reviewer returns findings for its assigned responsibility. Routine review uses the current single reviewer by default.

### Automated coverage

Cover valid and unknown roles, unsupported capabilities, and loss of independence when one worker is assigned both implementation and verification.

### Reproduce the check

Run one routine review and one explicitly selected split review on a pinned fixture. Compare loaded roles, the packets they received, and the orchestrator's final recommendation.

## Approvals and verification

Record agreed role inputs, outputs and capabilities, the verified revision, the adversarial review recommendation, and owner sign-off.

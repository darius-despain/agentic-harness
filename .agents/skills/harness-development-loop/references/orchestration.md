# Orchestrated development

Use when the user requests orchestration or subagents for development. Keep the parent skill's acceptance, verification, Git, credential and evidence rules. This mode adds no publication or deployment permission.

## Roles and runtime selection

| Role prompt | Preferred model | Reasoning | Scope |
| --- | --- | --- | --- |
| [Orchestrator](../agents/orchestrator.md) | Astra | high | Target, dispatch, integration, completion |
| [Implementer](../agents/implementer.md) | Sol | medium | One coherent change in assigned files |
| [Verifier](../agents/verifier.md) | Sol | medium | Independent behavioral verification; read-only by default |
| [Investigator](../agents/investigator.md) | Sol | high | Conditional failure diagnosis; read-only by default |

The root session should already use the requested Astra model. Do not claim a prompt switches its model. Resolve exact available model IDs from the current runtime, preserving a user-specified generation; pass model and reasoning through supported spawn/configuration fields. For example, a runtime offering `gpt-6-astra` and `gpt-6-sol` can use those IDs. If different-model spawning requires fresh context, use that mode and supply the task packet explicitly. Markdown role files and `agents/openai.yaml` do not enforce model routing.

If the requested model or delegation is unavailable, disclose the limitation. Continue authorized work directly where useful; do not silently claim the requested topology ran. Do not install runtime configuration or change global defaults as part of using this mode.

## Dispatch and integration

1. Root reads [orchestrator](../agents/orchestrator.md), establishes checkout ownership and observable acceptance criteria, then uses the [task contract](task-contract.md). Load only the role needed for each worker; supply its absolute prompt path and the absolute parent skill path, or inline their relevant instructions when file access is unavailable.
2. Keep trivial changes direct. For larger work, dispatch one coherent implementation task. Parallelize only independent work with disjoint file ownership and explicit interface agreements. Prefer a small pool; use at most three simultaneous workers and the runtime's lower limit, reserving capacity for diagnosis where practical. Only the root delegates.
3. Workers share a filesystem unless the runtime says otherwise. A role's read-only default is an instruction, not process isolation. Assign one writer per mutable file, including tests and generated artifacts. Coordinate shared test services, caches and outputs; serialize commands that mutate the same resource. Stop affected work and reassign ownership before overlapping edits or root integration.
4. Once relevant files are stable, give a verifier the acceptance criteria, actual change scope and checks. Let it inspect the diff and behavior independently rather than supplying the implementer's conclusions as truth. Identify the checked revision or stable working-tree state; edits afterward invalidate affected results.
5. Route clear defects to the existing implementer. Use an investigator only when the cause is uncertain. Classify changed code, existing behavior, environment, credentials and external dependencies separately. After two unsuccessful correction cycles on the same failure, the root reassesses the premise and owns the next diagnostic decision; this is not a completion limit or permission to abandon independent work. Do not retry unchanged access failures.
6. Root checks returned evidence, resolves conflicting findings, inspects the combined diff and runs any outstanding required checks. Recheck affected behavior after integration. Keep syntax, tests, service health and user-flow results distinct. Formal PR/branch review remains a separately requested `harness-pr-review` workflow.
7. Root alone writes and verifies the configured journal and reports completion. Workers return evidence; they do not create duplicate session records. Preserve authorized commit/PR attribution using the actual committing runtime identity.

## Context and cost

- Start workers with a focused fresh-context packet rather than the full conversation. Include relevant user constraints, existing work and acceptance criteria so savings do not remove necessary context.
- Reuse workers for corrections to the same task; send changed requirements or evidence as deltas. Avoid speculative scouts, duplicate implementation and habitual full-suite reruns.
- Require concise paths, commands, outcomes and unresolved questions. Root reads supporting code/output when needed; worker confidence alone is not validation.
